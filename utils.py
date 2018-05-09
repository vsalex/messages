import random
import string


def generate_random_str(length=8):
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
