# Suite: L1 Unit Indexing Job Lifecycle

## Назначение

Проверяет доменную lifecycle-логику `IndexingJobService` (state transitions, progress payload, provider errors) без внешних IO-зависимостей.

## Тестовый скрипт

- [`tests/unit/test_indexing_job.py`](../../../tests/unit/test_indexing_job.py)

## Что покрывается

- Lifecycle переходы `queued -> running -> completed/failed/canceled`.
- Стабильный payload статуса: `job_id/status/progress/details`.
- Metadata embedder run settings (`model`, optional `dimensions`, optional `instruction`, `truncate`).
- Provider errors (`model_not_found`, `context_length_exceeded`, `timeout`, `connection_error`) и `provider_error` flag.
- Validation и invalid transitions.
- Mapping domain error в стандартный error envelope.

## Ключевые тест-кейсы

- [`test_start_job_and_get_status()`](../../../tests/unit/test_indexing_job.py:39)
- [`test_mark_running_update_progress_and_complete()`](../../../tests/unit/test_indexing_job.py:69)
- [`test_fail_job_marks_provider_error()`](../../../tests/unit/test_indexing_job.py:88)
- [`test_invalid_transition_is_rejected()`](../../../tests/unit/test_indexing_job.py:117)

## Команда запуска

- `uv run pytest tests/unit/test_indexing_job.py`

## Связанные требования

- [`tasks_descriptions/tasks/task-04-backend-indexing-job-progress.md`](../../../tasks_descriptions/tasks/task-04-backend-indexing-job-progress.md)
- [`docs/architecture/stage-2-specification.md`](../../architecture/stage-2-specification.md:263)
