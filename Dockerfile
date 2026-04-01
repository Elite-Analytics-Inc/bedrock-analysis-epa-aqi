FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir duckdb==1.5.1 adbc-driver-flightclient==1.4.0

WORKDIR /app
COPY bedrock_sdk/ /bedrock_sdk/
COPY analysis.py .

CMD ["python", "analysis.py"]
