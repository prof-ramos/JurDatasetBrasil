"""
Orquestrador do Pipeline JurDatasetBrasil.
Executa os passos do pipeline sequencialmente ou individualmente.
"""

import argparse
import sys
from loguru import logger

# Importar scripts como módulos
# Nota: Isso assume que os scripts têm funções main() ou podem ser importados
# Para simplificar, vamos usar subprocess ou importar as funções main se refatorarmos
# Como os scripts têm `if __name__ == "__main__": main()`, podemos importar e chamar main()

import importlib

def _load_step_module(step_num: int):
    """Carrega o módulo de um passo específico sob demanda."""
    step_names = {
        1: "01_convert_to_markdown",
        2: "02_create_chunks",
        3: "03_generate_examples",
        4: "04_validate_quality",
        5: "05_export_to_jsonl"
    }
    try:
        return importlib.import_module(step_names[step_num])
    except ImportError as e:
        logger.error(f"Erro ao importar script do passo {step_num}: {e}")
        raise
    except KeyError:
        raise ValueError(f"Passo {step_num} inválido.")


def run_step(step_num: int):
    """Executa um passo específico."""
    logger.info(f"\n=== Executando Passo {step_num} ===")
    try:
        module = _load_step_module(step_num)
        if hasattr(module, "main"):
            module.main()
            return True
        else:
            logger.error(f"Módulo do passo {step_num} não tem função main()")
            return False
    except Exception as e:
        logger.error(f"Erro ao executar passo {step_num}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Pipeline JurDatasetBrasil")
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Executar apenas um passo específico"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Começar a partir de um passo específico"
    )

    args = parser.parse_args()

    if args.step:
        # Executar passo único
        if not run_step(args.step):
            logger.error("Passo falhou.")
            sys.exit(1)
        logger.success(f"\nPasso {args.step} executado com sucesso!")
    else:
        # Executar pipeline completo ou parcial
        start = args.start_from or 1

        for i in range(start, 6):
            if not run_step(i):
                logger.error("Pipeline interrompido devido a erro.")
                sys.exit(1)

        logger.success("\nPipeline executado com sucesso!")

if __name__ == "__main__":
    main()
