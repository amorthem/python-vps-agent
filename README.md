# VPS Metrics API

A lightweight, minimal Python Flask microservice to monitor real-time CPU and RAM usage/availability on Ubuntu / Linux VPS servers via a simple HTTP GET endpoint secured with a query parameter token.

---

## 🚀 Features

- **Lightweight & Fast**: Consumes minimal system resources (~20-30 MB RAM).
- **Simple Authentication**: Secures your metrics endpoint using a query parameter token (`?token=YOUR_TOKEN`).
- **Real-time Stats**: Uses `psutil` to fetch precise CPU usage percentage and detailed RAM metrics (Total, Used, Available, Usage %).
- **JSON Output**: Clean and standardized JSON format ready for backend consumption or dashboard integration.

---

## 🛠️ Requirements

- **OS**: Ubuntu 20.04 / 22.04 / 24.04 (or any Debian-based Linux distribution)
- **Python**: Python 3.8+

---

## 📦 Installation & Setup

### 1. Install System Dependencies

Update packages and install `python3-psutil`, `python3-flask`, and `python3-gunicorn` using `apt`:

```bash
sudo apt update && sudo apt install -y python3-psutil python3-flask python3-gunicorn
```

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/vps-metrics-api.git
cd vps-metrics-api
```

### 3. Configure Your Secret Token

Open `app.py` in your preferred editor (e.g., `nano app.py`) and change `API_TOKEN` to a secure key:

```python
API_TOKEN = "your_secret_token_here"
```

---

## 🏃 Running the Application

### Option A: Direct Test Run

Run the app directly with Python:

```bash
python3 app.py
```

*The server will start listening on port `5000` (`http://0.0.0.0:5000`).*

---

### Option B: Background Service with `systemd` (Recommended)

To ensure the API starts automatically upon server reboot and stays running in the background:

1. Create a `systemd` service file:

```bash
sudo nano /etc/systemd/system/vps-metrics.service
```

2. Paste the following configuration (adjust `/path/to/vps-metrics-api` accordingly):

```ini
[Unit]
Description=VPS Metrics Micro-API Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/vps-metrics-api
ExecStart=/usr/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vps-metrics
sudo systemctl start vps-metrics
```

4. Check status:

```bash
sudo systemctl status vps-metrics
```

---

## 📡 API Usage

### Endpoint

```http
GET /metrics?token=YOUR_SECRET_TOKEN
```

### Example Request

```bash
curl -X GET "http://<YOUR_SERVER_IP>:5000/metrics?token=your_secret_token_here"
```

### Example Response (`200 OK`)

```json
{
  "status": "success",
  "cpu": {
    "usage_percent": 12.5
  },
  "ram": {
    "total_mb": 4096,
    "used_mb": 976,
    "available_mb": 3120,
    "usage_percent": 23.8
  }
}
```

### Error Response (`401 Unauthorized`)

If the token is invalid or missing:

```json
{
  "status": "error",
  "message": "Unauthorized: Invalid or missing token"
}
```

---

## 🔒 Security Tips

- **Firewall Rules**: If only your main backend server queries this API, restrict port `5000` using `ufw`:
  ```bash
  sudo ufw allow from <YOUR_BACKEND_IP> to any port 5000 proto tcp
  ```
- **HTTPS**: For production environments across public networks, consider putting `Nginx` as a reverse proxy with Let's Encrypt SSL/TLS.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
