import emoji, random, pprint

el = emoji.EMOJI_DATA
el = el.items()

emoji_list = list()

for i in el:
    emoji_list.append(i[0])

pprint.pprint(''.join(random.choice(emoji_list) for _ in range(4)))

while True:
    pprint.pprint(''.join(random.choice(emoji_list) for _ in range(1)))




@app.get("/{short_key}")
async def redirect_to_original(short_key: str):
    if short_key in short_links:
        url = short_links[short_key]['url']
        return RedirectResponse(url)  # 원래 URL로 리디렉션
    else:
        raise HTTPException(status_code=404, detail="Short link not found")