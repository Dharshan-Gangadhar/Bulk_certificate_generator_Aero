import time

def test_create_job(client):
    response = client.post("/api/v1/jobs", json={
        "recipients": [
            {
                "recipient_name": "Alice Smith",
                "recipient_email": "alice@example.com",
                "course_name": "Python for Beginners"
            },
            {
                "recipient_name": "Bob Jones",
                "recipient_email": "bob@example.com",
                "course_name": "Advanced Python"
            }
        ]
    })
    
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert data["total_certificates"] == 2
    
def test_create_job_invalid_input(client):
    # Empty recipients
    response = client.post("/api/v1/jobs", json={"recipients": []})
    assert response.status_code == 422
    
    # Invalid email
    response = client.post("/api/v1/jobs", json={
        "recipients": [
            {
                "recipient_name": "Charlie",
                "recipient_email": "not-an-email",
                "course_name": "Testing 101"
            }
        ]
    })
    assert response.status_code == 422

def test_job_flow(client):
    # 1. Create a job
    response = client.post("/api/v1/jobs", json={
        "recipients": [
            {
                "recipient_name": "David",
                "recipient_email": "david@example.com",
                "course_name": "Backend Engineering"
            }
        ]
    })
    assert response.status_code == 202
    job_id = response.json()["id"]
    
    # Give the background task a little time to run
    time.sleep(1)
    
    # 2. Check job status
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    # It might be completed by now
    assert data["status"] in ["processing", "completed"]
    
    # 3. Check certificates
    response = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert response.status_code == 200
    data = response.json()
    assert len(data["certificates"]) == 1
    
    cert = data["certificates"][0]
    
    if cert["status"] == "generated":
        # 4. Try downloading if generated
        cert_id = cert["id"]
        response = client.get(f"/api/v1/certificates/{cert_id}/download")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
