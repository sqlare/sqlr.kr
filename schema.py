from typing import Union
from pydantic import *

class v1_Link(BaseModel):
    url: str
    password: Union[str, None] = None

class Link(BaseModel):
    url: str
    base: bool = False
    invisible: bool = False
