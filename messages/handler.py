import logging
import random
from time import sleep

from .constants import GET_ERRORS
from .backends.base import Message
from .utils import generate_random_str

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, backend, incoming_args: list, receive_message_delay_ms: int, message_prefix: str,
                 generator_key: str, message_errors_queue: str, message_error_chance_int: int, generator_ttl_ms: int,
                 generate_message_delay_ms: int):

        self.backend = backend
        self.incoming_args = incoming_args

        self.receive_message_delay_ms = receive_message_delay_ms
        self.message_prefix = message_prefix
        self.generator_key = generator_key
        self.message_errors_queue = message_errors_queue
        self.message_error_chance_int = message_error_chance_int
        self.generator_ttl_ms = generator_ttl_ms
        self.generate_message_delay_ms = generate_message_delay_ms

        self.is_generator = False
        self.terminate_handler = False

        print("message_prefix", message_prefix, self.message_prefix)

    def generate_message(self) -> Message:
        return Message(
            key=f"{self.message_prefix}{generate_random_str()}",
            value=generate_random_str(20),
        )

    def _is_message_error(self, message: Message) -> bool:
        """Simulating % error."""
        number = random.randint(1, 100)
        if number < self.message_error_chance_int:
            return True
        return False

    def run(self):
        self._process_incoming_args()

        if self.terminate_handler:
            return

        while True:
            self._process_messages()

    def _process_incoming_args(self):
        """Process script incoming args. Some args may terminate handler."""
        for arg in self.incoming_args:
            if arg.value == GET_ERRORS:
                errors = self.backend.get_all(self.message_errors_queue)
                logger.info(f"Errors messages are: {errors}")
                self.backend.delete(self.message_errors_queue)
                self.terminate_handler = arg.terminate_handler

    def _process_messages(self):
        if self.is_generator:
            self._process_as_generator()
            return

        self._process_as_receiver()

    # TODO TEST if i generator i try to send messages through backend
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
        sleep(self.generate_message_delay_ms / 1000)

    # TODO TEST if i generator i try to send receive through backend
    def _process_as_receiver(self):
        logger.debug("I'm receiver.")
        message = self.backend.receive(self.generator_key)
        is_generator_online = message.value

        logger.debug(f"Generator is {'online' if is_generator_online else 'offline'}.")
        if not is_generator_online:
            self.is_generator = self.backend.extend(
                key=self.generator_key,
                value=True,
                if_not_exist=True,
                expire_time_ms=self.generator_ttl_ms,
            )
            return

        message = self.backend.receive_by_prefix(self.message_prefix)

        if message and self._is_message_error(message):
            logger.debug(f"Error in message {message}. Appending message to {self.message_errors_queue}.")
            self.backend.append(self.message_errors_queue, message.value)

        sleep(self.receive_message_delay_ms / 1000)
