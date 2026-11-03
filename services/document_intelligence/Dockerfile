FROM python:3.11-slim
WORKDIR /app
COPY services/document_intelligence/src /app/src
RUN pip install --no-cache-dir fastapi 'uvicorn[standard]' 'pymupdf>=1.24,<2'
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "document_intelligence.main:app", "--host", "0.0.0.0", "--port", "8000"]
