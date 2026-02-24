"""Unit tests for indexing job lifecycle service."""

from __future__ import annotations

import pytest

from code_rag_backend.core.indexing_job import IndexingJobError, IndexingJobService


@pytest.fixture
def service() -> IndexingJobService:
    """Create fresh in-memory lifecycle service.

    Returns:
        IndexingJobService: Empty indexing job service.
    """
    return IndexingJobService()


def _embedder_settings(**overrides: object) -> dict[str, object]:
    """Build valid embedder settings payload for tests.

    Args:
        **overrides: Optional field overrides.

    Returns:
        dict[str, object]: Embedder settings payload.
    """
    payload: dict[str, object] = {
        "model": "qwen3-embedding",
        "dimensions": 1024,
        "instruction": "Represent this code for retrieval",
        "truncate": True,
    }
    payload.update(overrides)
    return payload


def test_start_job_and_get_status(service: IndexingJobService) -> None:
    """Create queued job and return stable status payload."""
    created = service.start_job(
        project_id="project-1",
        embedder_settings=_embedder_settings(),
    )

    assert created["status"] == "queued"
    assert created["progress"] == 0.0

    status = service.get_status(project_id="project-1")
    assert status["job_id"] == created["job_id"]
    assert status["status"] == "queued"
    assert status["progress"] == 0.0
    assert status["details"]["embedder"]["model"] == "qwen3-embedding"
    assert status["details"]["embedder"]["dimensions"] == 1024
    assert status["details"]["embedder"]["instruction"] == "Represent this code for retrieval"
    assert status["details"]["embedder"]["truncate"] is True


def test_start_job_rejects_active_job(service: IndexingJobService) -> None:
    """Reject creating second active job for the same project."""
    service.start_job(project_id="project-1", embedder_settings=_embedder_settings())

    with pytest.raises(IndexingJobError) as error:
        service.start_job(project_id="project-1", embedder_settings=_embedder_settings())

    assert error.value.code == "JOB_ALREADY_ACTIVE"


def test_mark_running_update_progress_and_complete(service: IndexingJobService) -> None:
    """Run happy path lifecycle from queued to completed."""
    service.start_job(project_id="project-1", embedder_settings=_embedder_settings())
    running = service.mark_running(project_id="project-1", total_items=10)
    assert running["status"] == "running"
    assert running["details"]["timestamps"]["started_at"] is not None

    progress = service.update_progress(project_id="project-1", processed_items=3, total_items=10)
    assert progress["status"] == "running"
    assert progress["progress"] == 0.3
    assert progress["details"]["processed_items"] == 3
    assert progress["details"]["total_items"] == 10

    completed = service.complete_job(project_id="project-1")
    assert completed["status"] == "completed"
    assert completed["progress"] == 1.0
    assert completed["details"]["timestamps"]["completed_at"] is not None


def test_fail_job_marks_provider_error(service: IndexingJobService) -> None:
    """Set failure payload including provider_error flag for provider failures."""
    service.start_job(project_id="project-1", embedder_settings=_embedder_settings())
    service.mark_running(project_id="project-1")

    failed = service.fail_job(
        project_id="project-1",
        code="model_not_found",
        message="Requested embedding model is missing",
        details={"model": "qwen3-embedding"},
    )

    assert failed["status"] == "failed"
    assert failed["error"]["code"] == "model_not_found"
    assert failed["error"]["provider_error"] is True
    assert failed["details"]["timestamps"]["failed_at"] is not None


def test_stop_job_transitions_to_canceled(service: IndexingJobService) -> None:
    """Cancel queued job and return short payload."""
    started = service.start_job(project_id="project-1", embedder_settings=_embedder_settings())

    canceled = service.stop_job(project_id="project-1")

    assert canceled["job_id"] == started["job_id"]
    assert canceled["status"] == "canceled"
    assert canceled["progress"] == 0.0


def test_invalid_transition_is_rejected(service: IndexingJobService) -> None:
    """Reject state transition after terminal state."""
    service.start_job(project_id="project-1", embedder_settings=_embedder_settings())
    service.complete_job(project_id="project-1")

    with pytest.raises(IndexingJobError) as error:
        service.stop_job(project_id="project-1")

    assert error.value.code == "INVALID_JOB_TRANSITION"


def test_update_progress_requires_running_state(service: IndexingJobService) -> None:
    """Reject progress updates while job is not running."""
    service.start_job(project_id="project-1", embedder_settings=_embedder_settings())

    with pytest.raises(IndexingJobError) as error:
        service.update_progress(project_id="project-1", processed_items=1, total_items=10)

    assert error.value.code == "INVALID_JOB_TRANSITION"


def test_start_job_validates_embedder_fields(service: IndexingJobService) -> None:
    """Reject invalid embedder settings for stable metadata contract."""
    with pytest.raises(IndexingJobError) as missing_model:
        service.start_job(project_id="project-1", embedder_settings={"truncate": True})
    assert missing_model.value.code == "VALIDATION_ERROR"

    with pytest.raises(IndexingJobError) as bad_dimensions:
        service.start_job(
            project_id="project-1",
            embedder_settings=_embedder_settings(dimensions=0),
        )
    assert bad_dimensions.value.code == "VALIDATION_ERROR"

    with pytest.raises(IndexingJobError) as bad_truncate:
        service.start_job(
            project_id="project-1",
            embedder_settings=_embedder_settings(truncate="yes"),
        )
    assert bad_truncate.value.code == "VALIDATION_ERROR"


def test_get_status_rejects_missing_job(service: IndexingJobService) -> None:
    """Return stable error code for unknown project job status request."""
    with pytest.raises(IndexingJobError) as error:
        service.get_status(project_id="missing")

    assert error.value.code == "JOB_NOT_FOUND"


def test_error_envelope_mapping(service: IndexingJobService) -> None:
    """Map lifecycle domain error to standard error envelope."""
    with pytest.raises(IndexingJobError) as error:
        service.get_status(project_id="missing")

    envelope = error.value.to_error_envelope()

    assert set(envelope.keys()) == {"error"}
    assert envelope["error"]["code"] == "JOB_NOT_FOUND"
    assert "message" in envelope["error"]
    assert isinstance(envelope["error"]["details"], dict)
