# Паттерн Фабрика с Регистрацией (Registry Factory)

## Что это такое?

**Фабрика с регистрацией** — это эволюция классического паттерна "Фабричный метод" (Factory Method), которая позволяет динамически расширять список создаваемых объектов без изменения кода самой фабрики.

В классической фабрике часто используется большой `if-elif-else` или `switch` для выбора класса:

```python
def create_db(type):
    if type == "postgres":
        return PostgresDB()
    elif type == "mysql":
        return MySQLDB()
    # Чтобы добавить новую БД, нужно менять этот код!
```

В **Фабрике с регистрацией** классы сами "сообщают" фабрике о своем существовании. Фабрика хранит реестр (словарь) соответствия "имя -> класс".

## Как это работает?

1.  **Интерфейс**: Определяется общий интерфейс для всех продуктов (например, `Database`).
2.  **Фабрика**: Содержит словарь `_registry = {}` и методы `register(name, class)` и `create(name)`.
3.  **Продукты**: При объявлении класса (или импорте модуля) регистрируют себя в фабрике.

## Пример кода

### 1. Фабрика

```python
class DatabaseFactory:
    _registry = {}

    @classmethod
    def register(cls, name: str, db_class: type):
        """Регистрация нового типа БД"""
        cls._registry[name] = db_class

    @classmethod
    def create(cls, name: str, **kwargs):
        """Создание экземпляра БД"""
        if name not in cls._registry:
            raise ValueError(f"Unknown database type: {name}")
        
        db_class = cls._registry[name]
        return db_class(**kwargs)
```

### 2. Использование (Декоратор)

Часто для удобства используют декоратор:

```python
def register_db(name):
    def decorator(cls):
        DatabaseFactory.register(name, cls)
        return cls
    return decorator

@register_db("postgres")
class PostgresDB:
    def __init__(self, host, port):
        print(f"Connecting to Postgres at {host}:{port}")

@register_db("mysql")
class MySQLDB:
    def __init__(self, host, port):
        print(f"Connecting to MySQL at {host}:{port}")
```

### 3. Клиентский код

```python
# Код фабрики не меняется при добавлении новых классов!
db = DatabaseFactory.create("postgres", host="localhost", port=5432)
```

## Преимущества и Недостатки

**Преимущества:**
*   **Open/Closed Principle**: Фабрика открыта для расширения, но закрыта для модификации.
*   **Decoupling**: Фабрика не зависит от конкретных классов продуктов.

**Недостатки:**
*   **Проблема импорта**: Чтобы класс зарегистрировался, Python должен "прочитать" файл с его кодом. Если вы просто запустите `main.py`, а классы лежат в `plugins/`, они не загрузятся сами. Приходится делать "магические" импорты всех модулей при старте.

Именно проблему "магических импортов" решает механизм **Entry Points**, описанный в [соседней статье](./entry_points_mechanism.md).