from flask import Flask, jsonify, request
import psutil

app = Flask(__name__)

# กำหนด Token ที่ต้องส่งมาด้วย
API_TOKEN = "your_secret_token_here"

@app.route('/metrics', methods=['GET'])
def get_metrics():
    # รับค่า token จาก query parameter (?token=...)
    token = request.args.get('token')
    
    # ตรวจสอบว่ามี token หรือไม่ และถูกต้องหรือไม่
    if not token or token != API_TOKEN:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
