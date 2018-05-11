import importlib
import logging
import sys

from .exceptions import SettingsError
from .handler import MessageHandler
from .settings import (
    MESSAGE_BACKEND, LOG_LEVEL, MESSAGE_BACKEND_HOST, MESSAGE_BACKEND_PORT, MESSAGE_BACKEND_PASSWORD,
    MESSAGE_ERROR_PRINT_ARG,
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


def get_message_backend_class():
    message_backend_list = MESSAGE_BACKEND.split(".")

    try:
        backend_module_path = ".".join(message_backend_list[:-1])
        backend_module = importlib.import_module(backend_module_path)
        backend_class = getattr(backend_module, message_backend_list[-1])
    except (IndexError, ImportError, AttributeError):
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    return backend_class


# TODO not need now - refactor
def get_args() -> list:
    args = []
    for arg in sys.argv:
        if arg == MESSAGE_ERROR_PRINT_ARG:
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
    # TODO refactor (it is 3 am now)
    return MessageHandler(backend=message_backend, print_errors=MESSAGE_ERROR_PRINT_ARG in get_args())


configure_logging()
