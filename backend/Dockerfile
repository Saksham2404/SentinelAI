FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend app and supporting files from the context
COPY app /app/backend/app
COPY models /app/backend/models
COPY data /app/data
COPY index_knowledge_base.py /app/index_knowledge_base.py
COPY create_tables.py /app/create_tables.py

ENV PYTHONPATH=/app
ENV PORT=8001

EXPOSE 8001

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
