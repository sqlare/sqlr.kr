from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import string

app = FastAPI()

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

# JSON 파일 이름
json_filename = "short_links.json"

# JSON 파일에서 데이터 로드
def load_short_links():
    try:
        with open(json_filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# JSON 파일에 데이터 저장
def save_short_links(links):
    with open(json_filename, "w") as file:
        json.dump(links, file)

# 단축 링크를 저장할 딕셔너리
short_links = load_short_links()

class Link(BaseModel):
    url: str

# 단축 링크 생성
def generate_short_link():
    letters = string.ascii_letters
    while True:
        short_key = ''.join(random.choice(letters) for _ in range(4))
        if short_key not in short_links:
            return short_key

@app.get("/list", response_class=HTMLResponse)
async def list(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "short_links": short_links})

@app.get("/{short_key}")
async def redirect_to_original(short_key: str):
    if short_key in short_links:
        url = short_links[short_key]
        return RedirectResponse(url)  # 원래 URL로 리디렉션
    else:
        raise HTTPException(status_code=404, detail="Short link not found")

# 단축 링크 생성 API
@app.post("/shorten")
async def shorten_link(link: Link):
    original_url = link.url

    # 이미 단축된 링크인지 확인
    for key, value in short_links.items():
        if value == original_url:
            return {"short_link": f"/{key}"}

    # 단축 링크 생성
    short_key = generate_short_link()
    short_links[short_key] = original_url
    save_short_links(short_links)
    return {"short_link": f"/{short_key}"}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1111)

# 코체 바보
