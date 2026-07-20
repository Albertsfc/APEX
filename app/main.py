"""
APEX - AI Accounts Payable & Receivable Engine
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.config import settings
from app.database.db_manager import init_db
from app.api.router import api_router

# Configurar logging
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title="APEX - AI Accounts Payable & Receivable Engine",
    description="Engine for AR/AP automation, reconciliation, fraud detection, and dunning.",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logging.info("Starting APEX Engine...")
    init_db()

app.include_router(api_router)

# Mount frontend
frontend_dir = os.path.join(settings.BASE_DIR, "frontend")
os.makedirs(frontend_dir, exist_ok=True) # garante que a pasta exista ao subir
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
