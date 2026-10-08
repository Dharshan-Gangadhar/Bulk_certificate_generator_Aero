from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from .. import models, schemas
from ..database import get_db
from ..worker import process_job_background

router = APIRouter(
    prefix="/api/v1",
    tags=["certificates"]
)

@router.post("/jobs", response_model=schemas.JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_generation_job(
    job_req: schemas.JobCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Submit a list of recipients for bulk certificate generation.
    Returns the job ID to track progress.
    """
    if not job_req.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty")
        
    # Create the job
    db_job = models.Job(total_certificates=len(job_req.recipients))
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Create certificate records
    db_certificates = []
    for recipient in job_req.recipients:
        db_cert = models.Certificate(
            job_id=db_job.id,
            recipient_name=recipient.recipient_name,
            recipient_email=recipient.recipient_email,
            course_name=recipient.course_name,
        )
        db_certificates.append(db_cert)
        
    db.bulk_save_objects(db_certificates)
    db.commit()
    
    # Trigger background processing
    background_tasks.add_task(process_job_background, db_job.id)
    
    return db_job

@router.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Check the status and progress of a generation job.
    """
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return db_job

@router.get("/jobs/{job_id}/certificates", response_model=schemas.JobStatusResponse)
def get_job_certificates(job_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about all certificates in a job.
    """
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return db_job

@router.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the generated certificate PDF file.
    """
    db_cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    if db_cert.status != models.CertificateStatus.GENERATED or not db_cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate is not ready or failed to generate")
        
    if not os.path.exists(db_cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on disk")
        
    return FileResponse(
        path=db_cert.file_path, 
        filename=f"{db_cert.recipient_name.replace(' ', '_')}_Certificate.pdf",
        media_type="application/pdf"
    )
