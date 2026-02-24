"""Domain model and lifecycle service for indexing jobs.

This module defines an in-memory job lifecycle used by API adapters to expose
stable indexing status and progress payloads for Web UI polling/SSE flows.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4


JobStatus = Literal["queued", "running", "completed", "failed", "canceled"]

_ACTIVE_STATUSES = frozenset({"queued", "running"})
_PROVIDER_ERROR_CODES = frozenset(
    {"model_not_found", "context_length_exceeded", "timeout", "connection_error"}
)
_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"running", "completed", "failed", "canceled"},
    "running": {"completed", "failed", "canceled"},
    "completed": set(),
    "failed": set(),
    "canceled": set(),
}


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format.

    Returns:
        str: Timestamp with timezone information.
    """
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class IndexingJobFailure:
    """Failure payload attached to failed indexing jobs.

    Attributes:
        code: Stable error code.
        message: Human-readable failure message.
        details: Additional structured context.
        provider_error: Whether failure originated from embedding provider.
    """

    code: str
    message: str
    details: dict[str, Any]
    provider_error: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize failure payload to dictionary.

        Returns:
            dict[str, Any]: Serialized failure payload.
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "provider_error": self.provider_error,
        }


@dataclass(slots=True)
class IndexingJobRecord:
    """In-memory representation of indexing lifecycle state.

    Attributes:
        job_id: Unique indexing job identifier.
        project_id: Project identifier owning the job.
        status: Current lifecycle state.
        progress: Progress in range [0.0, 1.0].
        processed_items: Number of processed units.
        total_items: Total units expected for indexing.
        embedder: Snapshot of embedder settings used for this run.
        created_at: UTC ISO timestamp when job was created.
        updated_at: UTC ISO timestamp of latest state update.
        started_at: UTC ISO timestamp when job entered running state.
        completed_at: UTC ISO timestamp when job completed.
        failed_at: UTC ISO timestamp when job failed.
        canceled_at: UTC ISO timestamp when job was canceled.
        error: Optional failure payload for failed state.
    """

    job_id: str
    project_id: str
    status: JobStatus
    progress: float
    processed_items: int
    total_items: int
    embedder: dict[str, Any]
    created_at: str
    updated_at: str
    started_at: str | None = None
    completed_at: str | None = None
    failed_at: str | None = None
    canceled_at: str | None = None
    error: IndexingJobFailure | None = None

    def to_job_dict(self) -> dict[str, Any]:
        """Return short job payload for start/stop endpoints.

        Returns:
            dict[str, Any]: Short job payload.
        """
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
        }

    def to_status_dict(self) -> dict[str, Any]:
        """Return full stable status payload.

        Returns:
            dict[str, Any]: Status payload compatible with Web UI contract.
        """
        payload: dict[str, Any] = {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "details": {
                "processed_items": self.processed_items,
                "total_items": self.total_items,
                "embedder": self.embedder,
                "timestamps": {
                    "created_at": self.created_at,
                    "updated_at": self.updated_at,
                    "started_at": self.started_at,
                    "completed_at": self.completed_at,
                    "failed_at": self.failed_at,
                    "canceled_at": self.canceled_at,
                },
            },
        }
        if self.error is not None:
            payload["error"] = self.error.to_dict()
        return payload


class IndexingJobError(Exception):
    """Domain error for indexing job lifecycle operations.

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


class IndexingJobService:
    """In-memory lifecycle service for indexing jobs.

    Service keeps latest job per project and validates lifecycle transitions:
    queued -> running -> completed/failed/canceled.
    """

    def __init__(self) -> None:
        """Initialize empty in-memory lifecycle store."""
        self._jobs_by_project: dict[str, IndexingJobRecord] = {}

    def start_job(self, *, project_id: str, embedder_settings: dict[str, Any]) -> dict[str, Any]:
        """Create new job in queued state for a project.

        Args:
            project_id: Project identifier.
            embedder_settings: Embedder configuration snapshot for the job.

        Returns:
            dict[str, Any]: Created job summary.

        Raises:
            IndexingJobError: If project id/settings are invalid or active job exists.
        """
        normalized_project_id = self._validate_project_id(project_id)
        active = self._jobs_by_project.get(normalized_project_id)
        if active is not None and active.status in _ACTIVE_STATUSES:
            raise IndexingJobError(
                code="JOB_ALREADY_ACTIVE",
                message="Project already has active indexing job.",
                details={
                    "project_id": normalized_project_id,
                    "job_id": active.job_id,
                    "status": active.status,
                },
            )

        now = _utc_now_iso()
        job = IndexingJobRecord(
            job_id=uuid4().hex[:12],
            project_id=normalized_project_id,
            status="queued",
            progress=0.0,
            processed_items=0,
            total_items=0,
            embedder=self._build_embedder_snapshot(embedder_settings),
            created_at=now,
            updated_at=now,
        )
        self._jobs_by_project[normalized_project_id] = job
        return job.to_job_dict()

    def get_status(self, *, project_id: str) -> dict[str, Any]:
        """Get full indexing status payload for a project.

        Args:
            project_id: Project identifier.

        Returns:
            dict[str, Any]: Stable status payload.

        Raises:
            IndexingJobError: If project has no job.
        """
        job = self._get_job(project_id=project_id)
        return job.to_status_dict()

    def mark_running(self, *, project_id: str, total_items: int | None = None) -> dict[str, Any]:
        """Move queued job to running state.

        Args:
            project_id: Project identifier.
            total_items: Optional total item count estimate.

        Returns:
            dict[str, Any]: Updated status payload.

        Raises:
            IndexingJobError: If transition is invalid or payload is invalid.
        """
        job = self._get_job(project_id=project_id)
        self._transition(job=job, to_status="running")

        if total_items is not None:
            if total_items < 0:
                raise IndexingJobError(
                    code="VALIDATION_ERROR",
                    message="total_items must be >= 0.",
                    details={"field": "total_items", "value": total_items},
                )
            job.total_items = total_items

        return job.to_status_dict()

    def update_progress(
        self,
        *,
        project_id: str,
        processed_items: int,
        total_items: int,
    ) -> dict[str, Any]:
        """Update running job progress.

        Args:
            project_id: Project identifier.
            processed_items: Number of processed items.
            total_items: Total number of items to process.

        Returns:
            dict[str, Any]: Updated status payload.

        Raises:
            IndexingJobError: If validation fails or state is not running.
        """
        job = self._get_job(project_id=project_id)
        if job.status != "running":
            self._raise_invalid_transition(job=job, to_status="running")

        if processed_items < 0:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="processed_items must be >= 0.",
                details={"field": "processed_items", "value": processed_items},
            )
        if total_items <= 0:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="total_items must be > 0.",
                details={"field": "total_items", "value": total_items},
            )
        if processed_items > total_items:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="processed_items must be <= total_items.",
                details={
                    "processed_items": processed_items,
                    "total_items": total_items,
                },
            )

        job.processed_items = processed_items
        job.total_items = total_items
        job.progress = round(processed_items / total_items, 6)
        job.updated_at = _utc_now_iso()
        return job.to_status_dict()

    def complete_job(self, *, project_id: str) -> dict[str, Any]:
        """Mark project indexing job as completed.

        Args:
            project_id: Project identifier.

        Returns:
            dict[str, Any]: Updated status payload.

        Raises:
            IndexingJobError: If transition is invalid.
        """
        job = self._get_job(project_id=project_id)
        self._transition(job=job, to_status="completed")
        job.progress = 1.0

        if job.total_items > 0:
            job.processed_items = max(job.processed_items, job.total_items)

        return job.to_status_dict()

    def fail_job(
        self,
        *,
        project_id: str,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Move project indexing job to failed state with failure payload.

        Args:
            project_id: Project identifier.
            code: Failure code.
            message: Failure message.
            details: Optional structured details.

        Returns:
            dict[str, Any]: Updated status payload.

        Raises:
            IndexingJobError: If transition is invalid or payload is invalid.
        """
        normalized_code = code.strip()
        normalized_message = message.strip()

        if not normalized_code:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="Failure code must not be empty.",
                details={"field": "code"},
            )
        if not normalized_message:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="Failure message must not be empty.",
                details={"field": "message"},
            )

        job = self._get_job(project_id=project_id)
        self._transition(job=job, to_status="failed")
        job.error = IndexingJobFailure(
            code=normalized_code,
            message=normalized_message,
            details=details or {},
            provider_error=normalized_code in _PROVIDER_ERROR_CODES,
        )
        return job.to_status_dict()

    def stop_job(self, *, project_id: str) -> dict[str, Any]:
        """Cancel queued/running indexing job.

        Args:
            project_id: Project identifier.

        Returns:
            dict[str, Any]: Updated job summary.

        Raises:
            IndexingJobError: If transition is invalid.
        """
        job = self._get_job(project_id=project_id)
        self._transition(job=job, to_status="canceled")
        return job.to_job_dict()

    def _get_job(self, *, project_id: str) -> IndexingJobRecord:
        """Find job by project id.

        Args:
            project_id: Project identifier.

        Returns:
            IndexingJobRecord: Found job.

        Raises:
            IndexingJobError: If job does not exist.
        """
        normalized_project_id = self._validate_project_id(project_id)
        job = self._jobs_by_project.get(normalized_project_id)
        if job is None:
            raise IndexingJobError(
                code="JOB_NOT_FOUND",
                message="Indexing job was not found for project.",
                details={"project_id": normalized_project_id},
            )
        return job

    def _transition(self, *, job: IndexingJobRecord, to_status: str) -> None:
        """Apply lifecycle transition and timestamps.

        Args:
            job: Job being transitioned.
            to_status: Target status.

        Raises:
            IndexingJobError: If transition is not allowed.
        """
        if to_status not in _ALLOWED_TRANSITIONS[job.status]:
            self._raise_invalid_transition(job=job, to_status=to_status)

        job.status = to_status
        timestamp = _utc_now_iso()
        job.updated_at = timestamp

        if to_status == "running" and job.started_at is None:
            job.started_at = timestamp
        elif to_status == "completed":
            job.completed_at = timestamp
        elif to_status == "failed":
            job.failed_at = timestamp
        elif to_status == "canceled":
            job.canceled_at = timestamp

    @staticmethod
    def _raise_invalid_transition(*, job: IndexingJobRecord, to_status: str) -> None:
        """Raise domain error for invalid state transition.

        Args:
            job: Current job.
            to_status: Target status.

        Raises:
            IndexingJobError: Always.
        """
        raise IndexingJobError(
            code="INVALID_JOB_TRANSITION",
            message="Indexing job transition is not allowed.",
            details={
                "job_id": job.job_id,
                "from_status": job.status,
                "to_status": to_status,
            },
        )

    @staticmethod
    def _validate_project_id(project_id: str) -> str:
        """Normalize and validate project identifier.

        Args:
            project_id: Project identifier candidate.

        Returns:
            str: Normalized project id.

        Raises:
            IndexingJobError: If identifier is invalid.
        """
        normalized = project_id.strip()
        if not normalized:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="project_id must not be empty.",
                details={"field": "project_id"},
            )
        return normalized

    @staticmethod
    def _build_embedder_snapshot(embedder_settings: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize embedder settings for status payload.

        Args:
            embedder_settings: Raw embedder settings.

        Returns:
            dict[str, Any]: Normalized settings snapshot.

        Raises:
            IndexingJobError: If payload is invalid.
        """
        model_raw = str(embedder_settings.get("model", "")).strip()
        if not model_raw:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="Embedder model is required.",
                details={"field": "embedder.model"},
            )

        dimensions_raw = embedder_settings.get("dimensions")
        dimensions: int | None
        if dimensions_raw is None:
            dimensions = None
        elif isinstance(dimensions_raw, int) and dimensions_raw > 0:
            dimensions = dimensions_raw
        else:
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="Embedder dimensions must be a positive integer.",
                details={"field": "embedder.dimensions", "value": dimensions_raw},
            )

        instruction_raw = embedder_settings.get("instruction")
        instruction: str | None = None
        if instruction_raw is not None:
            normalized_instruction = str(instruction_raw).strip()
            if normalized_instruction:
                instruction = normalized_instruction

        truncate_raw = embedder_settings.get("truncate", True)
        if not isinstance(truncate_raw, bool):
            raise IndexingJobError(
                code="VALIDATION_ERROR",
                message="Embedder truncate must be boolean.",
                details={"field": "embedder.truncate", "value": truncate_raw},
            )

        return {
            "model": model_raw,
            "dimensions": dimensions,
            "instruction": instruction,
            "truncate": truncate_raw,
        }
