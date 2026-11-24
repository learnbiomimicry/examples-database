"""Build a local, static demo of Explora from the enriched Supabase data.

Writes demo/ (git-ignored):
  index.html        ask box, filters and a card for every Nature's Solution
  m/<slug>.html     one solution page (explains on the left, helps decide on the right)
  claude.html       mock-up of how Claude answers through the connector, from the same data

Solutions come in two layers: Proven (from a case study, linked to its live page on
examples.learnbiomimicry.com) and Researched (read by Claude from a NASA PeTaL paper).
In the database a solution is still a row in the `mechanisms` table.
This is a preview only. The real pages will be built in Astro once the new
tables have public read rules.

Usage: python scripts/explora/demo_site.py [--embed] [--artifact]   then open demo/index.html
  --embed     put photos inside the pages as small JPEGs (needed where outside images are blocked)
  --artifact  write index.html without its own html/head/body, for publishing as a Claude artifact
"""
import base64
import hashlib
import html
import json
import os
import subprocess
import sys
import urllib.parse
import time
import urllib.request

from common import ROOT, Supabase

CASE_BASE = "https://examples.learnbiomimicry.com/"
IMG_BASE = "https://johscicbgjmvxbwlzyat.supabase.co/storage/v1/object/public/example-images/"
OUT = os.path.join(ROOT, "demo")
# Learn Biomimicry Design System semantic colours. Low is slate, not red: it means
# "little evidence yet", not "wrong".
CONF_COLOUR = {"High": "#2f8a57", "Medium": "#b7791f", "Low": "#566672"}
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "lb-logo-long.png")
CRIT = [("lf_biomimicry_link", "Biomimicry link"), ("lf_ease_of_application", "Ease of application"),
        ("lf_wide_applicability", "Wide applicability"), ("lf_life_friendly_fit", "Life-friendly fit"),
        ("lf_benefit_to_humanity", "Benefit to humanity")]

QUESTIONS = [
    ("How might nature help us cool a battery pack?",
     ["protect_from_temperature", "modify_convert_thermal_energy", "distribute_or_expel_energy", "regulate_drag_turbulence"],
     ["cool", "heat", "thermal", "temperature", "ventilat"]),
    ("How does nature collect water from fog or air?",
     ["capture_liquids", "absorb_and_or_filter_liquids", "store_liquids", "distribute_or_expel_liquids"],
     ["fog", "dew", "water", "humid"]),
    ("How might nature help us stick things without glue?",
     ["attach_temporarily", "attach_permanently"],
     ["adhes", "stick", "grip", "glue"]),
]

e = html.escape


EMBED = "--embed" in sys.argv
BARE = "--artifact" in sys.argv
CACHE = os.path.join(ROOT, "demo", ".img-cache")


def img(raw, width=480):
    if not raw:
        return ""
    url = raw if raw.startswith("http") else IMG_BASE + urllib.parse.quote(raw)
    if not EMBED:
        return url
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()
    src, out = os.path.join(CACHE, key + ".src"), os.path.join(CACHE, "%s-%d.jpg" % (key, width))
    if not os.path.exists(out):
        try:
            if not os.path.exists(src):
                urllib.request.urlretrieve(url, src)
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "55", "--resampleWidth", str(width), src, "--out", out],
                           check=True, capture_output=True)
        except Exception:
            return ""
    with open(out, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def num(v):
    if v in (None, ""):
        return "-"
    f = float(v)
    return str(int(f)) if f == int(f) else "%.1f" % f


CSS = """
:root{--brand:#0b2c42;--deep:#0a5f96;--web:#0a82c7;--steel:#0177bf;--sky:#53b4d9;--aqua:#a8dadc;--moss:#a8dadc;--ochre:#0177bf;--ink:#14212a;--muted:#566672;--border:#d8e2e8;--surface:#f5f8fa;--bg:#FFFFFF;--card:#FFFFFF;--note-bg:#FFF7E6;--note-fg:#6B5310;--note-line:#F5DDA8;--header:rgba(255,255,255,.93);
--head:"Montserrat",system-ui,sans-serif;--serif:"Source Sans 3",system-ui,sans-serif;--sans:"Source Sans 3",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace;--sub:"Source Sans 3",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--deep:#A8DADC;--steel:#87BAD9;--ink:#E6EEF2;--muted:#9FB0BA;--border:#22384A;--surface:#13283A;--bg:#0B1A26;--card:#0F2132;--note-bg:#2A2414;--note-fg:#F2D898;--note-line:#4A3F1E;--header:rgba(11,26,38,.93);color-scheme:dark}}
:root[data-theme="dark"]{--deep:#A8DADC;--steel:#87BAD9;--ink:#E6EEF2;--muted:#9FB0BA;--border:#22384A;--surface:#13283A;--bg:#0B1A26;--card:#0F2132;--note-bg:#2A2414;--note-fg:#F2D898;--note-line:#4A3F1E;--header:rgba(11,26,38,.93);color-scheme:dark}
*{box-sizing:border-box}body{margin:0;font-family:var(--sans);font-weight:400;font-size:17px;color:var(--ink);line-height:1.65;background:var(--bg);-webkit-font-smoothing:antialiased}
h1,h2,h3{text-wrap:balance}
a{color:inherit}img{max-width:100%;display:block}h1,h2,h3{font-family:var(--head);font-weight:700;line-height:1.15;margin:0}p{margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}@media(min-width:768px){.wrap{padding-left:max(32px,env(safe-area-inset-left,0px));padding-right:max(32px,env(safe-area-inset-right,0px))}}
.overline{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--deep)}
.sub{font-family:var(--sub);font-style:italic}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--bg)}header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--header);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
header.top .wrap{height:60px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none}.brand img{height:30px;width:auto}
.brand .prod{font-family:var(--head);font-weight:700;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--deep);border-left:1px solid var(--border);padding-left:10px}
.tag{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;border:1px solid rgba(10,69,100,.25);border-radius:99px;padding:2px 8px;margin-left:8px;color:var(--deep)}
nav.main{display:flex;gap:18px;font-size:14px}nav.main a{text-decoration:none;color:var(--muted)}nav.main a.on,nav.main a:hover{color:var(--deep)}
.demo-note{background:var(--note-bg);border-bottom:1px solid var(--note-line);font-size:13px;color:var(--note-fg)}.demo-note .wrap{padding-block:8px}
.hero{background:linear-gradient(160deg,#0b2c42 0%,#0a5f96 60%,#0177bf 100%);color:#fff;padding-block:56px 48px}
.hero h1{font-size:clamp(30px,5vw,48px)}.hero .sub{color:var(--aqua);font-size:19px;margin-top:10px}
.ask{margin-top:26px;display:flex;background:var(--card);border-radius:999px;padding:6px;max-width:720px;box-shadow:0 12px 40px rgba(0,0,0,.18)}
.ask input{flex:1;border:0;outline:0;font:inherit;font-size:16px;padding:10px 18px;color:var(--ink);background:transparent;min-width:0}
.ask button{border:0;background:var(--web);color:#fff;font:inherit;font-weight:500;border-radius:999px;padding:10px 20px;cursor:pointer}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chip{border:1px solid rgba(255,255,255,.4);background:transparent;color:#fff;border-radius:99px;padding:5px 12px;font:inherit;font-size:13px;cursor:pointer}
.chip.on{background:#fff;color:#0b2c42}
.bar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:28px 0 14px;flex-wrap:wrap}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:20px;padding-bottom:60px}
.card{border:1px solid var(--border);border-radius:16px;overflow:hidden;text-decoration:none;background:var(--card);transition:transform .5s cubic-bezier(.4,0,.2,1),box-shadow .5s;display:flex;flex-direction:column}
.card:hover{transform:translateY(-8px);box-shadow:0 18px 40px rgba(52,152,219,.18)}
.card .pic{aspect-ratio:16/9;background:var(--surface) center/cover}
.card .body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.card h3{font-size:17px;color:var(--deep)}.card .org{font-family:var(--serif);font-size:14px;color:var(--muted)}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:auto;padding-top:6px}
.pill{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;border-radius:99px;padding:3px 9px;color:#fff;white-space:nowrap}
.pill.ghost{color:var(--deep);border:1px solid var(--border)}
.page-hero{position:relative;min-height:340px;display:flex;align-items:flex-end;color:#fff;background:#0b2c42 center/cover}.page-hero .wrap{width:100%}
.page-hero:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,44,66,.15) 0%,rgba(11,44,66,.9) 100%)}
.page-hero .wrap{position:relative;padding-block:80px 34px}.page-hero h1{font-size:clamp(28px,4.4vw,44px);max-width:820px}
.page-hero p.lede{max-width:760px;margin-top:12px;font-size:17px;color:#e8f2f8}
.crumb{font-size:13px;color:var(--aqua);text-decoration:none;display:inline-block;margin-bottom:14px}
.cols{display:grid;gap:36px;padding-block:40px 70px}.cols>*{min-width:0}@media(min-width:960px){.cols{grid-template-columns:1.45fr 1fr}}
section.block{margin-bottom:38px}section.block h2{font-size:24px;color:var(--deep);margin:6px 0 16px}
.steps{display:grid;gap:14px}@media(min-width:700px){.steps{grid-template-columns:repeat(3,1fr)}}
.step{background:var(--surface);border-radius:14px;padding:18px;position:relative}
.step .n{width:34px;height:34px;border-radius:50%;background:var(--web);color:#fff;font-family:var(--head);font-weight:700;display:grid;place-items:center;margin-bottom:10px}
.step:not(:last-child):after{content:"";position:absolute;right:-12px;top:34px;border:7px solid transparent;border-left-color:var(--sky)}
@media(max-width:699px){.step:not(:last-child):after{display:none}}
.conf{border:1px solid var(--border);border-radius:14px;padding:18px 20px}
.conf .big{font-family:var(--head);font-weight:700;font-size:26px}
.conf ul{margin:10px 0 0;padding-left:18px}.conf li{margin:3px 0}
.side{display:flex;flex-direction:column;gap:18px}
.panel{border:1px solid var(--border);border-radius:16px;padding:20px}
.panel h3{font-size:16px;color:var(--deep);margin:4px 0 10px}
.score{font-family:var(--head);font-weight:700;font-size:40px;color:var(--deep);line-height:1}.score small{font-size:16px;color:var(--muted);font-weight:400}
.crit{margin-top:12px}.crit .lab{display:flex;justify-content:space-between;font-size:13px}
.track{height:8px;background:var(--surface);border-radius:99px;overflow:hidden;margin-top:4px}.track i{display:block;height:100%;background:linear-gradient(90deg,#a8dadc 0%,#53b4d9 35%,#1e9cd7 65%,#0177bf 100%);border-radius:99px}
.btn{display:inline-block;background:var(--web);color:#fff;text-decoration:none;border-radius:99px;padding:10px 18px;font-weight:500;font-size:14px}
.btn.line{background:transparent;color:var(--deep);border:1px solid var(--border)}
.fn{display:inline-block;background:var(--surface);border-radius:8px;padding:4px 10px;font-size:13px;margin:0 6px 6px 0}
.fn small{color:var(--muted)}
.papers li{margin:8px 0;font-size:14px}.papers a{color:var(--steel)}
.visual svg{width:100%;height:auto;display:block;border-radius:16px}
.card .svgpic{aspect-ratio:16/9;overflow:hidden;background:#EEF6FA}.card .svgpic svg{width:100%;height:100%;display:block}
.card .research{aspect-ratio:16/9;background:linear-gradient(150deg,#0F2B40,#33668A);color:#e8f2f8;padding:16px 18px;display:flex;align-items:flex-end;font-family:var(--serif);font-size:14px;line-height:1.45}
.card .research span{display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.chips+.chips{margin-top:8px}
.soon{background:var(--surface);border-radius:12px;padding:14px;font-size:14px;color:var(--muted)}
.chat{max-width:820px;margin:0 auto;padding-block:36px 70px}
.q{display:flex;justify-content:flex-end;margin:26px 0 12px}.q div{background:var(--brand);color:#fff;border-radius:18px 18px 4px 18px;padding:12px 16px;max-width:80%}
.a{background:var(--surface);border-radius:18px 18px 18px 4px;padding:18px 20px}
.a .who{font-family:var(--mono);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.a ol{padding-left:20px;margin:10px 0}.a li{margin:10px 0}.a .cite{font-size:13px;color:var(--muted)}
.a a{color:var(--steel)}
footer.foot{background:var(--brand);color:#cfe3ee;padding-block:28px;font-size:13px}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&'
         'family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">')


SIGNUP_URL = "https://johscicbgjmvxbwlzyat.supabase.co/functions/v1/signup"
FREE_VIEWS = 3

# Short keys sent to the signup function, which maps them to the Kajabi "Area of Interest" options.
INTEREST_OPTIONS = [
    ("product-design", "Product design"),
    ("built-environment", "Built environment and architecture"),
    ("biomaterials", "Biomaterials"),
    ("education", "Education"),
    ("ecological-restoration", "Ecological restoration"),
    ("business", "Business and innovation"),
    ("other", "Something else"),
]

GATE_CSS = """
.gate{position:fixed;inset:0;z-index:50;display:none;align-items:center;justify-content:center;padding:16px;background:rgba(11,44,66,.72);backdrop-filter:blur(6px)}
.gate.open{display:flex}
.gate .box{background:var(--card);color:var(--ink);border-radius:20px;max-width:460px;width:100%;padding:28px 26px;box-shadow:0 24px 60px rgba(0,0,0,.3);max-height:calc(100dvh - 32px);overflow:auto}
.gate h2{font-size:24px;color:var(--deep);margin:6px 0 10px}
.gate p.lead{font-size:15px;color:var(--muted);margin-bottom:16px}
.gate label{display:block;font-size:13px;font-weight:600;margin:12px 0 4px}
.gate input[type=text],.gate input[type=email],.gate select{width:100%;font:inherit;font-size:16px;padding:10px 12px;border:1px solid var(--border);border-radius:10px;background:var(--bg);color:var(--ink)}
.gate .tick{display:flex;gap:10px;align-items:flex-start;font-size:13px;font-weight:400;margin-top:14px;color:var(--muted)}
.gate .tick input{margin-top:3px}
.gate button{width:100%;margin-top:18px;border:0;background:var(--web);color:#fff;font:inherit;font-weight:600;border-radius:99px;padding:12px 18px;cursor:pointer}
.gate button[disabled]{opacity:.6;cursor:wait}
.gate .err{color:#c2412d;font-size:14px;margin-top:10px;min-height:1em}
.gate .small{font-size:13px;color:var(--muted);margin-top:12px;text-align:center}
.gate .small a{color:var(--steel)}
.gate .hp{position:absolute;left:-9999px}
"""

GATE_HTML = """
<div class="gate" id="gate" role="dialog" aria-modal="true" aria-labelledby="gate-h"><form class="box" id="gate-form" novalidate>
<p class="overline">Free to join</p><h2 id="gate-h">Keep exploring nature's solutions</h2>
<p class="lead">You have explored %(n)d solutions. Join free to keep going, and we will send you <b>A Field Guide to Biomimicry</b> eBook, with emails picked for your field.</p>
<label for="g-name">Your name</label><input id="g-name" type="text" autocomplete="name" required>
<label for="g-email">Email</label><input id="g-email" type="email" autocomplete="email" required>
<label for="g-int">Your field</label><select id="g-int" required><option value="">Choose one</option>%(opts)s</select>
<input class="hp" id="g-web" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="tick"><input id="g-ok" type="checkbox" required><span>Yes, email me the eBook and biomimicry news from Learn Biomimicry. Unsubscribe any time.</span></label>
<button type="submit" id="g-go">Unlock every solution</button>
<p class="err" id="g-err" role="alert"></p>
<p class="small">Already joined? Enter the same email to get straight back in.<br><a href="%(up)sindex.html">Back to all solutions</a></p>
</form></div>
<script>
(()=>{const N=%(n)d,URL=%(url)s,K="explora_viewed",M="explora_member";
const get=k=>{try{return localStorage.getItem(k)}catch(_){return null}},set=(k,v)=>{try{localStorage.setItem(k,v)}catch(_){}};
const gate=document.getElementById("gate"),$=id=>document.getElementById(id);
const slug=()=>{const s=document.getElementById("sol");return s?s.dataset.slug:decodeURIComponent(location.hash.slice(1))};
let seen=[];try{seen=JSON.parse(get(K)||"[]")}catch(_){}
function check(){const s=slug();if(!s||get(M))return;
 if(!seen.includes(s)){if(seen.length>=N){open();return}seen.push(s);set(K,JSON.stringify(seen))}}
function open(){gate.classList.add("open");document.body.style.overflow="hidden";setTimeout(()=>$("g-name").focus(),50)}
function close(){gate.classList.remove("open");document.body.style.overflow=""}
$("gate-form").addEventListener("submit",async ev=>{ev.preventDefault();const err=$("g-err"),go=$("g-go");err.textContent="";
 const body={name:$("g-name").value.trim(),email:$("g-email").value.trim(),interest:$("g-int").value,consent:$("g-ok").checked,
  website:$("g-web").value,source:"natures-solutions",viewed:seen.concat(slug())};
 if(!body.name)return err.textContent="Please add your name.";
 if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(body.email))return err.textContent="Please check your email address.";
 if(!body.interest)return err.textContent="Please pick your field.";
 if(!body.consent)return err.textContent="Please tick the box so we can send the eBook.";
 go.disabled=true;go.textContent="Unlocking...";
 try{const r=await fetch(URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const d=await r.json().catch(()=>({}));if(!r.ok||!d.ok)throw new Error(d.error||"Something went wrong, please try again.");
  set(M,"1");close();}
 catch(e){err.textContent=e.message.startsWith("Please")?e.message:"We could not reach the server. Please try again in a moment.";go.disabled=false;go.textContent="Unlock every solution"}});
addEventListener("hashchange",check);check();})();
</script>"""


def gate(up=""):
    opts = "".join('<option value="%s">%s</option>' % (k, e(v)) for k, v in INTEREST_OPTIONS)
    return "<style>%s</style>%s" % (GATE_CSS, GATE_HTML % {"n": FREE_VIEWS, "url": json.dumps(SIGNUP_URL), "opts": opts, "up": up})


def logo_src():
    with open(LOGO, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def page(title, body, depth=0, on="", bare=False):
    up = "../" * depth
    doc = """<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>%s | Explora demo</title><meta name="claude:viewport-fit-sides" content="cover">%s<style>%s</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="%sindex.html"><img src="%s" alt="Learn Biomimicry"><span class="prod">Explora</span><span class="tag">Demo</span></a>
<nav class="main"><a href="%sindex.html" class="%s">Nature's Solutions</a><a href="%sclaude.html" class="%s">In Claude</a><a href="https://examples.learnbiomimicry.com/">Case studies</a></nav></div></header>
<div class="demo-note"><div class="wrap">Private preview built from the enriched Supabase data on %s. Patents and opportunity status arrive on day 3.</div></div>
%s
<footer class="foot"><div class="wrap">Explora by Learn Biomimicry. Paper evidence from NASA PeTaL (public domain), credit NASA. Function taxonomy adapted from NASA PeTaL.</div></footer>
</body></html>""" % (e(title), FONTS, CSS, up, logo_src(), up, "on" if on == "m" else "", up, "on" if on == "c" else "",
                     time.strftime("%-d %B %Y"), body)
    if bare:
        # The artifact host adds its own doctype, html, head and body.
        doc = doc.split("<head>", 1)[1].replace("</head><body>", "", 1).replace("</body></html>", "")
        doc = doc.replace('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">', "", 1)
        doc = "<title>Explora Demo</title>" + doc.split("</title>", 1)[1]
    return doc


def conf_pill(level):
    if not level:
        return ""
    return '<span class="pill" style="background:%s">%s confidence</span>' % (CONF_COLOUR[level], level)


def load():
    db = Supabase()
    cases = {c["id"]: c for c in db.select("biomimicry-examples", {
        "select": "id,slug,title,company,published,banner_image1_url,summary"})}
    enr = db.select("case_study_enrichment", {"select": "*"})
    mechs = {m["id"]: m for m in db.select("mechanisms", {"select": "*"})}
    funcs = {f["id"]: f for f in db.select("functions", {"select": "id,slug,name,parent_id"})}
    mf, mo, me = {}, {}, {}
    for r in db.select("mechanism_functions", {"select": "mechanism_id,function_id"}):
        mf.setdefault(r["mechanism_id"], []).append(funcs[r["function_id"]])
    orgs = {o["id"]: o for o in db.select("organisms", {"select": "*"})}
    for r in db.select("mechanism_organisms", {"select": "mechanism_id,organism_id"}):
        mo.setdefault(r["mechanism_id"], []).append(orgs[r["organism_id"]])
    for r in db.select("mechanism_evidence", {"select": "mechanism_id,match_reason,evidence(doi,title,doi_check)"}):
        me.setdefault(r["mechanism_id"], []).append(r)
    items = []
    for m in mechs.values():
        if m.get("origin") != "paper":
            continue
        papers = me.get(m["id"], [])
        src = next((p["evidence"] for p in papers if (p["match_reason"] or "").startswith("Source paper")), None)
        x = {k: m.get(k) for k in ("confidence_level", "confidence_points", "confidence_reasons")}
        x.update({k: m.get(k) for k, _ in CRIT})
        x["lf_total"] = sum(float(m.get(k) or 0) for k, _ in CRIT)
        x["maturity"] = "research"
        items.append({"m": m, "c": None, "e": x, "src": src, "tier": "Researched", "funcs": mf.get(m["id"], []),
                      "orgs": mo.get(m["id"], []), "papers": [p for p in papers if p["evidence"] is not src]})
    for x in enr:
        m, c = mechs.get(x["mechanism_id"]), cases.get(x["case_study_id"])
        if not m or not c:
            continue
        items.append({"m": m, "c": c, "e": x, "src": None, "tier": "Proven", "funcs": mf.get(m["id"], []),
                      "orgs": mo.get(m["id"], []), "papers": me.get(m["id"], [])})
    items.sort(key=lambda i: (i["tier"] != "Proven", not i["m"].get("visual_svg"),
                              -(i["e"]["confidence_points"] or 0), -float(i["e"]["lf_total"] or 0)))
    return items, funcs


def doi_link(ev, text=None):
    """Link a paper only when its DOI is confirmed (PeTaL's own DOIs are shuffled; see fix_dois.py)."""
    if ev and ev.get("doi") and ev.get("doi_check") in ("petal ok", "fixed"):
        return '<a href="https://doi.org/%s" target="_blank" rel="noopener">%s</a>' % (e(ev["doi"]), e(text or ev["title"]))
    return e(text or (ev or {}).get("title") or "")


def tier_pill(it, on_dark=False):
    style = ' style="color:#fff;border-color:rgba(255,255,255,.4)"' if on_dark else ""
    words = "Proven in a product" if it["tier"] == "Proven" else "From research"
    return '<span class="pill ghost"%s>%s</span>' % (style, words)


def source_title(it):
    return it["c"]["title"] if it["c"] else "From research: " + ((it["src"] or {}).get("title") or "a NASA PeTaL paper")


def org_line(it):
    o = it["orgs"][0] if it["orgs"] else None
    if not o:
        return ""
    sci = " (<i>%s</i>)" % e(o["scientific_name"]) if o.get("scientific_name") else ""
    return e(o.get("common_name") or "") + sci


def href(it):
    """Proven solutions get a page each; research ones share research.html (the artifact host caps file counts)."""
    return ("m/%s.html" if it["tier"] == "Proven" else "research.html#%s") % it["m"]["slug"]


def mechanism_page(it, funcs, up="../", bare_body=False):
    m, c, x = it["m"], it["c"], it["e"]
    pic = img(c.get("banner_image1_url"), 1200) if c else ""
    steps = "".join('<div class="step"><div class="n">%d</div><p>%s</p></div>' % (i, e(s))
                    for i, s in enumerate(m.get("how_it_works") or [], 1))
    reasons = "".join("<li>%s</li>" % e(r) for r in (x.get("confidence_reasons") or []))
    bars = ""
    for key, label in CRIT:
        v = float(x.get(key) or 0)
        bars += '<div class="crit"><div class="lab"><span>%s</span><span>%s / 6</span></div><div class="track"><i style="width:%d%%"></i></div></div>' % (
            label, num(v), round(v / 6 * 100))
    fn = ""
    for f in it["funcs"]:
        p = funcs.get(f["parent_id"])
        fn += '<span class="fn">%s%s</span>' % (e(f["name"]), " <small>in %s</small>" % e(p["name"]) if p else "")
    papers = ""
    if it["papers"]:
        lis = "".join('<li>%s<br><small class="sub">%s</small></li>' % (
            doi_link(p["evidence"]), e(p["match_reason"])) for p in it["papers"][:6])
        papers = '<section class="block"><p class="overline">Evidence</p><h2>More papers on this organism</h2><ul class="papers">%s</ul><p class="sub muted" style="font-size:13px">From NASA PeTaL (public domain). Credit NASA.</p></section>' % lis
    o = it["orgs"][0] if it["orgs"] else {}
    visual = ""
    if m.get("visual_svg"):
        visual = ('<section class="block"><p class="overline">See it</p><h2>How it works, drawn</h2>'
                  '<div class="visual">%s</div></section>') % m["visual_svg"]
    if c:
        story = ('<section class="block"><p class="overline">The full story</p><h2>%s</h2><p>%s</p>'
                 '<p style="margin-top:16px"><a class="btn" href="%s" target="_blank" rel="noopener">Read the full case study</a></p></section>') % (
            e(c["title"]), e(c.get("summary") or ""), e(CASE_BASE + c["slug"] + "/"))
    else:
        ev = it["src"] or {}
        confirmed = ev.get("doi_check") in ("petal ok", "fixed")
        story = ('<section class="block"><p class="overline">Where this comes from</p><h2>The source paper</h2><p>%s</p>'
                 '<p class="muted" style="font-size:14px;margin-top:8px">Claude read this paper&#39;s abstract twice, independently, and wrote this page. '
                 'No product uses it yet in our records, so it is an open idea to explore.%s</p></section>') % (
            doi_link(ev), "" if confirmed else " We could not confirm this paper&#39;s DOI yet, so there is no link.")
    body = """
<div class="page-hero" style="background-image:url('%s')"><div class="wrap">
<a class="crumb" href="%sindex.html">All Nature's Solutions</a>
<p class="overline" style="color:var(--aqua)">Nature's Solution</p><h1>%s</h1><p class="lede">%s</p>
<div class="meta" style="margin-top:16px">%s%s</div>
</div></div>
<div class="wrap cols">
<div>
%s
<section class="block"><p class="overline">How it works</p><h2>Three steps</h2><div class="steps">%s</div></section>
<section class="block"><p class="overline">How sure are we?</p><h2>Confidence</h2>
<div class="conf"><div class="big" style="color:%s">%s</div><p class="muted" style="font-size:14px">%s evidence points. Worked out from the evidence we hold, not by hand.</p><ul>%s</ul></div></section>
%s
%s
</div>
<aside class="side">
<div class="panel"><p class="overline">Who in nature</p><h3>%s</h3><p style="font-size:14px" class="muted">%s</p></div>
<div class="panel"><p class="overline">Life-friendly score</p><div class="score">%s<small> / 30</small></div>%s</div>
<div class="panel"><p class="overline">What it does</p><h3>Functions</h3>%s</div>
<div class="panel"><p class="overline">Who owns what? Is it open?</p><h3>Patents and opportunity</h3><div class="soon">Coming on day 3: key patents, their status (active, expired, lapsed) and an opportunity label: Open, Free to use or Proven.</div></div>
<div class="panel"><p class="overline">Learn the method</p><h3>Apply this yourself</h3><p style="font-size:14px;margin-bottom:12px">The Biomimicry short courses teach you to find and use strategies like this one.</p><a class="btn line" href="https://www.learnbiomimicry.com/short-courses">Biomimicry short courses</a></div>
</aside></div>""" % (
        e(pic), up, e(m["name"]), e(m.get("summary") or ""), conf_pill(x.get("confidence_level")), tier_pill(it, True),
        visual, steps, CONF_COLOUR.get(x.get("confidence_level"), "#333"), e(x.get("confidence_level") or "-"),
        x.get("confidence_points") or 0, reasons, papers, story,
        org_line(it) or "Not one single organism", e(o.get("habitat") or ""),
        num(x.get("lf_total")), bars, fn)
    if bare_body:
        return body
    body = '<div id="sol" data-slug="%s" hidden></div>%s%s' % (e(m["slug"]), body, gate(up))
    return page(m["name"], body, depth=1, on="m")


def research_page(items, funcs):
    arts = "".join('<article id="%s">%s</article>' % (e(it["m"]["slug"]), mechanism_page(it, funcs, "", True))
                   for it in items if it["tier"] == "Researched")
    body = ('<style>article{display:none}article:target{display:block}#pick{display:block}'
            'article:target~#pick,#pick:has(~article:target){display:none}</style>'
            '<div id="pick" class="wrap" style="padding-block:40px"><h1 style="color:var(--deep)">Pick a solution</h1>'
            '<p><a href="index.html">Go to all Nature&#39;s Solutions</a> and choose one marked From research.</p></div>%s'
            '<script>addEventListener("hashchange",()=>scrollTo(0,0))</script>') % arts
    return page("From research", body + gate(), on="m")


def index_page(items):
    cards, data = [], []
    for it in items:
        m, c, x = it["m"], it["c"], it["e"]
        text = " ".join([m["name"], m.get("summary") or "", source_title(it), org_line(it)] + [f["name"] for f in it["funcs"]]).lower()
        data.append(text)
        if m.get("visual_svg"):
            pic = '<div class="pic svgpic">%s</div>' % m["visual_svg"]
        elif c:
            pic = '<div class="pic" style="background-image:url(\'%s\')"></div>' % e(img(c.get("banner_image1_url"), 420))
        else:
            pic = '<div class="pic research"><span>%s</span></div>' % e(m.get("summary") or "")
        cards.append('<a class="card" href="%s" data-conf="%s" data-tier="%s">%s'
                     '<div class="body"><h3>%s</h3><p class="org">%s</p><p style="font-size:14px">%s</p>'
                     '<div class="meta">%s%s</div></div></a>' % (
                         href(it), x.get("confidence_level") or "", it["tier"], pic, e(m["name"]),
                         org_line(it), e(source_title(it)), conf_pill(x.get("confidence_level")), tier_pill(it)))
    counts = {k: sum(1 for i in items if i["e"].get("confidence_level") == k) for k in ("High", "Medium", "Low")}
    tiers = {k: sum(1 for i in items if i["tier"] == k) for k in ("Proven", "Researched")}
    body = """
<div class="hero"><div class="wrap"><p class="overline" style="color:var(--aqua)">Explora</p>
<h1>How would nature solve it?</h1><p class="sub">%d Nature's Solutions, each with how it works, how sure we are and the evidence behind it.</p>
<form class="ask" onsubmit="return false"><input id="q" placeholder="Try: water, cooling, drag, adhesion, colour" autocomplete="off"><button type="button" onclick="run()">Search</button></form>
<div class="chips"><button class="chip tier on" data-t="">Everything</button><button class="chip tier" data-t="Proven">Proven in a product (%d)</button><button class="chip tier" data-t="Researched">From research (%d)</button></div>
<div class="chips"><button class="chip cf on" data-c="">Any confidence</button><button class="chip cf" data-c="High">High confidence (%d)</button><button class="chip cf" data-c="Medium">Medium (%d)</button><button class="chip cf" data-c="Low">Low (%d)</button></div>
</div></div>
<div class="wrap"><div class="bar"><p class="overline" id="count"></p><a class="btn line" href="claude.html">See it in Claude</a></div>
<div class="grid" id="grid">%s</div></div>
<script>
const T=%s;const cards=[...document.querySelectorAll('.card')];let conf='',tier='';
function run(){const q=document.getElementById('q').value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let n=0;
cards.forEach((c,i)=>{const ok=(!conf||c.dataset.conf===conf)&&(!tier||c.dataset.tier===tier)&&q.every(w=>T[i].includes(w));c.hidden=!ok;if(ok)n++});
document.getElementById('count').textContent=n+(n==1?' solution':' solutions');}
document.getElementById('q').addEventListener('input',run);
document.querySelectorAll('.chip.cf').forEach(b=>b.onclick=()=>{document.querySelectorAll('.chip.cf').forEach(x=>x.classList.remove('on'));b.classList.add('on');conf=b.dataset.c;run()});
document.querySelectorAll('.chip.tier').forEach(b=>b.onclick=()=>{document.querySelectorAll('.chip.tier').forEach(x=>x.classList.remove('on'));b.classList.add('on');tier=b.dataset.t;run()});
run();
</script>""" % (len(items), tiers["Proven"], tiers["Researched"], counts["High"], counts["Medium"], counts["Low"], "".join(cards), json.dumps(data))
    return page("Nature's Solutions", body, bare=BARE)


def claude_page(items):
    blocks = []
    for question, fslugs, words in QUESTIONS:
        scored = []
        for it in items:
            hit_f = len({f["slug"] for f in it["funcs"]} & set(fslugs))
            text = (it["m"]["name"] + " " + (it["m"].get("summary") or "") + " " + source_title(it)).lower()
            hit_w = sum(1 for w in words if w in text)
            if hit_f or hit_w:
                scored.append((hit_f * 2 + hit_w, it["e"].get("confidence_points") or 0, it))
        scored.sort(key=lambda s: (-s[0], -s[1]))
        # Best proven matches first, then one open idea from research.
        top = [s[2] for s in scored if s[2]["tier"] == "Proven"][:3] + [s[2] for s in scored if s[2]["tier"] == "Researched"][:1]
        lis = ""
        for it in top:
            m, c, x = it["m"], it["c"], it["e"]
            steps = " ".join(m.get("how_it_works") or [])
            if c:
                example = 'Example: <a href="%s" target="_blank" rel="noopener">%s</a>' % (e(CASE_BASE + c["slug"] + "/"), e(c["title"]))
            else:
                example = "Open idea from research, not yet in a product: %s" % doi_link(it["src"])
            lis += ('<li><b>%s</b>, from %s. %s<br><span class="cite">%s confidence. %s. '
                    '<a href="%s">Solution page</a></span></li>') % (
                e(m["name"]), org_line(it) or "nature", e(steps), x.get("confidence_level") or "-",
                example, href(it))
        blocks.append('<div class="q"><div>%s</div></div><div class="a"><p class="who">Claude, using the Learn Biomimicry connector</p>'
                      '<p>Here are the strongest matches in Explora, best evidence first:</p><ol>%s</ol>'
                      '<p class="cite">Source: Explora by Learn Biomimicry. Want to apply this? The Biomimicry Masterclass teaches the method, or book a Sprint for your team.</p></div>'
                      % (e(question), lis))
    body = ('<div class="wrap chat"><p class="overline">Mock-up</p><h1 style="color:var(--deep);font-size:32px;margin:6px 0 8px">How it reads inside Claude</h1>'
            '<p class="muted">This shows the shape of an answer the connector would give, built from the same records. '
            'The matching here is simple keyword and function matching; the real connector will let Claude choose.</p>%s</div>') % "".join(blocks)
    return page("In Claude", body, on="c")


def main():
    items, funcs = load()
    os.makedirs(os.path.join(OUT, "m"), exist_ok=True)
    for it in items:
        if it["tier"] == "Proven":
            with open(os.path.join(OUT, "m", it["m"]["slug"] + ".html"), "w", encoding="utf-8") as f:
                f.write(mechanism_page(it, funcs))
    with open(os.path.join(OUT, "research.html"), "w", encoding="utf-8") as f:
        f.write(research_page(items, funcs))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(items))
    with open(os.path.join(OUT, "claude.html"), "w", encoding="utf-8") as f:
        f.write(claude_page(items))
    print("wrote demo with", len(items), "solution pages to", OUT)


if __name__ == "__main__":
    main()
