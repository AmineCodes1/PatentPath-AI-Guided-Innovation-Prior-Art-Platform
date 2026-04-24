# PatentPath — AI-Guided Innovation & Prior Art Platform

---

## The Problem

### Innovation is Risky Without Prior Art Research

Every year, inventors, startups, and R&D teams invest enormous time and money building solutions — only to discover too late that their idea is already patented.

**Prior art research** — the process of finding existing patents that overlap with a new invention — is legally required before filing a patent. But doing it well is extraordinarily difficult:

- The European Patent Office (EPO) alone holds **over 150 million patent documents**
- Patent language is dense, technical, and inconsistent across jurisdictions
- Search requires mastering specialized query languages (CQL, CPC, IPC classifications)
- Interpreting results demands legal and domain expertise
- A single missed patent can invalidate an entire patent application — or worse, lead to costly infringement litigation

**For most teams, the current options are:**

| Option | Problem |
|---|---|
| Hire a patent attorney | Expensive ($5,000–$20,000+ per search) |
| Use raw patent databases (Espacenet, Google Patents) | Requires expertise, no AI assistance |
| Ignore prior art entirely | Legal and financial risk |

There is no accessible, AI-powered tool that guides innovators through the full prior art research workflow — from problem statement to actionable report — without needing a patent law background.

---

## The Solution

### PatentPath — Your AI Co-Pilot for Patent Research

PatentPath is a full-stack web platform that makes professional-grade prior art research accessible to any innovator. It combines **natural language processing**, **semantic AI scoring**, and **LLM-powered gap analysis** to guide users from a raw idea to a structured novelty assessment — in minutes, not weeks.

**Core philosophy:** you describe what you're building in plain language. PatentPath handles the patent database querying, the relevance scoring, the risk assessment, and the report generation.

### Architecture Overview

```
User (Browser)
     │
     ▼
React Frontend (Vite + Zustand)
     │
     ▼
FastAPI Backend  ←──→  Celery Worker Queue
     │                        │
     ├── PostgreSQL (data)     ├── Patent Search Jobs
     ├── Redis (cache/queue)   ├── AI Gap Analysis Jobs
     └── EPO OPS API           └── PDF Report Jobs
                                        │
                                   Local LLM (Ollama)
                                   qwen2.5:14b
```

The entire stack runs locally — no cloud dependencies, no API costs, full data privacy.

---

## Walkthrough of the Solution

### Step 1 — Create an Innovation Project

The user starts by creating an **Innovation Project**: a named workspace that captures the problem statement and domain (expressed as an IPC class — the international patent classification system). Everything in PatentPath is scoped to a project, making it easy to track multiple inventions in parallel.

> *Example: "Project: Smart Irrigation Controller — Problem: a low-power IoT device that uses soil sensor data and weather forecasts to optimize water usage for agriculture."*

---

### Step 2 — Build and Preview a Search Query

The user types their invention description in plain English. PatentPath immediately:

1. **Extracts keywords** using spaCy NLP (noun chunks, named entities, domain terms)
2. **Suggests IPC classes** — mapping domain keywords to the international classification tree (e.g., "irrigation" → A01G, "IoT" → H04W)
3. **Generates a CQL query** — the structured query language used by EPO's patent databases
4. **Validates the query** — checking syntax before any real search is run

The user can inspect the generated CQL, override it manually, and apply filters (publication date range, countries, applicant name, legal status — active, lapsed, pending).

This preview step ensures the search is tuned before committing to the full query.

---

### Step 3 — Execute the Search

With one click, the search is dispatched as an **asynchronous background job** via Celery. The EPO's Open Patent Services (OPS) API is queried, and results are fetched, processed, and ranked.

PatentPath scores every returned patent using **three independent NLP signals**:

| Signal | Method | Weight |
|---|---|---|
| BM25 | Keyword frequency & document length normalization | 30% |
| TF-IDF | Term rarity across the patent corpus | 30% |
| Semantic | Sentence-transformer embedding cosine similarity | 40% |

Each patent receives a **Composite Score** (0–1) and a **Risk Label**:

- `HIGH` — score > 0.75 — strong overlap, significant prior art risk
- `MEDIUM` — score 0.50–0.75 — partial overlap, needs review
- `LOW` — score 0.25–0.50 — weak overlap, minor concern
- `MINIMAL` — score < 0.25 — negligible relevance

---

### Step 4 — Review Results

The results page shows ranked patent cards. Each card displays:

- Publication number, title, applicants, and publication date
- A visual scoring breakdown (BM25 / TF-IDF / Semantic / Composite)
- A color-coded risk badge

Users can **filter live** by risk label, country of publication, and date range. Clicking any result expands a **Patent Detail Panel** showing:

- Full abstract and claims text
- INPADOC patent family (related patents across jurisdictions)
- Legal status (granted, lapsed, pending, opposition)
- Direct link to Espacenet for the official filing

High-risk patents can be bookmarked and saved to the project for later reference.

---

### Step 5 — AI Gap Analysis

Once results are in, the user triggers an **AI Gap Analysis**. PatentPath sends the top-ranked patents and the original problem statement to a local LLM (running via Ollama) and receives a structured novelty assessment:

- **Overall Risk Assessment** — HIGH / MEDIUM / LOW
- **Covered Aspects** — which parts of the invention are already claimed in prior art
- **Gap Aspects** — genuine innovation opportunities that are *not* covered
- **Differentiation Suggestions** — concrete recommendations to strengthen novelty
- **Feasibility Scores** across three dimensions:
  - *Technical Readiness* — how mature the underlying technology is
  - *Domain Specificity* — how niche and defensible the application is
  - *Claim Potential* — how likely novel claims are to be grantable
- A full **narrative analysis** written in plain English

This turns raw patent data into actionable innovation strategy.

---

### Step 6 — Generate a PDF Report

PatentPath compiles everything into a professional **PDF report** containing:

- Project overview and problem statement
- Top 5 prior art patents with scores and risk labels
- Full gap analysis and feasibility assessment
- Patent claims outline
- Recommended next steps checklist

The report is ready to share with a patent attorney, an R&D director, or a funding committee — without requiring any manual formatting.

---

## Key Functionalities

### Project Management
- Create and manage multiple innovation projects simultaneously
- Per-project activity **timeline** showing every search, analysis, and report event
- **Notes** system — attach written observations to projects or specific search sessions
- **Risk trend chart** — visualize how novelty risk evolves across searches over time
- Project archiving when work is complete

### Patent Search Engine
- Natural language → CQL query generation (no patent query expertise required)
- Live query preview with keyword and IPC extraction before execution
- Manual CQL override for power users
- Advanced filters: date range, country codes, IPC classes, applicant, legal status
- Interactive IPC Browser for exploring the full classification tree
- Asynchronous search with real-time status polling

### Scoring & Risk Assessment
- Three-signal NLP scoring pipeline (BM25 + TF-IDF + Semantic)
- Per-patent composite score with transparent signal breakdown
- Automatic risk labeling (HIGH / MEDIUM / LOW / MINIMAL)
- Aggregated session statistics: total results, risk distribution breakdown

### Patent Intelligence
- Full patent detail view: abstract, claims, applicants, dates
- INPADOC family view — see all related patents across countries
- Legal status check — know if a patent is active, lapsed, or pending
- Direct Espacenet links for official filings
- Patent bookmarking and saved references per project

### AI Gap Analysis
- LLM-powered novelty analysis running fully locally (Ollama + qwen2.5:14b)
- Identifies covered vs. uncovered aspects of the invention
- Generates concrete differentiation recommendations
- Three-dimension feasibility scoring
- Full narrative assessment in plain English

### Report Generation
- One-click PDF report generation
- Combines project context, patent results, AI analysis, and notes
- Downloadable, shareable, presentation-ready output
- Rendered via WeasyPrint from structured HTML templates

### Data & Privacy
- All data stored locally in PostgreSQL
- No invention details sent to external cloud services
- LLM inference runs on local GPU (Ollama)
- Patent data cached in Redis to minimize API calls
- JWT-authenticated user accounts with full session management

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Zustand, Tailwind CSS |
| Backend | FastAPI (Python 3.12), SQLAlchemy, Pydantic |
| AI / LLM | Ollama (qwen2.5:14b) via OpenAI-compatible API |
| NLP Scoring | spaCy, scikit-learn (BM25/TF-IDF), Sentence Transformers |
| Task Queue | Celery + Redis |
| Database | PostgreSQL |
| Patent Data | EPO Open Patent Services (OPS) API |
| PDF Generation | WeasyPrint + Jinja2 |
| Infrastructure | Docker Compose (6 services) |

---

# DEMO PAGE