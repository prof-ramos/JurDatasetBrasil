"""
Script 04: Validação de Qualidade e Deduplicação
Verifica qualidade dos exemplos gerados e remove duplicatas semânticas.
"""

import json
from typing import List, Dict
from tqdm import tqdm
from loguru import logger
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODELS,
    VALIDATION_SYSTEM_PROMPT, SIMILARITY_THRESHOLD,
    MIN_OUTPUT_LENGTH, MAX_OUTPUT_LENGTH, EMBEDDING_MODEL
)
from database import SupabaseDB
from utils.embedding_generator import get_embedding_generator

def validate_example_llm(
    example: Dict,
    client: OpenAI,
    model: str
) -> bool:
    """Valida qualidade do exemplo usando LLM."""

    prompt = f"""
    INSTRUÇÃO: {example['instruction']}
    RESPOSTA: {example['output']}

    Avalie se a resposta é correta, completa e relevante para a instrução.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": VALIDATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        content = response.choices[0].message.content.strip().upper()
        return "APROVADO" in content

    except Exception as e:
        logger.error(f"Erro na validação LLM: {e}")
        return False

def check_duplicates(
    example: Dict,
    db: SupabaseDB,
    generator,
    threshold: float = 0.95
) -> bool:
    """Verifica se já existe exemplo semanticamente idêntico."""

    # Busca exemplos similares no banco
    # Nota: SupabaseDB.search_similar_examples espera lista de floats
    # Se o embedding vier como string do banco, precisa converter
    embedding = example.get("embedding")

    if isinstance(embedding, str):
        embedding = json.loads(embedding)

    similars = db.search_similar_examples(
        query_embedding=embedding,
        limit=1
    )

    if not similars:
        return False

    # Se o mais similar tiver score muito alto e não for o próprio exemplo
    top_match = similars[0]

    # Se estamos validando um exemplo que JÁ está no banco, ele vai se encontrar
    # Então precisamos checar ID
    if str(top_match.get("id")) == str(example.get("id")):
        return False

    # O score retornado pela função RPC geralmente é 'similarity'
    score = top_match.get("similarity", 0.0)

    return score > threshold

def main():
    logger.info("=== Passo 4: Validação de Qualidade ===")

    db = SupabaseDB()
    generator = get_embedding_generator(model_name=EMBEDDING_MODEL)
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY
    )

    # Buscar exemplos para validar (simplificado: busca todos não validados)
    # Idealmente teríamos status 'pending_validation'
    examples = db.client.table("examples").select("*").limit(100).execute().data

    if not examples:
        logger.warning("Nenhum exemplo encontrado para validar.")
        return

    logger.info(f"Validando {len(examples)} exemplos...")

    valid_count = 0
    removed_count = 0

    for example in tqdm(examples):
        # 1. Validação Regras Básicas
        if len(example["output"]) < MIN_OUTPUT_LENGTH:
            logger.debug(f"Reprovado (curto): {example['id']}")
            # db.delete_example(example['id']) # Implementar delete se necessário
            continue

        if len(example["output"]) > MAX_OUTPUT_LENGTH:
            logger.debug(f"Reprovado (longo): {example['id']}")
            continue

        # 2. Validação de Duplicatas
        # Converter embedding string -> list se necessário
        if isinstance(example["embedding"], str):
            example["embedding"] = json.loads(example["embedding"])

        if check_duplicates(example, db, generator, threshold=SIMILARITY_THRESHOLD):
            logger.debug(f"Reprovado (duplicata): {example['id']}")
            removed_count += 1
            continue

        # 3. Validação LLM (Amostragem ou todos)
        # Para economizar tokens, podemos validar apenas uma porcentagem ou os duvidosos
        # Aqui validamos todos para garantir qualidade
        if validate_example_llm(example, client, LLM_MODELS["default"]):
            valid_count += 1
            # Marcar como validado no banco
            # db.update_example_status(example['id'], 'validated')
        else:
            logger.debug(f"Reprovado (LLM): {example['id']}")

    logger.success(f"Validação concluída.")
    logger.info(f"Aprovados: {valid_count}")
    logger.info(f"Duplicatas/Removidos: {removed_count}")

if __name__ == "__main__":
    main()
