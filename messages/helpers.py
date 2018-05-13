class IncomingArg:
    def __init__(self, incoming_value: str, value: str, terminate_handler: bool=False):
        self.incoming_value = incoming_value
        self.value = value
        self.terminate_handler = terminate_handler

    def __repr__(self):
        return f"{self.incoming_value} -> {self.value}"
