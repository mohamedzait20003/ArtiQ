FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared lib (will be copied to context by CI/CD)
COPY lib/ ./lib/

# Copy app directory
COPY app/ ./app/

# Copy include module
COPY include/ ./include/

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Run the main application
CMD ["python", "-m", "app.main"]
