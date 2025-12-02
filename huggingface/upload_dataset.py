"""
Script para upload automático do JurDatasetBrasil para Hugging Face Hub
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datasets import Dataset, DatasetDict, Features, Value, Sequence
from huggingface_hub import HfApi, login
from loguru import logger
import pandas as pd

# Configuração
HF_REPO_ID = os.getenv("HF_REPO_ID", "prof-ramos/JurDatasetBrasil")
HF_TOKEN = os.getenv("HF_TOKEN")
DATASET_DIR = Path("3-FinalDataset")

def load_jsonl_files(split: str) -> List[Dict]:
    """
    Carrega arquivos JSONL de um split específico

    Args:
        split: train, validation ou test

    Returns:
        Lista de exemplos
    """
    examples = []
    pattern = f"*{split}*.jsonl"

    logger.info(f"Buscando arquivos {pattern} em {DATASET_DIR}")

    for file_path in DATASET_DIR.glob(pattern):
        logger.info(f"Carregando {file_path.name}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    example = json.loads(line)
                    examples.append(example)

    logger.success(f"✓ {len(examples)} exemplos carregados para split '{split}'")
    return examples

def validate_examples(examples: List[Dict]) -> List[Dict]:
    """
    Valida e limpa exemplos

    Args:
        examples: Lista de exemplos

    Returns:
        Exemplos validados
    """
    valid_examples = []

    for i, example in enumerate(examples):
        # Campos obrigatórios
        if not example.get("instruction") or not example.get("output"):
            logger.warning(f"Exemplo {i} sem instruction/output, pulando...")
            continue

        # Normalizar estrutura
        normalized = {
            "instruction": example.get("instruction", ""),
            "input": example.get("input", ""),
            "output": example.get("output", ""),
            "difficulty": example.get("difficulty", "medio"),
            "task_type": example.get("task_type", "geral"),
            "exam_board": example.get("exam_board", ""),
            "exam_year": example.get("exam_year", 0),
            "area": example.get("metadata", {}).get("area", "Direito Administrativo"),
            "law_number": example.get("metadata", {}).get("law_number", ""),
            "article_ref": example.get("metadata", {}).get("article_ref", ""),
            "source_chunks": example.get("metadata", {}).get("source_chunks", []),
        }

        valid_examples.append(normalized)

    logger.info(f"✓ {len(valid_examples)}/{len(examples)} exemplos válidos")
    return valid_examples

def create_dataset_dict() -> DatasetDict:
    """
    Cria DatasetDict com todos os splits

    Returns:
        DatasetDict pronto para upload
    """
    dataset_dict = {}

    for split in ["train", "validation", "test"]:
        logger.info(f"\n📊 Processando split: {split}")

        # Carregar exemplos
        examples = load_jsonl_files(split)

        if not examples:
            logger.warning(f"⚠️  Nenhum exemplo encontrado para split '{split}', pulando...")
            continue

        # Validar
        valid_examples = validate_examples(examples)

        if not valid_examples:
            logger.warning(f"⚠️  Nenhum exemplo válido para split '{split}', pulando...")
            continue

        # Criar Dataset
        df = pd.DataFrame(valid_examples)
        dataset = Dataset.from_pandas(df)

        dataset_dict[split] = dataset
        logger.success(f"✓ Dataset '{split}' criado com {len(dataset)} exemplos")

    return DatasetDict(dataset_dict)

def upload_to_hub(
    dataset_dict: DatasetDict,
    repo_id: str,
    token: Optional[str] = None,
    private: bool = True
) -> None:
    """
    Upload dataset para Hugging Face Hub

    Args:
        dataset_dict: Dataset a ser enviado
        repo_id: ID do repositório (username/dataset-name)
        token: Token de autenticação HF
        private: Se o dataset deve ser privado
    """
    logger.info(f"\n🚀 Iniciando upload para {repo_id}")

    # Login
    if token:
        login(token=token)
        logger.success("✓ Autenticado no Hugging Face Hub")
    else:
        logger.warning("⚠️  HF_TOKEN não fornecido, usando autenticação local")

    # Upload
    try:
        dataset_dict.push_to_hub(
            repo_id=repo_id,
            private=private,
            token=token
        )
        logger.success(f"✓ Dataset enviado com sucesso para {repo_id}")
        logger.info(f"🔗 URL: https://huggingface.co/datasets/{repo_id}")

    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        raise

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("JurDatasetBrasil - Upload para Hugging Face Hub")
    logger.info("=" * 60)

    # Verificar diretório
    if not DATASET_DIR.exists():
        logger.error(f"❌ Diretório {DATASET_DIR} não encontrado!")
        return

    # Criar dataset
    dataset_dict = create_dataset_dict()

    if not dataset_dict:
        logger.error("❌ Nenhum split foi criado, abortando upload")
        return

    # Estatísticas
    logger.info("\n📊 Estatísticas finais:")
    for split, dataset in dataset_dict.items():
        logger.info(f"  - {split}: {len(dataset):,} exemplos")

    # Upload
    upload_to_hub(
        dataset_dict=dataset_dict,
        repo_id=HF_REPO_ID,
        token=HF_TOKEN,
        private=True  # Trocar para False quando quiser publicar
    )

    logger.success("\n✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
