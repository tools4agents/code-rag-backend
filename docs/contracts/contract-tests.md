# Contract Tests (Level 2)

Этот документ фиксирует L2 Contract tests и их связь со схемами в [`docs/contracts/v1/`](docs/contracts/v1/).

Навигационный индекс по тестам проекта: [`docs/testing/test-map.md`](../testing/test-map.md).
Детальное описание L2 suites:
- [`docs/testing/suites/contracts-v1.md`](../testing/suites/contracts-v1.md)
- [`docs/testing/suites/openapi-web-ui.md`](../testing/suites/openapi-web-ui.md)

## 1) Push-first (Batch)

**Schema**: [`docs/contracts/v1/push_batch.schema.json`](docs/contracts/v1/push_batch.schema.json)

### Valid
- `contract_version = "1.0"`, `project`, `source`, `batch_id`, `items: []`
- `items` содержит валидные элементы из [`push_item.schema.json`](docs/contracts/v1/push_item.schema.json)

### Invalid
- отсутствует `contract_version`
- `contract_version = "2.0"`
- отсутствует `items`
- `items` содержит объект без `node_id`

## 2) Push Item

**Schema**: [`docs/contracts/v1/push_item.schema.json`](docs/contracts/v1/push_item.schema.json)

### Valid
- минимальный item с `node_id`, `node_type`, `path`, `language`, `content`, `range`, `source_audit`

### Invalid
- `content` пустая строка
- `range` без `start_line` или `end_line`
- `source_audit` без `git_commit`

## 3) Push Acceptance

**Schema**: [`docs/contracts/v1/push_acceptance.schema.json`](docs/contracts/v1/push_acceptance.schema.json)

### Valid
- `accepted >= 0`, `rejected >= 0`, `errors: []`

### Invalid
- отсутствует `batch_id`
- `errors` содержит объект без `code` или `message`

## 4) Reconcile Request

**Schema**: [`docs/contracts/v1/reconcile_request.schema.json`](docs/contracts/v1/reconcile_request.schema.json)

### Valid
- `mode = dry_run` и `project`
- `mode = fix` + `namespace` optional

### Invalid
- `mode = diff`
- отсутствует `project`

## 5) Reconcile Response

**Schema**: [`docs/contracts/v1/reconcile_response.schema.json`](docs/contracts/v1/reconcile_response.schema.json)

### Valid
- `summary` содержит `missing`, `stale`, `orphan`
- `actions` пустой массив

### Invalid
- отсутствует `summary`
- `actions` содержит объект без `action`

## 6) Query Request

**Schema**: [`docs/contracts/v1/query_request.schema.json`](docs/contracts/v1/query_request.schema.json)

### Valid
- `query` + `project`

### Invalid
- отсутствует `query`

## 7) Query Response

**Schema**: [`docs/contracts/v1/query_response.schema.json`](docs/contracts/v1/query_response.schema.json)

### Valid
- `matches` массив из `SearchMatch` с audit metadata

### Invalid
- `matches` отсутствует

## 8) Error Envelope

**Schema**: [`docs/contracts/v1/error_envelope.schema.json`](docs/contracts/v1/error_envelope.schema.json)

### Valid
- `error.code`, `error.message`, `error.details`

### Invalid
- отсутствует `error`

## 9) Provider Capabilities

**Schema**: [`docs/contracts/v1/provider_capabilities.schema.json`](docs/contracts/v1/provider_capabilities.schema.json)

### Valid
- `provider = "ollama"`, `model = "qwen3-embedding"`, `capabilities.supports_dimensions = true`, `capabilities.supports_instruction = true`, `capabilities.max_context_tokens > 0`
- `provider = "ollama"`, `model = "bge-m3"`, `capabilities.supports_dimensions = false`, `capabilities.supports_instruction = false`, `capabilities.max_context_tokens > 0`
- optional `recommended_query_instruction` задан непустой строкой
- optional `supported_dimensions` задан объектом c `min` и `max`

### Invalid
- отсутствует `model`
- отсутствует `capabilities.supports_dimensions`
- отсутствует `capabilities.supports_instruction`
- отсутствует `capabilities.max_context_tokens`
- `max_context_tokens = 0`
- `recommended_query_instruction = ""`
- `supported_dimensions` без `min` или `max`
