import logging
from typing import List, Optional
from .factory import vector_db_factory, embedder_factory

logger = logging.getLogger(__name__)

class RagEngine:
    """
    The central orchestrator for RAG operations.
    """

    def __init__(self, vector_db_name: str, embedder_name: str, **kwargs):
        """
        Initialize the engine with specific implementations.

        Args:
            vector_db_name: Name of the vector DB plugin.
            embedder_name: Name of the embedder plugin.
            **kwargs: Additional configuration for plugins.
        """
        logger.info(f"Initializing RagEngine with {vector_db_name} and {embedder_name}")
        self.vector_db = vector_db_factory.create_instance(vector_db_name, **kwargs)
        self.embedder = embedder_factory.create_instance(embedder_name, **kwargs)

    def index_text(self, text: str, metadata: Optional[dict] = None):
        """
        Index a piece of text.
        """
        embedding = self.embedder.embed_text(text)
        self.vector_db.upsert(embedding, text, metadata)

    def search(self, query: str, limit: int = 5) -> List[dict]:
        """
        Search for relevant context.
        """
        query_embedding = self.embedder.embed_text(query)
        return self.vector_db.search(query_embedding, limit=limit)