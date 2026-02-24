"""Project registry domain model and in-memory repository.

This module provides a thin, deterministic backend core abstraction for
project management used by API adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format.

    Returns:
        str: Timestamp with timezone information.
    """
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class ProjectRecord:
    """Persistent view model for a registered project.

    Attributes:
        project_id: Stable project identifier.
        path: Absolute filesystem path to project root.
        display_name: Human-readable project name.
        created_at: UTC ISO timestamp when record was created.
        updated_at: UTC ISO timestamp when record was last changed.
    """

    project_id: str
    path: str
    display_name: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Convert record to plain dictionary.

        Returns:
            dict[str, Any]: Serialized record.
        """
        return asdict(self)


class RegistryError(Exception):
    """Domain error for project registry operations.

    Args:
        code: Stable machine-readable code.
        message: Human-readable error message.
        details: Additional structured context.
    """

    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_error_envelope(self) -> dict[str, Any]:
        """Map exception to standard error envelope.

        Returns:
            dict[str, Any]: Error envelope compatible with v1 schema.
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ProjectRegistry:
    """In-memory project registry with CRUD use-cases.

    This registry is intentionally simple and deterministic to keep API layers
    thin and focused on transport concerns.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._projects_by_id: dict[str, ProjectRecord] = {}

    def list_projects(self) -> list[dict[str, Any]]:
        """List registered projects.

        Returns:
            list[dict[str, Any]]: Projects sorted by display name.
        """
        projects = sorted(
            self._projects_by_id.values(),
            key=lambda item: item.display_name.casefold(),
        )
        return [project.to_dict() for project in projects]

    def create_project(self, *, path: str, display_name: str) -> dict[str, Any]:
        """Create and register a project.

        Args:
            path: Filesystem path to project root.
            display_name: Human-readable display name.

        Returns:
            dict[str, Any]: Created project record.

        Raises:
            RegistryError: If validation fails or project already exists.
        """
        normalized_path = self._validate_and_normalize_path(path)
        normalized_name = self._validate_display_name(display_name)

        project_id = self._build_project_id(normalized_path)
        if project_id in self._projects_by_id:
            raise RegistryError(
                code="PROJECT_ALREADY_EXISTS",
                message="Project is already registered for this path.",
                details={"path": normalized_path, "project_id": project_id},
            )

        self._ensure_display_name_is_unique(
            display_name=normalized_name,
            excluded_project_id=None,
        )

        now = _utc_now_iso()
        record = ProjectRecord(
            project_id=project_id,
            path=normalized_path,
            display_name=normalized_name,
            created_at=now,
            updated_at=now,
        )
        self._projects_by_id[project_id] = record
        return record.to_dict()

    def get_project(self, *, project_id: str) -> dict[str, Any]:
        """Get details for a single project.

        Args:
            project_id: Project identifier.

        Returns:
            dict[str, Any]: Project details.

        Raises:
            RegistryError: If project does not exist.
        """
        record = self._projects_by_id.get(project_id)
        if record is None:
            raise RegistryError(
                code="PROJECT_NOT_FOUND",
                message="Project was not found.",
                details={"project_id": project_id},
            )
        return record.to_dict()

    def update_project(self, *, project_id: str, display_name: str) -> dict[str, Any]:
        """Update project display name.

        Args:
            project_id: Project identifier.
            display_name: New display name.

        Returns:
            dict[str, Any]: Updated project details.

        Raises:
            RegistryError: If project is missing or validation fails.
        """
        record = self._projects_by_id.get(project_id)
        if record is None:
            raise RegistryError(
                code="PROJECT_NOT_FOUND",
                message="Project was not found.",
                details={"project_id": project_id},
            )

        normalized_name = self._validate_display_name(display_name)
        self._ensure_display_name_is_unique(
            display_name=normalized_name,
            excluded_project_id=project_id,
        )

        record.display_name = normalized_name
        record.updated_at = _utc_now_iso()
        return record.to_dict()

    def delete_project(self, *, project_id: str) -> dict[str, Any]:
        """Delete a project by identifier.

        Args:
            project_id: Project identifier.

        Returns:
            dict[str, Any]: Deleted project details.

        Raises:
            RegistryError: If project does not exist.
        """
        record = self._projects_by_id.pop(project_id, None)
        if record is None:
            raise RegistryError(
                code="PROJECT_NOT_FOUND",
                message="Project was not found.",
                details={"project_id": project_id},
            )
        return record.to_dict()

    @staticmethod
    def _build_project_id(path: str) -> str:
        """Build deterministic project identifier from normalized path.

        Args:
            path: Absolute normalized path.

        Returns:
            str: Deterministic short identifier.
        """
        digest = hashlib.sha1(path.encode("utf-8"), usedforsecurity=False).hexdigest()
        return digest[:12]

    @staticmethod
    def _validate_display_name(display_name: str) -> str:
        """Validate and normalize display name.

        Args:
            display_name: Display name candidate.

        Returns:
            str: Normalized display name.

        Raises:
            RegistryError: If display name is invalid.
        """
        normalized = display_name.strip()
        if not normalized:
            raise RegistryError(
                code="VALIDATION_ERROR",
                message="Display name must not be empty.",
                details={"field": "display_name"},
            )
        return normalized

    @staticmethod
    def _validate_and_normalize_path(path: str) -> str:
        """Validate and normalize project path.

        Args:
            path: Path candidate.

        Returns:
            str: Absolute normalized path string.

        Raises:
            RegistryError: If path is invalid.
        """
        normalized = str(Path(path).resolve())
        if not Path(normalized).exists() or not Path(normalized).is_dir():
            raise RegistryError(
                code="VALIDATION_ERROR",
                message="Project path must point to an existing directory.",
                details={"field": "path", "path": normalized},
            )
        return normalized

    def _ensure_display_name_is_unique(
        self,
        *,
        display_name: str,
        excluded_project_id: str | None,
    ) -> None:
        """Ensure display name uniqueness (case-insensitive).

        Args:
            display_name: Display name to check.
            excluded_project_id: Optional project excluded from check.

        Raises:
            RegistryError: If display name conflicts with another project.
        """
        wanted = display_name.casefold()
        for record in self._projects_by_id.values():
            if excluded_project_id is not None and record.project_id == excluded_project_id:
                continue
            if record.display_name.casefold() == wanted:
                raise RegistryError(
                    code="DISPLAY_NAME_CONFLICT",
                    message="Display name is already in use.",
                    details={"display_name": display_name},
                )

