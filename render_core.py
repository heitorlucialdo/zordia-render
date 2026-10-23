"""Renderizador de posts ZordIA: slides (JSON) -> PNG 1080x1350. Assets lidos de ./assets."""
import base64, pathlib
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).parent / "assets"

def _b64(p):
    return base64.b64encode(p.read_bytes()).decode()

Z_VIOLET = "data:image/png;base64," + _b64(A / "z_violet.png")
Z_BLACK = "data:image/png;base64," + _b64(A / "z_black.png")
FONT_URI = "data:font/woff2;base64," + _b64(A / "Geist-Variable.woff2")

BASE_CSS = f"""
@font-face{{font-family:Geist;src:url({FONT_URI}) format('woff2');font-weight:100 900}}
:root{{--v:#A23BFF;--v2:#7B2FE0;--deep:#2A0866;--ink:#0E0B14}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{font-family:Geist,sans-serif;-webkit-font-smoothing:antialiased;font-feature-settings:"ss01"}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;padding:84px 88px;display:flex;flex-direction:column}}
.slide>*{{position:relative;z-index:3}}
.fx{{position:absolute;z-index:0;pointer-events:none}}
.head{{display:flex;align-items:center;justify-content:space-between}}
.head img{{height:54px}}
.pg{{font-size:30px;font-weight:500;letter-spacing:.02em;opacity:.38}}
.swipe{{position:absolute;right:88px;bottom:80px;display:flex;align-items:center;gap:14px;font-size:27px;font-weight:450;
  border:1.5px solid currentColor;border-radius:99px;padding:12px 14px 12px 26px;opacity:.85;z-index:3}}
.swipe svg{{width:36px;height:36px}}
.hl{{background:linear-gradient(100deg,#C77DFF 0%,#A23BFF 45%,#7B2FE0 100%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.t-black{{background:#000;color:#fff}}
.t-white{{background:#fff;color:var(--ink)}}
.t-white .hl{{background:none;color:#7B2FE0}}
.t-violet{{background:linear-gradient(165deg,#4A12A8 0%,#2A0866 62%,#14032F 100%);color:#fff}}
.t-violet .hl{{background:none;color:#000}}
"""

ARROW = '<svg viewBox="0 0 36 36" fill="none"><circle cx="18" cy="18" r="16.5" stroke="currentColor" stroke-width="1.5"/><path d="M11 18h13m-5-5 5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def head(theme, page):
    z = Z_BLACK if theme == "t-violet" else Z_VIOLET
    return f'<div class="head"><img src="{z}" alt=""><span class="pg">{page}</span></div>'


def swipe(show=True):
    return f'<div class="swipe">arraste para o lado {ARROW}</div>' if show else ""


def cover(d):
    return f"""
<style>
.cover .spot{{left:50%;top:-260px;width:900px;height:1200px;translate:-50% 0;
  background:radial-gradient(50% 55% at 50% 30%,rgba(162,59,255,.55),rgba(162,59,255,.12) 55%,transparent 75%);filter:blur(30px)}}
.cover .bigz{{left:50%;top:150px;translate:-50% 0;width:600px;opacity:.85;filter:blur(1.5px) drop-shadow(0 0 60px rgba(162,59,255,.7))}}
.cover .fade{{left:0;right:0;bottom:0;height:900px;background:linear-gradient(transparent,#000 42%)}}
.cover h1{{font-size:104px;line-height:.98;font-weight:620;letter-spacing:-.045em;margin-top:auto;text-wrap:balance}}
.cover p{{font-size:36px;line-height:1.3;font-weight:400;opacity:.62;margin-top:34px;max-width:780px;margin-bottom:96px}}
</style>
<div class="slide t-black cover">
  <div class="fx spot"></div><img class="fx bigz" src="{Z_VIOLET}" alt=""><div class="fx fade"></div>
  {head('t-black', d.get('page',''))}
  <h1>{d['title']}</h1><p>{d.get('sub','')}</p>
  {swipe()}
</div>"""


def lista(d):
    items = "".join(f'<li><span class="ast">✱</span><span>{i}</span></li>' for i in d["items"])
    return f"""
<style>
.lista .ring{{right:-380px;top:120px;width:1100px;height:1100px;border-radius:50%;border:1.5px solid rgba(123,47,224,.10)}}
.lista .ring2{{right:-200px;top:300px;width:740px;height:740px;border-radius:50%;border:1.5px solid rgba(123,47,224,.08)}}
.lista ul{{list-style:none;margin-top:120px;display:flex;flex-direction:column;gap:58px}}
.lista li{{display:flex;gap:30px;font-size:66px;line-height:1.06;font-weight:560;letter-spacing:-.035em}}
.lista .ast{{color:#7B2FE0;font-size:52px;line-height:1.3;flex:none}}
.lista .close{{font-size:38px;line-height:1.35;margin-top:auto;margin-bottom:120px;max-width:840px;color:#3a3542}}
.lista .close b{{color:var(--ink);font-weight:620}}
</style>
<div class="slide t-white lista">
  <div class="fx ring"></div><div class="fx ring2"></div>
  {head('t-white', d.get('page',''))}
  <ul>{items}</ul>
  <p class="close">{d.get('close','')}</p>
  {swipe()}
</div>"""


def stats(d):
    main, a, b = d["main"], d["a"], d["b"]
    def small(x):
        return f"""<div class="card sm"><div class="ghost">{x['ghost']}</div>
        <div class="num hl">{x['num']}</div><div class="lab">{x['label']}</div></div>"""
    return f"""
<style>
.stats .beam{{left:-200px;top:-120px;width:340px;height:1900px;rotate:38deg;
  background:linear-gradient(90deg,transparent,rgba(162,59,255,.55),rgba(162,59,255,.12) 70%,transparent);filter:blur(18px)}}
.stats h2{{font-size:66px;line-height:1.04;font-weight:600;letter-spacing:-.04em;text-align:center;margin-top:70px;text-wrap:balance}}
.stats .src{{text-align:center;font-size:30px;opacity:.55;margin-top:26px}}
.stats .src b{{opacity:1;color:#fff;font-weight:520}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:64px}}
.card{{position:relative;overflow:hidden;border-radius:34px;padding:44px 46px;background:linear-gradient(160deg,rgba(255,255,255,.075),rgba(255,255,255,.025));
  border:1.5px solid rgba(255,255,255,.11);backdrop-filter:blur(24px)}}
.card.big{{grid-column:1/-1;height:330px}}
.card .ghost{{position:absolute;right:-20px;top:-70px;font-size:420px;font-weight:700;letter-spacing:-.06em;color:rgba(255,255,255,.035);line-height:1}}
.card .num{{font-size:150px;font-weight:600;letter-spacing:-.06em;line-height:.9;position:relative}}
.card.sm .num{{font-size:112px}}
.card .lab{{font-size:32px;opacity:.72;margin-top:18px;position:relative;font-weight:430;max-width:430px}}
.card.big .spark{{width:400px;right:40px;bottom:40px}}
.card .spark{{position:absolute;right:30px;bottom:34px}}
.tip{{position:absolute;right:56px;top:52px;font-size:20px;border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:8px 12px;background:rgba(0,0,0,.35)}}
.tip span{{display:block;opacity:.5;font-size:16px}}
</style>
<div class="slide t-black stats">
  <div class="fx beam"></div>
  {head('t-black', d.get('page',''))}
  <h2>{d['title']}</h2>
  <p class="src">{d.get('src','')}</p>
  <div class="grid2">
    <div class="card big"><div class="ghost">{main['ghost']}</div><div class="num hl">{main['num']}</div><div class="lab">{main['label']}</div>
      <div class="tip">{main['num']} total<span>{main.get('tip','')}</span></div>
      <svg class="spark" viewBox="0 0 470 160"><path d="M0 155 C 150 150, 260 135, 330 105 S 430 40, 470 0" stroke="#A23BFF" stroke-width="3" fill="none"/><circle cx="330" cy="105" r="9" fill="#C77DFF"/></svg></div>
    {small(a)}{small(b)}
  </div>
  {swipe()}
</div>"""


def donut(d):
    pct = d["pct"]
    deg = pct * 3.6
    layers = "".join(
        f'<div class="lay" style="transform:translateZ(-{i*2}px);filter:brightness({0.55 - i*0.012:.3f})"></div>'
        for i in range(1, 22))
    return f"""
<style>
.donut .glowb{{left:50%;top:420px;width:900px;height:600px;translate:-50% 0;background:radial-gradient(closest-side,rgba(162,59,255,.45),transparent);filter:blur(30px)}}
.donut h2{{font-size:72px;line-height:1.02;font-weight:600;letter-spacing:-.04em;margin-top:70px;max-width:860px;text-wrap:balance}}
.stage{{perspective:1600px;flex:1;display:grid;place-items:center}}
.ring3d{{position:relative;width:560px;height:560px;transform:rotateX(62deg) rotateZ(-28deg);transform-style:preserve-3d}}
.ring3d .lay,.ring3d .face{{position:absolute;inset:0;border-radius:50%;
  background:conic-gradient(#A23BFF 0 {deg}deg,#3a3446 {deg}deg 360deg);
  -webkit-mask:radial-gradient(closest-side,transparent 56%,#000 56.5%);mask:radial-gradient(closest-side,transparent 56%,#000 56.5%)}}
.ring3d .face{{background:conic-gradient(from 0deg,#D9A6FF 0,#A23BFF {deg*0.55}deg,#7B2FE0 {deg}deg,#4a4458 {deg}deg 360deg)}}
.legend{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:110px}}
.legend .n{{font-size:150px;font-weight:600;letter-spacing:-.06em;line-height:.85}}
.legend .l{{font-size:32px;opacity:.7;margin-top:14px;max-width:460px}}
.legend .keys{{display:flex;flex-direction:column;gap:14px;font-size:28px;padding-bottom:10px}}
.legend .keys span{{display:flex;align-items:center;gap:12px}}
.legend .sw{{width:20px;height:20px;border-radius:6px}}
</style>
<div class="slide t-black donut">
  <div class="fx glowb"></div>
  {head('t-black', d.get('page',''))}
  <h2>{d['title']}</h2>
  <div class="stage"><div class="ring3d">{layers}<div class="face"></div></div></div>
  <div class="legend"><div><div class="n hl">{pct}%</div><div class="l">{d.get('label','')}</div></div>
    <div class="keys"><span><i class="sw" style="background:#A23BFF"></i>{d.get('k1','')}</span><span><i class="sw" style="background:#4a4458"></i>{d.get('k2','')}</span><span style="opacity:.45;font-size:22px">Fonte: {d.get('src','')}</span></div></div>
  {swipe()}
</div>"""


def pergunta(d):
    return f"""
<style>
.perg .beam{{right:-260px;top:200px;width:420px;height:1700px;rotate:28deg;background:linear-gradient(90deg,transparent,rgba(199,125,255,.45),transparent);filter:blur(26px)}}
.qc{{margin:auto 0;border-radius:44px;padding:64px 60px;background:linear-gradient(160deg,rgba(255,255,255,.13),rgba(255,255,255,.04));
  border:1.5px solid rgba(255,255,255,.2);backdrop-filter:blur(30px)}}
.qp{{display:inline-block;background:#000;color:#fff;font-size:28px;font-weight:560;border-radius:99px;padding:12px 28px}}
.qc h2{{font-size:76px;line-height:1.02;font-weight:600;letter-spacing:-.04em;margin-top:44px;text-wrap:balance}}
.qc p{{font-size:36px;line-height:1.35;opacity:.82;margin-top:30px}}
.qc .ans{{margin-top:44px;border-radius:20px;background:rgba(0,0,0,.28);padding:28px 32px;font-size:30px;line-height:1.4}}
</style>
<div class="slide t-violet perg">
  <div class="fx beam"></div>
  {head('t-violet', d.get('page',''))}
  <div class="qc"><span class="qp">{d.get('tag','')}</span><h2>{d['q']}</h2><p>{d.get('p','')}</p><div class="ans">{d.get('ans','')}</div></div>
  {swipe()}
</div>"""


def cta(d):
    return f"""
<style>
.cta .spot{{left:50%;top:-300px;width:1000px;height:1300px;translate:-50% 0;background:radial-gradient(45% 50% at 50% 35%,rgba(162,59,255,.5),transparent 72%);filter:blur(30px)}}
.cta .bigz{{left:50%;top:130px;translate:-50% 0;width:560px;opacity:.5;filter:blur(2px)}}
.cta .fade{{left:0;right:0;bottom:0;height:950px;background:linear-gradient(transparent,#000 40%)}}
.cta h2{{font-size:88px;line-height:1.0;font-weight:610;letter-spacing:-.045em;text-align:center;margin-top:auto;text-wrap:balance}}
.cta .pill{{margin:56px auto 0;background:linear-gradient(100deg,#B65CFF,#7B2FE0);border-radius:22px;padding:34px 54px;font-size:40px;font-weight:500;text-align:center;box-shadow:0 20px 80px rgba(162,59,255,.45)}}
.cta .pill b{{font-weight:700}}
.cta .hint{{display:flex;gap:22px;align-items:flex-start;margin:34px auto 130px;max-width:820px;border:1.5px solid rgba(255,255,255,.16);border-radius:22px;padding:28px 32px;font-size:28px;line-height:1.4;opacity:.85}}
.cta .hint i{{flex:none;width:44px;height:44px;border-radius:50%;border:2px solid #A23BFF;color:#C77DFF;display:grid;place-items:center;font-style:normal;font-weight:600}}
</style>
<div class="slide t-black cta">
  <div class="fx spot"></div><img class="fx bigz" src="{Z_VIOLET}" alt=""><div class="fx fade"></div>
  {head('t-black', d.get('page',''))}
  <h2>{d['title']}</h2>
  <div class="pill">{d['pill']}</div>
  <div class="hint"><i>?</i><span>{d.get('hint','')}</span></div>
</div>"""


def impacto(d):
    return f"""
<style>
.imp .big{{left:50%;top:40px;translate:-50% 0;font-size:1100px;font-weight:700;letter-spacing:-.08em;line-height:1;
  background:linear-gradient(180deg,rgba(162,59,255,.55),rgba(162,59,255,0) 80%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.imp .spot{{left:50%;top:-300px;width:1000px;height:1100px;translate:-50% 0;background:radial-gradient(40% 45% at 50% 40%,rgba(162,59,255,.4),transparent 70%);filter:blur(30px)}}
.imp h2{{font-size:96px;line-height:.98;font-weight:620;letter-spacing:-.045em;margin-top:auto;text-wrap:balance}}
.imp .pill{{margin-top:54px;align-self:flex-start;background:#fff;color:#000;border-radius:99px;padding:24px 40px;font-size:34px;font-weight:540;margin-bottom:20px}}
.imp .pill b{{color:#7B2FE0}}
</style>
<div class="slide t-black imp">
  <div class="fx spot"></div><div class="fx big">{d.get('bg','IA')}</div>
  {head('t-black','')}
  <h2>{d['title']}</h2><div class="pill">{d['pill']}</div>
</div>"""


def destaque(d):
    cards = "".join(
        f'<div class="c"><div class="n hl" style="background:linear-gradient(100deg,#C77DFF,#A23BFF 50%,#7B2FE0);-webkit-background-clip:text;background-clip:text;color:transparent">{n}</div><div class="l">{l}</div></div>'
        for n, l in d["cards"])
    return f"""
<style>
.dst h2{{font-size:70px;line-height:1.02;font-weight:600;letter-spacing:-.04em;margin-top:90px;max-width:880px;text-wrap:balance}}
.dst .p{{font-size:34px;line-height:1.4;color:#5b5566;margin-top:28px;max-width:820px}}
.dst .row{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:auto;margin-bottom:40px}}
.dst .c{{border-radius:34px;background:#0E0B14;color:#fff;padding:46px 44px;position:relative;overflow:hidden}}
.dst .c .n{{font-size:140px;font-weight:600;letter-spacing:-.06em;line-height:.9}}
.dst .c .l{{font-size:30px;line-height:1.3;margin-top:18px;opacity:.8}}
.dst .foot{{font-size:34px;line-height:1.35;text-align:center;margin-bottom:10px}}
.dst .foot b{{font-weight:620}}
</style>
<div class="slide t-white dst">
  {head('t-white','')}
  <h2>{d['title']}</h2><p class="p">{d.get('p','')}</p>
  <div class="row">{cards}</div>
  <p class="foot">{d.get('foot','')}</p>
</div>"""


LAYOUTS = dict(cover=cover, lista=lista, stats=stats, donut=donut,
               pergunta=pergunta, cta=cta, impacto=impacto, destaque=destaque)


def render_pngs(slides):
    """slides: lista de dicts com 'layout' + campos. Retorna lista de bytes PNG."""
    out = []
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for s in slides:
            fn = LAYOUTS.get(s.get("layout"))
            if not fn:
                continue
            html = f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head><body>{fn(s)}</body></html>"
            pg.set_content(html, wait_until="networkidle")
            pg.wait_for_timeout(200)
            out.append(pg.screenshot())
        br.close()
    return out
