"""
Script 01: Conversão de Documentos para Markdown
Usa Docling para converter arquivos DOCX/PDF da pasta raw para markdown limpo.
"""

import os
import time
from pathlib import Path
from typing import List
from loguru import logger
from docling.document_converter import DocumentConverter

from config import RAW_DOCS_DIR, MARKDOWN_DIR, NUM_WORKERS

def get_files_to_process() -> List[Path]:
    """Lista arquivos suportados no diretório raw."""
    supported_extensions = {".docx", ".pdf", ".doc", ".rtf"}
    files = []

    for ext in supported_extensions:
        files.extend(list(RAW_DOCS_DIR.rglob(f"*{ext}")))


    return files

def convert_document(file_path: Path, converter: DocumentConverter) -> bool:
    """Converte um único documento para markdown."""
    try:
        relative_path = file_path.relative_to(RAW_DOCS_DIR)
        output_path = MARKDOWN_DIR / relative_path.with_suffix(".md")

        # Pular se já existe
        if output_path.exists():
            logger.info(f"Skipping {relative_path} (já existe)")
            return True

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Convertendo: {relative_path}")
        if file_path.suffix.lower() == '.rtf':
            txt_path = output_path.parent / f"{file_path.stem}.txt"
            subprocess.check_call(['textutil', '-convert', 'txt', str(file_path), '-output', str(txt_path)])
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                markdown_content = f"# {file_path.stem}\n\n{content}"
            finally:
                txt_path.unlink(missing_ok=True)
        else:
            result = converter.convert(file_path)
            markdown_content = result.document.export_to_markdown()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)


        logger.success(f"✓ Convertido: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao converter {file_path}: {e}")
        return False

def main():
    logger.info("=== Passo 1: Conversão para Markdown ===")

    files = get_files_to_process()
    if not files:
        logger.warning("Nenhum arquivo encontrado para processar.")
        return

    logger.info(f"Encontrados {len(files)} arquivos.")

    converter = DocumentConverter()

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(convert_document, file_path, converter) for file_path in files]
        success_count = sum(f.result() for f in futures)

    logger.info(f"Concluído. Sucesso: {success_count}/{len(files)}")


if __name__ == "__main__":
    main()
