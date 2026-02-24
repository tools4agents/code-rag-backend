import logging
from importlib.metadata import entry_points
from typing import Any, Dict, Type, TypeVar, Generic

T = TypeVar("T")

logger = logging.getLogger(__name__)

class PluginFactory(Generic[T]):
    """
    Универсальная фабрика для загрузки плагинов через Python Entry Points.
    """

    def __init__(self, group: str):
        self.group = group
        self._cached_classes: Dict[str, Type[T]] = {}

    def get_plugin_class(self, name: str) -> Type[T]:
        """
        Находит и загружает класс плагина по его имени в группе.
        """
        if name in self._cached_classes:
            return self._cached_classes[name]

        # В Python 3.10+ entry_points() возвращает объект с методом select()
        eps = entry_points().select(group=self.group)
        
        for ep in eps:
            if ep.name == name:
                plugin_class = ep.load()
                self._cached_classes[name] = plugin_class
                return plugin_class

        available = [ep.name for ep in eps]
        raise ValueError(
            f"Плагин '{name}' не найден в группе '{self.group}'. "
            f"Доступные плагины: {available}"
        )

    def create_instance(self, name: str, **kwargs) -> T:
        """
        Создает экземпляр плагина с переданными параметрами.
        """
        plugin_class = self.get_plugin_class(name)
        logger.info(f"Создание экземпляра плагина '{name}' из группы '{self.group}'")
        return plugin_class(**kwargs)

# Специализированные фабрики
vector_db_factory = PluginFactory(group="rag4code.vector_db")
embedder_factory = PluginFactory(group="rag4code.embedder")