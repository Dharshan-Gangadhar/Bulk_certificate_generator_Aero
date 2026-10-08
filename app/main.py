from fastapi import FastAPI
from .database import engine
from . import models
from .routers import certificates

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="API for generating certificates in bulk for event participants.",
    version="1.0.0"
)

# Include routers
app.include_router(certificates.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Bulk Certificate Generator API. Visit /docs for API documentation."}
