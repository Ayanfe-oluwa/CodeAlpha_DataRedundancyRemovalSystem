# CodeAlpha Task 1:  Cloud-Based Data Redundancy Removal System
Prepared by: Kolade Ayanfe Samuel
Student ID: CA/DF1/322525

A Python REST API that validates incoming records, classifies submissions as unique, duplicate, or potential conflict, and prevents duplicate email identifiers from being stored.

## Features

- Input validation using Pydantic.
- Email normalization for matching.
- Duplicate detection against PostgreSQL or a local SQLite database.
- Database-level unique constraint to prevent duplicate identifiers.
- Conflict classification when the identifier matches but other fields differ.
- REST endpoints for creating and listing records.
- Automated tests.
- Docker and Docker Compose support.

## Architecture

Client -> FastAPI -> validation and matching -> PostgreSQL unique constraint -> JSON response.

The application performs a lookup for useful classification, while the database unique constraint is the final integrity safeguard. A concurrent insert conflict is handled without storing a duplicate.

## Requirements

- Python 3.12 or later
- Docker Desktop with Docker Compose (recommended for PostgreSQL), or a local Python environment

## Run with Docker Compose

1. Copy `.env.example` to `.env`.
2. Replace the example password with a strong local password.
3. Start the service:

   ```bash
   docker compose up --build
   ```

4. Open the interactive API documentation at `http://localhost:8000/docs`.
5. Check health at `http://localhost:8000/health`.

Do not commit `.env` or production credentials to GitHub.

## Run locally with SQLite

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The default local database is `redundancy.db`. To use PostgreSQL, set `DATABASE_URL` to a valid SQLAlchemy URL, for example:

`postgresql+psycopg://username:password@localhost:5432/redundancy`

## API examples

### Submit a record

`POST /records`

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "description": "Example customer"
}
```

Possible statuses:

- `unique`: validated and stored.
- `duplicate`: matching record already exists; not inserted.
- `potential_conflict`: identifier exists but other fields differ; not inserted and requires review.
- Invalid input returns HTTP `422`.

### List records

`GET /records?limit=100&offset=0`

### Get a record

`GET /records/1`

### Health check

`GET /health`

## Run tests

```bash
pytest -q
```

Tests cover unique insertion, exact duplicates, conflicting submissions, invalid email input, and the health endpoint.

## Data-matching policy and limitations

This starter project treats normalized email as the unique identifier. Two records with the same normalized email are not inserted twice. If their names or descriptions differ, the API returns `potential_conflict` rather than deleting or overwriting existing data.

Email normalization uses trimming and case-folding. Real deployments should confirm the identity rules appropriate for their domain. Similar names alone are not sufficient evidence that two people are the same.

The project creates tables at application startup for simplicity. For production use, add database migrations, authentication and authorization, rate limiting, structured audit logging, encrypted transport, monitoring, backups, and secret management. Never expose a database publicly without appropriate network and access controls.

## Cloud deployment

The application is containerized and can be deployed to a container-capable cloud service with a managed PostgreSQL database. Configure `DATABASE_URL` and secrets in the cloud provider's secret manager or environment configuration. Enable HTTPS and restrict database network access. Exact deployment steps depend on the chosen provider.

## Suggested next improvements

- Add authentication and role-based access control.
- Add review/resolve endpoints for potential conflicts.
- Add audit records for accepted, duplicate, and flagged submissions.
- Add database migrations with Alembic.
- Add CI testing with GitHub Actions.
- Add metrics for duplicate rate and validation failures.

## License

Choose a license appropriate for the assignment before publishing.
"# CodeAlpha_DataRedundancyRemovalSystem" 
