# Contracts: code-rag

Этот каталог содержит Contract-First артефакты `code-rag`.

Stage 2 описывает контракты текстом и примерами в [`docs/architecture/stage-2-specification.md`](docs/architecture/stage-2-specification.md). Stage 3 должен зафиксировать **формальные схемы** (JSON Schema или эквивалент), чтобы:

- L2 Contract tests могли валидировать payloads;
- backend, UI и интеграции (например `code-atlas`) могли развиваться независимо.

## Версионирование

- Директория версии (`v1/`, `v2/`, ...) соответствует `contract_version` из push-first контракта.
- Breaking change любой схемы -> новая директория версии.
- Non-breaking change -> расширение схемы внутри текущей директории.

### Политика совместимости

- `contract_version = "1.0"` фиксируется для всех payloads `v1/`.
- Изменения, меняющие обязательные поля, типы или enum значения в несовместимом виде, считаются breaking.
- Добавление новых **optional** полей в `v1/` считается non-breaking.

## v1 (целевой набор схем)

В версии `v1/` поддерживаются схемы:

- `push_batch.schema.json` (см. [`docs/architecture/stage-2-specification.md:92`](docs/architecture/stage-2-specification.md:92))
- `push_item.schema.json` (см. [`docs/architecture/stage-2-specification.md:104`](docs/architecture/stage-2-specification.md:104))
- `push_acceptance.schema.json` (см. [`docs/architecture/stage-2-specification.md:130`](docs/architecture/stage-2-specification.md:130))
- `reconcile_request.schema.json` (см. [`docs/architecture/stage-2-specification.md:180`](docs/architecture/stage-2-specification.md:180))
- `reconcile_response.schema.json` (см. [`docs/architecture/stage-2-specification.md:204`](docs/architecture/stage-2-specification.md:204))
- `query_request.schema.json` (см. [`docs/architecture/stage-2-specification.md:220`](docs/architecture/stage-2-specification.md:220))
- `query_response.schema.json` (см. [`docs/architecture/stage-2-specification.md:229`](docs/architecture/stage-2-specification.md:229))
- `error_envelope.schema.json` (см. [`docs/architecture/stage-2-specification.md:236`](docs/architecture/stage-2-specification.md:236))
- `provider_capabilities.schema.json` (см. требования к провайдерам в [`docs/architecture/stage-2-specification.md:70`](docs/architecture/stage-2-specification.md:70))

### Provider capabilities (v1)

Схема [`docs/contracts/v1/provider_capabilities.schema.json`](docs/contracts/v1/provider_capabilities.schema.json) фиксирует кросс-модельные поля:

- `supports_dimensions`
- `supports_instruction`
- `max_context_tokens`
- `recommended_query_instruction` (optional)

Эти поля позволяют явно описывать различия между `qwen3-embedding` и `bge-m3` в рамках единого provider contract.

## Web API для Web UI

Web UI требования перечислены в [`docs/architecture/stage-2-specification.md:295`](docs/architecture/stage-2-specification.md:295).

Формат контракта UI<->backend: OpenAPI в файле [`docs/contracts/web-ui.openapi.yaml`](docs/contracts/web-ui.openapi.yaml).

## Как валидировать contract payloads

Практическая матрица кейсов описана в [`docs/contracts/contract-tests.md`](docs/contracts/contract-tests.md).

Рекомендуемый воспроизводимый путь валидации:

1. Запустить тесты контрактов (`pytest`) для позитивных и негативных payloads.
2. Проверить, что `contract_version = "1.0"` проходит только для схем `v1/`.
3. Проверить shape для error envelope и query response в L2 contract tests.
