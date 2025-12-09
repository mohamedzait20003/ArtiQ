FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN chmod +x ./src/run

ENTRYPOINT ["./src/run"]
