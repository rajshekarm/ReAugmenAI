FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY services/ingestion/src /app/src
RUN pip install --no-cache-dir fastapi 'uvicorn[standard]'
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "ingestion.main:app", "--host", "0.0.0.0", "--port", "8000"]
