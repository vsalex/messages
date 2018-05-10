# Default python logging module levels
# If set this to "DEBUG" you will see what's going on - recommended for first look at application
LOG_LEVEL = "DEBUG"

MESSAGE_BASE = "MESSAGES"
MESSAGE_PREFIX = f"{MESSAGE_BASE}:"

GENERATOR_KEY = f"GENERATOR-OF-{MESSAGE_BASE}-PRESENT"

# With respect of latency
GENERATOR_TIMEOUT_MS = 2000

GENERATE_MESSAGE_DELAY_MS = 500
RECEIVE_MESSAGE_DELAY_MS = 550

# Dotted path to backend class
MESSAGE_BACKEND = 'messages.backends.redis.RedisMessageBackend'
MESSAGE_BACKEND_HOST = 'localhost'
MESSAGE_BACKEND_PORT = 6379
