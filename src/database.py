import chromadb
from chromadb.utils import embedding_functions
import os
from typing import Optional

# Setup local database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "db")

class MutualFundsDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Load local BGE-small-en embedding function
        self.bge_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en-v1.5"
        )

    def get_collection(self, name: str = "mutual_funds_collection"):
        """Get or create collection with local BGE-small-en-v1.5 embeddings."""
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.bge_ef
        )

    def delete_collection(self, name: str = "mutual_funds_collection"):
        """Deletes collection completely (useful for clean daily rebuilds)."""
        try:
            self.client.delete_collection(name=name)
        except Exception:
            pass
