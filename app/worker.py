from sqlalchemy.orm import Session
from .models import Job, Certificate, JobStatus, CertificateStatus
from .cert_generator import generate_certificate
from .database import SessionLocal
import traceback

def process_job_background(job_id: int):
    """
    Background worker to generate certificates for a given job.
    """
    # Create a new database session for the background task
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.PROCESSING
        db.commit()

        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()
        
        success_count = 0
        fail_count = 0

        for cert in certificates:
            try:
                # Generate certificate
                file_path = generate_certificate(cert.recipient_name, cert.course_name)
                
                # Update status on success
                cert.status = CertificateStatus.GENERATED
                cert.file_path = file_path
                success_count += 1
            except Exception as e:
                # Update status on failure
                cert.status = CertificateStatus.FAILED
                cert.error_message = str(e)
                fail_count += 1
            
            # Update job progress incrementally
            job.successful_certificates = success_count
            job.failed_certificates = fail_count
            
            # Commit after each certificate to update progress
            db.commit()

        # Finalize job status
        job.status = JobStatus.COMPLETED
        db.commit()

    except Exception as e:
        # If the entire job fails catastrophically
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            db.commit()
        print(f"Job {job_id} failed catastrophically: {e}")
        traceback.print_exc()
    finally:
        db.close()
