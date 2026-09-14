import os
import json
import shutil
import subprocess
from flask import Flask, jsonify, request
import psutil

app = Flask(__name__)

# ดึงค่า API_TOKEN จาก Environment Variable
# หากหาไม่เจอ จะใช้ค่า default 'fallback_secret_token'
API_TOKEN = os.getenv("API_TOKEN", "fallback_secret_token")

def check_auth():
    token = request.args.get('token')
    if not token or token != API_TOKEN:
        return False
    return True

@app.route('/metrics', methods=['GET'])
def get_metrics():
    if not check_auth():
        return jsonify({
            "status": "error",
            "message": "Unauthorized: Invalid or missing token"
        }), 401

    cpu_percent = psutil.cpu_percent(interval=1)
    vm = psutil.virtual_memory()
    
    return jsonify({
        "status": "success",
        "cpu": {
            "usage_percent": cpu_percent
        },
        "ram": {
            "total_mb": vm.total // (1024 * 1024),
            "used_mb": vm.used // (1024 * 1024),
            "available_mb": vm.available // (1024 * 1024),
            "usage_percent": vm.percent
        }
    })

@app.route('/docker-stats', methods=['GET'])
def get_docker_stats():
    if not check_auth():
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    docker_bin = '/usr/bin/docker'

    # ตรวจสอบว่าได้ทำการ mount binary เข้ามาใน Container แล้วหรือยัง
    if not os.path.exists(docker_bin):
        return jsonify({
            "status": "error",
            "message":
                "ไม่พบ /usr/bin/docker ใน Container (โปรด mount -v"
                " /usr/bin/docker:/usr/bin/docker)"
        }), 404

    try:
        result = subprocess.run([
            docker_bin,
            "stats",
            "--no-stream",
            "--format",
            "{{json .}}",
        ],
                                capture_output=True,
                                text=True,
                                check=True)

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))

        return jsonify({"status": "success", "data": containers})

    except subprocess.CalledProcessError as e:
        # หากพบ error ตรงนี้ มักเกิดจากไม่ได้ mount /var/run/docker.sock
        return jsonify({
            "status": "error",
            "message":
                "ไม่สามารถเข้าถึง Docker Daemon ได้ (โปรดตรวจสอบการ mount"
                " /var/run/docker.sock)",
            "details": e.stderr.strip(),
        }), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)