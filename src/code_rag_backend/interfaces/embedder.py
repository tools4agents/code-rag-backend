from abc import ABC, abstractmethod
from typing import Any, Dict, List

class EmbedderInterface(ABC):
    """
    Абстрактный интерфейс для моделей эмбеддингов.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Инициализация адаптера с произвольными параметрами конфигурации.
        """
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Генерация эмбеддинга для одной строки текста.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Генерация эмбеддингов для списка документов.
        """
        pass