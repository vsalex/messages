from .helpers import IncomingArg

GET_ERRORS = 'GET-ERRORS'

INCOMING_ARGS = (
    IncomingArg('getErrors', GET_ERRORS, terminate_handler=True),
)
