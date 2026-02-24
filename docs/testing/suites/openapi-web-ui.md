# Suite: L2 Web UI OpenAPI Contract

## Назначение

Проверяет валидность и контрактную целостность Web UI OpenAPI спецификации [`docs/contracts/web-ui.openapi.yaml`](../../contracts/web-ui.openapi.yaml).

## Тестовый скрипт

- [`tests/contracts/test_openapi_contract.py`](../../../tests/contracts/test_openapi_contract.py)

## Что покрывается

- Структурная валидность OpenAPI документа.
- Наличие обязательных operations для Projects/Indexing/Catalogs.
- Стабильный контракт `IndexStatus`: `progress`, `details`, optional `error`.
- Согласованность shape `ErrorEnvelope` с [`error_envelope.schema.json`](../../contracts/v1/error_envelope.schema.json).
- Наличие model-specific embedder settings и capabilities.

## Ключевые тест-кейсы

- [`test_openapi_spec_is_valid()`](../../../tests/contracts/test_openapi_contract.py:26)
- [`test_projects_resource_operations_present()`](../../../tests/contracts/test_openapi_contract.py:31)
- [`test_indexing_status_schema_includes_progress_details_and_error()`](../../../tests/contracts/test_openapi_contract.py:52)
- [`test_error_envelope_shape_matches_v1_schema()`](../../../tests/contracts/test_openapi_contract.py:59)
- [`test_embedder_settings_support_model_specific_fields()`](../../../tests/contracts/test_openapi_contract.py:84)

## Команда запуска

- `uv run pytest tests/contracts/test_openapi_contract.py`

## Связанные требования

- [`tasks_descriptions/tasks/task-02-web-ui-api-contract-openapi.md`](../../../tasks_descriptions/tasks/task-02-web-ui-api-contract-openapi.md)
- [`docs/architecture/stage-2-specification.md`](../../architecture/stage-2-specification.md:334)
