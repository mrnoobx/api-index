FROM python:3.11-slim

WORKDIR /app

COPY terabox_api.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Expose Flask port
EXPOSE 5000

# Start using Gunicorn (production server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "terabox_api:app"]
