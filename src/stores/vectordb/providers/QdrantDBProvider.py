from numpy import rec
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from qdrant_client import QdrantClient, models


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_mthod: str):
        self.db_path = db_path
        self.distance_mthod = None
        self.client = None
        self.logger = logging.getLogger(__name__)
        if distance_mthod == DistanceMethodEnums.COSINE.value:
            self.distance_mthod = models.Distance.COSINE
        elif distance_mthod == DistanceMethodEnums.DOT.value:
            self.distance_mthod = models.Distance.DOT
        else:
            self.distance_mthod = models.Distance.EUCLID

    def connect(self):
        try:
            self.client = QdrantClient(path=self.db_path)
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to QdrantDB: {e}")
            return False

    def disconnect(self):
        self.client = None
        return True

    def is_collection_exists(self, collection_name: str) -> bool:
        try:
            return self.client.collection_exists(collection_name)
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False

    def list_all_collections(self) -> list:
        try:
            return self.client.get_collections()
        except Exception as e:
            self.logger.error(f"Error listing collections: {e}")
            return []

    def get_collection_info(self, collection_name: str) -> dict:
        try:
            return self.client.get_collection(collection_name).dict()
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            return {}

    def delete_collection(self, collection_name: str) -> bool:
        if self.is_collection_exists(collection_name):
            try:
                self.client.delete_collection(collection_name)
                return True
            except Exception as e:
                self.logger.error(f"Error deleting collection: {e}")
                return False

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        if self.is_collection_exists(collection_name):
            if do_reset:
                _ = self.delete_collection(collection_name)
            else:
                self.logger.error(
                    f"Collection {collection_name} already exists and do_reset is False."
                )
                return False
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_mthod
                ),
            )
            return True
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ) -> str:
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        _ = self.client.upload_records(
            collection_name=collection_name,
            records=[
                models.Record(
                    id=[record_id],
                    vector=vector,
                    payload={"text": text, "metadata": metadata},
                )
            ],
        )
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50,
    ) -> list:
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = list(range(0, len(texts)))
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        total_records = len(texts)
        for i in range(0, total_records, batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
            batch_records = [
                models.Record(
                    id=batch_record_ids[j],
                    vector=batch_vectors[j],
                    payload={"text": batch_texts[j], "metadata": batch_metadata[j]},
                )
                for j in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )

            except Exception as e:
                self.logger.error(f"Error inserting batch starting at index {i}: {e}")
                return False
        return True

    def search_by_vector(
        self,
        collection_name: str,
        vector: list,
        limit: int = 5,
    ) -> list:
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
            )
            formatted_results = [
                {
                    "id": res.id,
                    "score": res.score,
                    "text": res.payload.get("text", ""),
                    "metadata": res.payload.get("metadata", {}),
                }
                for res in results
            ]
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error searching by vector: {e}")
            return []
