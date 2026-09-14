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

def get_docker_executable():
    # 1. เช็กผ่าน system PATH ตามปกติ
    docker_bin = shutil.which('docker')
    if docker_bin:
        return docker_bin

    # 2. หากไม่พบใน system PATH ให้เช็กจาก System Direct Paths (รวมถึง /usr/bin/docker)
    known_paths = [
        '/usr/bin/docker',          # Ubuntu / Debian default path
        '/usr/local/bin/docker',    # Custom / Manual install
        '/snap/bin/docker',         # Ubuntu Snap install
        '/bin/docker'
    ]

    for path in known_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    return None

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
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    docker_bin = get_docker_executable()

    # หากเช็กทุก path แล้วยังไม่เจอ
    if not docker_bin:
        return jsonify({
            "status": "error",
            "message": "ไม่พบคำสั่ง docker ในระบบ"
        }), 404

    try:
        # ใช้ docker_bin (ที่เป็น Full Path เช่น /usr/bin/docker) ในการรัน
        result = subprocess.run(
            [docker_bin, "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            check=True
        )

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))

        return jsonify({
            "status": "success",
            "data": containers
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": "ไม่สามารถดึงข้อมูล Docker ได้ (โปรดเช็กว่า Docker service กำลังทำงานอยู่หรือไม่)",
            "details": e.stderr.strip()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)