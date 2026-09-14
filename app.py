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
            "message": "Unauthorized: Invalid or missing token"
        }), 401

    # 1. ตรวจสอบว่ามีคำสั่ง docker ในเครื่องหรือไม่
    if not shutil.which('docker'):
        return jsonify({
            "status": "error",
            "message": "ไม่พบคำสั่ง docker ในระบบ"
        }), 404

    try:
        # 2. เรียกใช้คำสั่ง docker stats
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            check=True
        )

        # 3. แปลงผลลัพธ์จาก string JSON (บรรทัดต่อบรรทัด) ให้เป็น Python List
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))

        return jsonify({
            "status": "success",
            "data": containers
        })

    except subprocess.CalledProcessError as e:
        # เกิดกรณีที่รัน docker ได้ แต่มี error (เช่น Docker daemon ไม่ได้เปิด หรือไม่มีสิทธิ์เข้าถึง socket)
        return jsonify({
            "status": "error",
            "message": "ไม่สามารถดึงข้อมูล Docker ได้ (โปรดเช็กว่า Docker Daemon ทำงานอยู่หรือไม่)",
            "details": e.stderr.strip()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)