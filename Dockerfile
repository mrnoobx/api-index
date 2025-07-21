FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

# ✅ Fixed: Using gthread worker
CMD ["gunicorn", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:5000", "terabox_api:app"]
