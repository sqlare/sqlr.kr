from typing import Union
from pydantic import *

class Link(BaseModel):
    url: str
    password: Union[str, None] = None

class Link_Donate(BaseModel):
    url: str

class Link_QRCODE(BaseModel):
    data: str
    version: Union[int, None] = 1
    error_correction: Union[int, None] = 0
    box_size: Union[int, None] = 10
    border: Union[int, None] = 4
    mask_pattern: Union[int, None] = 0

#key and password
class Password(BaseModel):
    password: Union[str, None] = None
