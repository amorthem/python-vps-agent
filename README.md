# Flask System Metrics API (Dockerized)

แอปพลิเคชัน REST API สำหรับดึงข้อมูลการใช้งาน CPU และ RAM ของเครื่อง Host (Ubuntu) เขียนด้วย Python (Flask) รันผ่าน Gunicorn บน Docker Compose รองรับการทำงานให้อัตโนมัติหลัง Reboot เครื่อง และมีความปลอดภัยด้วย API Token authentication ผ่าน Environment Variables

## 🛠️ โครงสร้างโปรเจกต์ (Project Structure)

```text
.
├── app.py              # โค้ดหลัก Flask API
├── Dockerfile          # สำหรับ Build Docker Image (ใช้ Gunicorn)
├── docker-compose.yml  # ไฟล์กำหนดค่าบริการและการรัน Container
├── requirements.txt    # รายชื่อ Python packages (Flask, psutil, Gunicorn)
├── .env                # ไฟล์เก็บ Sensitive Config (เช่น API Token)
└── README.md           # เอกสารอธิบายการใช้งาน
```

### 1. Getting Started

```bash
git clone https://github.com/amorthem/python-vps-agent
cd vps-metrics-api
```

### 2. Configure Your Secret Token
```bash
cp .env.example .env
```

### 3. Build image
```bash
docker compose up -d --build
```

### 4. Test Request
```bash
curl "http://localhost:8000/metrics?token=your_super_secret_token_12345"
```

## Response
```bash
{
  "status": "success",
  "cpu": {
    "usage_percent": 12.5
  },
  "ram": {
    "available_mb": 11420,
    "total_mb": 16384,
    "usage_percent": 30.3,
    "used_mb": 4964
  }
}
```