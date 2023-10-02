from typing import *
import random
import string
import hashlib
import hmac
import redis.asyncio as redis
import secrets
import emoji

emoji_data = emoji.EMOJI_DATA
emoji_data = emoji_data.items()
emoji_list = list()
for _ in emoji_data:
    emoji_list.append(_[0])

def pool():
    return redis.ConnectionPool(host='localhost', port=6379, db=0)

class security():
    def __init__(self, password: str, salt: bytes = None, password_hash: bytes = None, algorithm: str = 'sha3_256', iterations: int = 100000, dklen: Union[int, None] = None) -> None:
        self.password = password.encode()
        self.salt = salt
        self.password_hash = password_hash
        self.algorithm = algorithm
        self.iterations = iterations
        self.dklen = dklen

    def hash_new_password(self) -> Tuple[bytes, bytes]:
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac(self.algorithm, self.password, salt, self.iterations, self.dklen)
        return salt, password_hash

    def is_correct_password(self) -> bool:
        return hmac.compare_digest(self.password_hash, hashlib.pbkdf2_hmac(self.algorithm, self.password, self.salt, self.iterations, self.dklen))

async def generate_key(length: int = 4) -> AsyncGenerator:
    key = ''.join(random.choice(string.ascii_letters) for _ in range(length))

    try:
        db = redis.Redis(connection_pool=pool())
        await db.json().get(key)
        await db.close()
        length + 1
    except:
        await db.close()
        yield key
        raise StopAsyncIteration


async def generate_emoji_key(length: int = 4) -> AsyncGenerator:
    key = ''.join(random.choice(emoji_list) for _ in range(length))

    try:
        db = redis.Redis(connection_pool=pool())
        await db.json().get(key)
        await db.close()
        length + 1
    except:
        await db.close()
        yield key
        raise StopAsyncIteration

