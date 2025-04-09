# Stage 1: Install Dependencies
FROM arm64v8/python:3.9-slim AS builder
WORKDIR /app

# Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements
COPY ./requirements.txt /app/

# Set environment variables to reduce Python memory usage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install only runtime dependencies
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install --extra-index-url https://www.piwheels.org/simple \
    -r requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_md

# Stage 2: Runtime
FROM arm64v8/python:3.9-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/rasa /usr/local/bin/
COPY --from=builder /usr/local/bin/python /usr/local/bin/

# Copy only the model file
COPY ./rasa/models/latest.tar.gz /app/models/latest.tar.gz

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose Rasa API
EXPOSE 5005

# Run Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--model", "/app/models/latest.tar.gz", "--endpoints", "/app/config/endpoints.yml"]
