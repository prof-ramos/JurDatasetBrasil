"""
Script 03: Geração de Exemplos (Q/A)
Consulta chunks do Supabase e usa LLM para gerar pares de instrução/resposta.
"""

import json
import time
from typing import List, Dict
from tqdm import tqdm
from loguru import logger
from openai import OpenAI
from pydantic import BaseModel, Field

from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODELS,
    GENERATION_SYSTEM_PROMPT, MAX_EXAMPLES_PER_CHUNK,
    GENERATION_BATCH_SIZE, API_DELAY, EMBEDDING_MODEL,
    get_config
)
from database import SupabaseDB
from utils.embedding_generator import get_embedding_generator

# Modelo Pydantic para validação da saída do LLM
class QAExample(BaseModel):
    instruction: str = Field(..., description="A pergunta ou instrução")
    output: str = Field(..., description="A resposta correta e fundamentada")
    difficulty: str = Field(..., description="Nível de dificuldade: facil, medio, dificil")
    task_type: str = Field(..., description="Tipo da questão: objetiva, discursiva, conceito")

class QABatch(BaseModel):
    examples: List[QAExample]

def generate_examples_from_chunk(
    chunk: Dict,
    client: OpenAI,
    model: str
) -> List[Dict]:
    """Gera exemplos a partir de um chunk usando LLM."""

    prompt = f"""
    TEXTO DE REFERÊNCIA:
    {chunk['content']}

    METADADOS:
    Lei: {chunk['metadata'].get('law_number', 'N/A')}
    Ano: {chunk['metadata'].get('year', 'N/A')}

    TAREFA:
    Gere {MAX_EXAMPLES_PER_CHUNK} questões jurídicas baseadas EXCLUSIVAMENTE neste texto.
    Retorne em formato JSON compatível com o schema.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        # Tentar adaptar diferentes formatos de resposta JSON
        examples_data = []
        if "examples" in parsed:
            examples_data = parsed["examples"]
        elif isinstance(parsed, list):
            examples_data = parsed
        else:
            # Tentar encontrar lista em chaves
            for key, value in parsed.items():
                if isinstance(value, list):
                    examples_data = value
                    break

        # Validar e formatar
        valid_examples = []
        for ex in examples_data:
            try:
                # Normalizar chaves
                if "question" in ex: ex["instruction"] = ex.pop("question")
                if "answer" in ex: ex["output"] = ex.pop("answer")

                valid_examples.append(ex)
            except Exception:
                continue

        return valid_examples

    except Exception as e:
        logger.error(f"Erro na geração LLM: {e}")
        return []

def get_or_create_dataset(db: SupabaseDB, split: str = "train") -> str:
    """
    Busca ou cria o dataset atual no banco de dados.

    Args:
        db: Instância do SupabaseDB
        split: Split do dataset (train, validation, test)

    Returns:
        UUID do dataset
    """
    dataset_name = get_config("dataset.name", "JurDatasetBrasil")
    dataset_version = get_config("dataset.current_version", "v0.1")
    dataset_description = get_config("dataset.description", "Dataset jurídico brasileiro")

    # Tentar buscar dataset existente
    result = db.client.table("datasets").select("*")\
        .eq("name", dataset_name)\
        .eq("version", dataset_version)\
        .eq("split", split)\
        .execute()

    if result.data:
        dataset_id = result.data[0]["id"]
        logger.info(f"✓ Dataset encontrado: {dataset_name} {dataset_version} ({split}) - ID: {dataset_id}")
        return dataset_id

    # Criar novo dataset
    new_dataset = db.client.table("datasets").insert({
        "name": dataset_name,
        "version": dataset_version,
        "split": split,
        "description": f"{dataset_description} - Split: {split}"
    }).execute()

    dataset_id = new_dataset.data[0]["id"]
    logger.success(f"✓ Dataset criado: {dataset_name} {dataset_version} ({split}) - ID: {dataset_id}")
    return dataset_id

def main():
    logger.info("=== Passo 3: Geração de Exemplos (LLM) ===")

    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY não configurada!")
        return

    # Inicializar
    db = SupabaseDB(use_service_role=True)
    generator = get_embedding_generator(model_name=EMBEDDING_MODEL)
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY
    )

    # Obter ou criar dataset
    dataset_id = get_or_create_dataset(db, split="train")

    # Buscar chunks não processados usando o novo índice
    chunks = db.client.table("chunks")\
        .select("*")\
        .eq("processed_for_generation", False)\
        .limit(100)\
        .execute().data

    if not chunks:
        logger.warning("Nenhum chunk não processado encontrado no banco.")
        return

    logger.info(f"Gerando exemplos para {len(chunks)} chunks não processados...")

    total_generated = 0
    chunks_processed = []

    for chunk in tqdm(chunks):
        examples = generate_examples_from_chunk(
            chunk,
            client,
            LLM_MODELS["default"]
        )

        if not examples:
            # Marcar como processado mesmo sem exemplos gerados
            chunks_processed.append(chunk["id"])
            continue

        # Preparar para salvar
        examples_to_save = []

        # Gerar embeddings das instruções
        instructions = [ex["instruction"] for ex in examples]
        embeddings = generator.generate_embeddings_batch(instructions, show_progress=False)

        for i, ex in enumerate(examples):
            record = {
                "dataset_id": dataset_id,
                "instruction": ex["instruction"],
                "output": ex["output"],
                "difficulty": ex.get("difficulty", "medio"),
                "task_type": ex.get("task_type", "geral"),
                "embedding": embeddings[i],
                "law_id": chunk.get("law_id"),
                "chunk_ids": [chunk["id"]],
                "tags": ["generated", "llm"]
            }
            examples_to_save.append(record)

        count = db.insert_examples_batch(examples_to_save)
        total_generated += count

        # Adicionar chunk à lista de processados
        chunks_processed.append(chunk["id"])

        time.sleep(API_DELAY)

    # Marcar chunks como processados em batch
    if chunks_processed:
        for chunk_id in chunks_processed:
            db.client.table("chunks")\
                .update({"processed_for_generation": True})\
                .eq("id", chunk_id)\
                .execute()
        logger.info(f"✓ {len(chunks_processed)} chunks marcados como processados")

    logger.success(f"Total de exemplos gerados: {total_generated}")

if __name__ == "__main__":
    main()
