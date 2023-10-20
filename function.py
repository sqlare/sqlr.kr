import sqlite3
from typing import *
import random, string, secrets, hashlib, hmac, emoji, metadata_parser

class Database:
    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # Create a table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def insert_key(self, key: str, value: str):
        self.cursor.execute("INSERT INTO keys (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def check_key_exists(self, key: str) -> bool:
        self.cursor.execute("SELECT value FROM keys WHERE key = ?", (key,))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()

class Security:
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

emoji_data = emoji.EMOJI_DATA
emoji_data = emoji_data.items()
emoji_list = list()
for _ in emoji_data: emoji_list.append(_[0])

def get_metadata(url: str):
    metadata = metadata_parser.MetadataParser(url, search_head_only=False, requests_timeout=10)
    return metadata.metadata

async def generate_key(url: str, length: int = 4) -> AsyncGenerator:
    db = Database('eng.db')  # Database for English keys
    while True:
        key = ''.join(random.choice(string.ascii_letters) for _ in range(length))

        if not db.check_key_exists(key):
            yield key, url
            db.insert_key(key, url)  # URL을 값으로 설정
        else:
            length += 1

async def generate_emoji_key(url: str, length: int = 4) -> AsyncGenerator:
    db = Database('emoji.db')  # Database for Emoji keys
    while True:
        key = ''.join(random.choice(emoji_list) for _ in range(length))

        if not db.check_key_exists(key):
            yield key, url
            db.insert_key(key, url)  # URL을 값으로 설정
        else:
            length += 1

# 코체 멍청이
