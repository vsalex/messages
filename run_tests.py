import logging
import unittest
from unittest import mock

from messages.backends.base import BaseMessageBackend, Message
from messages.exceptions import SettingsError
from messages.helpers import IncomingArg
from messages.initializer import get_incoming_args, get_message_backend_class
from messages.handler import MessageHandler

logging.disable(logging.CRITICAL)


class TestInitializer(unittest.TestCase):
    def test_get_incoming_args(self):
        incoming_args = [
            "notPresentedArg",
            "presentedArg"
        ]
        available_args = (
            IncomingArg("presentedArg", "PRESENTED-ARG"),
        )
        result = get_incoming_args(incoming_args, available_args)
        self.assertSequenceEqual(
            available_args,
            result,
        )

    def test_get_message_backend_class_settings_error(self):
        with self.assertRaises(SettingsError):
            get_message_backend_class("Hello world!")

    def test_get_message_backend_class_base(self):
        result = get_message_backend_class("messages.backends.base.BaseMessageBackend")
        self.assertEqual(result, BaseMessageBackend)


class TestHandler(unittest.TestCase):

    def setUp(self):
        self.message_handler = MessageHandler(
            backend=None,
            incoming_args=[],
            receive_message_delay_ms=1,
            message_prefix="TEST_MESSAGE_PREFIX",
            generator_key="TEST_GENERATOR_KEY",
            message_errors_queue="TEST_MESSAGE_ERRORS_QUEUE",
            message_error_chance_int=1,
            generator_ttl_ms=1,
            generate_message_delay_ms=1,
        )

    def test_process_as_generator(self):
        backend = mock.Mock()
        self.message_handler.backend = backend
        self.message_handler._process_as_generator()

        backend.extend.assert_called_once()
        backend.send.assert_called_once()

    def test_process_as_receiver_receive(self):
        backend = mock.Mock()
        self.message_handler.backend = backend
        self.message_handler._process_as_receiver()

        backend.receive.assert_called_once()
        backend.receive_by_prefix.assert_called_once()

    def test_process_as_receiver_become_generator(self):
        backend = mock.Mock()
        self.message_handler.backend = backend
        backend.receive.return_value = Message("TEST_GENERATOR_KEY", False)
        self.message_handler._process_as_receiver()

        backend.extend.assert_called_once()


if __name__ == '__main__':
    unittest.main()
