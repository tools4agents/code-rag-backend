# Suite: L2 Contracts v1 JSON Schemas

## Назначение

Проверяет формальные JSON Schema контракты пакета `v1` в [`docs/contracts/v1/`](../../contracts/v1/).

## Тестовый скрипт

- [`tests/contracts/test_v1_schemas.py`](../../../tests/contracts/test_v1_schemas.py)

## Что покрывается

- Push-first contract: batch/item/acceptance.
- Reconcile request/response.
- Query request/response.
- Error envelope.
- Provider capabilities, включая различия `qwen3-embedding` и `bge-m3`.

## Ключевые тест-кейсы

- [`test_push_batch_valid_minimal()`](../../../tests/contracts/test_v1_schemas.py:75)
- [`test_push_item_invalid_empty_content()`](../../../tests/contracts/test_v1_schemas.py:118)
- [`test_error_envelope_valid()`](../../../tests/contracts/test_v1_schemas.py:250)
- [`test_provider_capabilities_valid_qwen()`](../../../tests/contracts/test_v1_schemas.py:268)
- [`test_provider_capabilities_valid_bge_m3()`](../../../tests/contracts/test_v1_schemas.py:286)

## Команда запуска

- `uv run pytest tests/contracts/test_v1_schemas.py`

## Связанные требования

- [`docs/contracts/contract-tests.md`](../../contracts/contract-tests.md)
- [`docs/architecture/stage-2-specification.md`](../../architecture/stage-2-specification.md:274)
