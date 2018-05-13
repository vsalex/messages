import importlib
import logging
import sys

from .constants import INCOMING_ARGS
from .exceptions import SettingsError
from .handler import MessageHandler
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
DEFAULT_ERROR_MESSAGE = "MESSAGE_BACKEND must be dotted path to message backend class " \
                        "e.g. 'messages.backends.redis.RedisMessageBackend'"


def configure_logging():
    logging.basicConfig(format='%(levelname)s %(message)s',)
    log_level = getattr(logging, LOG_LEVEL, None)
    if not log_level:
        print(f"Wrong log level '{LOG_LEVEL}'. Set default log level to '{DEFAULT_LOG_LEVEL}'.")
        log_level = getattr(logging, DEFAULT_LOG_LEVEL)
    logging.getLogger().setLevel(log_level)


# TODO TESTS for this function
# TODO i think here will be good func with arguments, not just functions
def get_message_backend_class():
    message_backend_list = MESSAGE_BACKEND.split(".")

    try:
        backend_module_path = ".".join(message_backend_list[:-1])
        backend_module = importlib.import_module(backend_module_path)
        backend_class = getattr(backend_module, message_backend_list[-1])
    except (IndexError, ImportError, AttributeError):
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    return backend_class


# TODO TEST if app run with some other args
def get_incoming_args() -> list:
    args = []

    for arg in INCOMING_ARGS:
        if arg.incoming_value in sys.argv:
            args.append(arg)

    return args


def get_message_backend():
    backend_class = get_message_backend_class()
    return backend_class(
        redis=StrictRedis(
            password=MESSAGE_BACKEND_PASSWORD,
            host=MESSAGE_BACKEND_HOST,
            port=MESSAGE_BACKEND_PORT,
            db=0,
            decode_responses=True,
        ),
    )


def get_app():
    message_backend = get_message_backend()
    return MessageHandler(
        backend=message_backend,
        incoming_args=get_incoming_args(),
        receive_message_delay_ms=RECEIVE_MESSAGE_DELAY_MS,
        message_prefix=MESSAGE_PREFIX,
        generator_key=GENERATOR_KEY,
        message_errors_queue=MESSAGE_ERRORS_QUEUE,
        message_error_chance_int=MESSAGE_ERROR_CHANCE_INT,
        generator_ttl_ms=GENERATOR_TTL_MS,
        generate_message_delay_ms=GENERATE_MESSAGE_DELAY_MS,
    )


configure_logging()
