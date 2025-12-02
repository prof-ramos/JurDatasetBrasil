"""
Módulo de conexão e operações com Supabase.
Implementa as operações CRUD para as tabelas do schema unificado.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from supabase import create_client, Client
from loguru import logger
import numpy as np

from config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_SERVICE_ROLE_KEY,
    EMBEDDING_DIMENSION
)


class SupabaseDB:
    """Gerenciador de conexão e operações com Supabase."""

    def __init__(self, use_service_role: bool = False):
        """
        Inicializa conexão com Supabase.

        Args:
            use_service_role: Se True, usa service role key (bypass RLS)
        """
        api_key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_KEY

        if not SUPABASE_URL or not api_key:
            raise ValueError("Credenciais do Supabase não configuradas")

        self.client: Client = create_client(SUPABASE_URL, api_key)
        logger.info(f"✓ Conectado ao Supabase ({('service role' if use_service_role else 'anon key')})")

    # =========================================================================
    # LAWS (Leis)
    # =========================================================================

    def insert_law(
        self,
        law_number: str,
        law_type: str,
        title: Optional[str] = None,
        year: Optional[int] = None,
        jurisdiction: str = "BR",
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Insere uma nova lei."""
        data = {
            "law_number": law_number,
            "law_type": law_type,
            "title": title,
            "year": year,
            "jurisdiction": jurisdiction,
            "source_url": source_url,
            "is_active": True
        }

        result = self.client.table("laws").insert(data).execute()
        logger.info(f"✓ Lei {law_number} inserida com sucesso")
        return result.data[0] if result.data else {}

    def get_law_by_number(self, law_number: str) -> Optional[Dict[str, Any]]:
        """Busca lei pelo número."""
        result = self.client.table("laws")\
            .select("*")\
            .eq("law_number", law_number)\
            .execute()

        return result.data[0] if result.data else None

    def get_or_create_law(
        self,
        law_number: str,
        law_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Busca lei existente ou cria nova."""
        existing = self.get_law_by_number(law_number)
        if existing:
            logger.debug(f"Lei {law_number} já existe no banco")
            return existing

        return self.insert_law(law_number, law_type, **kwargs)

    # =========================================================================
    # ARTICLES (Artigos)
    # =========================================================================

    def insert_article(
        self,
        law_id: str,
        article_ref: str,
        full_text: str,
        structure_json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Insere um novo artigo."""
        data = {
            "law_id": law_id,
            "article_ref": article_ref,
            "full_text": full_text,
            "structure_json": structure_json
        }

        result = self.client.table("articles").insert(data).execute()
        logger.debug(f"✓ Artigo {article_ref} inserido")
        return result.data[0] if result.data else {}

    def get_articles_by_law(self, law_id: str) -> List[Dict[str, Any]]:
        """Busca todos os artigos de uma lei."""
        result = self.client.table("articles")\
            .select("*")\
            .eq("law_id", law_id)\
            .order("article_ref")\
            .execute()

        return result.data or []

    # =========================================================================
    # CHUNKS (Pedaços para RAG)
    # =========================================================================

    def insert_chunk(
        self,
        content: str,
        embedding: List[float],
        law_id: Optional[str] = None,
        article_id: Optional[str] = None,
        source_type: str = "lei",
        chunk_index: int = 0,
        tokens: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Insere um chunk com seu embedding."""
        # Converte embedding para formato pgvector
        embedding_str = f"[{','.join(map(str, embedding))}]"

        data = {
            "law_id": law_id,
            "article_id": article_id,
            "source_type": source_type,
            "chunk_index": chunk_index,
            "content": content,
            "tokens": tokens,
            "metadata": metadata or {},
            "embedding": embedding_str
        }

        result = self.client.table("chunks").insert(data).execute()
        logger.debug(f"✓ Chunk {chunk_index} inserido")
        return result.data[0] if result.data else {}

    def search_similar_chunks(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca chunks similares usando busca vetorial.

        Args:
            query_embedding: Vetor de consulta
            limit: Número máximo de resultados
            filters: Filtros adicionais (ex: {"source_type": "lei"})

        Returns:
            Lista de chunks ordenados por similaridade
        """
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        # Construir query com RPC para busca vetorial
        result = self.client.rpc(
            "match_chunks",
            {
                "query_embedding": embedding_str,
                "match_threshold": 0.5,
                "match_count": limit
            }
        ).execute()

        return result.data or []

    # =========================================================================
    # DATASETS (Versões e Splits)
    # =========================================================================

    def insert_dataset(
        self,
        name: str,
        version: str,
        split: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Insere ou atualiza um dataset."""
        data = {
            "name": name,
            "version": version,
            "split": split,
            "description": description
        }

        result = self.client.table("datasets")\
            .upsert(data, on_conflict="name,version,split")\
            .execute()

        logger.info(f"✓ Dataset {name} v{version} ({split}) registrado")
        return result.data[0] if result.data else {}

    def get_dataset(
        self,
        name: str,
        version: str,
        split: str
    ) -> Optional[Dict[str, Any]]:
        """Busca um dataset específico."""
        result = self.client.table("datasets")\
            .select("*")\
            .eq("name", name)\
            .eq("version", version)\
            .eq("split", split)\
            .execute()

        return result.data[0] if result.data else None

    # =========================================================================
    # EXAMPLES (Exemplos de Treino)
    # =========================================================================

    def insert_example(
        self,
        dataset_id: str,
        instruction: str,
        output: str,
        embedding: List[float],
        input_text: Optional[str] = None,
        task_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        exam_board: Optional[str] = None,
        exam_year: Optional[int] = None,
        tags: Optional[List[str]] = None,
        law_id: Optional[str] = None,
        article_id: Optional[str] = None,
        chunk_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Insere um exemplo de treino."""
        embedding_str = f"[{','.join(map(str, embedding))}]"

        data = {
            "dataset_id": dataset_id,
            "instruction": instruction,
            "input": input_text or "",
            "output": output,
            "task_type": task_type,
            "difficulty": difficulty,
            "exam_board": exam_board,
            "exam_year": exam_year,
            "tags": tags or [],
            "embedding": embedding_str,
            "law_id": law_id,
            "article_id": article_id,
            "chunk_ids": chunk_ids or []
        }

        result = self.client.table("examples").insert(data).execute()
        logger.debug(f"✓ Exemplo inserido: {instruction[:50]}...")
        return result.data[0] if result.data else {}

    def get_examples_by_dataset(
        self,
        dataset_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Busca exemplos de um dataset."""
        query = self.client.table("examples")\
            .select("*")\
            .eq("dataset_id", dataset_id)\
            .order("created_at", desc=True)

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data or []

    def search_similar_examples(
        self,
        query_embedding: List[float],
        limit: int = 3,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca exemplos similares (para few-shot learning).

        Args:
            query_embedding: Vetor de consulta
            limit: Número de exemplos similares
            filters: Filtros adicionais

        Returns:
            Lista de exemplos ordenados por similaridade
        """
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        result = self.client.rpc(
            "match_examples",
            {
                "query_embedding": embedding_str,
                "match_threshold": 0.5,
                "match_count": limit
            }
        ).execute()

        return result.data or []

    # =========================================================================
    # BATCH OPERATIONS (Operações em Lote)
    # =========================================================================

    def insert_chunks_batch(self, chunks: List[Dict[str, Any]]) -> int:
        """Insere múltiplos chunks de uma vez."""
        if not chunks:
            return 0

        # Converter embeddings para string
        for chunk in chunks:
            if isinstance(chunk.get("embedding"), list):
                chunk["embedding"] = f"[{','.join(map(str, chunk['embedding']))}]"

        result = self.client.table("chunks").insert(chunks).execute()
        count = len(result.data) if result.data else 0
        logger.info(f"✓ {count} chunks inseridos em batch")
        return count

    def insert_examples_batch(self, examples: List[Dict[str, Any]]) -> int:
        """Insere múltiplos exemplos de uma vez."""
        if not examples:
            return 0

        # Converter embeddings para string
        for example in examples:
            if isinstance(example.get("embedding"), list):
                example["embedding"] = f"[{','.join(map(str, example['embedding']))}]"

        result = self.client.table("examples").insert(examples).execute()
        count = len(result.data) if result.data else 0
        logger.info(f"✓ {count} exemplos inseridos em batch")
        return count

    # =========================================================================
    # STATISTICS (Estatísticas)
    # =========================================================================

    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do banco de dados."""
        stats = {}

        tables = ["laws", "articles", "chunks", "datasets", "examples"]
        for table in tables:
            result = self.client.table(table)\
                .select("id", count="exact")\
                .execute()
            stats[table] = result.count or 0

        return stats


if __name__ == "__main__":
    # Teste de conexão
    try:
        db = SupabaseDB()
        stats = db.get_stats()

        logger.info("=== Estatísticas do Banco de Dados ===")
        for table, count in stats.items():
            logger.info(f"{table}: {count} registros")

    except Exception as e:
        logger.error(f"Erro ao conectar: {e}")
