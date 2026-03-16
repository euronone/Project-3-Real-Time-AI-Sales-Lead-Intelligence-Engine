# SalesIQ Deployment Guide

## Local Development

### Prerequisites
- Docker Desktop
- Python 3.12+
- Node.js 20+

### Quick Start (Docker Compose)

```bash
# Clone and enter project
cd "Project-3-Real-Time-AI-Sales-Lead-Intelligence-Engine"

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Fill in required keys (see Environment Variables section below)
# Then start all services:
docker-compose up -d

# Apply DB migrations
cd backend && alembic upgrade head

# Check services are running
docker-compose ps
```

### Manual Local Development (no Docker)

```bash
# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Celery worker (separate terminal)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info -Q transcription,analysis,prediction,notifications

# Frontend (separate terminal)
cd frontend
npm install
npm run dev    # starts on http://localhost:3000
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
# App
APP_ENV=development
APP_SECRET_KEY=<random-256-bit-secret>
APP_CORS_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=postgresql+asyncpg://salesiq:salesiq@localhost:5432/salesiq

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=<random-256-bit-secret>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=<your-openai-key>
OPENAI_MODEL=gpt-4o
OPENAI_WHISPER_MODEL=whisper-1

# Twilio
TWILIO_ACCOUNT_SID=<your-sid>
TWILIO_AUTH_TOKEN=<your-token>
TWILIO_PHONE_NUMBER=<your-number>
TWILIO_API_KEY_SID=<api-key-sid>
TWILIO_API_KEY_SECRET=<api-key-secret>

# AWS S3
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_S3_BUCKET=salesiq-recordings
AWS_S3_REGION=us-east-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
NEXT_PUBLIC_TWILIO_DEVICE_TOKEN_URL=http://localhost:8000/api/v1/calls/token
```

---

## CI/CD (GitHub Actions)

Three workflows in `.github/workflows/`:

| Workflow | File | Trigger | Steps |
|---|---|---|---|
| Backend CI | `ci-backend.yml` | Push to any branch | ruff lint → mypy → pytest |
| Frontend CI | `ci-frontend.yml` | Push to any branch | eslint → tsc --noEmit → next build → vitest |
| Deploy | `deploy.yml` | Push to `main` or tag | Full CI → build Docker images → push to ECR → deploy to ECS |

**Required GitHub Secrets:**
- `OPENAI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `JWT_SECRET_KEY`, `APP_SECRET_KEY`
- `DATABASE_URL` (production RDS)
- `REDIS_URL` (production ElastiCache)

---

## Production Deployment (AWS)

### Infrastructure

| Service | AWS Component |
|---|---|
| FastAPI API | ECS Fargate (auto-scaled) |
| Celery Workers | ECS Fargate (separate task, 4 worker pools) |
| PostgreSQL | AWS RDS PostgreSQL 16 (Multi-AZ) |
| Redis | AWS ElastiCache Redis 7 |
| Call Recordings | AWS S3 (private bucket, BlockPublicAccess on) |
| Frontend | Next.js on ECS or Vercel; static assets via CloudFront |
| Secrets | AWS Secrets Manager |
| Monitoring | CloudWatch Logs + Metrics; optionally Prometheus + Grafana |

### Celery Worker Pools

Run separate ECS tasks per queue for independent scaling:

```bash
# Transcription workers (scale based on queue depth)
celery -A app.tasks.celery_app worker -Q transcription --concurrency=4

# Analysis workers (GPT-4o calls — limit concurrency for cost control)
celery -A app.tasks.celery_app worker -Q analysis --concurrency=2

# Prediction workers
celery -A app.tasks.celery_app worker -Q prediction --concurrency=4

# Notification workers
celery -A app.tasks.celery_app worker -Q notifications --concurrency=8
```

### Health Checks

The backend exposes:
- `GET /health` — returns `{"status": "ok"}` (used by ECS health check and load balancer)
- `GET /ready` — returns `{"status": "ready"}` when DB and Redis are reachable

### Deployment Steps (manual)

```bash
# 1. Build and push Docker images
docker build -t salesiq-backend ./backend
docker tag salesiq-backend:latest <ECR_URI>/salesiq-backend:latest
docker push <ECR_URI>/salesiq-backend:latest

docker build -t salesiq-frontend ./frontend
docker tag salesiq-frontend:latest <ECR_URI>/salesiq-frontend:latest
docker push <ECR_URI>/salesiq-frontend:latest

# 2. Apply migrations (run as one-time ECS task or via CI)
docker run --env-file .env salesiq-backend alembic upgrade head

# 3. Update ECS service to use new image
aws ecs update-service --cluster salesiq-prod --service salesiq-api --force-new-deployment
aws ecs update-service --cluster salesiq-prod --service salesiq-celery --force-new-deployment
```

### Production S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::salesiq-recordings/*",
    "Condition": {
      "StringNotEquals": {
        "aws:PrincipalArn": "arn:aws:iam::<account>:role/salesiq-backend-task-role"
      }
    }
  }]
}
```

Access recordings only via presigned URLs generated by `StorageService.get_presigned_url()`.

---

## Rollback Procedure

1. ECS service rollback: re-deploy previous task definition revision.
2. Database rollback: `alembic downgrade -1` (requires staging validation first).
3. Never delete migration files — always create a new `downgrade` migration if needed.
