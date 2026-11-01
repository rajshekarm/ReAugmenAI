FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml README.md ./
COPY apps ./apps
RUN pip install --no-cache-dir .
RUN useradd -r -u 10001 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
