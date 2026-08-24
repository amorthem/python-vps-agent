FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# รัน Gunicorn พร้อมตั้งค่า Workers (สูตรทั่วไป: 2 * จำนวน CPU core + 1)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]