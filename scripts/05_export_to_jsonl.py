"""
Script 05: Exportação para JSONL
Exporta exemplos validados para formato de treino (JSONL).
"""

import os
import jsonlines
from typing import List, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime

from config import DATASET_DIR
from database import SupabaseDB

def export_dataset(
    db: SupabaseDB,
    dataset_id: str = "jurdataset_v1",
    output_format: str = "sharegpt"
) -> Optional[Path]:
    """
    Exporta dataset para arquivo JSONL.

    Args:
        output_format: 'sharegpt' (conversational) ou 'alpaca' (instruction/input/output)
    """
    if output_format not in ("sharegpt", "alpaca"):
        logger.error(f"Formato inválido: {output_format}. Use 'sharegpt' ou 'alpaca'.")
        raise ValueError(f"Formato de saída não suportado: {output_format}")

    # Buscar exemplos (idealmente apenas os validados)
    try:
        examples = db.get_examples_by_dataset(dataset_id)
    except Exception as e:
        logger.error(f"Erro ao buscar exemplos do banco de dados: {e}")
        return None

    if not examples:
        logger.warning(f"Nenhum exemplo encontrado para o dataset {dataset_id}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = DATASET_DIR / f"jurdataset_{output_format}_{timestamp}.jsonl"

    logger.info(f"Exportando {len(examples)} exemplos para {output_file}...")

    count = 0
    failed = 0
    with jsonlines.open(output_file, mode='w') as writer:
        for ex in examples:
            try:
                # Validar campos obrigatórios
                if "instruction" not in ex or "output" not in ex:
                    logger.warning(f"Exemplo {ex.get('id')} sem campos obrigatórios, pulando...")
                    failed += 1
                    continue

                if output_format == "sharegpt":
                    # Formato ShareGPT: conversations list
                    record = {
                        "conversations": [
                            {"from": "human", "value": ex["instruction"]},
                            {"from": "gpt", "value": ex["output"]}
                        ],
                        "system": "Você é um assistente jurídico especializado em Direito Brasileiro."
                    }
                elif output_format == "alpaca":
                    # Formato Alpaca: instruction, input, output
                    record = {
                        "instruction": ex["instruction"],
                        "input": ex.get("input", ""),
                        "output": ex["output"]
                    }
                else:
                    # Isso nunca deveria acontecer se a validação foi feita
                    logger.error(f"Formato desconhecido: {output_format}")
                    failed += 1
                    continue

                # Adicionar metadados se útil
                # record["metadata"] = ...

                writer.write(record)
                count += 1

            except Exception as e:
                logger.error(f"Erro ao exportar exemplo {ex.get('id')}: {e}")
                failed += 1

    logger.success(f"✓ Exportação concluída: {count} registros salvos, {failed} falharam.")
    return output_file

def main():
    logger.info("=== Passo 5: Exportação Final ===")

    try:
        db = SupabaseDB()

        # Exportar formato ShareGPT (padrão para muitos fine-tunes atuais)
        output_path = export_dataset(db, output_format="sharegpt")
        if output_path:
            logger.info(f"Arquivo exportado: {output_path}")

        # Exportar formato Alpaca (opcional)
        # output_path = export_dataset(db, output_format="alpaca")
        # if output_path:
        #     logger.info(f"Arquivo exportado: {output_path}")

    except Exception as e:
        logger.error(f"Erro fatal durante exportação: {e}")
        raise

if __name__ == "__main__":
    main()
