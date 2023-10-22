from typing import *
from variable import *
import random
import string
import hashlib
import hmac
import redis.asyncio as redis
import secrets
import metadata_parser
import qrcode
import io

def pool(db_num: int = 0):
    return redis.ConnectionPool().from_url(f"{DB}/{db_num}")

def HTTP_404(request: object):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

def HTTP_401(request: object):
    return templates.TemplateResponse("401.html", {"request": request}, status_code=401)

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

def get_metadata(url: str):
    metadata = metadata_parser.MetadataParser(url, search_head_only=False, requests_timeout=10)
    return metadata.metadata

async def generate_key(length: int = 4) -> AsyncGenerator:
    __length__ = length
    while True:
        key = ''.join(random.choice(string.ascii_letters) for _ in range(__length__))

        db = redis.Redis(connection_pool=pool())
        db_key = await db.json().get(key)
        await db.close()

        if db_key == None:
            yield key
            break
        else:
            __length__ += 1

async def generate_emoji_key(length: int = 4) -> AsyncGenerator:
    __length__ = length
    while True:
        key = ''.join(random.choice(emoji_list) for _ in range(length))

        db = redis.Redis(connection_pool=pool())
        db_key = await db.json().get(key)
        await db.close()

        if db_key == None:
            yield key
            break
        else:
            __length__ += 1

def generate_qr_code_image(data: str):
    img = qrcode.make(data)
    img_byte_array = io.BytesIO()
    img.save(img_byte_array)
    img_byte_array.seek(0)

    return img_byte_array
