from time import sleep

from redis import StrictRedis

from backends.redis import RedisMessageBackend
from settings import (
    MESSAGE_PREFIX, GENERATOR_KEY, GENERATOR_TIMEOUT_MS, GENERATE_MESSAGE_DELAY_MS, MAX_ATTEMPTS_ON_KEY_CONFLICTS,
    RECEIVE_MESSAGE_DELAY_MS,
)
from exceptions import KeyConflictError
from utils import generate_random_str


redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class MessageReceiver:
    pass


class MessageSender:
    pass


class MessageHandler(RedisMessageBackend):
    """
    Генератор всегда в транзакции удаляет этот ключ и создает его заново
    1. Есть ключ - идем по пути обработчика сообщений
    2. Нет ключа - пробую в транзакции его поставить и если возвращается True, то становлюсь генератором
    """
    # TODO add layer between redis keys, get, transaction, etc. functions to make possibility of any other message
    # backend

    def __init__(self, backend, generator_id=GENERATOR_KEY, generator_ttl_ms=GENERATOR_TIMEOUT_MS):
        self.backend = backend

        self.is_generator = False
        self.generator_id = generator_id
        self.generator_ttl_ms = generator_ttl_ms

        self.generated_message_key = None
        self.generated_message = None

        self.received_message_key = None

    def run(self):
        while True:
            if self.is_generator:
                print("I'm a generator")
                self.prolong_generator()
                self.send_message()
                sleep(GENERATE_MESSAGE_DELAY_MS / 1000)
                continue

            print("I'm not a generator")
            is_generator_online = self.backend.get(self.generator_id)
            print(f"is a generator online ? - {is_generator_online}")
            if is_generator_online:
                self.receive_messages()
            else:
                self.backend.transaction(self.try_to_update_to_generator, self.generator_id)

    def send_message(self):
        for _ in range(MAX_ATTEMPTS_ON_KEY_CONFLICTS):
            self.generated_message_key = f"{MESSAGE_PREFIX}{generate_random_str()}"
            self.generated_message = generate_random_str(20)
            try:
                self.backend.transaction(self._send_message, self.received_message_key)
            except KeyConflictError:
                continue
            return

    def _send_message(self, pipe):
        value = pipe.get(self.generated_message_key)
        if value:
            raise KeyConflictError
        print(f"sending message {self.generated_message_key} {self.generated_message}")
        pipe.multi()  # TODO is it need here?
        pipe.set(self.generated_message_key, self.generated_message)

    def prolong_generator(self):
        self.backend.transaction(self._prolong_generator, self.generator_id)

    def _prolong_generator(self, pipe):
        print("Extending as a generator")
        pipe.delete(self.generator_id)
        pipe.set(self.generator_id, True, nx=True, px=self.generator_ttl_ms)

    def receive_messages(self):
        for self.received_message_key in self.backend.keys(f"{MESSAGE_PREFIX}*"):
            self.backend.transaction(self._receive_message, self.received_message_key)
            sleep(RECEIVE_MESSAGE_DELAY_MS / 1000)

    # TODO think about transactions functions - it is Redis dependent and this is bad for abstractions
    # pack transactions into a functions i think
    def _receive_message(self, pipe):
        value = pipe.get(self.received_message_key)
        if not value:
            return
        print(f"receiving {self.received_message_key} {value}")
        pipe.multi()  # TODO is it need here?
        pipe.delete(self.received_message_key)

    def try_to_update_to_generator(self, pipe):
        print("Trying to update to generator")
        is_set = pipe.set(self.generator_id, True, nx=True, px=self.generator_ttl_ms)
        print(f"is set to generator? {is_set}")
        if not is_set:
            return
        print("I'm generator now")
        self.is_generator = True


if __name__ == '__main__':
    app = MessageHandler(backend=redis)
    app.run()
