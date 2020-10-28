import importlib
import logging
import sys
from typing import List, Tuple

from .constants import INCOMING_ARGS
from .exceptions import SettingsError
from .handler import MessageHandler
from .helpers import IncomingArg
from .settings import (
    MESSAGE_BACKEND, LOG_LEVEL, MESSAGE_BACKEND_HOST, MESSAGE_BACKEND_PORT, MESSAGE_BACKEND_PASSWORD,
    MESSAGE_PREFIX, GENERATOR_KEY, MESSAGE_ERRORS_QUEUE, MESSAGE_ERROR_CHANCE_INT, GENERATOR_TTL_MS,
    GENERATE_MESSAGE_DELAY_MS, RECEIVE_MESSAGE_DELAY_MS,
)


try:
    from redis import StrictRedis
except ImportError:
    raise SettingsError("It seems that redis package is not set.")

DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_ERROR_MESSAGE = (
    "MESSAGE_BACKEND must be dotted path to message backend class "
    "e.g. 'messages.backends.redis.RedisMessageBackend'"
)


def configure_logging():
    logging.basicConfig(format='%(levelname)s %(message)s',)
    log_level = getattr(logging, LOG_LEVEL, None)
    if not log_level:
        print(f"Wrong log level '{LOG_LEVEL}'. Set default log level to '{DEFAULT_LOG_LEVEL}'.")
        log_level = getattr(logging, DEFAULT_LOG_LEVEL)
    logging.getLogger().setLevel(log_level)


def get_incoming_args(incoming_args: List[str], available_args: Tuple[IncomingArg, ...]) -> List[IncomingArg]:
    args = []

    for arg in available_args:
        if arg.incoming_value in incoming_args:
            args.append(arg)

    return args


def get_message_backend_class(message_backend: str):
    """
    Dynamically imports and returns backend class based on full path to backend class.
    """
    message_backend_list = message_backend.split(".")

    try:
        backend_module_path = ".".join(message_backend_list[:-1])
        backend_module = importlib.import_module(backend_module_path)
        backend_class = getattr(backend_module, message_backend_list[-1])
    except (IndexError, ImportError, AttributeError, ValueError):
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    return backend_class


def get_message_backend(
        message_backend: str,
        message_backend_password: str,
        message_backend_host: str,
        message_backend_port: int
):
    """
    Initializes and returns backend class.
    """

    backend_class = get_message_backend_class(message_backend)

    return backend_class(
        redis=StrictRedis(
            password=message_backend_password,
            host=message_backend_host,
            port=message_backend_port,
            db=0,
            decode_responses=True,
        ),
    )


def get_app():
    """
    Initializes MessageHandler based on settings.
    """

    message_backend = get_message_backend(
        message_backend=MESSAGE_BACKEND,
        message_backend_password=MESSAGE_BACKEND_PASSWORD,
        message_backend_host=MESSAGE_BACKEND_HOST,
        message_backend_port=MESSAGE_BACKEND_PORT,
    )
    return MessageHandler(
        backend=message_backend,
        incoming_args=get_incoming_args(sys.argv, INCOMING_ARGS),
        receive_message_delay_ms=RECEIVE_MESSAGE_DELAY_MS,
        message_prefix=MESSAGE_PREFIX,
        generator_key=GENERATOR_KEY,
        message_errors_queue=MESSAGE_ERRORS_QUEUE,
        message_error_chance_int=MESSAGE_ERROR_CHANCE_INT,
        generator_ttl_ms=GENERATOR_TTL_MS,
        generate_message_delay_ms=GENERATE_MESSAGE_DELAY_MS,
    )


configure_logging()
