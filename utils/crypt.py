import random
import string

def random_string(length: int = 64):
    chars = list(string.ascii_lowercase)
    chars += list([c.upper() for c in chars])
    chars += list(string.digits)
    random_value = "".join(list([random.choice(chars) for i in range(0,length)]))
    return random_value
