# Gunakan image Python resmi
FROM python:3.11-slim

# Set direktori kerja di container
WORKDIR /app

# Salin file requirements.txt dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi project ke dalam container
COPY . .

# Jalankan Uvicorn dengan app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
