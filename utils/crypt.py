import random
import string
import hashlib
import rsa
import base64

def random_string(length: int = 64) -> str:
    chars = list(string.ascii_lowercase)
    chars += list([c.upper() for c in chars])
    chars += list(string.digits)
    random_value = "".join(list([random.choice(chars) for i in range(0,length)]))
    return random_value

def hash_string(input: str) -> str:
    input = input.encode()
    return hashlib.sha256(input).hexdigest()

def sign_string(data: str, ) -> bytes:
    with open("priv.pem", "rb") as key_file:
        private_key = key_file.read()
    private_key = rsa.PrivateKey.load_pkcs1(private_key)
    signature = rsa.sign(data.encode(), private_key, "SHA-256")
    signature: bytes = base64.b64encode(signature).decode()
    return signature

def verify_signature(data: str, signature: str) -> bool:
    signature: bytes = base64.b64decode(signature)
    with open("pub.pem", "rb") as key_file:
        public_key = key_file.read()
        print(public_key)
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key)
    valid = rsa.verify(data.encode(), signature, public_key)
    return valid

def get_public_key() -> str:
    with open("pub.pem", "r") as key_file:
        public_key = key_file.read()
    print(public_key)
    return public_key