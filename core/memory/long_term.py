"""
Aara Long-Term Memory
Semantic memory storage using ChromaDB for vector similarity search.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import hashlib

from config.settings import SETTINGS

logger = logging.getLogger(__name__)


class LongTermMemory:
    """Manages long-term semantic memory using ChromaDB."""

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize long-term memory.

        Args:
            persist_directory: Directory for ChromaDB storage
        """
        self.persist_dir = Path(persist_directory) if persist_directory else SETTINGS.data_dir / "chromadb"
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None
        self._available = False
        self._init_chromadb()

    def _init_chromadb(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False,
            ))

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name="aara_memories",
                metadata={"description": "Aara's long-term memory storage"},
            )

            self._available = True
            logger.info(f"Long-term memory initialized at {self.persist_dir}")

        except ImportError:
            logger.warning("ChromaDB not installed. Long-term memory unavailable. Run: pip install chromadb")
            self._available = False
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._available = False

    def is_available(self) -> bool:
        """Check if long-term memory is available."""
        return self._available

    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for a memory."""
        timestamp = datetime.now().isoformat()
        content = f"{text}{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()

    def store(self, text: str, metadata: Optional[dict] = None) -> Optional[str]:
        """
        Store a memory.

        Args:
            text: The text content to store
            metadata: Optional metadata dict

        Returns:
            Memory ID if successful, None otherwise
        """
        if not self._available:
            logger.warning("Long-term memory not available, cannot store")
            return None

        try:
            memory_id = self._generate_id(text)
            meta = metadata or {}
            meta["timestamp"] = datetime.now().isoformat()
            meta["text_length"] = len(text)

            self._collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[memory_id],
            )

            logger.debug(f"Stored memory: {text[:50]}... (id: {memory_id})")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None

    def query(self, text: str, n_results: int = 5) -> list[dict]:
        """
        Query for relevant memories.

        Args:
            text: Query text
            n_results: Number of results to return

        Returns:
            List of matching memories with metadata
        """
        if not self._available:
            logger.warning("Long-term memory not available, cannot query")
            return []

        try:
            results = self._collection.query(
                query_texts=[text],
                n_results=n_results,
            )

            memories = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                ids = results.get("ids", [[]])[0]

                for i, doc in enumerate(docs):
                    memories.append({
                        "id": ids[i] if ids else None,
                        "content": doc,
                        "metadata": metas[i] if metas else {},
                        "relevance": 1 - (distances[i] if distances else 0),  # Convert distance to relevance
                    })

            logger.debug(f"Found {len(memories)} relevant memories for query")
            return memories

        except Exception as e:
            logger.error(f"Failed to query memories: {e}")
            return []

    def forget(self, memory_id: str) -> bool:
        """
        Delete a specific memory.

        Args:
            memory_id: ID of memory to delete

        Returns:
            True if successful
        """
        if not self._available:
            return False

        try:
            self._collection.delete(ids=[memory_id])
            logger.debug(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all memories.

        Returns:
            True if successful
        """
        if not self._available:
            return False

        try:
            # Delete and recreate collection
            self._client.delete_collection("aara_memories")
            self._collection = self._client.create_collection(
                name="aara_memories",
                metadata={"description": "Aara's long-term memory storage"},
            )
            logger.info("All long-term memories cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False

    def get_stats(self) -> dict:
        """Get memory storage statistics."""
        if not self._available:
            return {"available": False}

        try:
            count = self._collection.count()
            return {
                "available": True,
                "total_memories": count,
                "persist_directory": str(self.persist_dir),
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"available": True, "error": str(e)}

    def store_conversation_summary(self, summary: str, topic: str = "conversation") -> Optional[str]:
        """
        Store a conversation summary for later retrieval.

        Args:
            summary: Summary text
            topic: Topic/category for the memory

        Returns:
            Memory ID if successful
        """
        return self.store(summary, metadata={
            "type": "conversation_summary",
            "topic": topic,
        })

    def store_user_preference(self, preference: str, category: str = "general") -> Optional[str]:
        """
        Store a user preference.

        Args:
            preference: The preference text
            category: Category (e.g., "apps", "habits", "interests")

        Returns:
            Memory ID if successful
        """
        return self.store(preference, metadata={
            "type": "user_preference",
            "category": category,
        })

    def get_relevant_context(self, current_message: str, max_items: int = 3) -> str:
        """
        Get relevant context from long-term memory for a conversation.

        Args:
            current_message: Current user message
            max_items: Maximum number of memories to include

        Returns:
            Formatted context string
        """
        memories = self.query(current_message, n_results=max_items)

        if not memories:
            return ""

        context_parts = ["Relevant memories:"]
        for mem in memories:
            if mem.get("relevance", 0) > 0.5:  # Only include if fairly relevant
                context_parts.append(f"- {mem['content']}")

        if len(context_parts) > 1:
            return "\n".join(context_parts)
        return ""
