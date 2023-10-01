from typing import Union
from pydantic import *

class Link(BaseModel):
    url: str
    password: Union[str, None] = None

#key and password
class KP(BaseModel):
    key: str
    password: Union[str, None] = None
