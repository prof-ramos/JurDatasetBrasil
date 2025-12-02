"""
Configurações centralizadas do JurDatasetBrasil.
Carrega variáveis de ambiente e define constantes do projeto.
"""

import os
from pathlib import Path
from typing import Optional
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
# SUPABASE
# =============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Credenciais do Supabase não configuradas. Algumas funcionalidades estarão desabilitadas.")

# =============================================================================
# OPENROUTER / LLMs
# =============================================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Modelos disponíveis
LLM_MODELS = {
    "gemini": "google/gemini-flash-1.5",
    "grok": "x-ai/grok-beta",
    "default": "google/gemini-flash-1.5"
}

# =============================================================================
# EMBEDDINGS
# =============================================================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

# =============================================================================
# CONFIGURAÇÕES DO PIPELINE
# =============================================================================

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Geração de exemplos
MAX_EXAMPLES_PER_CHUNK = int(os.getenv("MAX_EXAMPLES_PER_CHUNK", "3"))
GENERATION_BATCH_SIZE = int(os.getenv("GENERATION_BATCH_SIZE", "10"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# Qualidade
MIN_OUTPUT_LENGTH = int(os.getenv("MIN_OUTPUT_LENGTH", "50"))
MAX_OUTPUT_LENGTH = int(os.getenv("MAX_OUTPUT_LENGTH", "1000"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))

# =============================================================================
# EXECUÇÃO
# =============================================================================
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))
API_DELAY = float(os.getenv("API_DELAY", "1.0"))
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
    lambda msg: print(msg, end=""),
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
GENERATION_SYSTEM_PROMPT = """Você é um especialista em Direito brasileiro com foco em questões estilo CESPE/FGV.
Sua tarefa é criar questões jurídicas precisas, objetivas e baseadas EXCLUSIVAMENTE no texto fornecido.

REGRAS OBRIGATÓRIAS:
1. Use SOMENTE informações contidas no texto fornecido
2. Não invente dados, casos ou interpretações
3. Mantenha a precisão técnica e a terminologia jurídica correta
4. Cite artigos e parágrafos quando relevante
5. Crie questões que testem compreensão, não memorização
6. Varie o nível de dificuldade (fácil, médio, difícil)
7. Responda de forma completa mas concisa (50-500 palavras)

FORMATOS ACEITOS:
- Questões objetivas (V/F com justificativa)
- Questões discursivas
- Análise de casos práticos
- Explicação de conceitos
"""

VALIDATION_SYSTEM_PROMPT = """Você é um validador técnico de conteúdo jurídico.
Avalie se a resposta está CORRETA e COMPLETA baseando-se exclusivamente no texto de referência.

Retorne apenas:
- "APROVADO" se a resposta está correta e bem fundamentada
- "REPROVADO: [motivo]" se houver erro factual, imprecisão ou informação não baseada no texto
"""

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def get_model_name(model_type: str = "default") -> str:
    """Retorna o nome completo do modelo LLM."""
    return LLM_MODELS.get(model_type, LLM_MODELS["default"])

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
        return False

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
    validate_config()
