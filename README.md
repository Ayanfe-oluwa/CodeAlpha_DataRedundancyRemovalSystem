# CodeAlpha Task 1: Cloud-Based Data Redundancy Removal System

**Project Name:** DataGuard  
**Prepared by:** Kolade Ayanfe Samuel  
**Student ID:** CA/DF1/322525  
**Repository:** CodeAlpha_DataRedundancyRemovalSystem

## 1. Project Overview

DataGuard is a Python-based Cloud Data Redundancy Removal System designed to validate incoming records, identify duplicate submissions, detect potential conflicts, and maintain database integrity.

The system uses FastAPI to provide REST API functionality and a web-based dashboard that allows users to submit, monitor, search, view, and delete records.

By validating incoming information against existing database entries, DataGuard helps prevent unnecessary duplication and improves data consistency.

## 2. Key Features

### Data Validation and Redundancy Detection
- Input validation using Pydantic.
- Email normalization for consistent record matching.
- Automatic duplicate detection.
- Potential conflict identification when an existing email identifier is submitted with different information.
- Database-level unique constraints to prevent duplicate identifiers.
- Only validated, unique records are stored.

### DataGuard Web Dashboard
- Interactive dashboard for managing stored records.
- Record submission form.
- Real-time system connection status.
- Overview of total and unique stored records.
- Duplicate and potential conflict counters.
- Search functionality for stored records.
- Individual record deletion with confirmation.
- Automatic dashboard refresh after successful operations.
- Responsive interface for different screen sizes.

### Backend and Database
- REST API developed with FastAPI.
- SQLAlchemy database integration.
- SQLite support for local development.
- PostgreSQL configuration support.
- Automatic database table initialization.
- Error handling and database transaction management.

### Development and Deployment
- Automated API tests.
- Dockerfile and Docker Compose support.
- Interactive API documentation.
- Environment-based database configuration.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend REST API |
| SQLAlchemy | Database operations and ORM |
| SQLite | Local database |
| PostgreSQL | Alternative database for deployment |
| Pydantic | Input validation |
| HTML5 | Dashboard structure |
| CSS3 | Dashboard styling and responsiveness |
| JavaScript | Dashboard interactions and API communication |
| Docker | Application containerization |
| Pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

## 4. System Architecture

The application follows a client-server architecture.

**Dashboard / API Client → FastAPI Backend → Input Validation → Duplicate and Conflict Detection → Database → JSON Response**

The frontend communicates with the backend through HTTP requests. The backend validates submitted records, checks existing identifiers, and stores only unique records.

The database unique constraint provides an additional safeguard against duplicate insertion, including concurrent submissions.

## 5. Project Structure

```text
CodeAlpha_DataRedundancyRemovalSystem/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## 6. Installation and Setup

### Requirements
- Python 3.12 or later.
- Visual Studio Code or another Python development environment.
- Git.
- Docker Desktop (optional).

### Run Locally with SQLite

**Step 1: Clone the repository**

```bash
git clone https://github.com/Ayanfe-oluwa/CodeAlpha_DataRedundancyRemovalSystem.git
```

**Step 2: Enter the project directory**

```bash
cd CodeAlpha_DataRedundancyRemovalSystem
```

**Step 3: Create a virtual environment**

```bash
python -m venv .venv
```

**Step 4: Activate the virtual environment**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

**Step 5: Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**Step 6: Start the application**

```bash
python -m uvicorn app.main:app --reload
```

**Step 7: Open the application**

- Web Dashboard: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs
- Alternative API Documentation: http://127.0.0.1:8000/redoc
- Health Check: http://127.0.0.1:8000/health

The default local database is `redundancy.db`.

## 7. How to Use the Dashboard

1. Start the FastAPI application.
2. Open the DataGuard dashboard in your browser.
3. Navigate to the Submit New Record section.
4. Enter the person's name, email address, and description.
5. Click **Validate and Save Record**.
6. The system checks the submitted information against existing records.
7. The result is displayed on the dashboard.
8. View stored records in the Stored Records section.
9. Use the search field to locate specific records.
10. Click the Delete button beside a record to remove it after confirming the action.

Deleting a record removes it from the database. The dashboard refreshes automatically after successful deletion.

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Displays the DataGuard dashboard |
| GET | `/health` | Checks application status |
| POST | `/records` | Validates and submits a new record |
| GET | `/records` | Retrieves stored records |
| GET | `/records/{record_id}` | Retrieves a specific record |
| DELETE | `/records/{record_id}` | Deletes a selected record |

### Example: Submit a Record

**POST `/records`**

Request body:

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "description": "Example customer record"
}
```

Possible response classifications:

- `unique`: The record is valid and has been stored.
- `duplicate`: A matching record already exists and has not been inserted again.
- `potential_conflict`: The email identifier already exists, but other information differs. The submission is not stored and requires review.

Invalid input returns HTTP `422`.

### Example: Delete a Record

**DELETE `/records/1`**

This deletes the record with ID 1 if it exists.

## 9. Data-Matching Policy

The system uses normalized email addresses as unique identifiers.

- Email addresses are trimmed and case-folded before matching.
- Matching email addresses with identical names and descriptions are classified as duplicates.
- Matching email addresses with different names or descriptions are classified as potential conflicts.
- Potential conflicts are not automatically overwritten or deleted.
- Only unique, validated records are inserted.

This approach helps preserve existing information and reduces accidental data loss.

## 10. Testing

Run the automated tests using:

```bash
pytest -q
```

The test suite covers the API functionality implemented in the project, including record submission, duplicate detection, conflict classification, invalid input, and health checks.

Manual dashboard testing should also include:
- Submitting a unique record.
- Submitting the same record again.
- Submitting the same email with different details.
- Searching for stored records.
- Deleting a selected record.
- Refreshing the dashboard to verify database persistence.

## 11. Docker Deployment

The project includes Docker configuration for containerized deployment.

To start the application:

```bash
docker compose up --build
```

Before deployment:
1. Configure the required environment variables.
2. Set a secure database password.
3. Configure the database connection.
4. Keep credentials outside the Git repository.
5. Use HTTPS and appropriate access controls in production.

The application supports PostgreSQL configuration through a SQLAlchemy-compatible `DATABASE_URL`, depending on the installed database driver and environment configuration.

## 12. Limitations and Future Improvements

The current implementation provides core redundancy detection and record management functionality.

Potential future improvements include:

- User authentication and role-based access control.
- A dedicated conflict review and resolution interface.
- Persistent audit logs for record creation and deletion.
- Database migrations using Alembic.
- Improved dashboard analytics.
- Advanced record matching beyond email identifiers.
- Automated continuous integration using GitHub Actions.
- Cloud hosting with managed database services.

The dashboard's duplicate and conflict counters currently use browser local storage, so they represent activity recorded in that browser rather than system-wide historical statistics.

## 13. Security Considerations

For production deployment, the system should include authentication, authorization, secure database credentials, HTTPS, access restrictions, database backups, and audit logging.

The current dashboard is intended for development and demonstration. Its record deletion endpoint does not yet require user authentication.

Never commit `.env` files, database passwords, API keys, or other private credentials to GitHub.

## 14. Conclusion

DataGuard demonstrates how Python, FastAPI, database management, and frontend technologies can be combined to build a practical data redundancy removal system.

The project provides an integrated solution for validating records, detecting duplicates, identifying potential conflicts, managing stored information, and preventing unnecessary duplicate entries.

It also demonstrates practical knowledge of REST API development, database integrity, frontend-backend integration, and version control.

