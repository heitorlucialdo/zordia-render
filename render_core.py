"""Renderizador de posts ZordIA v2: slides (JSON) -> imagens 1080x1350.

Convenção de texto (vale pra todo campo de texto):
  <b>trecho</b>                -> trecho forte (o resto fica apagado)
  <span class="hl">trecho</span> -> trecho em roxo/gradiente
Fotos (campo "img"): "foto:arquivo.jpg" (pasta assets/fotos) ou URL https.
"""
import base64, math, pathlib, random
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).parent / "assets"


def _uri(p, mime):
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


Z = {k: _uri(A / f"z_{k}.png", "image/png") for k in ("violet", "black", "light", "white")}
FONT = _uri(A / "Geist-Variable.woff2", "font/woff2")


def foto(src):
    if not src:
        return ""
    if src.startswith("foto:"):
        p = A / "fotos" / src[5:]
        if p.exists():
            return _uri(p, "image/png" if p.suffix == ".png" else "image/jpeg")
        return ""
    return src if src.startswith("http") else ""


def strong(t):
    """Título sem <b> fica todo forte (a IA às vezes esquece a marcação)."""
    t = t or ""
    return t if "<b>" in t else f"<b>{t}</b>"


# ---------------------------------------------------------------- ícones
_IC = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "pergunta": '<circle cx="12" cy="12" r="9.5"/><path d="M9.2 9.2a2.9 2.9 0 0 1 5.6 1c0 1.9-2.8 2.6-2.8 2.6"/><path d="M12 17h.01"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "diagonal": '<path d="M7 17 17 7M8 7h9v9"/>',
    "engrenagem": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/>',
    "pessoa": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/>',
    "raio": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "grafico": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    "relogio": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3.2 2"/>',
    "chat": '<path d="M21 12a8.5 8.5 0 0 1-12.3 7.6L3 21l1.5-5.4A8.5 8.5 0 1 1 21 12z"/>',
    "calendario": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "dinheiro": '<circle cx="12" cy="12" r="9.5"/><path d="M15 9.4c-.5-1-1.6-1.6-3-1.6-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.4 0-2.6-.6-3-1.6M12 6v1.8M12 16.2V18"/>',
    "robo": '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16.5h5"/>',
    "alvo": '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="1.5"/>',
}


def ic(name, size=40, sw=1.8):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{_IC.get(name, _IC["seta"])}</svg>')


# ---------------------------------------------------------------- peças comuns
def head(theme, page):
    z = Z["black"] if theme == "violet" else Z["violet"]
    return f'<div class="head"><img src="{z}" alt=""><span class="pg">{page or ""}</span></div>'


def swipe(pos="br"):
    return f'<div class="swipe {pos}">arraste para o lado <span class="sc">{ic("seta", 30, 2)}</span></div>'


def mesh():
    random.seed(3)
    paths = []
    for k in range(16):
        y = -80 + k * 95
        a, b, c = random.randint(-160, 160), random.randint(-200, 200), random.randint(-120, 120)
        paths.append(f'<path d="M-120 {y} C 260 {y+a}, 760 {y+b}, 1220 {y+c}"/>')
    for k in range(9):
        x = -60 + k * 150
        paths.append(f'<path d="M{x} -60 C {x+120} 400, {x-90} 900, {x+60} 1420"/>')
    return ('<svg class="fx mesh" viewBox="0 0 1080 1350" preserveAspectRatio="none" fill="none" '
            f'stroke="rgba(255,255,255,.075)" stroke-width="1.6">{"".join(paths)}</svg>')


def ui_bg():
    """Fragmentos de interface apagados ao fundo da capa."""
    def bars(n, w0):
        return "".join(f'<i style="width:{w0 - (j * 37) % 140}px"></i>' for j in range(n))
    return f"""<div class="fx uibg">
      <div class="pan" style="left:40px;top:150px;width:330px"><u></u>{bars(5,300)}</div>
      <div class="pan" style="right:40px;top:120px;width:360px"><u></u>{bars(6,330)}</div>
      <div class="pan" style="right:20px;top:560px;width:300px">{bars(5,270)}</div>
      <div class="chip" style="left:70px;top:420px"><div><span>IA</span></div></div>
      <div class="ln" style="left:0;right:0;top:330px"></div><div class="ln v" style="left:760px;top:60px;bottom:620px"></div>
    </div>"""


def glass_icon(content, size=520):
    return f'<div class="gicon" style="--s:{size}px">{content}</div>'


def q3d(size=820):
    layers = ",".join(
        f"{i}px {i}px 0 rgb({max(18, 74 - i)},{max(4, 22 - i // 2)},{max(40, 150 - i * 2)})" for i in range(1, 34))
    return (f'<div class="q3d" style="font-size:{size}px"><span class="bk" style="text-shadow:{layers}">?</span>'
            f'<span class="fr">?</span></div>')


def photo_or_fallback(src, cls="pimg"):
    s = foto(src)
    if s:
        return f'<img class="{cls}" src="{s}" alt="">'
    return f'<div class="{cls} pfb"><img src="{Z["violet"]}" alt=""></div>'


# ---------------------------------------------------------------- layouts
def cover(d):
    style = d.get("style", "icone")
    if style == "pergunta":
        return f"""<div class="slide t-violet cov-q">{mesh()}<div class="fx vglow"></div>
          {head('violet', d.get('page'))}
          <h1 class="cq fit">{d['title']}</h1>
          <p class="cqs">{d.get('sub','')}</p>
          {swipe('inline')}
          {q3d(760)}
        </div>"""
    if style == "foto" and foto(d.get("img")):
        return f"""<div class="slide t-dark cov-f"><img class="fx bgimg" src="{foto(d['img'])}" alt="">
          <div class="fx bgshade"></div>
          {head('dark', d.get('page'))}
          <h1 class="ct fit">{d['title']}</h1><p class="cs">{d.get('sub','')}</p>{swipe('center')}
        </div>"""
    return f"""<div class="slide t-dark cov-i">{ui_bg()}<div class="fx cglow"></div><div class="fx vfade"></div>
      {head('dark', d.get('page'))}
      <div class="gwrap">{glass_icon(f'<img src="{Z["light"]}" alt="">', 470)}</div>
      <h1 class="ct fit">{d['title']}</h1>
      <p class="cs">{d.get('sub','')}</p>
      {swipe('center')}
    </div>"""


def texto(d):
    th = d.get("theme", "dark")
    card = ""
    if d.get("img") is not None or d.get("img_caption"):
        cap = f'<div class="pcap">{d.get("img_caption","")}</div>' if d.get("img_caption") else ""
        card = f'<div class="pcard">{photo_or_fallback(d.get("img"))}{cap}</div>'
    return f"""<div class="slide t-{th} txt"><div class="fx dots"></div>
      {head(th, d.get('page'))}
      <h2 class="h fit">{strong(d['title'])}</h2>
      <p class="p">{d.get('text','')}</p>
      {card}
      <p class="p close">{d.get('close','')}</p>
      {swipe()}
    </div>"""


def lista(d):
    th = d.get("theme", "light")
    items = "".join(f'<li><span class="star">✱</span><span>{i}</span></li>' for i in d["items"])
    band = ""
    if d.get("img") is not None:
        band = (f'<div class="band">{photo_or_fallback(d.get("img"), "bimg")}<div class="tint"></div>'
                f'<div class="bshade"></div>{swipe("onband")}</div>')
    return f"""<div class="slide t-{th} lst{' hasband' if band else ''}"><div class="fx arcs"></div>
      {head(th, d.get('page'))}
      <ul class="fit">{items}</ul>
      <p class="p close">{d.get('close','')}</p>
      {band}
      {'' if band else swipe()}
    </div>"""


def numeros(d):
    th = d.get("theme", "light")
    cards = "".join(
        f'<div class="ncard"><div class="nn">{c["num"]}</div><div class="nl">{c["label"]}</div></div>'
        for c in d["cards"][:2])
    return f"""<div class="slide t-{th} num"><div class="fx arcs"></div>
      {head(th, d.get('page'))}
      <h2 class="h c fit">{strong(d['title'])}</h2>
      <p class="p c">{d.get('text','')}</p>
      <div class="nrow">{cards}</div>
      <p class="p c close">{d.get('close','')}</p>
      {swipe()}
    </div>"""


def comparativo(d):
    th = d.get("theme", "dark")
    cards = "".join(f'<div class="ocard">{c}</div>' for c in d["cards"][:2])
    img = f'<div class="pcard short">{photo_or_fallback(d.get("img"))}</div>' if d.get("img") is not None else ""
    return f"""<div class="slide t-{th} cmp"><div class="fx dots"></div><div class="fx bigarc"></div>
      {head(th, d.get('page'))}
      <h2 class="h grad fit">{d['title']}</h2>
      <p class="p">{d.get('lead','')}</p>
      <div class="orow">{cards}</div>
      {img}
      <p class="p close">{d.get('close','')}</p>
      {swipe()}
    </div>"""


def checklist(d):
    rows = ""
    for it in d["items"]:
        ok = it.get("ok", True)
        mark = (f'<span class="ck ok">{ic("check", 34, 2.4)}</span>' if ok
                else f'<span class="ck no">{ic("x", 26, 2.4)}</span>')
        rows += f'<li class="{"" if ok else "off"}">{mark}<span>{it["text"]}</span></li>'
    return f"""<div class="slide t-dark chk"><div class="fx dots"></div>
      {head('dark', d.get('page'))}
      <h2 class="h fit">{strong(d['title'])}</h2>
      <ul class="tree">{rows}</ul>
      <div class="callout">{d.get('callout','')}<span class="sc">{ic('seta', 30, 2)}</span></div>
      <div class="fx floor"></div>
      <div class="gq">{glass_icon('<span class="gqm">?</span>', 400)}</div>
    </div>"""


def pergunta(d):
    th = d.get("theme", "light")
    rows = "".join(f'<li>{ic("pergunta", 46, 1.6)}<span>{i}</span></li>' for i in d.get("items", []))
    return f"""<div class="slide t-{th} prg"><div class="fx arcs"></div>
      {head(th, d.get('page'))}
      <div class="body">
        <span class="tag">{d.get('tag','')}</span>
        <h2 class="hq fit">{d['q']}</h2>
        <p class="p">{d.get('sub','')}</p>
        <ul class="qlist">{rows}</ul>
        <div class="bar">{d.get('callout','')}</div>
      </div>
      {swipe()}
    </div>"""


def opcoes(d):
    a, b = d["cards"][:2]
    band = (f'<div class="tband">{photo_or_fallback(d.get("img"), "bimg")}<div class="tint"></div></div>'
            if d.get("img") is not None else "")
    return f"""<div class="slide t-light opc{' hasband' if band else ''}"><div class="fx arcs"></div>
      {band}
      {head('dark' if band else 'light', d.get('page'))}
      <div class="body">
        <span class="tag dark">{d.get('tag','')}</span>
        <h2 class="hq c fit">{d['q']}</h2>
        <div class="crow">
          <div class="occ">{ic(a.get('icon','pessoa'), 64, 1.6)}<p>{a['text']}</p></div>
          <div class="occ dk">{ic(b.get('icon','engrenagem'), 64, 1.6)}<p>{b['text']}</p></div>
        </div>
        <div class="bar">{d.get('callout','')}</div>
      </div>
      {swipe()}
    </div>"""


def conversa(d):
    msgs = ""
    for m in d["msgs"]:
        who = "rn" if m.get("from") == "renata" else "cl"
        msgs += f'<div class="msg {who}"><p>{m["text"]}</p><span>{m.get("time","")}</span></div>'
    return f"""<div class="slide t-dark cnv"><div class="fx dots"></div><div class="fx cglow2"></div>
      {head('dark', d.get('page'))}
      <h2 class="h fit">{strong(d['title'])}</h2>
      <div class="phone">
        <div class="ph-top"><div class="av"><img src="{Z['light']}" alt=""></div>
          <div><b>Renata</b><small>ZordIA · online agora</small></div></div>
        <div class="ph-body">{msgs}</div>
      </div>
      <p class="p close">{d.get('close','')}</p>
      {swipe()}
    </div>"""


def donut(d):
    pct = float(d["pct"])
    deg = pct * 3.6
    layers = "".join(
        f'<div class="lay" style="transform:translateZ(-{i*2}px);filter:brightness({0.55 - i*0.012:.3f})"></div>'
        for i in range(1, 22))
    return f"""<div class="slide t-dark dnt" style="--deg:{deg}deg"><div class="fx dots"></div><div class="fx dglow"></div>
      {head('dark', d.get('page'))}
      <h2 class="h fit">{strong(d['title'])}</h2>
      <div class="stage"><div class="ring3d">{layers}<div class="face"></div></div></div>
      <div class="legend"><div><div class="dn">{d['pct']}%</div><div class="dl">{d.get('label','')}</div></div>
        <div class="keys"><span><i style="background:#A23BFF"></i>{d.get('k1','')}</span>
        <span><i style="background:#3a3446"></i>{d.get('k2','')}</span><em>Fonte: {d.get('src','')}</em></div></div>
      {swipe()}
    </div>"""


def cta(d):
    s = foto(d.get("img"))
    icon = f'<img src="{Z["light"]}" alt="">'
    bg = (f'<img class="fx bgimg" src="{s}" alt=""><div class="fx bgshade2"></div>' if s
          else f'<div class="fx cglow"></div><div class="fx ctaz">{glass_icon(icon, 470)}</div><div class="fx vfade2"></div>')
    return f"""<div class="slide t-dark ct-s">{bg}
      {head('dark', d.get('page'))}
      <div class="ctb">
        {f'<img class="ctz" src="{Z["white"]}" alt="">' if s else ''}
        <h2 class="cth fit">{d['title']}</h2>
        <p class="p c">{d.get('text','')}</p>
        <div class="btn">{d.get('button','Comenta RENATA')} {ic('diagonal', 34, 2.2)}</div>
      </div>
    </div>"""


def impacto(d):
    return f"""<div class="slide t-dark imp"><div class="fx bigtxt">{d.get('bg','IA')}</div><div class="fx cglow"></div>
      {head('dark', '')}
      <h2 class="ct l fit">{d['title']}</h2>
      <div class="btn w">{d.get('button','Comenta RENATA')} {ic('diagonal', 34, 2.2)}</div>
    </div>"""


LAYOUTS = dict(cover=cover, texto=texto, lista=lista, numeros=numeros, comparativo=comparativo,
               checklist=checklist, pergunta=pergunta, opcoes=opcoes, conversa=conversa,
               donut=donut, cta=cta, impacto=impacto)

# ---------------------------------------------------------------- CSS
CSS = """
@font-face{font-family:Geist;src:url(__FONT__) format('woff2');font-weight:100 900}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden;background:#000}
body{font-family:Geist,sans-serif;-webkit-font-smoothing:antialiased}
.slide{--k:1;position:relative;width:1080px;height:1350px;overflow:hidden;padding:84px 96px;display:flex;flex-direction:column}
.slide>*{position:relative;z-index:3}
.slide>.fx,.fx{position:absolute;z-index:0;pointer-events:none}
.t-dark{background:#050407;color:#fff;--fg:#fff;--dim:rgba(255,255,255,.5);--line:rgba(255,255,255,.12)}
.t-light{background:#fff;color:#0B0910;--fg:#0B0910;--dim:rgba(11,9,16,.42);--line:rgba(11,9,16,.12)}
.t-violet{background:radial-gradient(120% 90% at 15% 0%,#5B18C9 0%,#2B0868 45%,#0B0216 100%);color:#fff;--fg:#fff;--dim:rgba(255,255,255,.62);--line:rgba(255,255,255,.18)}
.hl{background:linear-gradient(95deg,#DDBBFF 0%,#A23BFF 55%,#7B2FE0 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.t-light .hl{background:linear-gradient(95deg,#9A3BFF,#6A1FD0);-webkit-background-clip:text;background-clip:text}
.t-violet .hl{background:linear-gradient(95deg,#fff,#E3CCFF);-webkit-background-clip:text;background-clip:text}
b{font-weight:600;color:var(--fg)}
.head{display:flex;align-items:center;justify-content:space-between;height:56px;flex:none}
.head img{height:46px}
.pg{font-size:28px;font-weight:500;letter-spacing:.04em;opacity:.38}
.h{font-size:calc(74px*var(--k));line-height:1.06;font-weight:600;letter-spacing:-.035em;color:var(--dim);margin-top:96px;text-wrap:balance}
.h.c,.p.c{text-align:center}
.p{font-size:calc(40px*var(--k));line-height:1.42;color:var(--dim);letter-spacing:-.012em;margin-top:40px;text-wrap:pretty}
.p.close{margin-top:auto;margin-bottom:156px}
.swipe{display:inline-flex;align-items:center;gap:16px;font-size:27px;font-weight:450;border:2px solid currentColor;border-radius:99px;padding:10px 12px 10px 26px;opacity:.85;z-index:4}
.swipe .sc{display:grid;place-items:center;width:44px;height:44px;border:2px solid currentColor;border-radius:50%}
.swipe.br{position:absolute;right:96px;bottom:72px}
.swipe.center{align-self:center;margin:46px 0 6px}
.swipe.inline{align-self:flex-start;margin-top:44px}
.swipe.band{position:absolute;left:50%;bottom:448px;transform:translateX(-50%);background:rgba(255,255,255,.55);backdrop-filter:blur(8px);color:#0B0910;border-color:rgba(255,255,255,.8)}
.dots{inset:0;background-image:radial-gradient(rgba(255,255,255,.085) 1.1px,transparent 1.6px);background-size:10px 10px;-webkit-mask:linear-gradient(180deg,transparent,#000 30%,#000 75%,transparent)}
.t-light .dots{background-image:radial-gradient(rgba(0,0,0,.06) 1.1px,transparent 1.6px)}
.arcs{inset:0}
.arcs::before,.arcs::after{content:"";position:absolute;border-radius:50%;border:2px solid var(--line);opacity:.6}
.arcs::before{width:1300px;height:1300px;left:480px;top:-260px}
.arcs::after{width:900px;height:900px;left:640px;top:-40px}
.bigarc{inset:0}.bigarc::before{content:"";position:absolute;width:1100px;height:1100px;border-radius:50%;border:2px solid rgba(255,255,255,.06);left:-10px;top:180px}
/* capa ícone */
.uibg{inset:0;opacity:.5;filter:blur(1px);-webkit-mask:linear-gradient(180deg,#000 0%,#000 45%,transparent 70%)}
.uibg .pan{position:absolute;display:flex;flex-direction:column;gap:14px;padding:22px;border:1px solid rgba(255,255,255,.08);border-radius:14px;background:rgba(255,255,255,.02)}
.uibg .pan u{display:block;width:120px;height:16px;border-radius:4px;background:rgba(162,59,255,.35)}
.uibg .pan i{display:block;height:9px;border-radius:5px;background:rgba(255,255,255,.12)}
.uibg .ln{position:absolute;height:1px;background:rgba(255,255,255,.08)}.uibg .ln.v{width:1px;height:auto}
.uibg .chip{position:absolute;width:250px;height:250px;transform:rotateX(58deg) rotateZ(45deg);border:2px solid rgba(255,255,255,.18);display:grid;place-items:center}
.uibg .chip div{width:150px;height:150px;border:2px solid rgba(162,59,255,.5);display:grid;place-items:center}
.uibg .chip span{font-size:54px;font-weight:600;color:rgba(190,140,255,.7);transform:rotate(-45deg)}
.cglow{left:50%;top:-180px;width:1100px;height:1100px;transform:translateX(-50%);background:radial-gradient(closest-side,rgba(162,59,255,.42),rgba(162,59,255,.1) 55%,transparent);filter:blur(10px)}
.vfade{left:0;right:0;bottom:0;height:640px;background:linear-gradient(transparent,#050407 55%)}
.gwrap{display:flex;justify-content:center;margin-top:58px}
.gicon{position:relative;width:var(--s);height:var(--s);border-radius:calc(var(--s)*.27);display:grid;place-items:center;
  background:linear-gradient(150deg,rgba(255,255,255,.2),rgba(255,255,255,.02) 38%),linear-gradient(160deg,#2A1252,#0B0614 72%);
  box-shadow:inset 0 2px 0 rgba(255,255,255,.45),inset 0 -40px 90px rgba(0,0,0,.6),inset 18px 18px 60px rgba(162,59,255,.22),0 60px 160px rgba(162,59,255,.5),0 0 110px rgba(162,59,255,.3)}
.gicon::after{content:"";position:absolute;inset:0;border-radius:inherit;padding:3px;background:linear-gradient(140deg,rgba(230,205,255,.95),rgba(162,59,255,.25) 35%,rgba(255,255,255,0) 60%,rgba(162,59,255,.7));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.gicon img{width:60%;filter:drop-shadow(0 0 26px rgba(205,150,255,.95)) drop-shadow(0 0 70px rgba(162,59,255,.7))}
.ct{font-size:calc(116px*var(--k));line-height:1;font-weight:600;letter-spacing:-.045em;text-align:center;margin-top:auto;text-wrap:balance}
.ct.l{text-align:left}
.cs{font-size:40px;line-height:1.35;color:rgba(255,255,255,.72);text-align:center;margin-top:34px;text-wrap:balance}
/* capa pergunta */
.mesh{inset:0;width:100%;height:100%}
.vglow{right:-200px;top:300px;width:900px;height:900px;background:radial-gradient(closest-side,rgba(190,120,255,.35),transparent);filter:blur(20px)}
.cq{font-size:calc(132px*var(--k));line-height:.92;font-weight:700;letter-spacing:-.035em;text-transform:uppercase;margin-top:auto;max-width:900px;color:#fff;text-wrap:balance}
.cqs{font-size:44px;line-height:1.3;color:rgba(255,255,255,.8);margin-top:34px;max-width:760px}
.cov-q .swipe.inline{margin-bottom:150px}
.q3d{position:absolute;right:-90px;bottom:40px;line-height:1;font-weight:700;transform:rotate(14deg);z-index:2;filter:drop-shadow(0 40px 80px rgba(20,0,60,.6))}
.q3d span{display:block}.q3d .fr{position:absolute;inset:0;background:linear-gradient(160deg,#F6EDFF 0%,#C595FF 35%,#8A3DF0 70%,#5A16BF 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.q3d .bk{color:#3A0C82}
/* capa foto / cta foto */
.bgimg{inset:0;width:100%;height:100%;object-fit:cover}
.bgshade{inset:0;background:linear-gradient(180deg,rgba(5,4,7,.35),rgba(5,4,7,.2) 35%,rgba(5,4,7,.92) 72%,#050407)}
.bgshade2{inset:0;background:linear-gradient(180deg,rgba(5,4,7,.2),rgba(5,4,7,.55) 40%,rgba(5,4,7,.95) 70%)}
/* texto + foto */
.pcard{position:relative;margin-top:64px;height:560px;border-radius:36px;overflow:hidden;border:2px solid rgba(162,59,255,.45);box-shadow:0 30px 90px rgba(0,0,0,.5);flex:none}
.pcard.short{height:330px;margin-top:40px}
.pimg{width:100%;height:100%;object-fit:cover;display:block}
.pfb{display:grid;place-items:center;background:radial-gradient(60% 80% at 70% 30%,rgba(162,59,255,.55),transparent 70%),radial-gradient(50% 60% at 20% 80%,rgba(90,20,200,.6),transparent 70%),#0d0716}
.pfb img{width:34%;opacity:.35;filter:blur(1px)}
.pcap{position:absolute;left:0;right:0;bottom:0;padding:120px 44px 40px;font-size:36px;line-height:1.38;color:#fff;background:linear-gradient(transparent,rgba(5,4,7,.92) 55%)}
/* lista */
.lst ul{list-style:none;display:flex;flex-direction:column;gap:46px;margin-top:110px}
.lst li{display:flex;gap:26px;font-size:calc(62px*var(--k));line-height:1.06;font-weight:600;letter-spacing:-.03em;text-wrap:balance}
.lst .star{color:var(--dim);font-size:.8em;line-height:1.3;flex:none}
.lst.hasband ul{margin-top:90px;gap:34px}.lst.hasband li{font-size:calc(56px*var(--k))}
.lst.hasband .p.close{margin-top:40px}
.band{position:relative;flex:none;height:440px;margin:auto -96px -84px;overflow:hidden}
.lst.hasband .p.close{margin-bottom:56px}
.bshade{position:absolute;inset:0;background:linear-gradient(180deg,#fff 0%,rgba(255,255,255,0) 22%)}
.swipe.onband{position:absolute;right:96px;bottom:60px;color:#fff;background:rgba(10,6,20,.35);backdrop-filter:blur(6px)}
.tband{position:absolute;left:0;right:0;top:0;height:400px;overflow:hidden;z-index:2}
.bimg{width:100%;height:100%;object-fit:cover;display:block}
.tint{position:absolute;inset:0;background:#7B2FE0;mix-blend-mode:color}
.tband::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35),transparent 40%)}
/* numeros */
.num .h{margin-top:120px}
.nrow{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:64px}
.ncard{background:#0E0B14;border-radius:26px;padding:54px 44px 50px;min-height:300px;display:flex;flex-direction:column;justify-content:flex-end}
.t-dark .ncard{background:rgba(255,255,255,.05);border:1.5px solid rgba(255,255,255,.1)}
.nn{font-size:calc(128px*var(--k));line-height:.9;font-weight:600;letter-spacing:-.055em;background:linear-gradient(100deg,#E2C6FF,#A23BFF 60%,#7B2FE0);-webkit-background-clip:text;background-clip:text;color:transparent}
.nl{font-size:30px;line-height:1.25;color:#B98AFF;margin-top:22px;font-weight:500}
/* comparativo */
.h.grad{color:transparent;background:linear-gradient(100deg,#F0E2FF 0%,#C08BFF 45%,#8F4BFF 100%);-webkit-background-clip:text;background-clip:text;margin-top:100px}
.orow{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:48px}
.ocard{border:2px solid rgba(162,59,255,.5);background:rgba(162,59,255,.1);border-radius:16px;padding:30px 30px;font-size:30px;line-height:1.36;color:rgba(255,255,255,.92)}
/* checklist */
.tree{list-style:none;margin:70px 0 0 30px;padding-left:44px;border-left:2px solid rgba(255,255,255,.22);display:flex;flex-direction:column;gap:46px}
.tree li{position:relative;display:flex;align-items:center;gap:28px;font-size:46px;line-height:1.15;letter-spacing:-.02em;color:#fff}
.tree li::before{content:"";position:absolute;left:-44px;top:50%;width:30px;height:2px;background:rgba(255,255,255,.22)}
.tree li.off{color:rgba(255,255,255,.62)}
.ck{flex:none;display:grid;place-items:center;width:64px;height:64px;border-radius:50%}
.ck.ok{border:3px solid #A23BFF;color:#C58BFF;box-shadow:0 0 30px rgba(162,59,255,.45)}
.ck.no{border:3px dashed rgba(255,255,255,.45);color:rgba(255,255,255,.6)}
.callout{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:62px;padding:30px 30px 30px 40px;border-radius:16px;background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.12);font-size:34px;line-height:1.3}
.callout .sc{flex:none;display:grid;place-items:center;width:52px;height:52px;border:2px solid currentColor;border-radius:50%}
.floor{left:0;right:0;bottom:0;height:330px;background:linear-gradient(180deg,#14082A,#2A0B5E 60%,#3C1084);border-top:1px solid rgba(162,59,255,.4)}
.gq{position:absolute;left:50%;bottom:-175px;transform:translateX(-50%);z-index:3}
.gqm{font-size:280px;font-weight:700;line-height:1;background:linear-gradient(170deg,#F4E8FF,#B57BFF 55%,#7B2FE0);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 30px rgba(190,130,255,.8))}
/* pergunta */
.prg .body,.opc .body{margin-top:auto;margin-bottom:150px}
.tag{display:inline-block;font-size:30px;font-weight:500;padding:12px 30px;border-radius:99px;border:2px solid var(--line);color:var(--dim)}
.tag.dark{background:#0B0910;color:#fff;border-color:#0B0910}
.hq{font-size:calc(84px*var(--k));line-height:1.02;font-weight:600;letter-spacing:-.04em;margin-top:34px;text-wrap:balance}
.hq.c{text-align:center}
.prg .p{margin-top:24px}
.qlist{list-style:none;margin-top:44px}
.qlist li{display:flex;align-items:center;gap:22px;font-size:38px;padding:24px 0;border-bottom:2px solid var(--line);color:var(--fg)}
.qlist li:last-child{border-bottom:0}
.qlist svg{flex:none;color:var(--fg)}
.bar{margin-top:44px;padding:30px 44px;border-radius:12px;background:#0B0910;color:#fff;font-size:36px;line-height:1.3;text-align:center}
.t-dark .bar{background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.14)}
/* opcoes */
.opc{text-align:center}
.opc.hasband .head{color:#fff}
.opc.hasband .body{margin-top:300px;margin-bottom:auto}
.opc.hasband .hq{font-size:calc(70px*var(--k))}
.crow{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:48px;text-align:left}
.occ{border:2px solid rgba(11,9,16,.16);border-radius:10px;padding:40px 38px;min-height:calc(270px*var(--k));display:flex;flex-direction:column;justify-content:space-between;gap:30px}
.occ p{font-size:calc(36px*var(--k));line-height:1.2;font-weight:500;letter-spacing:-.02em}
.occ.dk{background:linear-gradient(135deg,#2B2730,#050407);color:#fff;border-color:#000}
.occ.dk svg{color:#C58BFF}
/* conversa */
.cnv .h{margin-top:70px}
.cglow2{right:-300px;top:380px;width:900px;height:900px;background:radial-gradient(closest-side,rgba(162,59,255,.32),transparent)}
.phone{margin-top:44px;flex:none;border-radius:40px;border:1.5px solid rgba(255,255,255,.12);background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,.6)}
.ph-top{display:flex;align-items:center;gap:22px;padding:26px 34px;border-bottom:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.03)}
.ph-top b{display:block;font-size:32px}.ph-top small{font-size:24px;color:#B98AFF}
.av{width:70px;height:70px;border-radius:50%;background:linear-gradient(150deg,#3a1878,#0b0614);display:grid;place-items:center;border:2px solid rgba(162,59,255,.6)}
.av img{width:56%}
.ph-body{display:flex;flex-direction:column;gap:14px;padding:28px 30px}
.msg{max-width:80%;padding:18px 26px 12px;border-radius:28px;font-size:calc(29px*var(--k));line-height:1.32}
.msg span{display:block;text-align:right;font-size:20px;opacity:.55;margin-top:6px}
.msg.cl{align-self:flex-start;background:#1D1A23;border-bottom-left-radius:8px}
.msg.rn{align-self:flex-end;background:linear-gradient(135deg,#7B2FE0,#5216B0);border-bottom-right-radius:8px}
.cnv .p.close{margin-top:36px;margin-bottom:auto}
/* donut */
.dglow{left:50%;top:430px;width:900px;height:620px;transform:translateX(-50%);background:radial-gradient(closest-side,rgba(162,59,255,.42),transparent);filter:blur(30px)}
.stage{perspective:1600px;flex:1;display:grid;place-items:center}
.ring3d{position:relative;width:540px;height:540px;transform:rotateX(62deg) rotateZ(-28deg);transform-style:preserve-3d}
.ring3d .lay,.ring3d .face{position:absolute;inset:0;border-radius:50%;background:conic-gradient(#A23BFF 0 var(--deg),#3a3446 var(--deg) 360deg);
  -webkit-mask:radial-gradient(closest-side,transparent 56%,#000 56.5%);mask:radial-gradient(closest-side,transparent 56%,#000 56.5%)}
.ring3d .face{background:conic-gradient(#E0C2FF 0,#A23BFF calc(var(--deg)*.55),#7B2FE0 var(--deg),#4a4458 var(--deg) 360deg)}
.legend{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:120px}
.dn{font-size:150px;font-weight:600;letter-spacing:-.06em;line-height:.85;background:linear-gradient(100deg,#E2C6FF,#A23BFF 60%,#7B2FE0);-webkit-background-clip:text;background-clip:text;color:transparent}
.dl{font-size:32px;color:rgba(255,255,255,.7);margin-top:16px;max-width:460px}
.keys{display:flex;flex-direction:column;gap:14px;font-size:28px;padding-bottom:10px}
.keys span{display:flex;align-items:center;gap:12px}.keys i{width:20px;height:20px;border-radius:6px}.keys em{font-style:normal;opacity:.45;font-size:22px}
/* cta */
.ctaz{left:50%;top:170px;transform:translateX(-50%);opacity:.9}
.vfade2{left:0;right:0;bottom:0;height:720px;background:linear-gradient(transparent,#050407 38%)}
.ctb{margin-top:auto;margin-bottom:96px;display:flex;flex-direction:column;align-items:center;text-align:center}
.ctz{height:64px;margin-bottom:40px}
.cth{font-size:calc(92px*var(--k));line-height:1.02;font-weight:600;letter-spacing:-.04em;text-wrap:balance}
.ct-s .p{color:rgba(255,255,255,.62)}
.btn{display:inline-flex;align-items:center;gap:14px;margin-top:56px;padding:30px 56px;border-radius:14px;font-size:38px;font-weight:600;color:#fff;background:linear-gradient(100deg,#B65CFF,#7B2FE0);box-shadow:0 24px 80px rgba(162,59,255,.5)}
.btn.w{align-self:flex-start;margin-bottom:40px}
/* impacto */
.bigtxt{left:50%;top:-40px;transform:translateX(-50%);font-size:1050px;font-weight:700;letter-spacing:-.08em;line-height:1;background:linear-gradient(180deg,rgba(162,59,255,.6),rgba(162,59,255,0) 80%);-webkit-background-clip:text;background-clip:text;color:transparent}
.imp .ct{font-size:calc(100px*var(--k))}
"""

FIT_JS = """() => {
  const s = document.querySelector('.slide'); const H = s.getBoundingClientRect().bottom; let k = 1;
  const flow = [...s.children].filter(e => getComputedStyle(e).position !== 'absolute');
  const over = () => flow.some(e => e.getBoundingClientRect().bottom > H + 1) ||
     [...s.querySelectorAll('.fit')].some(e => e.scrollWidth > e.clientWidth + 2);
  while (over() && k > 0.6) { k -= 0.04; s.style.setProperty('--k', k); }
  return k;
}"""


def render_pngs(slides, fmt="png"):
    out = []
    css = CSS.replace("__FONT__", FONT)
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for s in slides:
            fn = LAYOUTS.get(s.get("layout"))
            if not fn:
                continue
            html = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{fn(s)}</body></html>"
            pg.set_content(html, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.evaluate(FIT_JS)
            pg.wait_for_timeout(120)
            out.append(pg.screenshot(type="jpeg", quality=90) if fmt == "jpeg" else pg.screenshot())
        br.close()
    return out
