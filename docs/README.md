# PatentPath Setup Guide

PatentPath is an AI-guided innovation and prior-art platform that combines OPS search, NLP scoring, and AI-assisted gap analysis.

## Prerequisites

- Docker Desktop (with Docker Compose)
- EPO OPS account and API credentials
- Anthropic API key
- Git

## Installation

1. Clone the repository.

```bash
git clone <repository-url>
cd "PatentPath - AI-Guided Innovation & Prior Art Platform"
```

2. Copy the environment template.

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

3. Fill required credentials in .env.

- DATABASE_URL
- REDIS_URL
- EPO_CONSUMER_KEY
- EPO_CONSUMER_SECRET
- ANTHROPIC_API_KEY
- JWT_SECRET_KEY
- CORS_ORIGINS

4. Build and run services.

```bash
docker compose up --build
```

5. Verify running services.

- Frontend: http://localhost:5173
- API health: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

## First Use Walkthrough

1. Register a new account from the login page.
2. Create a project and add your invention problem statement.
3. Generate and review CQL, then run a prior-art search.
4. Review ranked patents and inspect risk labels.
5. Trigger gap analysis and review innovation opportunities.
6. Generate and download a patent preparation report.

## Troubleshooting

### Docker containers fail to start

- Ensure Docker Desktop is running.
- Check for occupied ports (5432, 6379, 8000, 5173).
- Rebuild images:

```bash
docker compose down
docker compose up --build
```

### EPO OPS authentication errors

- Confirm EPO credentials in .env are valid.
- Verify token and quota limits in OPS dashboard.

### Search returns no results

- Broaden the problem statement with wider technical terms.
- Remove restrictive filters (country/date/applicant).
- Try alternative IPC classes from the browser helper.

### Gap analysis is slow or fails

- Check ANTHROPIC_API_KEY in .env.
- Validate network access to Anthropic API.
- Retry after confirming backend and worker logs.

### PDF report generation fails

- Confirm worker and Redis services are healthy.
- Ensure gap analysis has completed for the session.
- Re-run report generation after backend restart.
