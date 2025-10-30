FROM python:3.13-slim

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Default command
ENTRYPOINT ["python", "main.py"]