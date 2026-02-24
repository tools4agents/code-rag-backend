"""Level-2 contract tests for JSON Schemas in `docs/contracts/v1/`.

These tests validate positive and negative payloads against the formal v1
contract package.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "docs" / "contracts" / "v1"


def _build_registry() -> Registry:
    """Build schema registry for local `$ref` resolution.

    Returns:
        Registry: Registry with all v1 schemas.
    """
    registry = Registry()
    for schema_path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        resource = Resource(contents=schema, specification=DRAFT202012)
        registry = registry.with_resource(uri=schema_path.name, resource=resource)
    return registry


REGISTRY = _build_registry()


def _validator(schema_name: str) -> Draft202012Validator:
    """Create schema validator by schema filename.

    Args:
        schema_name: Schema filename in `docs/contracts/v1/`.

    Returns:
        Draft202012Validator: Ready-to-use validator.
    """
    schema_path = SCHEMAS_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema=schema, registry=REGISTRY)


def _assert_valid(schema_name: str, payload: dict[str, Any]) -> None:
    """Assert that payload is valid for schema.

    Args:
        schema_name: Schema filename.
        payload: Payload to validate.
    """
    _validator(schema_name).validate(payload)


def _assert_invalid(schema_name: str, payload: dict[str, Any]) -> None:
    """Assert that payload is invalid for schema.

    Args:
        schema_name: Schema filename.
        payload: Payload to validate.
    """
    errors = list(_validator(schema_name).iter_errors(payload))
    assert errors, f"Payload unexpectedly valid for {schema_name}: {payload}"


def test_push_batch_valid_minimal() -> None:
    """Validate minimal valid push batch payload."""
    payload = {
        "contract_version": "1.0",
        "project": "root",
        "source": "code-atlas",
        "batch_id": "atlas-batch-1",
        "items": [],
    }
    _assert_valid("push_batch.schema.json", payload)


def test_push_batch_invalid_contract_version() -> None:
    """Reject unsupported contract version in push batch."""
    payload = {
        "contract_version": "2.0",
        "project": "root",
        "source": "code-atlas",
        "batch_id": "atlas-batch-1",
        "items": [],
    }
    _assert_invalid("push_batch.schema.json", payload)


def test_push_item_valid_minimal() -> None:
    """Validate minimal valid push item."""
    payload = {
        "node_id": "func:src/auth.py:AuthService.login",
        "node_type": "function",
        "path": "src/auth.py",
        "language": "python",
        "content": "def login(): ...",
        "range": {"start_line": 1, "end_line": 10},
        "source_audit": {
            "git_commit": "abc123",
            "git_branch": "main",
            "git_dirty": False,
            "captured_at": "2026-02-20T12:00:00Z",
        },
    }
    _assert_valid("push_item.schema.json", payload)


def test_push_item_invalid_empty_content() -> None:
    """Reject push item with empty content."""
    payload = {
        "node_id": "func:src/auth.py:AuthService.login",
        "node_type": "function",
        "path": "src/auth.py",
        "language": "python",
        "content": "",
        "range": {"start_line": 1, "end_line": 10},
        "source_audit": {
            "git_commit": "abc123",
            "git_branch": "main",
            "git_dirty": False,
            "captured_at": "2026-02-20T12:00:00Z",
        },
    }
    _assert_invalid("push_item.schema.json", payload)


def test_push_acceptance_valid() -> None:
    """Validate push acceptance response."""
    payload = {
        "batch_id": "atlas-batch-1",
        "accepted": 10,
        "rejected": 1,
        "errors": [
            {
                "node_id": "func:src/auth.py:broken",
                "code": "VALIDATION_ERROR",
                "message": "content is empty",
            }
        ],
    }
    _assert_valid("push_acceptance.schema.json", payload)


def test_push_acceptance_invalid_missing_message() -> None:
    """Reject push acceptance error item without message."""
    payload = {
        "batch_id": "atlas-batch-1",
        "accepted": 10,
        "rejected": 1,
        "errors": [{"node_id": "func:src/auth.py:broken", "code": "VALIDATION_ERROR"}],
    }
    _assert_invalid("push_acceptance.schema.json", payload)


def test_reconcile_request_valid() -> None:
    """Validate reconcile request in dry-run mode."""
    payload = {"project": "root", "mode": "dry_run"}
    _assert_valid("reconcile_request.schema.json", payload)


def test_reconcile_request_invalid_mode() -> None:
    """Reject reconcile request with unknown mode."""
    payload = {"project": "root", "mode": "diff"}
    _assert_invalid("reconcile_request.schema.json", payload)


def test_reconcile_response_valid() -> None:
    """Validate reconcile response shape."""
    payload = {
        "project": "root",
        "mode": "dry_run",
        "summary": {"missing": 2, "stale": 5, "orphan": 1},
        "actions": [],
    }
    _assert_valid("reconcile_response.schema.json", payload)


def test_reconcile_response_invalid_missing_summary() -> None:
    """Reject reconcile response without summary."""
    payload = {"project": "root", "mode": "dry_run", "actions": []}
    _assert_invalid("reconcile_response.schema.json", payload)


def test_query_request_valid() -> None:
    """Validate minimal query request."""
    payload = {"query": "Auth login", "project": "root"}
    _assert_valid("query_request.schema.json", payload)


def test_query_request_invalid_missing_query() -> None:
    """Reject query request without query text."""
    payload = {"project": "root"}
    _assert_invalid("query_request.schema.json", payload)


def test_query_response_valid() -> None:
    """Validate query response with audit metadata."""
    payload = {
        "matches": [
            {
                "score": 0.93,
                "node_id": "func:src/auth.py:AuthService.login",
                "path": "src/auth.py",
                "start_line": 1,
                "end_line": 10,
                "content": "def login(): ...",
                "metadata": {
                    "project": "root",
                    "namespace": "root/code_search/simple_file_chunks",
                    "chunk_id": "chunk-1",
                    "chunk_strategy": "simple_file_chunks",
                    "source_audit": {
                        "source_system": "code-atlas",
                        "source_batch_id": "atlas-batch-1",
                        "git_commit": "abc123",
                        "git_branch": "main",
                        "git_dirty": False,
                        "source_captured_at": "2026-02-20T12:00:00Z",
                    },
                    "index_audit": {
                        "indexed_at": "2026-02-20T12:05:00Z",
                        "indexer_version": "0.1.0",
                        "embedder_provider": "ollama",
                        "embedder_model": "qwen3-embedding",
                        "vector_backend": "qdrant",
                    },
                },
            }
        ]
    }
    _assert_valid("query_response.schema.json", payload)


def test_query_response_invalid_missing_matches() -> None:
    """Reject query response without matches list."""
    payload = {}
    _assert_invalid("query_response.schema.json", payload)


def test_error_envelope_valid() -> None:
    """Validate standard error envelope."""
    payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "invalid payload",
            "details": {"field": "query"},
        }
    }
    _assert_valid("error_envelope.schema.json", payload)


def test_error_envelope_invalid_missing_error() -> None:
    """Reject object without `error` root field."""
    payload = {"code": "VALIDATION_ERROR", "message": "invalid payload", "details": {}}
    _assert_invalid("error_envelope.schema.json", payload)


def test_provider_capabilities_valid_qwen() -> None:
    """Validate provider capabilities for qwen3-embedding."""
    payload = {
        "provider": "ollama",
        "model": "qwen3-embedding",
        "capabilities": {
            "supports_dimensions": True,
            "supports_instruction": True,
            "max_context_tokens": 32768,
            "recommended_query_instruction": (
                "Given a code search query, retrieve relevant code snippets"
            ),
            "supported_dimensions": {"min": 32, "max": 4096},
        },
    }
    _assert_valid("provider_capabilities.schema.json", payload)


def test_provider_capabilities_valid_bge_m3() -> None:
    """Validate provider capabilities for bge-m3."""
    payload = {
        "provider": "ollama",
        "model": "bge-m3",
        "capabilities": {
            "supports_dimensions": False,
            "supports_instruction": False,
            "max_context_tokens": 8192,
        },
    }
    _assert_valid("provider_capabilities.schema.json", payload)


def test_provider_capabilities_invalid_missing_model() -> None:
    """Reject provider capabilities without model field."""
    payload = {
        "provider": "ollama",
        "capabilities": {
            "supports_dimensions": True,
            "supports_instruction": True,
            "max_context_tokens": 32768,
        },
    }
    _assert_invalid("provider_capabilities.schema.json", payload)


def test_provider_capabilities_invalid_zero_context_window() -> None:
    """Reject provider capabilities with invalid context token limit."""
    payload = {
        "provider": "ollama",
        "model": "bge-m3",
        "capabilities": {
            "supports_dimensions": False,
            "supports_instruction": False,
            "max_context_tokens": 0,
        },
    }
    _assert_invalid("provider_capabilities.schema.json", payload)
