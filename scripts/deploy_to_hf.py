"""
Script para criar e fazer deploy do Space no Hugging Face
"""

import os
import shutil
from pathlib import Path
from huggingface_hub import HfApi, create_repo, login
from loguru import logger

# Configuração
SPACE_NAME = "JurDatasetBrasil-Explorer"
USERNAME = os.getenv("HF_USERNAME", "prof-ramos")
SPACE_ID = f"{USERNAME}/{SPACE_NAME}"
HF_TOKEN = os.getenv("HF_TOKEN")

def setup_space_directory(target_dir: Path) -> None:
    """
    Prepara diretório com arquivos necessários para o Space

    Args:
        target_dir: Diretório alvo
    """
    logger.info(f"Preparando arquivos em {target_dir}")

    # Criar diretório
    target_dir.mkdir(exist_ok=True, parents=True)

    # Copiar arquivos essenciais
    files_to_copy = {
        "huggingface/app.py": "app.py",
        ".space.yml": ".space.yml",
        "requirements-huggingface.txt": "requirements.txt",
        "huggingface/README.md": "README.md",
    }

    project_root = Path(__file__).parent.parent

    for src, dst in files_to_copy.items():
        src_path = project_root / src
        dst_path = target_dir / dst

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            logger.success(f"✓ Copiado: {src} → {dst}")
        else:
            logger.warning(f"⚠️  Arquivo não encontrado: {src}")

    logger.success(f"✓ Arquivos preparados em {target_dir}")

def create_space(space_id: str, token: str, private: bool = False) -> None:
    """
    Cria Space no Hugging Face

    Args:
        space_id: ID do space (username/space-name)
        token: Token HF
        private: Se o space deve ser privado
    """
    logger.info(f"Criando Space: {space_id}")

    try:
        # Login
        login(token=token)

        # Criar Space
        api = HfApi()
        url = create_repo(
            repo_id=space_id,
            token=token,
            repo_type="space",
            space_sdk="gradio",
            private=private,
            exist_ok=True
        )

        logger.success(f"✓ Space criado/verificado: {url}")
        return url

    except Exception as e:
        logger.error(f"❌ Erro ao criar Space: {e}")
        raise

def upload_to_space(space_id: str, local_dir: Path, token: str) -> None:
    """
    Faz upload dos arquivos para o Space

    Args:
        space_id: ID do space
        local_dir: Diretório local com arquivos
        token: Token HF
    """
    logger.info(f"Fazendo upload para {space_id}...")

    try:
        api = HfApi()

        # Upload de todos os arquivos do diretório
        api.upload_folder(
            folder_path=str(local_dir),
            repo_id=space_id,
            repo_type="space",
            token=token,
            commit_message="🚀 Initial deployment from JurDatasetBrasil"
        )

        logger.success(f"✓ Upload concluído!")
        logger.info(f"🔗 Space URL: https://huggingface.co/spaces/{space_id}")

    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        raise

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("JurDatasetBrasil - Deploy to Hugging Face Space")
    logger.info("=" * 60)

    # Verificar token
    if not HF_TOKEN:
        logger.error("❌ HF_TOKEN não configurado!")
        logger.info("Configure com: export HF_TOKEN='hf_...'")
        logger.info("Ou obtenha em: https://huggingface.co/settings/tokens")
        return

    # Preparar diretório temporário
    temp_dir = Path(__file__).parent.parent / "temp_hf_space"

    try:
        # 1. Preparar arquivos
        logger.info("\n📦 Passo 1: Preparando arquivos...")
        setup_space_directory(temp_dir)

        # 2. Criar Space
        logger.info(f"\n🌐 Passo 2: Criando Space '{SPACE_ID}'...")
        space_url = create_space(SPACE_ID, HF_TOKEN, private=False)

        # 3. Upload
        logger.info("\n📤 Passo 3: Fazendo upload...")
        upload_to_space(SPACE_ID, temp_dir, HF_TOKEN)

        # Sucesso!
        logger.success("\n✅ Deploy concluído com sucesso!")
        logger.info(f"\n🎉 Seu Space está disponível em:")
        logger.info(f"   {space_url}")
        logger.info(f"\n⏱️  O build pode levar alguns minutos...")
        logger.info(f"   Acompanhe em: https://huggingface.co/spaces/{SPACE_ID}")

    except Exception as e:
        logger.error(f"\n❌ Deploy falhou: {e}")
        raise

    finally:
        # Limpar diretório temporário
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info(f"🧹 Diretório temporário removido")

if __name__ == "__main__":
    main()
