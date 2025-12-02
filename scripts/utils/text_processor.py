"""
Processamento e limpeza de textos jurídicos.
Inclui normalização, chunking e extração de estrutura.
"""

import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import tiktoken
from loguru import logger


class TextProcessor:
    """Processador de textos jurídicos."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Inicializa o processador de texto.

        Args:
            encoding_name: Nome do encoding do tiktoken (default: cl100k_base para GPT-4)
        """
        try:
            self.encoder = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Falha ao carregar tiktoken: {e}. Usando contagem aproximada.")
            self.encoder = None

    def count_tokens(self, text: str) -> int:
        """Conta tokens no texto."""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Aproximação: ~1.3 tokens por palavra em português
            return int(len(text.split()) * 1.3)

    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto.

        Args:
            text: Texto bruto

        Returns:
            Texto limpo
        """
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)

        # Remove espaços antes de pontuação
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)

        # Normaliza quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove espaços no início e fim
        text = text.strip()

        return text

    def extract_article_structure(self, text: str) -> Dict[str, any]:
        """
        Extrai estrutura de um artigo (incisos, parágrafos, alíneas).

        Args:
            text: Texto do artigo

        Returns:
            Dicionário com estrutura hierárquica
        """
        structure = {
            "article_ref": None,
            "caput": None,
            "paragraphs": [],
            "items": [],
            "subitems": []
        }

        # Extrair referência do artigo (Art. X)
        article_match = re.search(r'Art\.\s*(\d+[º°]?[.-]?[A-Z]?)', text)
        if article_match:
            structure["article_ref"] = article_match.group(0)

        # Extrair parágrafos
        paragraphs = re.findall(r'§\s*(\d+[º°]?)[.\s]+(.*?)(?=§|\n\n|$)', text, re.DOTALL)
        structure["paragraphs"] = [
            {"ref": f"§{ref}", "text": self.clean_text(content)}
            for ref, content in paragraphs
        ]

        # Extrair incisos (I, II, III, etc.)
        items = re.findall(r'\b([IVX]+)\s*[–-]\s*(.*?)(?=\b[IVX]+\s*[–-]|\n\n|$)', text, re.DOTALL)
        structure["items"] = [
            {"ref": ref, "text": self.clean_text(content)}
            for ref, content in items
        ]

        # Extrair alíneas (a), b), c), etc.)
        subitems = re.findall(r'\b([a-z])\)\s*(.*?)(?=\b[a-z]\)|\n\n|$)', text, re.DOTALL)
        structure["subitems"] = [
            {"ref": f"{ref})", "text": self.clean_text(content)}
            for ref, content in subitems
        ]

        # Extrair caput (tudo antes do primeiro parágrafo/inciso)
        caput_match = re.search(
            r'Art\.\s*\d+[º°]?[.-]?[A-Z]?\s*[.-]?\s*(.*?)(?=§|[IVX]+\s*[–-]|\n\n|$)',
            text,
            re.DOTALL
        )
        if caput_match:
            structure["caput"] = self.clean_text(caput_match.group(1))

        return structure

    def split_into_chunks(
        self,
        text: str,
        chunk_size: int = 1500,
        chunk_overlap: int = 200
    ) -> List[Dict[str, any]]:
        """
        Divide texto em chunks com overlap.

        Args:
            text: Texto para dividir
            chunk_size: Tamanho máximo do chunk em tokens
            chunk_overlap: Overlap entre chunks em tokens

        Returns:
            Lista de dicionários com chunks e metadados
        """
        # Limpar texto
        text = self.clean_text(text)

        # Dividir em sentenças (aproximação)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # Se adicionar a sentença ultrapassar o limite, salvar chunk atual
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "content": chunk_text,
                    "tokens": self.count_tokens(chunk_text),
                    "chunk_index": chunk_index,
                    "start_sentence": current_chunk[0][:50] + "...",
                    "end_sentence": "..." + current_chunk[-1][-50:]
                })

                # Manter overlap
                overlap_tokens = 0
                overlap_sentences = []

                for s in reversed(current_chunk):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
                chunk_index += 1

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Adicionar último chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "tokens": self.count_tokens(chunk_text),
                "chunk_index": chunk_index,
                "start_sentence": current_chunk[0][:50] + "...",
                "end_sentence": "..." + current_chunk[-1][-50:]
            })

        logger.debug(f"Texto dividido em {len(chunks)} chunks")
        return chunks

    def extract_law_metadata(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai metadados de uma lei do texto.

        Args:
            text: Texto da lei

        Returns:
            Dicionário com metadados extraídos
        """
        metadata = {
            "law_number": None,
            "law_type": None,
            "title": None,
            "year": None
        }

        # Extrair número da lei
        law_match = re.search(
            r'Lei\s*(?:nº|n°|n\.?)?\s*(\d+[\.,]?\d*)[/\s]*(\d{4})?',
            text,
            re.IGNORECASE
        )
        if law_match:
            number = law_match.group(1).replace(',', '.')
            year = law_match.group(2)
            metadata["law_number"] = f"{number}/{year}" if year else number
            metadata["law_type"] = "lei"
            if year:
                metadata["year"] = year

        # Extrair título (geralmente após "Dispõe sobre" ou na primeira linha)
        title_patterns = [
            r'Dispõe\s+sobre\s+(.*?)(?:\.|$)',
            r'Estabelece\s+(.*?)(?:\.|$)',
            r'Institui\s+(.*?)(?:\.|$)',
            r'Regulamenta\s+(.*?)(?:\.|$)'
        ]

        for pattern in title_patterns:
            title_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                # Limitar tamanho do título
                if len(title) > 200:
                    title = title[:197] + "..."
                metadata["title"] = title
                break

        return metadata

    def detect_legal_area(self, text: str) -> Optional[str]:
        """
        Detecta área do direito baseado em palavras-chave.

        Args:
            text: Texto para análise

        Returns:
            Área detectada ou None
        """
        areas = {
            "Direito Administrativo": [
                "administrativo", "servidor público", "licitação", "contrato administrativo",
                "ato administrativo", "processo administrativo", "poder público"
            ],
            "Direito Constitucional": [
                "constitucional", "constituição", "direito fundamental", "estado democrático",
                "princípio constitucional", "controle de constitucionalidade"
            ],
            "Direito Penal": [
                "penal", "crime", "pena", "delito", "infração penal", "reclusão", "detenção"
            ],
            "Direito Civil": [
                "civil", "contrato", "obrigação", "propriedade", "sucessão", "família"
            ],
            "Direito Tributário": [
                "tributário", "tributo", "imposto", "taxa", "contribuição", "fiscal"
            ],
            "Direito do Trabalho": [
                "trabalho", "trabalhador", "empregado", "empregador", "CLT", "jornada"
            ]
        }

        text_lower = text.lower()
        scores = {}

        for area, keywords in areas.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[area] = score

        if scores:
            return max(scores, key=scores.get)

        return None


# Funções auxiliares para uso direto
def clean_text(text: str) -> str:
    """Atalho para limpar texto."""
    processor = TextProcessor()
    return processor.clean_text(text)


def split_into_chunks(
    text: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 200
) -> List[Dict[str, any]]:
    """Atalho para dividir em chunks."""
    processor = TextProcessor()
    return processor.split_into_chunks(text, chunk_size, chunk_overlap)


if __name__ == "__main__":
    # Teste
    sample_text = """
    Art. 1º Esta lei estabelece normas básicas sobre o processo administrativo.

    § 1º Os preceitos desta Lei também se aplicam aos órgãos dos Poderes Legislativo e Judiciário.

    § 2º Para os fins desta Lei, consideram-se:
    I - órgão - a unidade de atuação integrante da estrutura;
    II - entidade - a unidade de atuação dotada de personalidade jurídica;
    III - autoridade - o servidor ou agente público dotado de poder de decisão.
    """

    processor = TextProcessor()

    print("=== Teste de Processamento de Texto ===")
    print(f"Tokens: {processor.count_tokens(sample_text)}")

    structure = processor.extract_article_structure(sample_text)
    print(f"\nArtigo: {structure['article_ref']}")
    print(f"Parágrafos: {len(structure['paragraphs'])}")
    print(f"Incisos: {len(structure['items'])}")

    chunks = processor.split_into_chunks(sample_text, chunk_size=100)
    print(f"\nChunks: {len(chunks)}")
