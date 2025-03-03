# Stage 1: Install Dependencies
FROM arm64v8/python:3.9-slim AS builder
WORKDIR /app

# Copy dependencies
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Stage 2: Minimal Runtime
FROM arm64v8/python:3.9-slim
WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app /app

# Copy Rasa project files
COPY . .

# Copy pre-trained model
COPY rasa/models/latest.tar.gz /app/models/latest.tar.gz

# Expose Rasa API
EXPOSE 5005

# Run Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--model", "/app/models/latest.tar.gz"]
