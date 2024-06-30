""".. include:: README.md

This service is used to generate RAG answers.
"""

import numpy as np

from core.llmbackend.embedder_backend import AdaBackend
from core.llmbackend.llm_backend import GptBackend
from core.llmbackend.prompts.rag_prompt import RAG_PRIMER, RAG_QUERY, SUMMARY_PRIMER, SUMMARY_QUERY
from core.readers.pdf_readers import load_df
from core.readers.rag_schema import RagSchema
from core.settings.settings import Settings

VECTOR_STORE_PATH = Settings().VECTOR_STORE_PATH


class RagService:
    """RAG Service

    Use the rag_tunnel method to start the retrieval augmented generation.
    Best chunks are fetched from the vector store and summarized by a summary agent.
    A second agent uses the summary to generate a RAG answer.

    Args:
        embedder (AdaBackend): embedder backend
        llm (GptBackend): llm backend
        vector_store_path (str): path to the vector store
    """

    def __init__(self, embedder: AdaBackend, llm: GptBackend, vector_store_path: str) -> None:
        self.embedder = embedder
        self.llm = llm
        self.vector_store = load_df(file_path=vector_store_path)

    def rag_tunnel(self, query: str) -> str:
        """Start the RAG tunnel"""
        # Fetch top k chunks
        chunks, chunk_sources, page_numbers = self._fetch_top_k_chunks(query)
        # Summarize the chunks
        summary_query, summary_prompt = self._build_prompt(
            query, chunks, SUMMARY_QUERY, SUMMARY_PRIMER
        )
        chunks_summary = self.llm.get_completion(query=summary_query, primer_prompt=summary_prompt)
        # Generate RAG answer
        query, primer = self._build_prompt(query, chunks_summary, RAG_QUERY, RAG_PRIMER)
        rag_answer = self.llm.get_completion(query=query, primer_prompt=primer)
        # Add metadata to the llm answer
        rag_answer += "\n\n" + "#" * 55
        rag_answer += "\nfrom sources: " + str(chunk_sources)
        rag_answer += "\npage numbers: " + str(page_numbers)
        return rag_answer

    @staticmethod
    def _build_prompt(
        query: str, chunks: list[str] | str, query_prompt: str, primer_prompt: str
    ) -> tuple[str, str]:
        """Build the RAG prompts: fills the chunks and query system and query prompts.

        Args:
            query_prompt (str): query prompt
            primer_prompt (str): primer prompt
            query (str): query
            chunks (list[str] | str): list of top chunks or cleaned chunks

        Returns:
            str: RAG prompt
            str: RAG primer prompt
        """
        if isinstance(chunks, str):
            chunks = [chunks]

        chunks = "\n\n- " + "\n extract - '".join(chunks) + "'"

        # build the prompts
        query_prompt = query_prompt.replace("{query}", query)
        primer_prompt = primer_prompt.replace("{query}", query)
        query_prompt = query_prompt.replace("{chunks}", chunks)
        primer_prompt = primer_prompt.replace("{chunks}", chunks)
        return query_prompt, primer_prompt

    def _fetch_top_k_chunks(
        self, query: str, k: int = 20
    ) -> tuple[list[str], list[str], list[str]]:
        """Fetch top k chunks based on the query vector.

        Args:
            query (str): userquery
            k (int, optional): number of chunks to return. Defaults to 10.

        Returns:
            list[str]: list of top k chunks
        """
        # vectorize the query and compute similarities with the chunks
        query_vector = self.embedder.encode(query)
        similarities = self._compute_similiarities(query_vector)

        # select the top k chunks and their metadata from the vector store
        top_k_idx = sorted(similarities, key=similarities.get, reverse=True)[:k]
        top_chunks = [
            self.vector_store.iloc[idx][[RagSchema.CHUNK]].to_list()[0] for idx in top_k_idx
        ]

        metadata = [
            self.vector_store.iloc[idx][[RagSchema.PAGE_METADATA]].to_list()[0] for idx in top_k_idx
        ]

        page_numbers = [
            self.vector_store.iloc[idx][[RagSchema.PAGE_NUMBER]].to_list()[0] for idx in top_k_idx
        ]

        return top_chunks, list(set(metadata)), list(set(page_numbers))

    def _compute_similiarities(self, query_vector: list[float]) -> dict:
        """Compute similarities between the query vector and the chunks in the vector store.

        Args:
            query_vector (list[float]): embedded query

        Returns:
            dict: chunk_id -> similarity hashmap
        """
        similiarities = {}
        for row in self.vector_store.iterrows():
            v1 = row[1][RagSchema.CHUNK_W_METADATA_EMBEDDING]
            v2 = query_vector
            chunk_id = row[1][RagSchema.CHUNK_ID]
            similiarities[chunk_id] = self._cosine_similarity(embedding1=v1, embedding2=v2)
        return similiarities

    @staticmethod
    def _cosine_similarity(
        embedding1: list[float] | np.ndarray, embedding2: list[float] | np.ndarray
    ) -> float:
        """Compute cosine similarity between two vectors of identical length.

        Args:
            embedding1 (list[float] | np.ndarray): embedding vector 1
            embedding2 (list[float] | np.ndarray): embedding vector 2

        Returns:
            float: cosine similarity
        """
        # check input
        if len(embedding1) == 0 or len(embedding2) == 0:
            msg = "Embeddings cannot be empty"
            raise ValueError(msg)
        if len(embedding1) != len(embedding2):
            msg = "Embeddings must have the same dimension"
            raise ValueError(msg)
        if isinstance(embedding1, list):
            embedding1 = np.array(embedding1)
        if isinstance(embedding2, list):
            embedding2 = np.array(embedding2)
        if embedding1.ndim != 1 or embedding2.ndim != 1:
            msg = "Embeddings must be a 1 dimensional array"
            raise ValueError(msg)

        norm_a = np.linalg.norm(embedding1)
        norm_b = np.linalg.norm(embedding2)
        dot_product = np.dot(embedding1, embedding2)
        cosine = dot_product / (norm_a * norm_b)
        return cosine


if __name__ == "__main__":
    _embedder = AdaBackend(settings=Settings())
    _llm = GptBackend(settings=Settings())
    rag_service = RagService(embedder=_embedder, llm=_llm, vector_store_path=VECTOR_STORE_PATH)
    _query = "How do I compute the PNL of my company? And what does the PNL mean?"
    resp = rag_service.rag_tunnel(query=_query)
    print(resp)  # noqa: T201
