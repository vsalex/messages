import unittest

from messages.helpers import IncomingArg
from messages.initializer import get_incoming_args


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


if __name__ == '__main__':
    unittest.main()
