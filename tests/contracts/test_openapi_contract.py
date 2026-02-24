"""Level-2 contract tests for Web UI OpenAPI specification."""

from __future__ import annotations

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate


ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "contracts" / "web-ui.openapi.yaml"
ERROR_SCHEMA_PATH = ROOT / "docs" / "contracts" / "v1" / "error_envelope.schema.json"


def _load_openapi() -> dict:
    """Load OpenAPI document.

    Returns:
        dict: Parsed OpenAPI spec.
    """
    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


def test_openapi_spec_is_valid() -> None:
    """Validate OpenAPI document using standard validator."""
    validate(_load_openapi())


def test_projects_resource_operations_present() -> None:
    """Ensure Projects resource exposes required operations."""
    spec = _load_openapi()
    projects = spec["paths"]["/projects"]
    project_item = spec["paths"]["/projects/{project_id}"]

    assert "get" in projects
    assert "post" in projects
    assert "get" in project_item
    assert "patch" in project_item
    assert "delete" in project_item


def test_indexing_resource_operations_present() -> None:
    """Ensure Indexing resource exposes required operations."""
    spec = _load_openapi()
    assert "post" in spec["paths"]["/projects/{project_id}/index"]
    assert "get" in spec["paths"]["/projects/{project_id}/index/status"]
    assert "post" in spec["paths"]["/projects/{project_id}/index/stop"]


def test_indexing_status_schema_includes_progress_details_and_error() -> None:
    """Ensure indexing status contract is stable for progress/status UI rendering."""
    spec = _load_openapi()
    index_job = spec["components"]["schemas"]["IndexJob"]
    index_status = spec["components"]["schemas"]["IndexStatus"]
    status_details = spec["components"]["schemas"]["IndexStatusDetails"]
    embedder_run_settings = spec["components"]["schemas"]["EmbedderRunSettings"]
    timestamps = spec["components"]["schemas"]["IndexJobTimestamps"]
    indexing_error = spec["components"]["schemas"]["IndexingError"]

    assert index_job["required"] == ["job_id", "status", "progress"]
    assert index_status["required"] == ["job_id", "status", "progress", "details"]
    assert index_status["properties"]["details"]["$ref"] == "#/components/schemas/IndexStatusDetails"
    assert index_status["properties"]["error"]["$ref"] == "#/components/schemas/IndexingError"

    assert status_details["required"] == ["processed_items", "total_items", "embedder", "timestamps"]
    assert embedder_run_settings["required"] == ["model", "truncate"]
    assert timestamps["required"] == ["created_at", "updated_at"]
    assert indexing_error["required"] == ["code", "message", "details", "provider_error"]


def test_settings_catalog_operations_present() -> None:
    """Ensure settings catalogs are available for chunkers and embedders."""
    spec = _load_openapi()
    assert "get" in spec["paths"]["/catalogs/chunkers"]
    assert "get" in spec["paths"]["/catalogs/embedders"]


def test_error_envelope_shape_matches_v1_schema() -> None:
    """Validate OpenAPI ErrorEnvelope example against v1 JSON Schema."""
    spec = _load_openapi()
    schema = yaml.safe_load(ERROR_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema=schema)

    error_payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "invalid request",
            "details": {"field": "path"},
        }
    }

    validator.validate(error_payload)

    envelope_required = spec["components"]["schemas"]["ErrorEnvelope"]["required"]
    error_required = spec["components"]["schemas"]["ErrorEnvelope"]["properties"]["error"][
        "required"
    ]

    assert envelope_required == ["error"]
    assert error_required == ["code", "message", "details"]


def test_embedder_settings_support_model_specific_fields() -> None:
    """Ensure embedder settings include model-specific fields for Stage 3."""
    spec = _load_openapi()
    embedder_settings = spec["components"]["schemas"]["EmbedderSettings"]

    properties = embedder_settings["properties"]
    model_enum = properties["model"]["enum"]

    assert "qwen3-embedding" in model_enum
    assert "bge-m3" in model_enum
    assert "instruction" in properties
    assert "dimensions" in properties
    assert "truncate" in properties
    assert "provider_options" in properties


def test_embedder_catalog_includes_capabilities_shape() -> None:
    """Ensure embedder catalog items include capabilities contract."""
    spec = _load_openapi()
    item_schema = spec["components"]["schemas"]["EmbedderCatalogItem"]
    capabilities = spec["components"]["schemas"]["EmbedderCapabilities"]

    assert "capabilities" in item_schema["required"]
    assert capabilities["required"] == [
        "supports_dimensions",
        "supports_instruction",
        "max_context_tokens",
    ]
