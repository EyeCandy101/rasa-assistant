# Stage 1: Install Dependencies
FROM arm64v8/python:3.9-slim AS builder
WORKDIR /app

# Copy dependencies
COPY ./requirements.txt /app/

# Install Rasa and dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_md

# Stage 2: Minimal Runtime
FROM arm64v8/python:3.9-slim
WORKDIR /app

# Copy installed dependencies properly
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
# Copy spaCy language models
COPY --from=builder /root/.cache/spacy/ /root/.cache/spacy/

# Copy Rasa project files
COPY ./rasa /app/rasa

# Copy pre-trained model
COPY ./rasa/models/latest.tar.gz /app/models/latest.tar.gz

# Expose Rasa API
EXPOSE 5005

# Run Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--model", "/app/models/latest.tar.gz"]
