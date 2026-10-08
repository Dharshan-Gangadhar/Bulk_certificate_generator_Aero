import os
from app.cert_generator import generate_certificate
from app.worker import process_job_background
from app import models
from tests.conftest import TestingSessionLocal
import pytest

def test_generate_certificate():
    filepath = generate_certificate("Test User", "Test Course")
    
    assert os.path.exists(filepath)
    assert filepath.endswith(".pdf")
    
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

def test_worker_failure_handling(db_session, monkeypatch):
    """
    Test that if one certificate fails, the worker still continues processing others.
    """
    # Create a job
    job = models.Job(total_certificates=2)
    db_session.add(job)
    db_session.commit()
    
    # Create two certificates
    cert1 = models.Certificate(job_id=job.id, recipient_name="Good", recipient_email="good@a.com", course_name="C")
    cert2 = models.Certificate(job_id=job.id, recipient_name="Bad", recipient_email="bad@a.com", course_name="C")
    
    db_session.add_all([cert1, cert2])
    db_session.commit()
    
    # Mock generate_certificate to fail for the "Bad" recipient
    original_generate = generate_certificate
    
    def mock_generate(name, course):
        if name == "Bad":
            raise ValueError("Simulated failure")
        return original_generate(name, course)
        
    monkeypatch.setattr("app.worker.generate_certificate", mock_generate)
    
    # We also need to monkeypatch the SessionLocal in worker to use our db_session
    # Since worker creates its own session, we mock it.
    monkeypatch.setattr("app.worker.SessionLocal", lambda: TestingSessionLocal())
    
    # Process job
    process_job_background(job.id)
    
    # Verify outcomes
    db_session.refresh(job)
    assert job.status == models.JobStatus.COMPLETED
    assert job.successful_certificates == 1
    assert job.failed_certificates == 1
    
    db_session.refresh(cert1)
    assert cert1.status == models.CertificateStatus.GENERATED
    assert cert1.file_path is not None
    
    db_session.refresh(cert2)
    assert cert2.status == models.CertificateStatus.FAILED
    assert cert2.error_message == "Simulated failure"
    assert cert2.file_path is None
