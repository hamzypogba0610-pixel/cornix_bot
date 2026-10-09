FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY cfcx/ ./cfcx/
COPY configs/ ./configs/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "cfcx.serving.api:app", "--host", "0.0.0.0", "--port", "8000"]
