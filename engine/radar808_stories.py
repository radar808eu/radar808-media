"""RADAR 808 — Instagram story frames (1080x1920, safe zones top 250 / bottom 340). No stickers.
Usage: import asyncio, radar808_stories as S; asyncio.run(S.render(stories, "out_stories"))
Types:
  lineup(label, kicker, items=[(time, mkt, color, show, subject)], cta)  -> "Today on 808", morning
  newpost(label, time, img=<path to the IG cover PNG/JPG>, title, cta)   -> published with each post
  vote(label, kicker, question, a_k, a, b_k, b, cta)                      -> "vote 1 or 2 in the comments"
Every story: slug, type, bg (VOLT PINK BLUE ORANGE INK).
"""
import asyncio, pathlib
from playwright.async_api import async_playwright
import radar808_engine as R
from radar808_engine import VOLT, PINK, BLUE, ORANGE, INK, WHITE, GREY, fg_for, mascot, deco, CSS

W, H, PT, PB, PX = 1080, 1920, 250, 340, 70

def top(fg, label):
    inv_bg, inv_fg = (WHITE, INK) if fg == WHITE else (INK, WHITE)
    return f'<div class="row" style="justify-content:space-between"><div class="logo" style="color:{fg}">RADAR<br>808</div><div class="tag" style="background:{inv_bg};color:{inv_fg}"><span class="dot"></span>{label}</div></div>'

def bottom(fg):
    c = GREY if fg == WHITE else INK
    return f'<div class="row mono b" style="justify-content:space-between;font-size:22px;letter-spacing:3px;color:{c};border-top:3px solid {c};padding-top:16px"><div>REC ▶ STORY</div><div>@RADAR808.EU</div></div>'

def st_lineup(d):
    fg = fg_for(d["bg"])
    line = "rgba(255,255,255,.25)" if fg == WHITE else "rgba(11,11,11,.3)"
    rows = "".join(f'''<div class="row" style="gap:22px;padding:20px 0;border-bottom:2px solid {line}">
<div class="ab" style="font-size:46px;width:150px">{t}</div><div class="tag" style="background:{c};color:{INK};font-size:18px;flex:none">{m}</div>
<div class="col"><div class="ab" style="font-size:34px;line-height:1">{s}</div><div class="mono b" style="font-size:19px;opacity:.8">{x}</div></div></div>''' for t, m, c, s, x in d["items"])
    return d["bg"], fg, f'''<div class="mid" style="gap:28px">
<div class="mono b" style="font-size:26px;letter-spacing:4px">{d["kicker"]}</div>
<div class="ab" style="font-size:150px;line-height:.82;letter-spacing:-6px">TODAY<br>ON 808</div>
<div class="col">{rows}</div>
<div class="row" style="justify-content:space-between;align-items:center"><div style="font-size:34px;font-weight:800;max-width:600px">{d["cta"]}</div>{mascot(200, WHITE if fg==WHITE else INK, INK if fg==WHITE else WHITE, PINK, "shades")}</div>
</div>'''

def st_newpost(d):
    fg = fg_for(d["bg"])
    img = pathlib.Path(d["img"]).resolve().as_uri()
    sh = VOLT if d["bg"] != VOLT else INK
    return d["bg"], fg, f'''<div class="mid" style="gap:30px;align-items:center">
<div class="row" style="gap:16px;align-self:flex-start"><div class="tag" style="background:{PINK};color:{INK};font-size:24px"><span class="dot" style="background:{INK}"></span>NEW POST</div>
<div class="mono b" style="font-size:22px;letter-spacing:3px">{d["time"]}</div></div>
<div style="position:relative;transform:rotate(-2deg);border:10px solid {WHITE if fg==WHITE else INK};box-shadow:18px 18px 0 {sh}">
  <img src="{img}" style="display:block;width:640px;height:800px;object-fit:cover"></div>
<div class="ab" style="font-size:66px;line-height:.95;letter-spacing:-2px;text-align:center;margin-top:20px">{d["title"]}</div>
<div class="row" style="gap:18px;align-items:center"><div class="mono b" style="font-size:26px;letter-spacing:3px">{d["cta"]}</div>{mascot(120, WHITE if fg==WHITE else INK, INK if fg==WHITE else WHITE, PINK, "")}</div>
</div>'''

def st_vote(d):
    fg = fg_for(d["bg"])
    return d["bg"], fg, f'''{deco("dots", fg)}<div class="mid" style="gap:34px">
<div class="tag" style="background:{INK if fg==INK else WHITE};color:{WHITE if fg==INK else INK};align-self:flex-start;font-size:22px">{d["kicker"]}</div>
<div class="ab" style="font-size:96px;line-height:.9;letter-spacing:-3px">{d["question"]}</div>
<div class="col" style="gap:18px">
  <div class="row" style="gap:24px;background:{WHITE};color:{INK};padding:26px"><div class="ab" style="font-size:90px;line-height:1">1</div><div class="col"><div class="mono b" style="font-size:18px;letter-spacing:2px">{d["a_k"]}</div><div class="ab" style="font-size:52px;line-height:1">{d["a"]}</div></div></div>
  <div class="row" style="gap:24px;background:{INK};color:{WHITE};padding:26px"><div class="ab" style="font-size:90px;line-height:1;color:{VOLT}">2</div><div class="col"><div class="mono b" style="font-size:18px;letter-spacing:2px">{d["b_k"]}</div><div class="ab" style="font-size:52px;line-height:1">{d["b"]}</div></div></div>
</div>
<div class="row" style="justify-content:space-between;align-items:center"><div class="ab" style="font-size:48px;line-height:1.05;max-width:640px">{d["cta"]}</div>{mascot(200, INK if fg==INK else WHITE, WHITE if fg==INK else INK, BLUE, "shades")}</div>
</div>'''

TYPES = dict(lineup=st_lineup, newpost=st_newpost, vote=st_vote)

def html(stories):
    out = []
    for d in stories:
        bg, fg, body = TYPES[d["type"]](d)
        out.append(f'<div class="slide" style="width:{W}px;height:{H}px;padding:{PT}px {PX}px {PB}px;background:{bg};color:{fg}">{top(fg, d["label"])}{body}{bottom(fg)}</div>')
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(out)}</body></html>"

async def render(stories, outdir):
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    f = R.ROOT / "_stories.html"; f.write_text(html(stories))
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": W, "height": H}); await pg.goto(f.as_uri())
        await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(200)
        over = await pg.evaluate("[...document.querySelectorAll('.slide')].map((s,i)=>{const m=s.querySelector('.mid');return m && m.scrollHeight>m.clientHeight+2 ? i+1 : 0}).filter(Boolean)")
        if over: print("OVERFLOW stories", over)
        for i, el in enumerate(await pg.query_selector_all(".slide"), 1):
            await el.screenshot(path=str(outdir / f"radar808_story_{stories[i-1]['slug']}.png"))
        await b.close()
