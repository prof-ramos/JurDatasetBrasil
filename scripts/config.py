"""
Configurações centralizadas do JurDatasetBrasil.
Carrega variáveis de ambiente e define constantes do projeto a partir de config.yaml.
"""

import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Carrega variáveis de ambiente
load_dotenv()

# =============================================================================
# DIRETÓRIOS BASE
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DOCS_DIR = PROJECT_ROOT / os.getenv("RAW_DOCS_DIR", "0-RawDocs")
MARKDOWN_DIR = PROJECT_ROOT / os.getenv("MARKDOWN_DIR", "1-MarkdownClean")
CHUNKS_DIR = PROJECT_ROOT / os.getenv("CHUNKS_DIR", "2-Chunks")
DATASET_DIR = PROJECT_ROOT / os.getenv("DATASET_DIR", "3-FinalDataset")
BENCHMARKS_DIR = PROJECT_ROOT / os.getenv("BENCHMARKS_DIR", "4-Benchmarks")
MODELS_DIR = PROJECT_ROOT / os.getenv("MODELS_DIR", "5-Models")
LOGS_DIR = PROJECT_ROOT / os.getenv("LOGS_DIR", "logs")

# Criar diretórios se não existirem
for directory in [RAW_DOCS_DIR, MARKDOWN_DIR, CHUNKS_DIR, DATASET_DIR,
                  BENCHMARKS_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =============================================================================
# CARREGAMENTO DO CONFIG.YAML
# =============================================================================
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

def load_yaml_config():
    if not CONFIG_PATH.exists():
        logger.warning(f"Arquivo {CONFIG_PATH} não encontrado. Usando valores padrão.")
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Erro ao ler config.yaml: {e}")
        return {}

YAML_CONFIG = load_yaml_config()

# Helpers para acessar config com fallback
def get_config(path: str, default=None):
    """Acessa configuração aninhada ex: 'llm.generation.temperature'"""
    keys = path.split('.')
    value = YAML_CONFIG
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default

# =============================================================================
# SUPABASE
# =============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Use SERVICE_ROLE_KEY para operações de backend (bypassa RLS)
# Use ANON_KEY apenas para operações públicas
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or SUPABASE_SERVICE_ROLE_KEY

if not SUPABASE_KEY:
    logger.warning("SUPABASE_KEY/SERVICE_ROLE_KEY não configurada, usando ANON_KEY (permissões limitadas)")
    SUPABASE_KEY = SUPABASE_ANON_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Credenciais do Supabase não configuradas!")
    # Não levantar erro aqui para permitir que o build da Vercel funcione sem .env local
    # raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios. Configure o arquivo .env")

# =============================================================================
# OPENROUTER / LLMs
# =============================================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY não configurada. Funcionalidades de LLM estarão desabilitadas.")

# Modelos disponíveis (carregados do YAML ou fallback)
LLM_MODELS = get_config("llm.models", {
    "gemini": "google/gemini-flash-1.5",
    "grok": "x-ai/grok-beta",
    "default": "google/gemini-flash-1.5"
})

# =============================================================================
# EMBEDDINGS
# =============================================================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", get_config("embeddings.model", "sentence-transformers/all-MiniLM-L6-v2"))
try:
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", str(get_config("embeddings.dimension", 384))))
except ValueError:
    logger.warning("EMBEDDING_DIMENSION inválida, usando padrão 384")
    EMBEDDING_DIMENSION = 384

# =============================================================================
# CONFIGURAÇÕES DO PIPELINE
# =============================================================================

# Funções auxiliares para conversão segura
def safe_int(env_var: str, config_path: str, default: str) -> int:
    env_val = os.getenv(env_var)
    if env_val:
        try:
            return int(env_val)
        except ValueError:
            pass
    try:
        return int(get_config(config_path, default))
    except (ValueError, TypeError):
        logger.warning(f"Valor inválido para {config_path}, usando padrão {default}")
        return int(default)

def safe_float(env_var: str, config_path: str, default: str) -> float:
    env_val = os.getenv(env_var)
    if env_val:
        try:
            return float(env_val)
        except ValueError:
            pass
    try:
        return float(get_config(config_path, default))
    except (ValueError, TypeError):
        logger.warning(f"Valor inválido para {config_path}, usando padrão {default}")
        return float(default)

# Chunking
CHUNK_SIZE = safe_int("CHUNK_SIZE", "pipeline.chunk_size", "1500")
CHUNK_OVERLAP = safe_int("CHUNK_OVERLAP", "pipeline.chunk_overlap", "200")

# Geração de exemplos
MAX_EXAMPLES_PER_CHUNK = safe_int("MAX_EXAMPLES_PER_CHUNK", "pipeline.max_examples_per_chunk", "3") # Valor padrão hardcoded se não estiver no yaml
GENERATION_BATCH_SIZE = safe_int("GENERATION_BATCH_SIZE", "llm.generation.batch_size", "10")
TEMPERATURE = safe_float("TEMPERATURE", "llm.generation.temperature", "0.3")

# Qualidade
MIN_OUTPUT_LENGTH = safe_int("MIN_OUTPUT_LENGTH", "pipeline.min_output_length", "50")
MAX_OUTPUT_LENGTH = safe_int("MAX_OUTPUT_LENGTH", "pipeline.max_output_length", "1000")
SIMILARITY_THRESHOLD = safe_float("SIMILARITY_THRESHOLD", "pipeline.similarity_threshold", "0.85")

# =============================================================================
# EXECUÇÃO
# =============================================================================
NUM_WORKERS = safe_int("NUM_WORKERS", "execution.num_workers", "4")
API_DELAY = safe_float("API_DELAY", "execution.api_delay", "1.0")
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# =============================================================================
# LOGGING
# =============================================================================
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# Configurar logger
logger.remove()
logger.add(
    LOGS_DIR / "jurdataset_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="00:00",
    retention="30 days",
    compression="zip"
)
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True
)

# =============================================================================
# SCHEMA DE VALIDAÇÃO
# =============================================================================
EXAMPLE_SCHEMA = {
    "type": "object",
    "required": ["instruction", "output"],
    "properties": {
        "instruction": {"type": "string", "minLength": 10},
        "input": {"type": "string"},
        "output": {"type": "string", "minLength": MIN_OUTPUT_LENGTH, "maxLength": MAX_OUTPUT_LENGTH},
        "metadata": {
            "type": "object",
            "properties": {
                "law_number": {"type": "string"},
                "article_ref": {"type": "string"},
                "area": {"type": "string"},
                "difficulty": {"type": "string", "enum": ["facil", "medio", "dificil"]},
                "exam_board": {"type": "string"},
                "exam_year": {"type": "integer"},
                "source_chunks": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}

# =============================================================================
# PROMPTS DE SISTEMA
# =============================================================================
GENERATION_SYSTEM_PROMPT = get_config("prompts.generation_system", """Você é um especialista em Direito brasileiro.
Crie questões jurídicas precisas baseadas no texto fornecido.""")

VALIDATION_SYSTEM_PROMPT = get_config("prompts.validation_system", """Você é um validador técnico.
Avalie se a resposta está correta baseando-se no texto de referência.""")

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def get_model_name(model_type: str = "default") -> str:
    """Retorna o nome completo do modelo LLM."""
    return LLM_MODELS.get(model_type, LLM_MODELS.get("default", "google/gemini-flash-1.5"))

def validate_config() -> bool:
    """Valida se as configurações mínimas estão presentes."""
    required_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY
    }

    missing = [k for k, v in required_vars.items() if not v]

    if missing:
        logger.error(f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing)}")
        logger.error("Configure o arquivo .env baseado em .env.example")
        # Em ambiente de build (Vercel), podemos não ter .env, então retornamos False mas não quebramos se for import
        if os.getenv("VERCEL"):
             logger.warning("Rodando na Vercel, ignorando falta de .env no build time.")
             return True
        raise ValueError(f"Configuração inválida: variáveis ausentes: {', '.join(missing)}")

    logger.info("✓ Configuração validada com sucesso")
    return True

if __name__ == "__main__":
    # Teste de configuração
    logger.info("=== Configuração do JurDatasetBrasil ===")
    logger.info(f"Ambiente: {ENV}")
    logger.info(f"Debug: {DEBUG}")
    logger.info(f"Diretório raiz: {PROJECT_ROOT}")
    logger.info(f"Modelo de embedding: {EMBEDDING_MODEL}")
    logger.info(f"Chunk size: {CHUNK_SIZE} tokens")
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        sys.exit(1)
