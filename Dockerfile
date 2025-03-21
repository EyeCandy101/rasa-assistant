# Stage 1: Install Dependencies
FROM arm64v8/python:3.9-slim AS builder
WORKDIR /app

# Install build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy dependencies
COPY ./requirements.txt /app/

# Install pre-built wheels for spaCy dependencies
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    cython==0.29.32 \
    blis==0.7.9 \
    spacy==3.4.4 \
    --extra-index-url https://www.piwheels.org/simple

# Install Rasa and other dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_md && \
    python -c "import en_core_web_md; print(en_core_web_md.__file__)" && \
    python -c "import spacy; print(spacy.util.get_data_path())"
    
# Stage 2: Minimal Runtime
FROM arm64v8/python:3.9-slim
WORKDIR /app

# Copy installed dependencies properly
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
# Copy spaCy language models
#COPY --from=builder /root/.cache/spacy/ /root/.cache/spacy/

# Copy Rasa project files
COPY ./rasa /app/rasa

# Copy pre-trained model
COPY ./rasa/models/latest.tar.gz /app/models/latest.tar.gz

# Expose Rasa API
EXPOSE 5005

# Run Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--model", "/app/models/latest.tar.gz"]
