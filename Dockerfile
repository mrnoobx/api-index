FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

# ✅ Correct worker: use gthread for async Flask
CMD ["gunicorn", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:$PORT", "terabox_api:app"]
