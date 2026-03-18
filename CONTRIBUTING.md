# Contributing to PatentPath

Thank you for contributing.
This guide defines coding style, commit conventions, and branch naming rules for a consistent project workflow.

## Development Principles

- Keep changes scoped and task-focused.
- Prefer small, reviewable pull requests.
- Maintain strict typing in Python and TypeScript.
- Preserve existing architecture and naming conventions.

## Code Style Guide

### Python (backend)

- Follow PEP 8.
- Use type hints for all public functions.
- Keep modules cohesive and documented with module docstrings.
- Run lint checks before opening PR:

```bash
ruff check backend/
```

- Run tests locally:

```bash
pytest backend/tests/
```

### TypeScript (frontend)

- Use strict TypeScript types (avoid any).
- Keep components focused and reusable.
- Prefer typed API client functions and typed store actions.
- Run lint checks before opening PR:

```bash
npx eslint frontend/src/ --ext .ts,.tsx
```

## Commit Message Format (Conventional Commits)

Use this pattern:

```text
type(scope): short imperative summary
```

Examples:

- feat(search): add CSV export endpoint for session results
- fix(auth): return 401 for expired refresh token
- docs(manual): add troubleshooting and technical notes
- refactor(ui): extract loading overlay into shared component
- test(nlp): add integration tests for scoring pipeline

Recommended types:

- feat
- fix
- docs
- refactor
- test
- chore
- ci

## Branch Naming Convention

Use one of these prefixes:

- feature/<short-description>
- fix/<short-description>
- docs/<short-description>

Examples:

- feature/ipc-browser-modal
- fix/search-export-content-type
- docs/user-manual-api-reference

## Pull Request Checklist

Before requesting review, confirm:

- code builds and tests pass locally,
- lint checks pass,
- docs are updated when behavior changes,
- no secrets were committed,
- API changes are reflected in docs/API_REFERENCE.md.

## Security and Secrets

- Never commit real credentials.
- Keep secrets in environment variables.
- Use .env.example as the template for required settings.

## Reporting Issues

Please include:

- clear reproduction steps,
- expected behavior,
- actual behavior,
- logs/errors and environment details.
