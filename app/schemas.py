from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RecordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank.")
        return value

    @field_validator("description")
    @classmethod
    def trim_description(cls, value: str | None) -> str | None:
        return value.strip() if value else value

class RecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    description: str | None
    created_at: datetime

class SubmissionResult(BaseModel):
    status: str
    inserted: bool
    message: str
    record: RecordRead | None = None
    existing_record_id: int | None = None
