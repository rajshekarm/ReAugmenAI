FROM python:3.11-slim
WORKDIR /app
COPY services/ingestion/src /app/src
RUN pip install --no-cache-dir fastapi 'uvicorn[standard]' sqlalchemy psycopg[binary] boto3 python-multipart
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "ingestion.main:app", "--host", "0.0.0.0", "--port", "8000"]
