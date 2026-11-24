"""Tests for storage abstraction and local backend file persistence.
"""
import pytest
from pathlib import Path
from src.storage.storage_manager import LocalStorageBackend, GCSStorageBackend

def test_local_storage_crud(tmp_path):
    backend = LocalStorageBackend(base_dir=tmp_path)
    content = b"PDF_HEADER_MOCK_DATA"
    
    # 1. Save
    file_ref = backend.save_file("report.pdf", content)
    assert Path(file_ref).exists()
    
    # 2. Read
    read_back = backend.get_file(file_ref)
    assert read_back == content
    
    # 3. List
    files = backend.list_files()
    assert len(files) == 1
    assert files[0]["file_name"] == "report.pdf"
    
    # 4. Delete
    deleted = backend.delete_file(file_ref)
    assert deleted is True
    assert not Path(file_ref).exists()

def test_gcs_fallback_when_unconfigured():
    # When no bucket is configured, GCS backend falls back to local storage cleanly
    gcs = GCSStorageBackend(bucket_name="")
    assert gcs._fallback is not None
