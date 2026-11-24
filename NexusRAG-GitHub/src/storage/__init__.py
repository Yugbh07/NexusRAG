"""Storage package for document persistence with Local and Google Cloud Storage (GCS) support.
"""
from .storage_manager import StorageBackend, LocalStorageBackend, GCSStorageBackend, get_storage_manager

__all__ = ["StorageBackend", "LocalStorageBackend", "GCSStorageBackend", "get_storage_manager"]
