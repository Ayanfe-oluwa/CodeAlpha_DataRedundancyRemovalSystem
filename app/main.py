
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Record
from app.schemas import RecordCreate, RecordRead, SubmissionResult


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# FastAPI application
app = FastAPI(
    title="Cloud Data Redundancy Removal System",
    description=(
        "An API for validating incoming records, detecting duplicates, "
        "identifying potential conflicts, and maintaining database integrity."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# Serve frontend static files
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# MAIN DASHBOARD
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(STATIC_DIR / "index.html")


# Email normalization
def normalize_email(email: str) -> str:
    return email.strip().casefold()


# HEALTH CHECK
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "cloud-data-redundancy-system"
    }


# SUBMIT AND VALIDATE RECORDS
@app.post("/records", response_model=SubmissionResult, status_code=200)
def submit_record(
    payload: RecordCreate,
    db: Session = Depends(get_db)
):
    normalized_email = normalize_email(str(payload.email))

    existing = db.scalar(
        select(Record).where(
            Record.normalized_email == normalized_email
        )
    )

    if existing:
        same_name = (
            existing.name.strip().casefold()
            == payload.name.strip().casefold()
        )

        same_description = (
            (existing.description or "").strip()
            == (payload.description or "").strip()
        )

        if same_name and same_description:
            return SubmissionResult(
                status="duplicate",
                inserted=False,
                message=(
                    "A matching record already exists. "
                    "No new record was added."
                ),
                existing_record_id=existing.id,
            )

        return SubmissionResult(
            status="potential_conflict",
            inserted=False,
            message=(
                "The email identifier already exists, but other fields differ. "
                "The submission was not inserted and should be reviewed."
            ),
            existing_record_id=existing.id,
        )

    record = Record(
        name=payload.name,
        email=str(payload.email),
        normalized_email=normalized_email,
        description=payload.description,
    )

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except IntegrityError:
        db.rollback()

        existing = db.scalar(
            select(Record).where(
                Record.normalized_email == normalized_email
            )
        )

        return SubmissionResult(
            status="duplicate",
            inserted=False,
            message=(
                "A matching record was added concurrently. "
                "No duplicate was stored."
            ),
            existing_record_id=existing.id if existing else None,
        )

    return SubmissionResult(
        status="unique",
        inserted=True,
        message="Record validated and stored successfully.",
        record=record,
    )

# DELETE A SPECIFIC RECORD
@app.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = db.get(Record, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found."
        )

    db.delete(record)
    db.commit()

    return {
        "status": "success",
        "message": f"Record {record_id} deleted successfully."
    }

# RETRIEVE ALL RECORDS
@app.get("/records", response_model=list[RecordRead])
def list_records(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Record)
        .order_by(Record.id)
        .offset(offset)
        .limit(limit)
    ).all()


# RETRIEVE A SPECIFIC RECORD
@app.get("/records/{record_id}", response_model=RecordRead)
def get_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = db.get(Record, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found."
        )

    return record
