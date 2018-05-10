import logging
from time import sleep

from .backends.base import Message
from .settings import (
    MESSAGE_PREFIX, GENERATOR_KEY, GENERATOR_TIMEOUT_MS, GENERATE_MESSAGE_DELAY_MS, RECEIVE_MESSAGE_DELAY_MS,
)
from .utils import generate_random_str


logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, backend, receive_message_delay_ms=RECEIVE_MESSAGE_DELAY_MS, message_prefix=MESSAGE_PREFIX,
                 generator_key=GENERATOR_KEY, generator_ttl_ms=GENERATOR_TIMEOUT_MS):

        self.backend = backend
        self.receive_message_delay_ms = receive_message_delay_ms
        self.message_prefix = message_prefix
        self.generator_key = generator_key
        self.generator_ttl_ms = generator_ttl_ms

        self.is_generator = False

    @staticmethod
    def generate_message() -> Message:
        return Message(
            key=f"{MESSAGE_PREFIX}{generate_random_str()}",
            value=generate_random_str(20),
        )

    def run(self):
        while True:
            self._process_messages()

    def _process_messages(self):
        if self.is_generator:
            self._process_as_generator()
            return

        self._process_as_receiver()

    def _process_as_generator(self):
        logger.debug("I'm a generator.")
        self.backend.extend(
            key=self.generator_key,
            value=True,
            if_not_exist=True,
            expire_time_ms=self.generator_ttl_ms,
        )
        random_message = self.generate_message()
        self.backend.send(random_message)
        sleep(GENERATE_MESSAGE_DELAY_MS / 1000)

    def _process_as_receiver(self):
        logger.debug("I'm receiver.")
        message = self.backend.receive(self.generator_key)
        is_generator_online = message.value

        logger.debug(f"Generator is {'online' if is_generator_online else 'offline'}.")
        if is_generator_online:
            message = self.backend.receive_by_prefix(self.message_prefix)
            sleep(self.receive_message_delay_ms / 1000)
            return

        self.is_generator = self.backend.extend(
            key=self.generator_key,
            value=True,
            if_not_exist=True,
            expire_time_ms=self.generator_ttl_ms,
        )
