from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router

app = FastAPI(
    title="Social Intelligence Engine",
    description="Discover communities, resolve entities, and infer relationships",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Social Intelligence Engine API"}


@app.get("/health")
def health():
    return {"status": "ok"}
