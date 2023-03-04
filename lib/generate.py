import random
import string


def generate_random_digits_string(count=None):
    if count is None:
        count = random.randint(5, 10)
    result = ""
    for i in range(0, count):
        nr = random.randint(0, 9)
        result = f"{result}{nr}"
    return result


def generate_random_letters_string(count=None):
    if count is None:
        count = random.randint(5, 10)
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(count))
