# TODO Make flexible backend setting

MESSAGE_BASE = "MESSAGES"
MESSAGE_PREFIX = f"{MESSAGE_BASE}:"

GENERATOR_KEY = f"GENERATOR-OF-{MESSAGE_BASE}-PRESENT"

# Remember of request to backend latency here
GENERATOR_TIMEOUT_MS = 3000

GENERATE_MESSAGE_DELAY_MS = 500
RECEIVE_MESSAGE_DELAY_MS = 550


###################
# Internal values #
###################
MAX_ATTEMPTS_ON_KEY_CONFLICTS = 10
