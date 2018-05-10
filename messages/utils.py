import random
import string


def generate_random_str(length: int=8) -> str:
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
