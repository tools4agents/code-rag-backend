# Suite: L1 Unit Project Registry

## Назначение

Проверяет доменную логику `ProjectRegistry` без внешних IO-зависимостей.

## Тестовый скрипт

- [`tests/unit/test_project_registry.py`](../../../tests/unit/test_project_registry.py)

## Что покрывается

- CRUD операции registry (`create/list/get/update/delete`).
- Валидация пути и display name.
- Конфликты по path/display_name.
- Not found сценарии.
- Mapping domain error в стандартный error envelope.

## Ключевые тест-кейсы

- [`test_create_and_get_project()`](../../../tests/unit/test_project_registry.py:22)
- [`test_create_project_rejects_duplicate_path()`](../../../tests/unit/test_project_registry.py:44)
- [`test_delete_project_success()`](../../../tests/unit/test_project_registry.py:103)
- [`test_error_envelope_mapping()`](../../../tests/unit/test_project_registry.py:123)

## Команда запуска

- `uv run pytest tests/unit/test_project_registry.py`

## Связанные требования

- [`tasks_descriptions/tasks/task-03-backend-project-registry-crud.md`](../../../tasks_descriptions/tasks/task-03-backend-project-registry-crud.md)
- [`docs/architecture/stage-2-specification.md`](../../architecture/stage-2-specification.md:263)
