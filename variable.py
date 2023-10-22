from fastapi.templating import *
import dotenv
import emoji

templates = Jinja2Templates(directory="templates")

emoji_data = emoji.EMOJI_DATA
emoji_data = emoji_data.items()
emoji_list = list()
for _ in emoji_data:
    emoji_list.append(_[0])

DOMAIN = dotenv.get_key(".env", "DOMAIN")
DB = dotenv.get_key(".env", "DB")
KEY_DB = dotenv.get_key(".env", "KEY_DB")
DONATE_DB = dotenv.get_key(".env", "DONATE_DB")
PEPPER_DB = dotenv.get_key(".env", "PEPPER_DB")
EMOJI_DB = dotenv.get_key(".env", "EMOJI_DB")
