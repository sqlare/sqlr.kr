from typing import *
import random
import string
import hashlib
import hmac
import redis.asyncio as redis
import secrets
import nest_asyncio

nest_asyncio.apply()

def pool():
    return redis.ConnectionPool(host='localhost', port=6379, db=0)

class security():
    def __init__(self, password: str, salt: bytes = None, password_hash: bytes = None, algorithm: str = 'sha3_256') -> None:
        self.password = password.encode()
        self.salt = salt
        self.password_hash = password_hash
        self.algorithm = algorithm

    def hash_new_password(self) -> Tuple[bytes, bytes]:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(self.algorithm, self.password, salt, 100000)
        return salt, password_hash

    def is_correct_password(self) -> bool:
        return hmac.compare_digest(self.password_hash, hashlib.pbkdf2_hmac(self.algorithm, self.password, self.salt, 100000))

async def generate_key(length: int = 4) -> AsyncGenerator:
    while True:
        key = ''.join(random.choice(string.ascii_letters) for _ in range(length))

        try:
            db = redis.Redis(connection_pool=pool())
            await db.json().get(key)
            await db.close()
            length + 1
            yield key
        except:
            await db.close()
            yield key
            break
