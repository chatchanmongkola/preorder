# Dev-only image. Runs FastAPI with autoreload against the source mounted
# from the host by docker-compose. Not used for the Vercel production deploy.
FROM python:3.11-slim

WORKDIR /app

# System deps needed to build psycopg2 / bcrypt wheels on some platforms.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
