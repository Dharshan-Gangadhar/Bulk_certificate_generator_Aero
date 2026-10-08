from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from .models import JobStatus, CertificateStatus

class RecipientBase(BaseModel):
    recipient_name: str = Field(..., min_length=1)
    recipient_email: EmailStr
    course_name: str = Field(..., min_length=1)

class JobCreate(BaseModel):
    recipients: List[RecipientBase] = Field(..., min_items=1)

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    course_name: str
    status: CertificateStatus
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    total_certificates: int
    successful_certificates: int
    failed_certificates: int
    
    class Config:
        from_attributes = True

class JobStatusResponse(JobResponse):
    certificates: List[CertificateResponse] = []
