from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class VectorDBInterface(ABC):
    """
    Абстрактный интерфейс для векторных баз данных.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Инициализация адаптера с произвольными параметрами конфигурации.
        """
        pass

    @abstractmethod
    def add_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        """
        Добавление векторов и метаданных в базу.
        """
        pass

    @abstractmethod
    def search(self, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск ближайших векторов.
        """
        pass