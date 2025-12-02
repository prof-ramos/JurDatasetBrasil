from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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

# Configurações estáticas (simplificadas para deployment)
LLM_MODELS = {
    "gemini": {
        "model": "google/gemini-flash-1.5",
        "provider": "openrouter",
        "temperature": 0.3
    },
    "grok": {
        "model": "x-ai/grok-beta",
        "provider": "openrouter",
        "temperature": 0.3
    }
}

GENERATION_SYSTEM_PROMPT = """Você é um assistente especializado em Direito Administrativo Brasileiro.
Gere exemplos de treinamento baseados em legislação brasileira."""

VALIDATION_SYSTEM_PROMPT = """Você é um revisor especializado em Direito Administrativo Brasileiro.
Valide a precisão e qualidade dos exemplos de treinamento."""

@app.get("/")
def read_root():
    return {
        "message": "JurDatasetBrasil API is running",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
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
    return {
        "status": "healthy",
        "service": "JurDatasetBrasil API",
        "version": "0.1.0"
    }
