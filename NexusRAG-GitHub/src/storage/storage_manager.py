"""Storage Manager module for NexusRAG.
Provides cloud-agnostic storage abstraction with Local and Google Cloud Storage (GCS) backends.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import shutil

from ..config import STORAGE_BACKEND, GCS_BUCKET_NAME, STORAGE_DIR
from ..utils.logger import get_logger

logger = get_logger("nexusrag.storage")

class StorageBackend(ABC):
    """Abstract interface for document file persistence."""

    @abstractmethod
    def save_file(self, file_name: str, data: bytes) -> str:
        """Saves file bytes and returns reference path/URI."""
        pass

    @abstractmethod
    def get_file(self, file_ref: str) -> bytes:
        """Retrieves raw bytes for a stored file."""
        pass

    @abstractmethod
    def delete_file(self, file_ref: str) -> bool:
        """Deletes a stored file."""
        pass

    @abstractmethod
    def list_files(self) -> List[Dict[str, Any]]:
        """Lists metadata of all stored files."""
        pass

class LocalStorageBackend(StorageBackend):
    """Local file system implementation for development and offline operation."""

    def __init__(self, base_dir: Path = STORAGE_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized LocalStorageBackend at '{self.base_dir}'")

    def save_file(self, file_name: str, data: bytes) -> str:
        safe_name = Path(file_name).name
        target_path = self.base_dir / safe_name
        with open(target_path, "wb") as f:
            f.write(data)
        logger.info(f"Saved local file: {target_path} ({len(data)} bytes)")
        return str(target_path)

    def get_file(self, file_ref: str) -> bytes:
        path = Path(file_ref)
        if not path.is_absolute():
            path = self.base_dir / path
        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {path}")
        with open(path, "rb") as f:
            return f.read()

    def delete_file(self, file_ref: str) -> bool:
        path = Path(file_ref)
        if not path.is_absolute():
            path = self.base_dir / path
        if path.exists():
            path.unlink()
            logger.info(f"Deleted local file: {path}")
            return True
        return False

    def list_files(self) -> List[Dict[str, Any]]:
        files = []
        for p in self.base_dir.glob("*.pdf"):
            files.append({
                "file_name": p.name,
                "file_ref": str(p),
                "size_bytes": p.stat().st_size,
                "backend": "local"
            })
        return files

class GCSStorageBackend(StorageBackend):
    """Google Cloud Storage (GCS) backend for scalable cloud object storage."""

    def __init__(self, bucket_name: str = GCS_BUCKET_NAME):
        self.bucket_name = bucket_name
        self.client = None
        self.bucket = None

        if not bucket_name:
            logger.warning("GCS_BUCKET_NAME not provided. GCS backend will fall back to local storage.")
            self._fallback = LocalStorageBackend()
            return

        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            self._fallback = None
            logger.info(f"Connected to Google Cloud Storage bucket: '{bucket_name}'")
        except Exception as e:
            logger.warning(f"Could not connect to GCS bucket '{bucket_name}': {e}. Falling back to LocalStorageBackend.")
            self._fallback = LocalStorageBackend()

    def save_file(self, file_name: str, data: bytes) -> str:
        if self._fallback:
            return self._fallback.save_file(file_name, data)
        try:
            blob = self.bucket.blob(file_name)
            blob.upload_from_string(data, content_type="application/pdf")
            gcs_uri = f"gs://{self.bucket_name}/{file_name}"
            logger.info(f"Uploaded file to GCS: {gcs_uri}")
            return gcs_uri
        except Exception as e:
            logger.error(f"GCS upload failed: {e}. Falling back to local storage.")
            fallback = LocalStorageBackend()
            return fallback.save_file(file_name, data)

    def get_file(self, file_ref: str) -> bytes:
        if self._fallback or file_ref.startswith("C:") or file_ref.startswith("/"):
            return (self._fallback or LocalStorageBackend()).get_file(file_ref)
        try:
            blob_name = file_ref.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Failed to read from GCS: {e}")
            raise

    def delete_file(self, file_ref: str) -> bool:
        if self._fallback or not file_ref.startswith("gs://"):
            return (self._fallback or LocalStorageBackend()).delete_file(file_ref)
        try:
            blob_name = file_ref.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"Deleted GCS blob: {file_ref}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete GCS blob: {e}")
            return False

    def list_files(self) -> List[Dict[str, Any]]:
        if self._fallback:
            return self._fallback.list_files()
        try:
            blobs = self.bucket.list_blobs()
            return [{
                "file_name": b.name,
                "file_ref": f"gs://{self.bucket_name}/{b.name}",
                "size_bytes": b.size,
                "backend": "gcs"
            } for b in blobs]
        except Exception as e:
            logger.error(f"Failed to list GCS files: {e}")
            return []

_storage_instance = None

def get_storage_manager() -> StorageBackend:
    """Returns the configured storage backend."""
    global _storage_instance
    if _storage_instance is None:
        if STORAGE_BACKEND == "gcs" and GCS_BUCKET_NAME:
            _storage_instance = GCSStorageBackend(GCS_BUCKET_NAME)
        else:
            _storage_instance = LocalStorageBackend()
    return _storage_instance
