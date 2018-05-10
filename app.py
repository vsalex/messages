from messages.handler import MessageHandler
from messages.initializer import get_message_backend


if __name__ == '__main__':
    message_backend = get_message_backend()
    app = MessageHandler(backend=message_backend)
    app.run()
