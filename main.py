from fastapi import *
from fastapi.responses import *
from fastapi.middleware.cors import *
from pydantic import *
from typing import *
from function import *
from schema import *
from variable import *
from redis.commands.json.path import Path
import base64

app = FastAPI(title="sqlr.kr",
    description="sqlr.kr is a URL shortening service.",
    version="redis-a4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

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

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}

@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    key = await anext(generate_emoji_key())
    url_hash = base64.b85encode(body.url.encode())

    if body.password == None:
        hgQs = {"url": url_hash.hex()}
    else:
        salt, password_hash = security(body.password).hash_new_password()
        hgQs = {"url": url_hash.hex(), "salt": salt.hex(), "password_hash": password_hash.hex()}

    db = redis.Redis(connection_pool=pool(EMOJI_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}

@app.post("/tossDonate", response_class=ORJSONResponse)
async def shorten_donate(request: Request, body: Link_Donate):
    if not body.url.startswith("https://toss.me"):
        return ORJSONResponse(content={"error": "이 기능은 무조건 'https://toss.me'로 시작해야해요."}, status_code=400)
    
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.url.encode())
    hgQs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=pool(DONATE_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    return {"short_link": f"{DOMAIN}/d/{key}"}

@app.post("/shorten_qr_code", response_class=FileResponse)
async def generate_qr_code(body: Link_QRCODE):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.url.encode())
    hgQs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), hgQs)
    await db.close()

    img = generate_qr_code_image(f"{DOMAIN}/{key}").read()

    return HTMLResponse(content=f'<img src="data:image/png;base64,{base64.b64encode(img).decode()}" />')

@app.get("/{short_key}")
async def redirect_to_original(request: Request, short_key: str, password: Union[str, None] = None):
    db_c = redis.Redis(connection_pool=pool(KEY_DB))
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()

    if db == None:
        db_c = redis.Redis(connection_pool=pool(EMOJI_DB))
        db = await db_c.json().jsonget(short_key, Path.root_path())
        await db_c.close()

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
    except:
        return HTTP_404(request)

    try:
        salt = bytes.fromhex(db["salt"])
        password_hash = bytes.fromhex(db["password_hash"])
    except:
        return RedirectResponse(url)

    if isinstance(password, str):
        if security(str(password), salt, password_hash).is_correct_password():
            return RedirectResponse(url)
        else:
            return HTTP_401(request)
    else:
        return HTTP_401(request)

@app.get("/d/{short_key}")
async def redirect_to_original(request: Request, short_key: str):
    db_c = redis.Redis(connection_pool=pool(DONATE_DB))
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
    except:
        return HTTP_404(request)

    return RedirectResponse(url)

@app.get("/api/metadata", response_class=ORJSONResponse)
async def metadata(url: str):
    return get_metadata(url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1111)

# 코체 바보
