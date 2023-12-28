import random
import string
import hashlib

def random_string(length: int = 64) -> str:
    chars = list(string.ascii_lowercase)
    chars += list([c.upper() for c in chars])
    chars += list(string.digits)
    random_value = "".join(list([random.choice(chars) for i in range(0,length)]))
    return random_value

def hash_string(input: str) -> str:
    input = input.encode()
    return hashlib.sha256(input).hexdigest()
