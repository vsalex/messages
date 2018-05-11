# TODO think about settings for different env - dev, test, prod...

# Default python logging module levels
# If set this to "DEBUG" you will see what's going on - recommended for first look at application
LOG_LEVEL = "DEBUG"

# Dotted path to backend class
MESSAGE_BACKEND = 'messages.backends.redis.RedisMessageBackend'
MESSAGE_BACKEND_HOST = 'localhost'
MESSAGE_BACKEND_PORT = 6379
MESSAGE_BACKEND_PASSWORD = None


MESSAGE_BASE = "MESSAGES"
MESSAGE_PREFIX = f"{MESSAGE_BASE}:"

GENERATOR_KEY = f"GENERATOR-OF-{MESSAGE_BASE}-PRESENT"
MESSAGE_ERRORS_QUEUE = f"{MESSAGE_BASE}-RECEIVED-ERRORS"
# Between 1 and 100
MESSAGE_ERROR_CHANCE_INT = 5
MESSAGE_ERROR_PRINT_ARG = "getErrors"

# With respect of latency
GENERATOR_TIMEOUT_MS = 2000

GENERATE_MESSAGE_DELAY_MS = 500
RECEIVE_MESSAGE_DELAY_MS = 550
