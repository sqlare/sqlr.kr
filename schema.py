from typing import Union
from pydantic import *

class Link(BaseModel):
    url: str
    password: Union[str, None] = None

class Link_Donate(BaseModel):
    url: str

class Link_QRCODE(BaseModel):
    url: str

#key and password
class Password(BaseModel):
    password: str
