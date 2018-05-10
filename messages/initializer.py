import importlib
import logging

from .exceptions import SettingsError
from .settings import MESSAGE_BACKEND, LOG_LEVEL

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
    except IndexError:
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    try:
        backend_module = importlib.import_module(backend_module_path)
    except ImportError:
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    try:
        backend_class = getattr(backend_module, message_backend_list[-1])
    except AttributeError:
        raise SettingsError(DEFAULT_ERROR_MESSAGE)

    return backend_class


def get_message_backend():
    backend_class = get_message_backend_class()
    return backend_class(
        redis=StrictRedis(host='localhost', port=6379, db=0, decode_responses=True),
    )


configure_logging()
