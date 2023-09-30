from main import *
from function import *
from schema import *
from redis.commands.json.path import Path

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.post("/shorten", response_class=ORJSONResponse)
async def api_v1_shorten_link(body: v1_Link):
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

@router.get("/{short_key}")
async def redirect_to_original(short_key: str):
    db = redis.Redis(connection_pool=pool())
    url = await db.json().jsonget(short_key, Path.root_path())
    url = str(url).replace("{'url': '", "").replace("}", "")

    return RedirectResponse(url)
