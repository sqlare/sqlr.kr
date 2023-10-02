from fastapi import *
from fastapi.responses import *
from fastapi.templating import *
from fastapi.middleware.cors import *
from pydantic import *
from typing import *
from function import *
from schema import *
from redis.commands.json.path import Path
import base64

app = FastAPI(title="sqlr.kr", description="sqlr.kr 은 링크단축 서비스 입니다.", version="a2.1.0")

origins = [
    "http://sqlr.kr:3000",
    "http://sqlr.kr",
    "https://sqlr.kr",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten", response_class=ORJSONResponse)
async def shorten_link(body: Link):
    key = await anext(generate_key())

    url_hash = base64.b85encode(body.url.encode())

    if body.password == None:
        hgQs = {"url": url_hash.hex()}
    else:
        salt, password_hash = security(body.password).hash_new_password()
        hgQs = {"url": url_hash.hex(), "salt": salt.hex(), "password_hash": password_hash.hex()}

    db = redis.Redis(connection_pool=pool())
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"https://sqlr.kr/{key}"}

@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    key = await anext(generate_emoji_key())
    
    url_hash = base64.b85encode(body.url.encode())

    if body.password == None:
        hgQs = {"url": url_hash.hex()}
    else:
        salt, password_hash = security(body.password).hash_new_password()
        hgQs = {"url": url_hash.hex(), "salt": salt.hex(), "password_hash": password_hash.hex()}

    db = redis.Redis(connection_pool=pool())
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"https://sqlr.kr/{key}"}

@app.get("/{short_key}")
async def redirect_to_original(short_key: str, password: Union[str, None] = None):
    db_c = redis.Redis(connection_pool=pool())
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()
    url = bytes.fromhex(db["url"]).decode("utf-8")
    url = base64.b85decode(url).decode("utf-8")

    try:
        salt = bytes.fromhex(db["salt"])
        password_hash = bytes.fromhex(db["password_hash"])

        if security(password, salt, password_hash).is_correct_password():
            return RedirectResponse(url)

    except:
        raise HTTPException(status_code=401, detail="Password required or incorrect")

@app.get("/api/meta", response_class=ORJSONResponse)
async def metadata(url: str):
    return get_metadata(url)
