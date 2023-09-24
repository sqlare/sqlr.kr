from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import random
import string

app = FastAPI()

# 단축 링크를 저장할 딕셔너리
short_links = {}

class Link(BaseModel):
    url: str

# 단축 링크 생성
def generate_short_link():
    letters = string.ascii_letters
    while True:
        short_key = ''.join(random.choice(letters) for _ in range(4))
        if short_key not in short_links:
            return short_key

@app.post("/shorten/")
async def shorten_link(link: Link):
    short_key = generate_short_link()
    short_links[short_key] = link.url
    return {"short_link": f"https://z.64bit.kr/{short_key}"}

@app.get("/{short_key}")
async def redirect_to_original(short_key: str):
    if short_key in short_links:
        url = short_links[short_key]
        return RedirectResponse(url)
    else:
        raise HTTPException(status_code=404, detail="Short link not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1111)
