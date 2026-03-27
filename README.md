# PatentPath - AI-Guided Innovation and Prior Art Platform

PatentPath is an academic full-stack platform that helps innovation teams transform invention ideas into structured prior-art insights.
It combines Espacenet retrieval, transparent NLP scoring, AI-assisted gap analysis, and report generation in one workflow.

## Architecture Diagram

- Main workflow: [diagrams/main_workflow.svg](diagrams/main_workflow.svg)
- NLP pipeline: [diagrams/nlp_pipeline.svg](diagrams/nlp_pipeline.svg)
- Data flow: [diagrams/data_flow.svg](diagrams/data_flow.svg)

## Tech Stack

![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%2B%20TypeScript-003399)
![Backend](https://img.shields.io/badge/Backend-FastAPI%200.115-5580C8)
![Database](https://img.shields.io/badge/Database-PostgreSQL%2016-1A1A2E)
![Cache](https://img.shields.io/badge/Cache-Redis%207.2-C00000)
![Queue](https://img.shields.io/badge/Queue-Celery%205.3-548235)
![NLP](https://img.shields.io/badge/NLP-BM25%20%7C%20TF--IDF%20%7C%20MiniLM-ED7D31)
![AI](https://img.shields.io/badge/AI-Claude%20Sonnet-70AD47)
![Infra](https://img.shields.io/badge/Infra-Docker%20Compose-595959)

## Quick Start

From clone to running stack in 5 commands:

```bash
git clone <repository-url>
cd "PatentPath - AI-Guided Innovation & Prior Art Platform"
cp .env.example .env
docker compose up --build
# open http://localhost:5173
```

PowerShell equivalent for the environment file copy:

```powershell
Copy-Item .env.example .env
```

After startup:

- Frontend: http://localhost:5173
- API base: http://localhost:8000/api/v1
- Swagger: http://localhost:8000/docs

Detailed setup guidance is in [docs/README.md](docs/README.md).

## Features (F-01 to F-15)

- [x] F-01 Problem statement to query workflow
- [x] F-02 Auto-generated CQL preview
- [x] F-03 Query refinement with filters
- [x] F-04 Espacenet prior-art retrieval
- [x] F-05 Patent result exploration and detail views
- [x] F-06 Composite NLP similarity scoring (BM25 + TF-IDF + Semantic)
- [x] F-07 AI-generated gap analysis
- [x] F-08 Feasibility assessment scoring
- [x] F-09 Innovation project workspace (CRUD)
- [x] F-10 Patent preparation PDF report generation
- [x] F-11 Timeline, notes, and novelty-risk tracking
- [x] F-12 IPC/CPC classification browser helper
- [x] F-13 Patent family view (INPADOC)
- [x] F-14 Search history panel
- [x] F-15 In-app documentation and algorithm diagrams

## Academic Context

PatentPath was developed for:

- Institution: ENSA Kenitra
- Course context: Management de l'Innovation Challenge
- Supervisor: Prof. BENBRAHIM Fatima Zahra
- Academic year: 2025-2026

## Team

- Team member 1: ABDELMOUMEN Mohamed Amine
- Team member 2: BAHI Mehdi


## Legal and Disclaimer

PatentPath is an academic computational support tool and does not provide legal advice.
Always consult a qualified patent attorney or patent agent before filing a patent application.

## License

MIT License.
See [LICENSE](LICENSE)
