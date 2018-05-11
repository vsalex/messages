import logging

from .base import BaseMessageBackend, Message
from .constants import MAX_ATTEMPTS_ON_KEY_CONFLICTS
from .exceptions import KeyConflictError

logger = logging.getLogger(__name__)


class RedisMessageBackend(BaseMessageBackend):
    def __init__(self, redis):
        self.redis = redis

        self.send_message: Message = None
        self.receive_message: Message = None
        self.receive_key = None

        self.extend_message: Message = None
        self.extend_expire_time_ms: int = None
        self.extend_if_not_exist: bool = None
        self.extend_is_set = False

    def send(self, message: Message):
        for _ in range(MAX_ATTEMPTS_ON_KEY_CONFLICTS):
            self.send_message = message
            try:
                self.redis.transaction(self._send, self.send_message.key)
            except KeyConflictError:
                logger.warning(f"Key {self.send_message.key} conflict error!")
                continue
            return

    def _send(self, pipe):
        value = pipe.get(self.send_message.key)
        if value:
            raise KeyConflictError
        logger.debug(f"Sending message {self.send_message}.")
        pipe.set(self.send_message.key, self.send_message.value)

    def receive(self, key) -> Message:
        return Message(
            key=key,
            value=self.redis.get(key),
        )

    def receive_by_prefix(self, prefix) -> Message:
        for self.receive_key in self.redis.keys(f"{prefix}*"):
            self.redis.transaction(self._receive_by_prefix, self.receive_key)
            return self.receive_message

    def _receive_by_prefix(self, pipe):
        self.receive_message = None
        value = pipe.get(self.receive_key)

        if not value:
            return

        self.receive_message = Message(key=self.receive_key, value=value)
        logger.debug(f"Received message {self.receive_message}.")
        pipe.delete(self.receive_key)

    def extend(self, key, value, if_not_exist, expire_time_ms) -> bool:
        self.extend_message = Message(key, value)
        self.extend_expire_time_ms, self.extend_if_not_exist = expire_time_ms, if_not_exist
        self.redis.transaction(self._extend, self.extend_message.key)
        return self.extend_is_set

    def _extend(self, pipe):
        logger.debug(f"Extending {self.extend_message}.")
        pipe.delete(self.extend_message.key)
        self.extend_is_set = pipe.set(
            self.extend_message.key,
            self.extend_message.value,
            nx=self.extend_if_not_exist,
            px=self.extend_expire_time_ms,
        )

    def delete(self, key) -> bool:
        return self.redis.delete(key)

    def append(self, key, value) -> bool:
        return self.redis.rpush(key, value)

    # TODO refactor
    def get_all(self, key) -> list:
        return self.redis.lrange(key, -1000, 1000)
