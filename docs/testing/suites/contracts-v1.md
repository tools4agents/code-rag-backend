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
- Негативные сценарии required/type/enum по каждой схеме и nested `$ref` валидация для `push_batch -> push_item`.

## Ключевые тест-кейсы

- [`test_push_batch_invalid_item_missing_node_id()`](../../../tests/contracts/test_v1_schemas.py:122)
- [`test_push_item_invalid_missing_git_commit()`](../../../tests/contracts/test_v1_schemas.py:205)
- [`test_query_request_invalid_top_k_type()`](../../../tests/contracts/test_v1_schemas.py:341)
- [`test_error_envelope_valid_business_error()`](../../../tests/contracts/test_v1_schemas.py:403)
- [`test_provider_capabilities_valid_qwen_with_instruction()`](../../../tests/contracts/test_v1_schemas.py:464)
- [`test_provider_capabilities_invalid_empty_instruction_hint()`](../../../tests/contracts/test_v1_schemas.py:548)

## Команда запуска

- `uv run pytest tests/contracts/test_v1_schemas.py`

## Ожидаемый результат

- Полный suite проходит локально: `38 passed`.

## Связанные требования

- [`docs/contracts/contract-tests.md`](../../contracts/contract-tests.md)
- [`docs/architecture/stage-2-specification.md`](../../../../../docs/architecture/stage-2-specification.md:274)
