"""RADAR 808 — slide engine v2 (Instagram 4:5 + TikTok 9:16). Usage:
    import asyncio, radar808_engine as R
    asyncio.run(R.render(posts, "out"))
A post = dict(slug, show, mkt, date "gg.mm.aa", wk, np=(title, artist), batacc=<accent>, batx=<"", "waves","megaphone","console">, slides=[...]).
Slide types and fields (bg = one of VOLT PINK BLUE ORANGE INK WHITE; deco = rings|grid|scan|dots|wave|word + word=):
  cover(kicker,title,tag,name,hook,tagbg?,tsize?,nsize?)        poster(strip,tag,stack=[(text,px)],hook,acc?)  -> THE RADAR cover
  tv(screen,chan,title,song,artist,hook)  -> VIRAL CHECK cover    cassette(title,date,kind,release,artist,hook) -> RELEASE FRIDAY cover
  paper(issue,lead_m,lead,lead_t,subs=[(mkt label,color,headline,text)]x4) -> THE WEEK cover (bg is white)
  beatcover(tag,name,prodfor,hook) -> BEHIND THE BEAT cover        facts(tag,headline,rows=[(k,v)])
  list(headline,rows=[(a,b,c)],tag?)   big(tag,big,mono,statement,para,np=True?)   points(tag,points,cta,cta2,next) -> last slide
  stats(headline,sub,hero_k,hero_v,boxes=[(k,v,px)],take) -> MARKET CHECK
  bars(tag,headline,axis,unit,rows=[(title,artist,value)])   -> single-series ranking chart (real data only)
  climb(tag,headline,axis,weeks,pos(None=not charted),floor,ticks,note) -> chart run over weeks (1 at top)
  heat(tag,headline,cols,rows=[(title,artist,[pos|None...])],legend) -> EURO 10 cross-border grid
last slide pose: post['pose']. mascot(w, body, eyes, accent, pose) poses: magnifier(Radar) waves(Viral) console(Beat) clipboard(Market) megaphone(Friday) trophy(Euro10) paper(Week) shades(special).
"""
import pathlib, asyncio
from playwright.async_api import async_playwright

import os
ROOT = pathlib.Path(os.environ.get("RADAR_DIR", pathlib.Path(__file__).parent))
FONTS = ROOT  # contains the 3 woff2 files (from: npm pack @fontsource/archivo-black @fontsource/space-mono, then tar xzf)
def _font(name):
    hits = list(FONTS.rglob(name))
    return hits[0] if hits else FONTS / name
AB = _font("archivo-black-latin-400-normal.woff2")
SM4 = _font("space-mono-latin-400-normal.woff2")
SM7 = _font("space-mono-latin-700-normal.woff2")
VOLT, PINK, BLUE, ORANGE, INK, WHITE, GREY = "#E8FF2B", "#FF3D8B", "#3D5AFE", "#FF6B1A", "#0B0B0B", "#FFFFFF", "#BDBDBD"

FORMATS = {
    "IG": dict(w=1080, h=1350, pt=60, pb=60, pl=60, pr=60),
    "TT": dict(w=1080, h=1920, pt=150, pb=380, pl=60, pr=130),  # TikTok UI safe zones
}

def fg_for(bg):
    return WHITE if bg in (INK, BLUE) else INK

def bat(w, c=INK, e=WHITE, a=PINK, extra=""):
    x = ""
    if extra == "waves":
        x = f'<path d="M30 70 Q 14 100 30 130" stroke="{a}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M16 60 Q -6 100 16 140" stroke="{a}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M170 70 Q 186 100 170 130" stroke="{a}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M184 60 Q 206 100 184 140" stroke="{a}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    if extra == "megaphone":
        x = f'<path d="M150 128 L 196 104 L 196 168 L 150 146 Z" fill="{a}"/><rect x="138" y="128" width="14" height="18" fill="{a}"/>'
    console = ""
    if extra == "console":
        console = f'<path d="M30 150 L 170 150 L 194 198 L 6 198 Z" fill="#2A2A2A" stroke="{e if c != INK else WHITE}" stroke-width="3"/><circle cx="42" cy="170" r="6" fill="{ORANGE}"/><circle cx="62" cy="170" r="6" fill="{VOLT}"/><circle cx="82" cy="170" r="6" fill="{PINK}"/><rect x="108" y="162" width="4" height="28" fill="{GREY}"/><rect x="128" y="162" width="4" height="28" fill="{GREY}"/><rect x="148" y="162" width="4" height="28" fill="{GREY}"/><rect x="103" y="172" width="14" height="7" fill="{WHITE}"/><rect x="123" y="180" width="14" height="7" fill="{WHITE}"/><rect x="143" y="166" width="14" height="7" fill="{WHITE}"/>'
    return f"""<svg width="{w}" height="{w}" viewBox="0 0 200 200" aria-hidden="true">
<path d="M60 112 C 32 92, 12 100, 4 122 C 20 118, 28 128, 30 142 C 40 132, 52 134, 62 142 Z" fill="{c}"/>
<path d="M140 112 C 168 92, 188 100, 196 122 C 180 118, 172 128, 170 142 C 160 132, 148 134, 138 142 Z" fill="{c}"/>
<polygon points="68,76 76,30 94,64" fill="{c}"/><polygon points="132,76 124,30 106,64" fill="{c}"/>
<circle cx="100" cy="106" r="44" fill="{c}"/>
<path d="M56 104 A 44 48 0 0 1 144 104" stroke="{a}" stroke-width="9" fill="none"/>
<rect x="47" y="94" width="17" height="28" rx="6" fill="{a}"/><rect x="136" y="94" width="17" height="28" rx="6" fill="{a}"/>
<circle cx="86" cy="100" r="10" fill="{e}"/><circle cx="114" cy="100" r="10" fill="{e}"/>
<circle cx="88" cy="102" r="4.5" fill="{c}"/><circle cx="116" cy="102" r="4.5" fill="{c}"/>
<path d="M91 120 Q 100 127 109 120" stroke="{e}" stroke-width="3" fill="none" stroke-linecap="round"/>{x}{console}</svg>"""

# ---------- decorations ----------
def deco(kind, fg, word=""):
    a = "rgba(11,11,11,0.14)" if fg == INK else "rgba(255,255,255,0.13)"
    if kind == "rings":
        return "".join(f'<div style="position:absolute;right:{r}px;bottom:{b}px;width:{s}px;height:{s}px;border:5px solid {a};border-radius:50%"></div>' for r, b, s in [(-380, -200, 1000), (-180, 0, 600), (20, 200, 200)])
    if kind == "grid":
        return f'<div style="position:absolute;inset:0;background-image:linear-gradient({a} 2px,transparent 2px),linear-gradient(90deg,{a} 2px,transparent 2px);background-size:90px 90px"></div>'
    if kind == "scan":
        return f'<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,{a} 0 2px,transparent 2px 9px)"></div>'
    if kind == "dots":
        return f'<div style="position:absolute;inset:0;background-image:radial-gradient({a} 3px,transparent 3.5px);background-size:28px 28px"></div>'
    if kind == "wave":
        pts = " ".join(f"{x},{300 + (120 if x % 80 == 40 else -120) * (0.4 + 0.6 * ((x * 7) % 11) / 11)}" for x in range(0, 1100, 40))
        return f'<svg style="position:absolute;left:0;bottom:22%" width="1080" height="600" viewBox="0 0 1080 600" aria-hidden="true"><polyline points="{pts}" fill="none" stroke="{a}" stroke-width="6"/></svg>'
    if kind == "word":
        stroke = "rgba(11,11,11,0.30)" if fg == INK else "rgba(255,255,255,0.32)"
        return f'<div class="ab" aria-hidden="true" style="position:absolute;right:-40px;top:42%;font-size:560px;line-height:.8;letter-spacing:-26px;color:transparent;-webkit-text-stroke:5px {stroke}">{word}</div>'
    return ""

# ---------- fixed elements ----------
def header(fg, show, mkt, n, tot):
    inv_bg, inv_fg = (WHITE, INK) if fg == WHITE else (INK, WHITE)
    return f"""<div class="row" style="justify-content:space-between;position:relative">
  <div class="logo" style="color:{fg}">RADAR<br>808</div>
  <div class="row" style="gap:12px">
    <div class="tag" style="background:{inv_bg};color:{inv_fg}"><span class="dot"></span>{show} · {mkt}</div>
    <div class="tag" style="border:2px solid {fg};color:{fg}">{n:02d} / {tot:02d}</div>
  </div></div>"""

def footer(fg, date, wk, last=False):
    c = GREY if fg == WHITE else INK
    right = "FOLLOW @RADAR808.EU" if last else "SWIPE ▶▶"
    return f"""<div class="row mono b" style="position:relative;justify-content:space-between;font-size:20px;letter-spacing:2px;color:{c};border-top:3px solid {c};padding-top:18px">
  <div>REC ▶ WK{wk} · {date}</div><div>{right}</div></div>"""

def nowplaying(fg, title, artist):
    bg, tx = (WHITE, INK) if fg == WHITE else (INK, WHITE)
    return f"""<div class="row np" style="position:relative;background:{bg};color:{tx}">
  <div class="tag" style="background:{tx};color:{bg};flex:none"><span class="dot"></span>NOW PLAYING</div>
  <div class="ab" style="font-size:26px;flex:none">{title}</div><div class="mono" style="font-size:18px">{artist}</div></div>"""

def lower(tag, name, tagbg=VOLT, size=104):
    return f"""<div class="col" style="align-items:flex-start">
    <div class="tag" style="background:{tagbg};color:{INK};font-size:22px;padding:8px 16px">{tag}</div>
    <div class="ab" style="background:{WHITE};color:{INK};font-size:{size}px;line-height:1;padding:10px 24px 16px;letter-spacing:-3px">{name}</div></div>"""

# ---------- slide types ----------
def s_cover(p, d):
    fg = fg_for(d["bg"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:26px">
  <div class="mono b" style="font-size:26px;letter-spacing:4px">{d['kicker']}</div>
  <div class="ab" style="font-size:{d.get('tsize',200)}px;line-height:.82;letter-spacing:-8px">{d['title']}</div>
  {lower(d['tag'], d['name'], d.get('tagbg', VOLT), d.get('nsize', 104)) if d.get('name') else ''}
  <div style="font-size:42px;font-weight:800;line-height:1.15;max-width:880px">{d['hook']}</div>
</div>"""

def s_facts(p, d):
    fg = fg_for(d["bg"])
    kc = VOLT if fg == WHITE else INK
    rows = "".join(f'<div class="fact" style="border-color:{"#3A3A3A" if fg==WHITE else "rgba(11,11,11,.3)"}"><div class="k" style="color:{kc}">{k}</div><div class="v">{v}</div></div>' for k, v in d["rows"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:28px">
  <div class="tag" style="background:{PINK};color:{INK};align-self:flex-start;font-size:22px">{d['tag']}</div>
  <div class="ab" style="font-size:{d.get('hsize',120)}px;line-height:.88;letter-spacing:-4px">{d['headline']}</div>
  <div class="col">{rows}</div>
</div>"""

def s_list(p, d):
    fg = fg_for(d["bg"])
    line = "rgba(11,11,11,.35)" if fg == INK else "rgba(255,255,255,.3)"
    rows = "".join(f"""<div class="row" style="gap:26px;align-items:flex-start;padding:18px 0;border-bottom:2px solid {line}">
<div class="mono b" style="width:{d.get('kw',150)}px;font-size:24px;flex:none;padding-top:6px">{a}</div>
<div class="col" style="gap:6px"><div class="ab" style="font-size:{d.get('isize',38)}px;line-height:1.05">{b}</div><div style="font-size:23px;font-weight:600;line-height:1.3">{c}</div></div></div>""" for a, b, c in d["rows"])
    tag = f'<div class="tag" style="background:{INK if fg==INK else WHITE};color:{WHITE if fg==INK else INK};align-self:flex-start;font-size:22px">{d["tag"]}</div>' if d.get("tag") else ""
    return d["bg"], fg, f"""
<div class="mid" style="gap:24px">
  {tag}
  <div class="ab" style="font-size:{d.get('hsize',140)}px;line-height:.82;letter-spacing:-6px">{d['headline']}</div>
  <div class="col">{rows}</div>
</div>"""

def s_big(p, d):
    fg = fg_for(d["bg"])
    tb, tf = (INK, WHITE) if fg == INK else (WHITE, INK)
    return d["bg"], fg, f"""
<div class="mid" style="gap:26px">
  <div class="tag" style="background:{tb};color:{tf};align-self:flex-start;font-size:22px">{d['tag']}</div>
  <div class="ab" style="font-size:{d.get('bsize',200)}px;line-height:.84;letter-spacing:-8px">{d['big']}</div>
  <div class="mono b" style="font-size:28px">{d['mono']}</div>
  <div style="font-size:50px;font-weight:800;line-height:1.16;max-width:940px">{d['statement']}</div>
  <div style="font-size:34px;font-weight:600;line-height:1.35;max-width:930px">{d.get('para','')}</div>
</div>
{nowplaying(fg, *p['np']) if d.get('np') else ''}"""

def s_points(p, d):
    fg = fg_for(d["bg"])
    acc = VOLT if fg == WHITE else INK
    pts = "".join(f'<div class="row" style="gap:24px;align-items:flex-start"><div class="ab" style="font-size:78px;color:{acc};line-height:1">0{i}</div><div style="font-size:{d.get("psize",44)}px;font-weight:700;line-height:1.2">{t}</div></div>' for i, t in enumerate(d["points"], 1))
    tb = VOLT if fg == WHITE else INK
    tf = INK if fg == WHITE else WHITE
    return d["bg"], fg, f"""
<div class="mid" style="gap:36px">
  <div class="tag" style="background:{tb};color:{tf};align-self:flex-start;font-size:22px">{d['tag']}</div>
  <div class="col" style="gap:34px">{pts}</div>
</div>
<div class="row" style="position:relative;justify-content:space-between;align-items:flex-end;margin-bottom:22px">
  <div class="col" style="gap:12px">
    <div class="ab" style="font-size:56px;line-height:1">{d['cta']}</div>
    <div style="font-size:28px;font-weight:600">{d['cta2']}</div>
    <div class="mono b" style="font-size:22px;color:{acc};letter-spacing:2px;margin-top:6px">{d['next']}</div>
  </div>
  {mascot(230, WHITE if fg==WHITE else INK, INK if fg==WHITE else WHITE, p.get('batacc', PINK), p.get('pose', p.get('batx','')))}
</div>
{nowplaying(fg, *p['np'])}"""

def s_stats(p, d):
    fg = fg_for(d["bg"])
    bd = INK if fg == INK else WHITE
    boxes = "".join(f'<div style="border:3px solid {bd};padding:18px;display:flex;flex-direction:column;gap:10px"><div class="mono b" style="font-size:15px;letter-spacing:2px">{k}</div><div class="ab" style="font-size:{s}px;line-height:1.05">{v}</div></div>' for k, v, s in d["boxes"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:26px">
  <div class="ab" style="font-size:{d.get('hsize',150)}px;line-height:.82;letter-spacing:-6px">{d['headline']}</div>
  <div class="ab" style="font-size:66px;line-height:1;color:{WHITE if fg==INK else VOLT};-webkit-text-stroke:{'3px '+INK if fg==INK else '0'}">{d.get('sub','')}</div>
  <div style="background:{INK if fg==INK else WHITE};color:{WHITE if fg==INK else INK};padding:22px 26px;display:flex;flex-direction:column;gap:8px">
    <div class="mono b" style="font-size:17px;letter-spacing:3px;color:{d['bg'] if d['bg']!=INK else VOLT}">{d['hero_k']}</div>
    <div class="ab" style="font-size:40px;line-height:1.05">{d['hero_v']}</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat({len(d['boxes'])},minmax(0,1fr));gap:14px">{boxes}</div>
  <div class="col" style="gap:10px">
    <div class="tag" style="background:{INK if fg==INK else WHITE};color:{WHITE if fg==INK else INK};align-self:flex-start;font-size:17px">THE TAKE</div>
    <div style="font-size:30px;font-weight:700;line-height:1.3">{d['take']}</div>
  </div>
</div>"""

def s_beatcover(p, d):
    fg = fg_for(d["bg"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:24px">
  <div class="row" style="justify-content:space-between;align-items:center;gap:20px">
    <div class="ab" style="font-size:128px;line-height:.84;letter-spacing:-5px;color:{d.get('tcol', ORANGE)}">BEHIND<br>THE<br>BEAT</div>
    {bat(340, WHITE, INK, ORANGE, 'console')}
  </div>
  <div class="col" style="align-items:flex-start">
    <div class="tag" style="background:{ORANGE};color:{INK};font-size:22px;padding:8px 16px">{d['tag']}</div>
    <div class="ab" style="background:{WHITE};color:{INK};font-size:100px;line-height:1;padding:10px 24px 16px;letter-spacing:-3px">{d['name']}</div>
    <div class="mono" style="border:2px solid {WHITE};border-top:none;padding:10px 22px;font-size:20px">{d['prodfor']}</div>
  </div>
  <div style="font-size:40px;font-weight:800;line-height:1.18;max-width:900px">{d['hook']}</div>
</div>"""

TYPES = dict(cover=s_cover, facts=s_facts, list=s_list, big=s_big, points=s_points, stats=s_stats, beatcover=s_beatcover)

# ---------- mascot poses (prop drawn over the base bat, same 200x200 box) ----------
def prop(kind, a):
    if kind == "magnifier":
        return f'<circle cx="160" cy="150" r="24" fill="rgba(255,255,255,.35)" stroke="{a}" stroke-width="8"/><line x1="177" y1="167" x2="196" y2="194" stroke="{a}" stroke-width="10" stroke-linecap="round"/>'
    if kind == "trophy":
        return f'<path d="M140 132 L 188 132 L 182 166 Q 164 178 146 166 Z" fill="{a}"/><rect x="158" y="172" width="12" height="14" fill="{a}"/><rect x="146" y="184" width="36" height="10" fill="{a}"/><path d="M140 138 Q 126 140 134 156" stroke="{a}" stroke-width="5" fill="none"/><path d="M188 138 Q 202 140 194 156" stroke="{a}" stroke-width="5" fill="none"/>'
    if kind == "paper":
        lines = "".join(f'<rect x="{x}" y="{y}" width="40" height="5" fill="#9E9E9E"/>' for x in (54, 104) for y in (172, 182, 192))
        return f'<rect x="44" y="146" width="112" height="54" fill="{WHITE}" stroke="{INK}" stroke-width="3"/><rect x="54" y="154" width="92" height="10" fill="{a}"/>{lines}'
    if kind == "shades":
        return f'<rect x="72" y="90" width="26" height="18" rx="4" fill="{INK}" stroke="{a}" stroke-width="3"/><rect x="102" y="90" width="26" height="18" rx="4" fill="{INK}" stroke="{a}" stroke-width="3"/><rect x="96" y="96" width="8" height="4" fill="{a}"/>'
    if kind == "clipboard":
        return f'<rect x="138" y="124" width="54" height="72" rx="4" fill="{WHITE}" stroke="{INK}" stroke-width="3"/><rect x="154" y="118" width="22" height="10" fill="{a}"/><rect x="148" y="170" width="8" height="18" fill="{a}"/><rect x="161" y="156" width="8" height="32" fill="{a}"/><rect x="174" y="142" width="8" height="46" fill="{a}"/>'
    return ""

def mascot(w, c, e, a, pose):
    base_extra = {"waves": "waves", "megaphone": "megaphone", "console": "console"}.get(pose, "")
    svg = bat(w, c, e, a, base_extra)
    return svg.replace("</svg>", prop(pose, a) + "</svg>")

# ---------- new layouts ----------
def s_poster(p, d):  # THE RADAR: name as a poster, vertical channel strip
    fg = fg_for(d["bg"])
    lines = "".join(f'<div class="ab" style="font-size:{s}px;line-height:.8;letter-spacing:-{s//22}px">{t}</div>' for t, s in d["stack"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:30px;padding-left:96px">
  <div class="ab" style="position:absolute;left:0;top:50%;transform:translate(-50%,-50%) rotate(-90deg) translateY(36px);white-space:nowrap;font-size:30px;letter-spacing:6px;background:{INK if fg==INK else WHITE};color:{d['bg']};padding:10px 26px">{d['strip']}</div>
  <div class="tag" style="background:{INK if fg==INK else WHITE};color:{WHITE if fg==INK else INK};align-self:flex-start;font-size:22px">{d['tag']}</div>
  <div class="col">{lines}</div>
  <div class="row" style="justify-content:space-between;align-items:flex-end;gap:20px">
    <div style="font-size:40px;font-weight:800;line-height:1.15;max-width:600px">{d['hook']}</div>
    {mascot(260, INK if fg==INK else WHITE, WHITE if fg==INK else INK, d.get('acc', PINK), 'magnifier')}
  </div>
</div>"""

def s_tv(p, d):  # VIRAL CHECK: content inside a TV screen
    fg = fg_for(d["bg"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:30px">
  <div style="position:relative;border:16px solid {GREY};border-radius:56px;background:{d['screen']};padding:44px 44px 50px;overflow:hidden;box-shadow:inset 0 0 0 6px {INK}">
    <div style="position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 3px,transparent 3px 8px)"></div>
    <div class="row" style="position:relative;justify-content:space-between">
      <div class="tag" style="background:{INK};color:{WHITE}"><span class="dot"></span>LIVE · CH 808</div>
      <div class="mono b" style="font-size:22px;letter-spacing:3px;color:{WHITE}">{d['chan']}</div>
    </div>
    <div class="ab" style="position:relative;font-size:170px;line-height:.82;letter-spacing:-7px;color:{WHITE};margin-top:34px">{d['title']}</div>
    <div class="ab" style="position:relative;display:inline-block;background:{VOLT};color:{INK};font-size:62px;line-height:1;padding:10px 20px 14px;margin-top:30px;letter-spacing:-2px">{d['song']}</div>
    <div class="mono b" style="position:relative;font-size:22px;color:{WHITE};margin-top:14px;letter-spacing:2px">{d['artist']}</div>
  </div>
  <div class="row" style="justify-content:space-between;align-items:center;gap:20px">
    <div style="font-size:40px;font-weight:800;line-height:1.15;max-width:640px">{d['hook']}</div>
    {mascot(220, WHITE if fg==WHITE else INK, INK if fg==WHITE else WHITE, BLUE, 'waves')}
  </div>
</div>"""

def s_cassette(p, d):  # RELEASE FRIDAY: release on a cassette label
    fg = fg_for(d["bg"])
    return d["bg"], fg, f"""
<div class="mid" style="gap:30px">
  <div class="ab" style="font-size:150px;line-height:.82;letter-spacing:-6px">{d['title']}</div>
  <div style="position:relative;background:{INK};border-radius:34px;padding:34px 40px 40px">
    <div style="background:{WHITE};border-radius:12px;padding:22px 26px">
      <div class="row" style="justify-content:space-between"><div class="mono b" style="font-size:20px;letter-spacing:3px">SIDE A · {d['date']}</div><div class="mono b" style="font-size:20px;letter-spacing:3px">{d['kind']}</div></div>
      <div class="ab" style="font-size:96px;line-height:.9;letter-spacing:-3px;margin-top:12px;color:{INK}">{d['release']}</div>
      <div class="mono b" style="font-size:24px;margin-top:8px;color:{INK}">{d['artist']}</div>
      <div class="row" style="justify-content:center;gap:120px;margin-top:22px;background:{d['bg']};border-radius:60px;padding:16px">
        <div style="width:70px;height:70px;border-radius:50%;background:{INK};border:10px solid {WHITE}"></div>
        <div style="width:70px;height:70px;border-radius:50%;background:{INK};border:10px solid {WHITE}"></div>
      </div>
    </div>
  </div>
  <div class="row" style="justify-content:space-between;align-items:center;gap:20px">
    <div style="font-size:38px;font-weight:800;line-height:1.15;max-width:650px">{d['hook']}</div>
    {mascot(210, INK, WHITE, VOLT, 'megaphone')}
  </div>
</div>"""

def s_bars(p, d):  # MARKET CHECK: single-series horizontal bars, direct labels
    fg = fg_for(d["bg"])
    mx = max(v for _, _, v in d["rows"])
    track = "rgba(255,255,255,.10)" if fg == WHITE else "rgba(11,11,11,.10)"
    rows = ""
    for i, (title, artist, v) in enumerate(d["rows"], 1):
        pct = v / mx * 100
        col = VOLT if i == 1 else (WHITE if fg == WHITE else INK)
        rows += f"""<div class="col" style="gap:10px">
  <div class="row" style="justify-content:space-between;align-items:baseline;gap:16px">
    <div class="row" style="gap:18px;align-items:baseline"><div class="ab" style="font-size:44px;width:70px">{i:02d}</div>
      <div class="col"><div class="ab" style="font-size:34px;line-height:1">{title}</div><div class="mono" style="font-size:18px;color:{GREY if fg==WHITE else INK}">{artist}</div></div></div>
    <div class="mono b" style="font-size:24px">{v}{d['unit']}</div></div>
  <div style="height:22px;background:{track};border-radius:0 6px 6px 0"><div style="height:100%;width:{pct:.1f}%;background:{col};border-radius:0 6px 6px 0"></div></div>
</div>"""
    return d["bg"], fg, f"""
<div class="mid" style="gap:30px">
  <div class="row" style="gap:14px">
    <div class="tag" style="background:{PINK};color:{INK};font-size:22px">{d['tag']}</div>
    {'<div class="tag" style="border:2px dashed '+fg+';color:'+fg+';font-size:18px">SAMPLE DATA</div>' if d.get('sample') else ''}
  </div>
  <div class="ab" style="font-size:110px;line-height:.85;letter-spacing:-4px">{d['headline']}</div>
  <div class="mono b" style="font-size:20px;letter-spacing:2px;color:{GREY if fg==WHITE else INK}">{d['axis']}</div>
  <div class="col" style="gap:26px">{rows}</div>
</div>"""

def s_climb(p, d):  # THE RADAR: chart position over weeks (1 at top)
    fg = fg_for(d["bg"])
    W, H, L, R, T, B = 920, 520, 70, 40, 30, 60
    weeks, pos = d["weeks"], d["pos"]
    top, bot = 1, d["floor"]
    x = lambda i: L + i * (W - L - R) / (len(weeks) - 1)
    y = lambda v: T + (v - top) / (bot - top) * (H - T - B)
    grid_c = "rgba(255,255,255,.18)"
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{y(v):.0f}" y2="{y(v):.0f}" stroke="{grid_c}" stroke-width="2"/><text x="{L-14}" y="{y(v)+8:.0f}" text-anchor="end" font-family="SM" font-weight="700" font-size="22" fill="{WHITE}">#{v}</text>' for v in d["ticks"])
    xl = "".join(f'<text x="{x(i):.0f}" y="{H-18}" text-anchor="middle" font-family="SM" font-weight="700" font-size="20" fill="{WHITE}">{w}</text>' for i, w in enumerate(weeks))
    pts = " ".join(f"{x(i):.0f},{y(v):.0f}" for i, v in enumerate(pos) if v)
    dots = "".join(f'<circle cx="{x(i):.0f}" cy="{y(v):.0f}" r="11" fill="{VOLT}" stroke="{d["bg"]}" stroke-width="4"/>' for i, v in enumerate(pos) if v)
    pk = min(v for v in pos if v); pi = pos.index(pk)
    label = f'<text x="{x(pi)-18:.0f}" y="{y(pk)-24:.0f}" text-anchor="end" font-family="AB" font-size="40" fill="{VOLT}">PEAK #{pk}</text>'
    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="overflow:visible">{grid}{xl}<polyline points="{pts}" fill="none" stroke="{VOLT}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>{dots}{label}</svg>'
    return d["bg"], fg, f"""
<div class="mid" style="gap:26px">
  <div class="row" style="gap:14px">
    <div class="tag" style="background:{VOLT};color:{INK};font-size:22px">{d['tag']}</div>
    {'<div class="tag" style="border:2px dashed #FFFFFF;color:#FFFFFF;font-size:18px">SAMPLE DATA</div>' if d.get('sample') else ''}
  </div>
  <div class="ab" style="font-size:120px;line-height:.85;letter-spacing:-5px">{d['headline']}</div>
  <div class="mono b" style="font-size:20px;letter-spacing:2px">{d['axis']}</div>
  {svg}
  <div style="font-size:34px;font-weight:700;line-height:1.25">{d['note']}</div>
</div>"""

def s_heat(p, d):  # EURO 10: tracks x countries, sequential single hue (volt), position in cell
    fg = fg_for(d["bg"])
    cols = d["cols"]
    def cell(v):
        if v is None:
            return f'<div class="mono b" style="height:64px;display:flex;align-items:center;justify-content:center;font-size:22px;color:#6E6E6E;border:2px solid #2E2E2E">—</div>'
        a = 1.0 if v <= 10 else .7 if v <= 25 else .45 if v <= 50 else .25  # 4 bins: brighter = higher
        txt = INK if a >= .7 else WHITE
        return f'<div class="mono b" style="height:64px;display:flex;align-items:center;justify-content:center;font-size:26px;background:rgba(232,255,43,{a:.2f});color:{txt}">{v}</div>'
    head = "".join(f'<div class="mono b" style="text-align:center;font-size:22px;letter-spacing:2px">{c}</div>' for c in cols)
    body = ""
    for i, (t, a, vals) in enumerate(d["rows"], 1):
        body += f'<div class="col" style="justify-content:center"><div class="ab" style="font-size:26px;line-height:1">{i}. {t}</div><div class="mono" style="font-size:16px;color:{GREY}">{a}</div></div>' + "".join(cell(v) for v in vals)
    return d["bg"], fg, f"""
<div class="mid" style="gap:26px">
  <div class="row" style="gap:14px">
    <div class="tag" style="background:{VOLT};color:{INK};font-size:22px">{d['tag']}</div>
    {'<div class="tag" style="border:2px dashed #FFFFFF;color:#FFFFFF;font-size:18px">SAMPLE DATA</div>' if d.get('sample') else ''}
  </div>
  <div class="ab" style="font-size:110px;line-height:.85;letter-spacing:-4px">{d['headline']}</div>
  <div style="display:grid;grid-template-columns:330px repeat({len(cols)},1fr);gap:8px;align-items:stretch">
    <div></div>{head}{body}
  </div>
  <div class="mono b" style="font-size:18px;letter-spacing:2px;color:{GREY}">{d['legend']}</div>
</div>"""

def s_paper(p, d):  # THE WEEK: front page
    fg = INK
    sub = "".join(f'<div class="col" style="gap:8px;border-top:3px solid {INK};padding-top:14px"><div class="mono b" style="font-size:18px;letter-spacing:2px;color:{c}">{m}</div><div class="ab" style="font-size:36px;line-height:1">{h}</div><div style="font-size:22px;font-weight:600;line-height:1.3">{t}</div></div>' for m, c, h, t in d["subs"])
    return WHITE, fg, f"""
<div class="mid" style="gap:22px">
  <div style="border-top:8px solid {INK};border-bottom:3px solid {INK};padding:12px 0" class="row">
    <div class="ab" style="font-size:150px;line-height:.85;letter-spacing:-6px;flex:1;text-align:center">THE WEEK</div>
  </div>
  <div class="row mono b" style="justify-content:space-between;font-size:20px;letter-spacing:2px;border-bottom:3px solid {INK};padding-bottom:10px"><div>{d['issue']}</div><div>EUROPEAN RAP · 5 STORIES</div></div>
  <div class="row" style="gap:28px;align-items:center">
    <div class="col" style="gap:12px;flex:1">
      <div class="tag" style="background:{PINK};color:{INK};align-self:flex-start;font-size:20px">{d['lead_m']}</div>
      <div class="ab" style="font-size:78px;line-height:.9;letter-spacing:-3px">{d['lead']}</div>
      <div style="font-size:28px;font-weight:600;line-height:1.3">{d['lead_t']}</div>
    </div>
    {mascot(230, INK, WHITE, PINK, 'paper')}
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">{sub}</div>
</div>"""

def s_poses(p, d):  # review sheet of mascot poses
    cells = "".join(f'<div class="col" style="align-items:center;gap:8px;background:{bg};padding:18px 0 14px">{mascot(250, c, e, a, pose)}<div class="mono b" style="font-size:20px;letter-spacing:2px;color:{fg_for(bg)}">{lab}</div></div>' for pose, lab, bg, c, e, a in d["poses"])
    return INK, WHITE, f"""
<div class="mid" style="gap:20px">
  <div class="ab" style="font-size:80px;line-height:.9;letter-spacing:-3px">MASCOT POSES</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">{cells}</div>
</div>"""

TYPES.update(poster=s_poster, tv=s_tv, cassette=s_cassette, bars=s_bars, climb=s_climb, heat=s_heat, paper=s_paper, poses=s_poses)


CSS = f"""
@font-face{{font-family:'AB';src:url('{AB.as_uri()}') format('woff2')}}
@font-face{{font-family:'SM';src:url('{SM4.as_uri()}') format('woff2');font-weight:400}}
@font-face{{font-family:'SM';src:url('{SM7.as_uri()}') format('woff2');font-weight:700}}
body{{margin:0;font-family:Inter,sans-serif}}
.slide{{position:relative;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column}}
.row{{display:flex;align-items:center}} .col{{display:flex;flex-direction:column}}
.mid{{position:relative;flex:1;display:flex;flex-direction:column;justify-content:center;padding:24px 0}}
.ab{{font-family:'AB',sans-serif}} .mono{{font-family:'SM',monospace}} .b{{font-weight:700}}
.logo{{font-family:'AB';font-size:40px;line-height:.9;letter-spacing:-1px}}
.tag{{display:flex;align-items:center;gap:10px;padding:9px 16px;font-family:'SM';font-weight:700;font-size:19px;letter-spacing:2px}}
.dot{{width:13px;height:13px;border-radius:50%;background:{PINK};display:inline-block}}
.np{{gap:16px;padding:14px 18px;margin-bottom:22px}}
.fact{{display:flex;gap:26px;padding:18px 0;border-bottom:1px solid}}
.fact .k{{width:240px;flex:none;font-family:'SM';font-weight:700;font-size:19px;letter-spacing:2px;padding-top:6px}}
.fact .v{{font-size:32px;font-weight:600;line-height:1.3}}
"""

def build_html(post, fmt):
    F = FORMATS[fmt]
    out = []
    tot = len(post["slides"])
    for i, d in enumerate(post["slides"], 1):
        bg, fg, body = TYPES[d["type"]](post, d)
        dec = deco(d.get("deco", ""), fg, d.get("word", ""))
        out.append(f"""<div class="slide" style="width:{F['w']}px;height:{F['h']}px;padding:{F['pt']}px {F['pr']}px {F['pb']}px {F['pl']}px;background:{bg};color:{fg}">{dec}
{header(fg, post['show'], post['mkt'], i, tot)}
{body}
{footer(fg, post['date'], post['wk'], i == tot)}
</div>""")
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(out)}</body></html>"

async def render(posts, outdir):
    outdir = pathlib.Path(outdir); outdir.mkdir(exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        for post in posts:
            for fmt in ("IG", "TT"):
                F = FORMATS[fmt]
                html = ROOT / f"_{post['slug']}_{fmt}.html"
                html.write_text(build_html(post, fmt))
                pg = await b.new_page(viewport={"width": F["w"], "height": F["h"]})
                await pg.goto(html.as_uri())
                await pg.evaluate("document.fonts.ready")
                await pg.wait_for_timeout(150)
                over = await pg.evaluate("[...document.querySelectorAll('.slide')].map((s,i)=>{const m=s.querySelector('.mid');return m && m.scrollHeight>m.clientHeight+2 ? i+1 : 0}).filter(Boolean)")
                if over: print("OVERFLOW", post['slug'], fmt, over)
                for i, el in enumerate(await pg.query_selector_all(".slide"), 1):
                    await el.screenshot(path=str(outdir / f"radar808_{post['mkt']}_{post['slug']}_{fmt}_{i:02d}.png"))
                await pg.close()
        await b.close()
