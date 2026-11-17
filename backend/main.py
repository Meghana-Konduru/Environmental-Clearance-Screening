from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.screening import router as screening_router

app = FastAPI(
    title="Environmental Clearance Pre-Screening API",
    description="Preliminary environmental clearance screening service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    screening_router,
    prefix="/api",
    tags=["Screening"]
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Environmental Clearance API"
    }