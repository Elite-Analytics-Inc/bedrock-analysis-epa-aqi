FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    duckdb==1.5.1 \
    fastavro==1.9.7

COPY bedrock_sdk/ /bedrock_sdk/
COPY analysis.py .

CMD ["python", "analysis.py"]
