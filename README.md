# code-rag-backend

Репозиторий backend-компонента для стека code-rag.

## Область ответственности

- Доменная и core-логика: `src/code_rag_backend/core/`
- Интерфейсы backend-компонента: `src/code_rag_backend/interfaces/`
- Контракты backend API: `docs/contracts/`
- Тесты backend-компонента: `tests/`
- Плагины и реализации компонентов: `packages/`

MCP transport слой живет в root-репозитории: `src/code_rag/mcp/`.

## Локальная проверка

- `uv run pytest`
