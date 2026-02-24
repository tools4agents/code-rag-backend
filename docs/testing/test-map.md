# Test Map: code-rag

Этот документ — **Map of Content** по тестовому контуру проекта.

Назначение: дать агенту и разработчику быстрый обзор того:
- какие тесты уже есть,
- где они лежат,
- что они проверяют,
- куда идти за детальным описанием.

## Как использовать карту

1. Выбери уровень теста (L1/L2/L3/L4).
2. Перейди к нужному домену.
3. Открой ссылку на suite-документ.
4. Из suite-документа перейди к конкретному скрипту/кейсам.

Это обеспечивает «ленивую загрузку» контекста: читаем только нужный раздел, а не весь тестовый контур сразу.

## Быстрые команды

- Все тесты: [`uv run pytest`](../../pyproject.toml)
- Только contract tests: [`uv run pytest tests/contracts`](../../tests/contracts/test_v1_schemas.py)
- Только unit tests: [`uv run pytest tests/unit`](../../tests/unit/test_project_registry.py)

## Навигационная карта

| Level | Домен | Suite описание | Тестовый скрипт |
|---|---|---|---|
| L2 | v1 JSON Schemas | [`contracts-v1.md`](./suites/contracts-v1.md) | [`tests/contracts/test_v1_schemas.py`](../../tests/contracts/test_v1_schemas.py) |
| L2 | Web UI OpenAPI | [`openapi-web-ui.md`](./suites/openapi-web-ui.md) | [`tests/contracts/test_openapi_contract.py`](../../tests/contracts/test_openapi_contract.py) |
| L1 | Project Registry core | [`unit-project-registry.md`](./suites/unit-project-registry.md) | [`tests/unit/test_project_registry.py`](../../tests/unit/test_project_registry.py) |
| L1 | Indexing Job lifecycle | [`unit-indexing-job-lifecycle.md`](./suites/unit-indexing-job-lifecycle.md) | [`tests/unit/test_indexing_job.py`](../../tests/unit/test_indexing_job.py) |
| L3 | Integration (placeholder) | TBD | TBD |
| L4 | E2E / Visual (placeholder) | TBD | TBD |

## Ссылки на подробные suite-описания

- [`docs/testing/suites/contracts-v1.md`](./suites/contracts-v1.md)
- [`docs/testing/suites/openapi-web-ui.md`](./suites/openapi-web-ui.md)
- [`docs/testing/suites/unit-project-registry.md`](./suites/unit-project-registry.md)
- [`docs/testing/suites/unit-indexing-job-lifecycle.md`](./suites/unit-indexing-job-lifecycle.md)

## Протокол обновления карты тестов

При добавлении/изменении тестов обязательно:
1. Обновить строку в карте выше (level/domain/suite/script).
2. Обновить соответствующий suite-файл:
   - назначение,
   - покрываемые требования,
   - список ключевых тест-кейсов,
   - команду запуска.
3. Добавить ссылку на suite и проверку в `Execution Status` task-файла.
4. Для новых направлений L3/L4 убрать `TBD` и добавить реальные ссылки.

## Связанные документы

- Матрица L2 payload-кейсов: [`docs/contracts/contract-tests.md`](../contracts/contract-tests.md)
- Канонический Test Design L1-L4: [`docs/architecture/stage-2-specification.md`](../architecture/stage-2-specification.md:259)
