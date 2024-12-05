from abc import ABC
from abc import abstractmethod


class BasicViewProvider(ABC):
    """
    Abstract View Provider for events prefs settings
    """

    @abstractmethod
    def put(self, key: str, value: str) -> None: ...

    @abstractmethod
    def get(self, key: str) -> str: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...
