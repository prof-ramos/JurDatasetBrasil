"""
Geração de embeddings para chunks e exemplos.
Suporta modelos locais (sentence-transformers) e APIs externas (OpenAI).
"""

from typing import List, Union, Optional
import numpy as np
from loguru import logger
import time

# Imports condicionais
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers não instalado. Use: pip install sentence-transformers")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class EmbeddingGenerator:
    """Gerador de embeddings com suporte a múltiplos backends."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Inicializa o gerador de embeddings.

        Args:
            model_name: Nome do modelo (ex: "sentence-transformers/all-MiniLM-L6-v2" ou "openai/text-embedding-3-small")
            api_key: API key para modelos externos (OpenAI)
            batch_size: Tamanho do batch para processamento
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = None
        self.backend = None

        # Detectar backend
        if model_name.startswith("openai/"):
            self._init_openai(api_key)
        else:
            self._init_sentence_transformers(model_name)

    def _init_sentence_transformers(self, model_name: str):
        """Inicializa modelo local sentence-transformers."""
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError(
                "sentence-transformers não instalado. "
                "Instale com: pip install sentence-transformers"
            )

        # Remove prefixo se existir
        if model_name.startswith("sentence-transformers/"):
            model_name = model_name.replace("sentence-transformers/", "")

        logger.info(f"Carregando modelo local: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.backend = "sentence-transformers"
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"✓ Modelo carregado (dimensão: {self.dimension})")

    def _init_openai(self, api_key: Optional[str]):
        """Inicializa cliente OpenAI."""
        if not HAS_OPENAI:
            raise ImportError(
                "openai não instalado. "
                "Instale com: pip install openai"
            )

        if not api_key:
            raise ValueError("API key da OpenAI não fornecida")

        self.model = OpenAI(api_key=api_key)
        self.backend = "openai"

        # Determinar dimensão baseado no modelo
        if "text-embedding-3-small" in self.model_name:
            self.dimension = 1536
        elif "text-embedding-3-large" in self.model_name:
            self.dimension = 3072
        elif "text-embedding-ada-002" in self.model_name:
            self.dimension = 1536
        else:
            self.dimension = 1536  # default

        logger.info(f"✓ Cliente OpenAI inicializado (dimensão: {self.dimension})")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats representando o embedding
        """
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido para embedding")
            return [0.0] * self.dimension

        if self.backend == "sentence-transformers":
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        elif self.backend == "openai":
            try:
                model_id = self.model_name.replace("openai/", "")
                response = self.model.embeddings.create(
                    model=model_id,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Erro ao gerar embedding via OpenAI: {e}")
                return [0.0] * self.dimension

        else:
            raise ValueError(f"Backend desconhecido: {self.backend}")

    def generate_embeddings_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Gera embeddings para múltiplos textos.

        Args:
            texts: Lista de textos
            show_progress: Se True, mostra progresso

        Returns:
            Lista de embeddings
        """
        if not texts:
            return []

        # Filtrar textos vazios
        valid_texts = [t if t and t.strip() else " " for t in texts]

        if self.backend == "sentence-transformers":
            embeddings = self.model.encode(
                valid_texts,
                batch_size=self.batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings.tolist()

        elif self.backend == "openai":
            embeddings = []
            model_id = self.model_name.replace("openai/", "")

            # Processar em batches (OpenAI limita a 2048 textos por request)
            for i in range(0, len(valid_texts), min(self.batch_size, 100)):
                batch = valid_texts[i:i + min(self.batch_size, 100)]

                try:
                    response = self.model.embeddings.create(
                        model=model_id,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)

                    if show_progress:
                        logger.info(f"Processados {min(i + self.batch_size, len(valid_texts))}/{len(valid_texts)}")

                    # Rate limiting
                    time.sleep(0.2)

                except Exception as e:
                    logger.error(f"Erro no batch {i}: {e}")
                    # Adicionar embeddings vazios para manter sincronização
                    embeddings.extend([[0.0] * self.dimension] * len(batch))

            return embeddings

        else:
            raise ValueError(f"Backend desconhecido: {self.backend}")

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calcula similaridade de cosseno entre dois embeddings.

        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding

        Returns:
            Similaridade entre 0 e 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Normalizar
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)

        # Calcular similaridade
        similarity = np.dot(vec1_norm, vec2_norm)

        return float(similarity)

    def find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Encontra os k embeddings mais similares.

        Args:
            query_embedding: Embedding de consulta
            candidate_embeddings: Lista de embeddings candidatos
            top_k: Número de resultados

        Returns:
            Lista de tuplas (índice, similaridade)
        """
        similarities = [
            (idx, self.cosine_similarity(query_embedding, emb))
            for idx, emb in enumerate(candidate_embeddings)
        ]

        # Ordenar por similaridade decrescente
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def get_dimension(self) -> int:
        """Retorna a dimensão dos embeddings."""
        return self.dimension

    def get_backend(self) -> str:
        """Retorna o backend utilizado."""
        return self.backend


# Cache global de geradores para evitar recarregar modelos
_generator_cache = {}


def get_embedding_generator(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    api_key: Optional[str] = None
) -> EmbeddingGenerator:
    """
    Retorna um gerador de embeddings (cached).

    Args:
        model_name: Nome do modelo
        api_key: API key (se necessário)

    Returns:
        Instância de EmbeddingGenerator
    """
    cache_key = f"{model_name}_{api_key}"

    if cache_key not in _generator_cache:
        _generator_cache[cache_key] = EmbeddingGenerator(model_name, api_key)

    return _generator_cache[cache_key]


if __name__ == "__main__":
    # Teste
    logger.info("=== Teste de Geração de Embeddings ===")

    # Testar com modelo local
    try:
        generator = EmbeddingGenerator("all-MiniLM-L6-v2")

        texts = [
            "O processo administrativo rege-se pelos princípios da legalidade.",
            "A administração pública deve seguir o princípio da publicidade.",
            "O gato subiu no telhado."
        ]

        logger.info("Gerando embeddings...")
        embeddings = generator.generate_embeddings_batch(texts, show_progress=True)

        logger.info(f"✓ Gerados {len(embeddings)} embeddings")
        logger.info(f"Dimensão: {len(embeddings[0])}")

        # Testar similaridade
        sim_1_2 = generator.cosine_similarity(embeddings[0], embeddings[1])
        sim_1_3 = generator.cosine_similarity(embeddings[0], embeddings[2])

        logger.info(f"\nSimilaridade texto1 x texto2: {sim_1_2:.3f}")
        logger.info(f"Similaridade texto1 x texto3: {sim_1_3:.3f}")

    except Exception as e:
        logger.error(f"Erro no teste: {e}")
