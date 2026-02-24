# Руководство по разработке плагинов для rag4code

`rag4code` использует модульную архитектуру, где функциональность (Векторные БД, Эмбеддинги) вынесена в отдельные плагины. Это руководство поможет вам создать свой собственный плагин.

## 1. Концепция

Плагин — это обычный Python-пакет, который:
1.  Реализует один из стандартных интерфейсов `rag4code-core`.
2.  Объявляет о себе через механизм `entry-points` в `pyproject.toml`.

## 2. Структура плагина

Рекомендуемая структура репозитория плагина:

```text
rag4code-myplugin/
├── pyproject.toml       # Манифест пакета и entry-points
├── README.md
└── src/
    └── rag4code_myplugin/
        ├── __init__.py
        └── adapter.py   # Реализация класса
```

## 3. Шаг за шагом: Создание плагина Векторной БД

### Шаг 1: pyproject.toml

Самое важное — секция `project.entry-points`.

```toml
[project]
name = "rag4code-myplugin"
version = "0.1.0"
dependencies = [
    "rag4code-core>=0.1.0",  # Для доступа к интерфейсам
    "some-db-client>=1.0.0"  # Ваши зависимости
]

[project.entry-points."rag4code.vector_db"]
my_db = "rag4code_myplugin.adapter:MyDBAdapter"
```

*   `rag4code.vector_db` — это имя группы (контракт).
*   `my_db` — это уникальное имя вашего плагина (будет использоваться в конфиге).
*   `rag4code_myplugin.adapter:MyDBAdapter` — путь к классу.

### Шаг 2: Реализация класса

Ваш класс должен наследовать интерфейс из `rag4code.core.interfaces`.

```python
from typing import List, Dict, Any
from rag4code.core.interfaces import VectorDBInterface

class MyDBAdapter(VectorDBInterface):
    def __init__(self, **kwargs):
        """
        Инициализация.
        kwargs — это параметры из конфига пользователя.
        """
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 1234)
        print(f"Connecting to MyDB at {self.host}:{self.port}")

    def add_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        # Ваша логика добавления векторов
        pass

    def search(self, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        # Ваша логика поиска
        return []
```

## 4. Тестирование с HPM

Чтобы протестировать плагин в составе `rag4code` во время разработки:

1.  Создайте манифест пакета для HPM (например, `hpm-registry/packages/my-plugin.yaml`).
2.  В секции `dev` укажите локальный путь к папке вашего плагина:
    ```yaml
    sources:
      dev:
        type: local
        path: ../packages/rag4code-myplugin
        editable: true
    ```
3.  Выполните `hpm sync`. HPM создаст виртуальное окружение, где ваш плагин будет установлен в режиме `editable`.
4.  Теперь `rag4code-core` увидит ваш плагин!