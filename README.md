# Bulk Certificate Generator

A robust API built with FastAPI and Python to handle bulk generation of certificates.

## Architecture & Design Decisions

### Background Processing
Bulk processing requires background jobs to avoid blocking the client request and causing timeouts. 
For simplicity and to minimize external dependencies for this project, I chose to use FastAPI's built-in `BackgroundTasks`. 
For a large-scale production system with potentially millions of records, a dedicated task queue like Celery paired with RabbitMQ or Redis would be more appropriate for better distribution and persistence of the queue.

### Storage
- **Database:** Uses SQLite for easy local setup, with SQLAlchemy as the ORM. This allows us to track the status of jobs and individual certificates.
- **File Storage:** Certificates are generated as PDF files using `reportlab` and saved to the local disk in the `output/` directory.

### Failure Handling
The system handles failures gracefully. If generating a single certificate fails (e.g. invalid template character, missing data), the system marks that specific certificate as `failed` with the error message and continues processing the rest of the job.

## Setup Instructions

1. Ensure you have Python 3.9+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

Run the test suite using pytest:
```bash
pytest
```
This will run the integration tests in the `tests/` directory.

## API Usage

### 1. Submit a Certificate Generation Request

Send a POST request to `/api/v1/jobs` with the list of recipients.

**Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "recipients": [
    {
      "recipient_name": "Alice Smith",
      "recipient_email": "alice@example.com",
      "course_name": "Advanced Python"
    },
    {
      "recipient_name": "Bob Jones",
      "recipient_email": "bob@example.com",
      "course_name": "Data Science 101"
    }
  ]
}'
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T10:00:00Z",
  "total_certificates": 2,
  "successful_certificates": 0,
  "failed_certificates": 0
}
```

### 2. Check Job Progress

Use the `id` from the creation step to poll for the job status.

**Request:**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/jobs/1' -H 'accept: application/json'
```

### 3. View Job Certificates Details

To see the detailed status of each certificate in the job.

**Request:**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/jobs/1/certificates' -H 'accept: application/json'
```

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  ...
  "certificates": [
    {
      "id": 1,
      "recipient_name": "Alice Smith",
      "recipient_email": "alice@example.com",
      "course_name": "Advanced Python",
      "status": "generated",
      "error_message": null,
      "created_at": "2023-10-27T10:00:00Z"
    }
  ]
}
```

### 4. Retrieve Generated Certificates

Once a certificate has a `status` of `generated`, use its `id` to download the PDF.

**Request:**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/certificates/1/download' --output Alice_Certificate.pdf
```
