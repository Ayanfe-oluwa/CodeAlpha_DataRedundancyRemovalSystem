from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Record
from app.schemas import RecordCreate, RecordRead, SubmissionResult

@asynccontextmanager
async def lifespan(app: FastAPI):
    # For this starter project, create tables at startup. For production, use migrations.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Cloud Data Redundancy Removal System",
    description="Validates incoming records, detects duplicate identifiers, and stores unique records.",
    version="1.0.0",
    lifespan=lifespan,
)

def normalize_email(email: str) -> str:
    # Email addresses are case-normalized for this project's matching policy.
    # In a production system, document and validate the chosen identity rules.
    return email.strip().casefold()

@app.get("/health")
def health():
    return {"status": "ok", "service": "cloud-data-redundancy-system"}

@app.post("/records", response_model=SubmissionResult, status_code=200)
def submit_record(payload: RecordCreate, db: Session = Depends(get_db)):
    normalized_email = normalize_email(str(payload.email))
    existing = db.scalar(
        select(Record).where(Record.normalized_email == normalized_email)
    )

    if existing:
        same_name = existing.name.strip().casefold() == payload.name.strip().casefold()
        same_description = (existing.description or "").strip() == (payload.description or "").strip()

        if same_name and same_description:
            return SubmissionResult(
                status="duplicate",
                inserted=False,
                message="A matching record already exists. No new record was added.",
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
        # Protects against a concurrent request inserting the same identifier
        # after the initial lookup.
        db.rollback()
        existing = db.scalar(
            select(Record).where(Record.normalized_email == normalized_email)
        )
        return SubmissionResult(
            status="duplicate",
            inserted=False,
            message="A matching record was added concurrently. No duplicate was stored.",
            existing_record_id=existing.id if existing else None,
        )

    return SubmissionResult(
        status="unique",
        inserted=True,
        message="Record validated and stored successfully.",
        record=record,
    )

@app.get("/records", response_model=list[RecordRead])
def list_records(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Record).order_by(Record.id).offset(offset).limit(limit)
    ).all()

@app.get("/records/{record_id}", response_model=RecordRead)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(Record, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record
