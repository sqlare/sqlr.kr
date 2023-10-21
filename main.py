from fastapi import *
from fastapi.responses import *
from fastapi.templating import *
from fastapi.middleware.cors import *
from pydantic import *
from base64 import *
from typing import *
import emoji
import metadata_parser
import sqlite3
from sqlite3 import *
from function import Database, Security, get_metadata, generate_key, generate_emoji_key

app = FastAPI(
    title="sqlr.kr",
    description="sqlr.kr is a URL shortening service.",
    version="a3.0.0",
)

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

class Link(BaseModel):
    url: str

# Create the 'keys' table if it doesn't exist
conn = sqlite3.connect('link.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        value TEXT
    )
''')
conn.commit()
conn.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten", response_class=ORJSONResponse)
async def shorten_link(body: Link):
    async for key, url in generate_key(body.url):
        conn = sqlite3.connect('link.db')
        c = conn.cursor()
        c.execute("INSERT INTO keys (key, value) VALUES (?, ?)", (key, url))
        conn.commit()
        conn.close()

        return {"short_link": f"https://sqlr.kr/{key}"}

@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    key = next(generate_emoji_key(body.url))
    conn = connect('link.db')
    c = conn.cursor()
    c.execute("INSERT INTO keys (key, value) VALUES (?, ?)", (key, body.url))
    conn.commit()
    conn.close()

    return {"short_link": f"https://sqlr.kr/{key}"}
    
@app.get("/{short_key}")
async def redirect_to_original(short_key: str):
    conn = connect('link.db')
    c = conn.cursor()
    c.execute("SELECT value FROM keys WHERE key = ?", (short_key,))
    result = c.fetchone()
    conn.close()

    if result:
        url = result[0]
        return RedirectResponse(url)
    else:
        # 404 에러 페이지 표시
        return templates.TemplateResponse("404.html", status_code=404)

def get_metadata_from_original(url: str):
    metadata = get_metadata(url)
    return metadata

@app.get("/api/metadata/{short_key}", response_class=ORJSONResponse)
async def metadata_from_short_link(short_key: str):
    conn = connect('link.db')
    c = conn.cursor()
    c.execute("SELECT value FROM keys WHERE key = ?", (short_key,))
    result = c.fetchone()
    conn.close()

    if result:
        url = result[0]
        metadata = get_metadata_from_original(url)
        return metadata
    else:
        raise HTTPException(status_code=404, detail="Shortened link not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1111)
# 코체 멍청이
