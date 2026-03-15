# SalesIQ Deployment Guide

## Local Development

```bash
# Start all services
docker-compose up -d

# Backend only
cd backend && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm run dev

# Celery worker
cd backend && celery -A app.tasks.celery_app worker --loglevel=info
```

## Environment Setup

1. Copy `.env.example` files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

2. Fill in required API keys:
   - `OPENAI_API_KEY` — OpenAI API key for GPT-4o and Whisper
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` — Twilio credentials
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` — AWS S3 access

3. Run database migrations:
   ```bash
   cd backend && alembic upgrade head
   ```

## Production Deployment

See `docker-compose.prod.yml` for production container configuration.

Recommended cloud setup:
- **Compute**: AWS ECS or Kubernetes
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Storage**: AWS S3
- **CDN**: CloudFront
