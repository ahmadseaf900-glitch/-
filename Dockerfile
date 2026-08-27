FROM python:3.10-slim

# تثبيت الحزم الأساسية للنظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# فتح المنفذ الخاص بـ Render
EXPOSE 10000

# أمر تشغيل السيرفر بواسطة Gunicorn لضمان استقرار Flask
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:10000", "main:app"]

