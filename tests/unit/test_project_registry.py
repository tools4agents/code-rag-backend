"""Unit tests for project registry CRUD logic."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_rag_backend.core.project_registry import ProjectRegistry, RegistryError


@pytest.fixture
def registry() -> ProjectRegistry:
    """Create fresh in-memory registry for each test.

    Returns:
        ProjectRegistry: Empty registry instance.
    """
    return ProjectRegistry()


def test_create_and_get_project(registry: ProjectRegistry) -> None:
    """Create project and fetch it back by identifier."""
    created = registry.create_project(path=".", display_name="Core Service")

    project_id = created["project_id"]
    fetched = registry.get_project(project_id=project_id)

    assert fetched["project_id"] == project_id
    assert fetched["display_name"] == "Core Service"
    assert Path(fetched["path"]).is_absolute()


def test_list_projects_sorted_by_display_name(registry: ProjectRegistry) -> None:
    """List projects sorted by display name case-insensitively."""
    registry.create_project(path=".", display_name="zeta")
    registry.create_project(path="docs", display_name="Alpha")

    listed = registry.list_projects()

    assert [item["display_name"] for item in listed] == ["Alpha", "zeta"]


def test_create_project_rejects_duplicate_path(registry: ProjectRegistry) -> None:
    """Reject creating a second project for the same path."""
    registry.create_project(path=".", display_name="Core Service")

    with pytest.raises(RegistryError) as error:
        registry.create_project(path=".", display_name="Another Name")

    assert error.value.code == "PROJECT_ALREADY_EXISTS"
    assert "project_id" in error.value.details


def test_create_project_rejects_duplicate_display_name(registry: ProjectRegistry) -> None:
    """Reject duplicate display name even with different case."""
    registry.create_project(path=".", display_name="Core Service")

    with pytest.raises(RegistryError) as error:
        registry.create_project(path="docs", display_name="core service")

    assert error.value.code == "DISPLAY_NAME_CONFLICT"


def test_create_project_rejects_invalid_path(registry: ProjectRegistry) -> None:
    """Reject invalid project root path."""
    with pytest.raises(RegistryError) as error:
        registry.create_project(path="./definitely-missing-dir", display_name="Broken")

    assert error.value.code == "VALIDATION_ERROR"
    assert error.value.details["field"] == "path"


def test_update_project_success(registry: ProjectRegistry) -> None:
    """Update display name for existing project."""
    created = registry.create_project(path=".", display_name="Core Service")

    updated = registry.update_project(
        project_id=created["project_id"],
        display_name="Core Service Renamed",
    )

    assert updated["display_name"] == "Core Service Renamed"
    assert updated["updated_at"] >= updated["created_at"]


def test_update_project_rejects_missing_project(registry: ProjectRegistry) -> None:
    """Reject update for unknown project id."""
    with pytest.raises(RegistryError) as error:
        registry.update_project(project_id="missing", display_name="Name")

    assert error.value.code == "PROJECT_NOT_FOUND"


def test_get_project_rejects_missing_project(registry: ProjectRegistry) -> None:
    """Reject get operation for unknown project id."""
    with pytest.raises(RegistryError) as error:
        registry.get_project(project_id="missing")

    assert error.value.code == "PROJECT_NOT_FOUND"


def test_delete_project_success(registry: ProjectRegistry) -> None:
    """Delete existing project and ensure it is removed."""
    created = registry.create_project(path=".", display_name="Core Service")

    deleted = registry.delete_project(project_id=created["project_id"])
    assert deleted["project_id"] == created["project_id"]

    with pytest.raises(RegistryError) as error:
        registry.get_project(project_id=created["project_id"])
    assert error.value.code == "PROJECT_NOT_FOUND"


def test_delete_project_rejects_missing_project(registry: ProjectRegistry) -> None:
    """Reject delete operation for unknown project id."""
    with pytest.raises(RegistryError) as error:
        registry.delete_project(project_id="missing")

    assert error.value.code == "PROJECT_NOT_FOUND"


def test_error_envelope_mapping(registry: ProjectRegistry) -> None:
    """Map domain error to stable error envelope shape."""
    with pytest.raises(RegistryError) as error:
        registry.get_project(project_id="missing")

    envelope = error.value.to_error_envelope()

    assert set(envelope.keys()) == {"error"}
    assert envelope["error"]["code"] == "PROJECT_NOT_FOUND"
    assert "message" in envelope["error"]
    assert isinstance(envelope["error"]["details"], dict)
