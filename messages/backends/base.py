from abc import abstractmethod, ABC


class Message:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def __str__(self):
        return f"{self.key}: {self.value}"


class BaseMessageBackend(ABC):
    """Every message backend class must be subclass of this class."""

    @abstractmethod
    def send(self, message: Message):
        pass

    @abstractmethod
    def receive(self, key) -> Message:
        pass

    @abstractmethod
    def receive_by_prefix(self, prefix) -> Message:
        pass

    @abstractmethod
    def extend(self, key, value, if_not_exist: bool, expire_time_ms: int) -> bool:
        pass

    @abstractmethod
    def delete(self, key) -> bool:
        pass

    @abstractmethod
    def append(self, key, value) -> bool:
        pass

    @abstractmethod
    def get_all(self, key) -> list:
        pass
