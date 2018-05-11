import logging
import random
from time import sleep

from .backends.base import Message
from .settings import (
    MESSAGE_PREFIX, GENERATOR_KEY, MESSAGE_ERRORS_QUEUE, MESSAGE_ERROR_CHANCE_INT, GENERATOR_TIMEOUT_MS,
    GENERATE_MESSAGE_DELAY_MS, RECEIVE_MESSAGE_DELAY_MS,
)
from .utils import generate_random_str


logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, backend, print_errors=False, receive_message_delay_ms=RECEIVE_MESSAGE_DELAY_MS,
                 message_prefix=MESSAGE_PREFIX, generator_key=GENERATOR_KEY, message_errors_queue=MESSAGE_ERRORS_QUEUE,
                 message_error_chance_int=MESSAGE_ERROR_CHANCE_INT, generator_ttl_ms=GENERATOR_TIMEOUT_MS):

        self.backend = backend
        self.print_errors = print_errors

        self.receive_message_delay_ms = receive_message_delay_ms
        self.message_prefix = message_prefix
        self.generator_key = generator_key
        self.message_errors_queue = message_errors_queue
        self.message_error_chance_int = message_error_chance_int
        self.generator_ttl_ms = generator_ttl_ms

        self.is_generator = False

    @staticmethod
    def generate_message() -> Message:
        return Message(
            key=f"{MESSAGE_PREFIX}{generate_random_str()}",
            value=generate_random_str(20),
        )

    def _is_message_error(self, message: Message) -> bool:
        """Simulating % error."""
        number = random.randint(1, 100)
        if number < self.message_error_chance_int:
            return True
        return False

    def run(self):
        if self.print_errors:
            errors = self.backend.get_all(self.message_errors_queue)
            logger.info(f"Errors messages are: {errors}")
            self.backend.delete(self.message_errors_queue)
            return

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

            if self._is_message_error(message):
                logger.debug(f"Error in message {message}. Appending message to {self.message_errors_queue}.")
                self.backend.append(self.message_errors_queue, message.value)

            sleep(self.receive_message_delay_ms / 1000)
            return

        self.is_generator = self.backend.extend(
            key=self.generator_key,
            value=True,
            if_not_exist=True,
            expire_time_ms=self.generator_ttl_ms,
        )
