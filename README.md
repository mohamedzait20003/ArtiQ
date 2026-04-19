# ArtiQ — AI/ML Artifact Registry & Evaluation Platform

ArtiQ is a full-stack platform for discovering, registering, and automatically scoring AI/ML artifacts (models and datasets) from GitHub and HuggingFace. It runs a multi-metric evaluation pipeline and surfaces a single trustworthiness score per artifact.

---

## Architecture

```
Angular Frontend (AWS Amplify)
        │
        ▼
AWS API Gateway → Lambda Service (FastAPI + Mangum)
                        │
                        ▼ spawns ephemeral task
                AWS Fargate (Evaluation Pipeline)
                        │
                        ▼
                   MongoDB Atlas
```

**Stack**

| Layer | Technology |
|---|---|
| Frontend | Angular 17, TypeScript, Node.js 22 |
| API | Python 3.11, FastAPI, AWS Lambda (SAM) |
| Evaluation | AWS Fargate, Docker (ECR) |
| Database | MongoDB Atlas |
| Auth | JWT + bcrypt |
| CI/CD | GitHub Actions |
| Cloud | AWS (Lambda, Fargate, ECR, Amplify, S3) |

---

## Evaluation Pipeline

When an artifact is submitted, Fargate runs a 7-step pipeline:

```
1. Validate Artifact
2. Fetch Metadata (GitHub / HuggingFace)
3. Parallel Evaluation ──┬── Bus Factor
                         ├── Performance Claims
                         ├── Ramp-up Time
                         ├── Size Score
                         ├── License
                         ├── Availability
                         ├── Code Quality
                         ├── Dataset Quality
                         ├── Reviewedness
                         └── Download & Upload
4. Lineage Extraction
5. Tree Score Calculation
6. Aggregate Scores → Net Score
7. Save Ratings to DB
```

The **Net Score** is the average across all applicable metrics, giving each artifact a single trustworthiness rating.

---

## Project Structure

```
.
├── frontend/                        # Angular application
└── backend/
    ├── lib/                         # Shared utilities (AWS, cache, pipeline, ORM)
    ├── database/
    │   ├── migrations/              # Schema migrations
    │   └── seeders/                 # Seed data
    ├── scripts/                     # DB, key generation, and run scripts
    └── services/
        ├── lambda-service/          # FastAPI REST API (deployed via AWS SAM)
        └── fargate-service/         # Evaluation pipeline (deployed via Docker/ECR)
            └── app/
                ├── jobs/            # One file per pipeline step/metric
                ├── models/          # MongoDB ODM models
                ├── providers/       # GitHub, HuggingFace, and LLM agents
                └── utils/           # Encryption, artifact helpers
```

---

## Getting Started

### Prerequisites

- [Node.js 22+](https://nodejs.org/)
- [Python 3.11+](https://www.python.org/downloads/)
- [Angular CLI](https://angular.io/cli) — `npm install -g @angular/cli`
- [Docker](https://www.docker.com/) (for Fargate service)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) (for Lambda deployment)
- MongoDB instance (local or Atlas)

### Environment Setup

Copy the example env file and fill in your values:

```bash
cp backend/.env.example backend/.env
```

Required variables:

```
MONGODB_URI=
ARTIFACT_ENCRYPTION_KEY=
JWT_SECRET_KEY=
PASSWORD_SALT=
GH_TOKEN=
HF_TOKEN=
AWS_REGION=us-east-2
```

Generate secrets with the provided scripts:

```bash
python backend/scripts/generate_jwt_secret.py
python backend/scripts/generate_key.py
python backend/scripts/generate_salt.py
```

### Installation

```bash
git clone https://github.com/mohamedzait20003/ArtiQ.git
cd ArtiQ
```

```bash
# Backend dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### Database Setup

```bash
python backend/scripts/migrate.py   # Run migrations
python backend/scripts/seed.py      # Seed roles and admin users
```

### Running Locally

```bash
# Lambda API (backend)
cd backend/services/lambda-service
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
ng serve
```

Navigate to `http://localhost:4200`.

---

## CI/CD

GitHub Actions runs on every push and pull request:

| Job | Trigger |
|---|---|
| Lambda — test & lint | All branches |
| Fargate — lint & validate | All branches |
| Frontend — build & test | All branches |
| Build & push Fargate image to ECR | Push to `main` |
| Deploy Lambda via AWS SAM | Push to `main` |
| Deploy frontend to AWS Amplify | Push to `main` |

---

## Roles

| Role | Access |
|---|---|
| Admin | Full access — manage users, roles, artifacts |
| Manager | Submit and review artifacts |
| User | Browse and view artifact ratings |
