# NexusRAG Automated Testing Report

**Date of Execution:** November 2026  
**Test Framework:** Pytest 9.2.0 (Python 3.13 / 3.11)  
**Total Tests Executed:** 22  
**Tests Passed:** 22  
**Tests Failed:** 0  
**Execution Duration:** 2.91 seconds  
**Pass Rate:** 100.0%  

---

## 1. Test Suite Execution Summary Table

| Test Identifier | Test Module | Objective | Test Input | Expected Output | Actual Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `test_extract_valid_pdf` | `test_pdf_extraction.py` | Verify multi-page text extraction and metadata tracking | `cloud_computing_sample.pdf` (3 pages) | Total pages = 3, chars > 1000, page text clean | 3 pages extracted, 5863 chars, valid text | **PASSED** |
| `test_extract_empty_bytes` | `test_pdf_extraction.py` | Verify error handling for 0-byte uploaded files | `b""` | `ValueError` raised with "empty" message | `ValueError` raised as expected | **PASSED** |
| `test_extract_corrupted_pdf_bytes` | `test_pdf_extraction.py` | Verify graceful recovery from corrupt PDF streams | Corrupt byte sequence | `ValueError` raised with "Invalid or corrupted" | `ValueError` raised as expected | **PASSED** |
| `test_unsupported_file_extension` | `test_pdf_extraction.py` | Prevent non-PDF file processing | `notes.txt` file | `ValueError` raised indicating unsupported type | `ValueError` raised as expected | **PASSED** |
| `test_clean_text_whitespace` | `test_pdf_extraction.py` | Verify whitespace & newline normalization | Irregular spaces & `\r\n\n\n\n` | Normalized spaces & max `\n\n` | Whitespace sanitized cleanly | **PASSED** |
| `test_chunking_metadata_and_count` | `test_chunking.py` | Validate sliding window chunking & metadata integrity | Mock ExtractedDocument (3 pages) | Chunks $\ge 3$, each has `doc_id`, `page_number`, `chunk_id` | Metadata preserved across all chunks | **PASSED** |
| `test_chunking_overlap_validation` | `test_chunking.py` | Ensure overlap < chunk size constraint | `chunk_overlap=200`, `chunk_size=200` | `ValueError` raised | `ValueError` raised as expected | **PASSED** |
| `test_chunk_serialization_roundtrip` | `test_chunking.py` | Verify dictionary serialization & deserialization | `TextChunk` instance | `to_dict()` and `from_dict()` match exactly | Exact roundtrip match | **PASSED** |
| `test_embedder_dimension_and_shape` | `test_embeddings.py` | Validate embedding vector shape and dimension | 2 text strings | `np.ndarray` shape `(2, 384)`, dtype `float32` | Shape `(2, 384)` verified | **PASSED** |
| `test_embedder_normalization` | `test_embeddings.py` | Validate $L_2$ unit normalization for cosine similarity | Natural language query | Vector $L_2$ norm $\approx 1.0 \pm 1e-4$ | Norm = $1.0000$ verified | **PASSED** |
| `test_embedder_empty_input` | `test_embeddings.py` | Handle empty text input list | `[]` | Empty array of shape `(0, 384)` | Returned shape `(0, 384)` | **PASSED** |
| `test_embedder_empty_query_raises` | `test_embeddings.py` | Reject empty or whitespace query | `"   "` | `ValueError` raised | `ValueError` raised as expected | **PASSED** |
| `test_add_and_search_vector_store` | `test_vector_store.py` | Test FAISS `IndexFlatIP` cosine similarity search | 2 synthetic chunks + unit vectors | Top result has similarity $\approx 1.0$ | Top chunk retrieved with score $1.0000$ | **PASSED** |
| `test_search_empty_store` | `test_vector_store.py` | Search against empty vector index | Query vector on empty store | Return empty list `[]` without crashing | Returned `[]` with log warning | **PASSED** |
| `test_persistence_roundtrip` | `test_vector_store.py` | Verify saving and reloading index from disk | Indexed chunk saved to tmp file | Loaded index matches original chunk count | Loaded successfully, count = 1 | **PASSED** |
| `test_adaptive_retrieval_empty_index` | `test_adaptive_retrieval.py` | Handle empty index in adaptive retriever | Query on empty store | Status = `EMPTY_INDEX`, escalated = `False` | Status `EMPTY_INDEX` returned | **PASSED** |
| `test_adaptive_retrieval_confident` | `test_adaptive_retrieval.py` | Verify direct confident match without escalation | Highly relevant query | Status = `CONFIDENT`, escalated = `False`, $K=3$ | Confident status, score > 0.50 | **PASSED** |
| `test_adaptive_retrieval_escalation` | `test_adaptive_retrieval.py` | Verify escalation triggered on ambiguous score | Ambiguous query with high threshold | Status = `ESCALATED_RECOVERED`, escalated = `True` | Escalated to $K=6$, recovered | **PASSED** |
| `test_rag_query_with_sources` | `test_rag_pipeline.py` | End-to-end RAG query and source attribution | "What is Google Cloud Run?" | Answer returned with citations and timing | Complete answer with source citations | **PASSED** |
| `test_rag_empty_query_raises` | `test_rag_pipeline.py` | Reject empty question in RAG engine | `"   "` | `ValueError` raised | `ValueError` raised as expected | **PASSED** |
| `test_local_storage_crud` | `test_storage.py` | Verify local storage save, read, list, and delete | Binary PDF content | File written, read back, listed, and deleted | All CRUD operations verified | **PASSED** |
| `test_gcs_fallback_when_unconfigured` | `test_storage.py` | Verify graceful fallback when GCS is unconfigured | `GCSStorageBackend("")` | Fallback to `LocalStorageBackend` active | Fallback established cleanly | **PASSED** |

---

## 2. Conclusion
All 22 unit, integration, and guardrail tests passed with zero errors. The system exhibits high stability across edge cases including empty inputs, corrupt PDF binaries, empty vector stores, ambiguous queries, and missing cloud credentials.
