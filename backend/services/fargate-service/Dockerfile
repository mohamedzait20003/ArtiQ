FROM python:3.11-slim

WORKDIR /app

# Declare build arguments for tokens
ARG HF_TOKEN
ARG GH_TOKEN
ARG MONGODB_URI
ARG ARTIFACT_ENCRYPTION_KEY

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared lib (will be copied to context by CI/CD)
COPY lib/ ./lib/

# Copy app directory
COPY app/ ./app/

# Copy include module
COPY include/ ./include/

# Set environment variables from build args
ENV GH_TOKEN=${GH_TOKEN}
ENV HF_TOKEN=${HF_TOKEN}
ENV MONGODB_URI=${MONGODB_URI}
ENV ARTIFACT_ENCRYPTION_KEY=${ARTIFACT_ENCRYPTION_KEY}

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Run the main application
CMD ["python", "-m", "app.main"]
