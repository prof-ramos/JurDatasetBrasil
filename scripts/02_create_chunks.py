"""
Script 02: Criação de Chunks e Embeddings
Lê arquivos Markdown, divide em chunks semânticos, gera embeddings e salva no Supabase.
"""

import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from loguru import logger

from config import MARKDOWN_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
from database import SupabaseDB
from utils.text_processor import TextProcessor
from utils.embedding_generator import get_embedding_generator

def process_file(
    file_path: Path,
    processor: TextProcessor,
    generator,
    db: SupabaseDB
):
    """Processa um arquivo markdown: chunking + embedding + save."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extrair metadados básicos
        metadata = processor.extract_law_metadata(content)
        area = processor.detect_legal_area(content)
        if area:
            metadata["area"] = area

        # Buscar ou criar Lei no banco
        law_id = None
        if metadata.get("law_number"):
            law = db.get_or_create_law(
                law_number=metadata["law_number"],
                law_type=metadata.get("law_type", "lei"),
                title=metadata.get("title"),
                year=int(metadata["year"]) if metadata.get("year") else None
            )
            law_id = law.get("id")

        # Dividir em chunks
        chunks_data = processor.split_into_chunks(
            content,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        if not chunks_data:
            logger.warning(f"Nenhum chunk gerado para {file_path.name}")
            return

        # Preparar batch de chunks
        chunks_to_insert = []
        texts_to_embed = [c["content"] for c in chunks_data]

        # Gerar embeddings em batch
        embeddings = generator.generate_embeddings_batch(texts_to_embed, show_progress=False)

        if len(embeddings) != len(chunks_data):
            logger.error(f"Erro: esperados {len(chunks_data)} embeddings, recebidos {len(embeddings)} para {file_path.name}")
            return

        for i, chunk in enumerate(chunks_data):
            chunk_record = {
                "law_id": law_id,
                "source_type": "lei",  # Pode ser refinado
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "tokens": chunk["tokens"],
                "metadata": {
                    "filename": file_path.name,
                    "start_sentence": chunk["start_sentence"],
                    "end_sentence": chunk["end_sentence"],
                    **metadata
                },
                "embedding": embeddings[i]
            }
            chunks_to_insert.append(chunk_record)

        # Salvar no banco
        count = db.insert_chunks_batch(chunks_to_insert)
        logger.info(f"✓ {file_path.name}: {count} chunks salvos")

    except Exception as e:
        logger.error(f"Erro ao processar {file_path}: {e}")

def main():
    logger.info("=== Passo 2: Criação de Chunks e Embeddings ===")

    # Inicializar componentes
    db = SupabaseDB()
    processor = TextProcessor()
    generator = get_embedding_generator(model_name=EMBEDDING_MODEL)

    # Listar arquivos MD
    files = list(MARKDOWN_DIR.rglob("*.md"))
    if not files:
        logger.warning("Nenhum arquivo Markdown encontrado.")
        return

    logger.info(f"Processando {len(files)} arquivos...")

    for file_path in tqdm(files):
        process_file(file_path, processor, generator, db)

if __name__ == "__main__":
    main()
