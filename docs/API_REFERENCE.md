# PatentPath API Reference

Base path: /api/v1

Authentication model:

- Most endpoints require Authorization: Bearer <token>.
- In the current implementation, protected routes expect a bearer token and resolve user context from token format used by backend dependencies.

## Health

### GET /health

- Auth required: No
- Description: Service and dependency health check (DB + Redis)
- Key parameters: None
- Example response shape:

```json
{
  "status": "ok",
  "db_connected": true,
  "redis_connected": true,
  "timestamp": "2026-03-17T10:15:30.123Z"
}
```

## Auth

### POST /auth/register

- Auth required: No
- Description: Create a user account and return access token
- Key parameters:
  - body.email (string, email)
  - body.password (string, min length 8)
  - body.display_name (string)
- Example response shape:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### POST /auth/login

- Auth required: No
- Description: Authenticate user credentials and return access token
- Key parameters:
  - body.email
  - body.password
- Example response shape:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### GET /auth/me

- Auth required: Yes
- Description: Return current user profile
- Key parameters: Authorization header
- Example response shape:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Student",
  "created_at": "2026-03-17T10:15:30.123Z"
}
```

### POST /auth/refresh

- Auth required: Yes
- Description: Return a new token from a valid existing token
- Key parameters: Authorization header
- Example response shape:

```json
{
  "access_token": "new-jwt-token",
  "token_type": "bearer"
}
```

## Search

### POST /search/preview-query

- Auth required: Yes
- Description: Generate and validate CQL preview for an invention description
- Key parameters:
  - body.query_text
  - body.filters (optional)
- Example response shape:

```json
{
  "cql_generated": "(ti=\"autonomous\" OR ab=\"autonomous\") AND ipc=\"G06N\"",
  "keywords_extracted": ["autonomous", "navigation"],
  "ipc_suggestions": ["G06N", "G06F"],
  "is_valid": true,
  "validation_error": null,
  "metadata": {
    "truncated": "false"
  }
}
```

### POST /search/execute

- Auth required: Yes
- Description: Create a pending search session and dispatch background task
- Key parameters:
  - body.project_id
  - body.query_text
  - body.cql_override (optional)
  - body.filters (optional)
- Example response shape:

```json
{
  "session_id": "uuid",
  "status": "PENDING",
  "estimated_seconds": 15
}
```

### GET /search/session/{session_id}

- Auth required: Yes
- Description: Return one search session
- Key parameters:
  - path.session_id
- Example response shape:

```json
{
  "id": "uuid",
  "project_id": "uuid",
  "query_text": "autonomous vehicle navigation",
  "cql_generated": "...",
  "filters_json": {},
  "result_count": 20,
  "status": "COMPLETE",
  "executed_at": "2026-03-17T10:15:30.123Z"
}
```

### GET /search/session/{session_id}/results

- Auth required: Yes
- Description: Paginated scored results for a session
- Key parameters:
  - path.session_id
  - query.page (default 1)
  - query.per_page (default 20, max 50)
  - query.risk_filter (optional list)
- Example response shape:

```json
{
  "session_id": "uuid",
  "total_count": 42,
  "page": 1,
  "per_page": 20,
  "total_pages": 3,
  "results": [
    {
      "patent": {
        "publication_number": "EP1234567",
        "title": "Navigation method",
        "abstract": "...",
        "applicants": ["Example Corp"],
        "publication_date": "2024-05-20",
        "espacenet_url": "https://worldwide.espacenet.com/...",
        "legal_status": "Active"
      },
      "bm25_score": 0.42,
      "tfidf_cosine": 0.76,
      "semantic_cosine": 0.64,
      "composite_score": 0.64,
      "risk_label": "MEDIUM",
      "rank": 1
    }
  ],
  "gap_analysis": null
}
```

### POST /search/session/{session_id}/save-patent

- Auth required: Yes
- Description: Save a selected patent reference within a session context
- Key parameters:
  - path.session_id
  - body.publication_number
  - body.notes (optional)
- Example response shape:

```json
{
  "session_id": "uuid",
  "project_id": "uuid",
  "saved_patent": "EP1234567",
  "saved_count": 1
}
```

### GET /search/session/{session_id}/stats

- Auth required: Yes
- Description: Aggregated search statistics
- Key parameters:
  - path.session_id
- Example response shape:

```json
{
  "total_results": 42,
  "risk_distribution": {
    "HIGH": 4,
    "MEDIUM": 11,
    "LOW": 20,
    "MINIMAL": 7
  },
  "avg_composite_score": 0.48,
  "top_ipc_classes": ["G06N", "G06F"]
}
```

### GET /search/session/{session_id}/results/export

- Auth required: Yes
- Description: Download all session results as CSV
- Key parameters:
  - path.session_id
- Example response shape: text/csv file stream

## Projects

### POST /projects

- Auth required: Yes
- Description: Create project
- Key parameters:
  - body.title
  - body.problem_statement
  - body.domain_ipc_class (optional)
- Example response shape: ProjectRead

### GET /projects

- Auth required: Yes
- Description: List user projects
- Key parameters: None
- Example response shape: array of ProjectRead

### GET /projects/{project_id}

- Auth required: Yes
- Description: Get one owned project
- Key parameters: path.project_id
- Example response shape: ProjectRead

### PUT /projects/{project_id}

- Auth required: Yes
- Description: Update project
- Key parameters:
  - path.project_id
  - body fields from ProjectUpdate
- Example response shape: ProjectRead

### DELETE /projects/{project_id}

- Auth required: Yes
- Description: Archive project
- Key parameters: path.project_id
- Example response shape: ProjectRead

### GET /projects/{project_id}/sessions

- Auth required: Yes
- Description: List sessions for a project
- Key parameters: path.project_id
- Example response shape:

```json
[
  {
    "id": "uuid",
    "query_text": "...",
    "cql_generated": "...",
    "result_count": 20,
    "status": "COMPLETE",
    "executed_at": "2026-03-17T10:15:30.123Z"
  }
]
```

### GET /projects/{project_id}/timeline

- Auth required: Yes
- Description: Return timeline events
- Key parameters: path.project_id
- Example response shape:

```json
[
  {
    "event_type": "SEARCH",
    "timestamp": "2026-03-17T10:15:30.123Z",
    "title": "Search completed",
    "summary": "42 results scored",
    "session_id": "uuid"
  }
]
```

### GET /projects/{project_id}/risk-trend

- Auth required: Yes
- Description: Return novelty risk trend series
- Key parameters: path.project_id
- Example response shape:

```json
[
  {
    "session_date": "2026-03-17",
    "overall_risk": "MEDIUM",
    "avg_composite_score": 0.58
  }
]
```

### POST /projects/{project_id}/notes

- Auth required: Yes
- Description: Create project note
- Key parameters:
  - path.project_id
  - body.title
  - body.content
  - body.linked_session_id (optional)
- Example response shape: note object with id/project_id/title/content/linked_session_id/created_at

### GET /projects/{project_id}/notes

- Auth required: Yes
- Description: List notes
- Key parameters: path.project_id
- Example response shape: array of note objects

### DELETE /projects/{project_id}/notes/{note_id}

- Auth required: Yes
- Description: Delete note
- Key parameters:
  - path.project_id
  - path.note_id
- Example response shape: no content (204)

## Patents

### GET /patents/{publication_number}

- Auth required: No
- Description: Return full patent record (cached/refreshed)
- Key parameters: path.publication_number
- Example response shape: PatentRecordRead

### GET /patents/{publication_number}/claims

- Auth required: No
- Description: Return claims text (fetch on demand)
- Key parameters: path.publication_number
- Example response shape:

```json
{
  "publication_number": "EP1234567",
  "claims": "1. A method comprising ..."
}
```

### GET /patents/{publication_number}/family

- Auth required: No
- Description: Return INPADOC family member list
- Key parameters: path.publication_number
- Example response shape:

```json
{
  "publication_number": "EP1234567",
  "family_members": [
    {
      "publication_number": "WO2024001234",
      "title": "Navigation method",
      "publication_date": "2024-01-11"
    }
  ]
}
```

### GET /patents/{publication_number}/legal

- Auth required: No
- Description: Return legal status (24h cache policy)
- Key parameters: path.publication_number
- Example response shape:

```json
{
  "publication_number": "EP1234567",
  "legal_status": "Active"
}
```

## Analysis

### POST /analysis/session/{session_id}/gap-analysis

- Auth required: Yes
- Description: Trigger gap analysis task
- Key parameters: path.session_id
- Example response shape:

```json
{
  "job_id": "celery-job-id",
  "status": "PENDING"
}
```

### GET /analysis/session/{session_id}/gap-analysis

- Auth required: Yes
- Description: Return completed gap analysis or processing state
- Key parameters: path.session_id
- Example response shape:

```json
{
  "status": "PROCESSING"
}
```

or

```json
{
  "id": "uuid",
  "session_id": "uuid",
  "overall_risk": "MEDIUM",
  "covered_aspects": ["..."],
  "gap_aspects": ["..."],
  "suggestions": ["..."],
  "narrative_text": "...",
  "model_used": "claude-sonnet-4-20250514",
  "generated_at": "2026-03-17T10:15:30.123Z",
  "feasibility_technical": 3.5,
  "feasibility_domain": 4.0,
  "feasibility_claim": 3.8
}
```

### GET /analysis/session/{session_id}/feasibility

- Auth required: Yes
- Description: Return feasibility subscores and composite percentage
- Key parameters: path.session_id
- Example response shape:

```json
{
  "status": "COMPLETE",
  "session_id": "uuid",
  "technical_readiness": 4,
  "domain_specificity": 3,
  "claim_potential": 4,
  "composite_percentage": 73.33,
  "commentary": "..."
}
```

## Reports

### POST /reports/generate

- Auth required: Yes
- Description: Trigger PDF generation task
- Key parameters:
  - body.project_id
  - body.session_id
- Example response shape:

```json
{
  "job_id": "celery-job-id",
  "status": "PENDING"
}
```

### GET /reports/status/{job_id}

- Auth required: Yes
- Description: Poll report task state
- Key parameters: path.job_id
- Example response shape:

```json
{
  "job_id": "celery-job-id",
  "status": "READY",
  "download_url": "/api/v1/reports/download/celery-job-id"
}
```

### GET /reports/download/{job_id}

- Auth required: Yes
- Description: Download generated PDF report
- Key parameters: path.job_id
- Example response shape: application/pdf stream

## Classifications

### GET /classifications/ipc

- Auth required: No
- Description: Return full curated IPC tree
- Key parameters: None
- Example response shape:

```json
{
  "sections": [
    {
      "section": "G",
      "title": "Physics",
      "classes": [
        {
          "code": "G06N",
          "title": "Computing based on biological models",
          "description": "...",
          "keywords": ["machine learning", "deep learning"]
        }
      ]
    }
  ]
}
```

### GET /classifications/ipc/search?q={term}

- Auth required: No
- Description: Return top fuzzy IPC matches by code/title/keywords
- Key parameters: query.q
- Example response shape: array of IPC class objects

### GET /classifications/ipc/{code}

- Auth required: No
- Description: Return one IPC class entry
- Key parameters: path.code
- Example response shape: single IPC class object

---

Swagger UI is available at /docs from the backend server.
