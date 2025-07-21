FROM python:3.11-slim

WORKDIR /app

COPY terabox_api.py requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "terabox_api.py"]
