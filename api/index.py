from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao sys.path para importar scripts
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from scripts.config import LLM_MODELS, GENERATION_SYSTEM_PROMPT, VALIDATION_SYSTEM_PROMPT

app = FastAPI(
    title="JurDatasetBrasil API",
    description="API para acesso aos dados e configurações do JurDatasetBrasil",
    version="0.1.0"
)

# Configurar CORS
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "JurDatasetBrasil API is running",
        "docs": "/docs"
    }

@app.get("/config/models")
def get_models():
    """Retorna os modelos LLM configurados."""
    return LLM_MODELS

@app.get("/config/prompts")
def get_prompts():
    """Retorna os prompts de sistema configurados."""
    return {
        "generation_system": GENERATION_SYSTEM_PROMPT,
        "validation_system": VALIDATION_SYSTEM_PROMPT
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
