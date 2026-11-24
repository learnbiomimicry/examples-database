"""Hand-drawn SVG illustrations for three Nature's Solutions.

Each SVG carries its own background, so it reads the same in light and dark mode.
Run: python scripts/explora/visuals/make_visuals.py [--save]  (--save writes them to mechanisms.visual_svg)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "font-family=\"IBM Plex Sans, system-ui, sans-serif\""
DEEP, STEEL, SKY, AQUA, MOSS, OCHRE, INK = "#0A4564", "#33668A", "#87BAD9", "#A8DADC", "#576E3D", "#B0A64C", "#231F20"
WARM = "#D98A3D"


def svg(body, label, pid, w=640, h=360):
    """Arrowheads: use marker-end="url(#ar-sky)" etc. Ids get a per-visual prefix so inline SVGs never clash."""
    marks = ""
    for name, col in (("sky", SKY), ("warm", WARM), ("ink", INK), ("steel", STEEL)):
        marks += ('<marker id="%s-%s" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
                  '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>') % (pid, name, col)
    body = body.replace("url(#ar-", "url(#%s-" % pid)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="%s" %s>'
            '<defs>%s</defs>%s</svg>') % (w, h, label, FONT, marks, body)


def badge(x, y, n, fill=DEEP, text="#fff"):
    return '<circle cx="%d" cy="%d" r="12" fill="%s"/><text x="%d" y="%d" font-size="13" font-weight="700" fill="%s" text-anchor="middle">%d</text>' % (
        x, y, fill, x, y + 4.5, text, n)


def label(x, y, n, lines, fill=INK, bfill=DEEP, anchor="start"):
    out = badge(x, y, n, bfill)
    for i, t in enumerate(lines):
        out += '<text x="%d" y="%d" font-size="14" fill="%s" text-anchor="%s">%s</text>' % (x + 20, y + 5 + i * 18, fill, anchor, t)
    return out


# 1. Namib Desert beetle: catching fog on bumps
def beetle():
    b = '<rect width="640" height="360" rx="16" fill="#EEF6FA"/>'
    # fog
    import random
    rnd = random.Random(4)
    for _ in range(46):
        x, y = rnd.uniform(150, 420), rnd.uniform(28, 120)
        b += '<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity=".75"/>' % (x, y, rnd.uniform(1.5, 3), SKY)
    b += '<text x="285" y="22" font-size="13" fill="%s" text-anchor="middle" font-style="italic">fog drifting in from the sea</text>' % STEEL
    for x in (200, 290, 380):
        b += '<path d="M%d,108 l18,22" stroke="%s" stroke-width="2" marker-end="url(#ar-sky)" fill="none"/>' % (x, SKY)
    # tilted shell surface (beetle stands head down into the wind)
    g = '<rect x="20" y="200" width="600" height="46" rx="6" fill="%s"/>' % DEEP
    g += '<text x="300" y="229" font-size="13" fill="#cfe3ee" text-anchor="middle">waxy surface that repels water</text>'
    for i, cx in enumerate((100, 210, 320, 430)):
        g += '<ellipse cx="%d" cy="201" rx="30" ry="13" fill="%s"/>' % (cx, AQUA)
    g += '<circle cx="100" cy="186" r="4" fill="%s"/><circle cx="92" cy="190" r="3" fill="%s"/>' % (STEEL, STEEL)
    g += '<circle cx="210" cy="182" r="9" fill="%s"/>' % STEEL
    g += '<circle cx="320" cy="175" r="16" fill="%s"/>' % STEEL
    g += '<circle cx="530" cy="182" r="17" fill="%s"/>' % STEEL
    for dy in (-8, 0, 8):
        g += '<path d="M%d,%d h-28" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".6"/>' % (500, 182 + dy, STEEL)
    b += '<g transform="rotate(14 320 210)">%s</g>' % g
    # labels
    b += label(20, 70, 1, ["Fog droplets stick", "to water-loving bumps"])
    b += label(440, 70, 2, ["Droplets join and grow", "until they are heavy"])
    b += '<path d="M470,92 L355,165" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % INK
    b += label(330, 318, 3, ["Heavy drops roll down the", "waxy surface to the mouth"])
    b += '<path d="M500,300 L526,254" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % INK
    b += '<path d="M28,96 L28,147 L80,147" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % INK
    # legend
    b += '<ellipse cx="34" cy="322" rx="12" ry="6" fill="%s"/><text x="54" y="327" font-size="13" fill="%s">water-loving bump</text>' % (AQUA, INK)
    b += '<rect x="22" y="336" width="24" height="10" rx="2" fill="%s"/><text x="54" y="346" font-size="13" fill="%s">water-repelling wax</text>' % (DEEP, INK)
    return svg(b, "Fog droplets gather on water-loving bumps on a beetle's back, grow, then roll down to its mouth", "vb")


# 2. Termite-style cooling: day and night
def building(x0, wall, room):
    s = '<rect x="%d" y="140" width="180" height="160" fill="%s"/>' % (x0, wall)
    for cx in (x0 + 25, x0 + 135):
        s += '<rect x="%d" y="80" width="20" height="62" fill="%s"/>' % (cx, wall)
    for i in range(3):
        s += '<rect x="%d" y="%d" width="140" height="36" rx="3" fill="%s"/>' % (x0 + 20, 158 + i * 46, room)
    return s


def termite():
    b = '<rect width="640" height="360" rx="16" fill="#F2F7EE"/>'
    b += '<path d="M16,0 h294 v330 h-310 v-304 a16,16 0 0 1 16,-16 z" fill="#EAF4FA"/>'
    b += '<path d="M330,0 h294 a16,16 0 0 1 16,16 v314 h-310 z" fill="#0F2B40"/>'
    b += '<line x1="0" y1="300" x2="640" y2="300" stroke="%s" stroke-width="3"/>' % MOSS
    # day
    b += '<circle cx="40" cy="44" r="18" fill="#F2C14E"/>'
    for a in range(0, 360, 45):
        r = math.radians(a)
        b += '<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#F2C14E" stroke-width="2.5" stroke-linecap="round"/>' % (
            40 + 24 * math.cos(r), 44 + 24 * math.sin(r), 40 + 32 * math.cos(r), 44 + 32 * math.sin(r))
    b += building(70, "#E3B676", "#F7F1E3")
    for x in (128, 160, 192):
        b += '<path d="M%d,62 q6,8 0,16 q-6,8 0,16 v8" stroke="%s" stroke-width="2.5" fill="none" marker-end="url(#ar-warm)"/>' % (x, WARM)
    for i in range(3):
        b += '<text x="160" y="%d" font-size="12" fill="%s" text-anchor="middle">cool room</text>' % (180 + i * 46, STEEL)
    b += label(80, 24, 1, ["Day: thick walls soak up heat"])
    # night
    b += '<path d="M600,34 a16,16 0 1 0 12,26 a13,13 0 1 1 -12,-26 z" fill="#E6EEF2"/>'
    b += building(390, "#4E6E86", "#1C3A52")
    for x in (350, 600):
        d = 1 if x < 400 else -1
        b += '<path d="M%d,282 h%d" stroke="%s" stroke-width="3" marker-end="url(#ar-sky)"/>' % (x, d * 32, SKY)
    for x in (430, 480, 530):
        b += '<path d="M%d,284 v-130" stroke="%s" stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#ar-sky)"/>' % (x, SKY)
    for x in (425, 535):
        b += '<path d="M%d,96 v-44" stroke="%s" stroke-width="3" marker-end="url(#ar-warm)"/>' % (x, WARM)
    b += label(346, 315, 2, ["Cool night air drawn in low"], fill="#E6EEF2", bfill=STEEL)
    b += label(452, 24, 3, ["Warm air leaves", "up tall shafts"], fill="#E6EEF2", bfill=WARM)
    b += '<text x="320" y="350" font-size="13" fill="%s" text-anchor="middle" font-style="italic">Inspired by how termite mounds are said to stay cool</text>' % MOSS
    return svg(b, "By day thick walls absorb heat; at night cool air enters low and warm air leaves through tall shafts", "vt")


# 3. Humpback whale flipper: bumps on the leading edge
def flipper_path():
    pts = []
    n, top, bot = 9, (118, 40), (72, 316)
    for i in range(n * 8 + 1):
        t = i / (n * 8)
        x = top[0] + (bot[0] - top[0]) * t
        y = top[1] + (bot[1] - top[1]) * t
        bump = abs(math.sin(math.pi * n * t)) * 9 * (1 - 0.5 * t)
        pts.append((x - bump, y))
    d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
    d += " Q100,330 112,310 C140,250 150,120 150,60 Q148,30 118,40 Z"
    return d


def airfoil(x, y, bumpy):
    a = '<g transform="translate(%d %d) rotate(16)">' % (x, y)
    a += '<path d="M0,0 C10,-26 110,-30 230,0 C110,8 10,14 0,0 Z" fill="%s"/>' % ("#5C7F96" if not bumpy else DEEP)
    a += '</g>'
    return a


def whale():
    b = '<rect width="640" height="360" rx="16" fill="#EEF6FA"/>'
    b += '<g transform="translate(22 46) scale(.82)"><path d="%s" fill="%s"/></g>' % (flipper_path(), DEEP)
    b += '<text x="110" y="350" font-size="12" fill="%s" text-anchor="middle">flipper seen from above</text>' % STEEL
    b += label(12, 22, 1, ["Bumps along", "the front edge"])
    b += '<line x1="200" y1="10" x2="200" y2="350" stroke="#D5E4EC" stroke-width="1.5"/>'
    # smooth edge, stalling
    b += '<text x="220" y="30" font-size="14" font-weight="700" fill="%s">Smooth edge, steep angle</text>' % INK
    for i, yy in enumerate((70, 92)):
        b += '<path d="M220,%d H300" stroke="%s" stroke-width="2" fill="none"/>' % (yy, SKY)
    b += airfoil(310, 100, False)
    b += '<path d="M220,92 H300 C320,80 345,64 380,58 C420,52 460,60 520,48" stroke="%s" stroke-width="2" fill="none" marker-end="url(#ar-sky)"/>' % SKY
    b += '<path d="M220,70 H300 C330,56 380,40 520,30" stroke="%s" stroke-width="2" fill="none" marker-end="url(#ar-sky)"/>' % SKY
    for cx, cy, r in ((420, 96, 12), (465, 112, 15), (515, 126, 13), (560, 138, 10)):
        b += '<path d="M%d,%d a%d,%d 0 1 1 -%d,0 a%d,%d 0 1 1 %d,4" stroke="%s" stroke-width="1.6" fill="none" opacity=".8"/>' % (
            cx + r, cy, r, r, 2 * r, r * .7, r * .7, r * 1.4, "#9AA9B3")
    b += '<text x="220" y="150" font-size="13" fill="%s">flow breaks away: stall</text>' % "#6B7B86"
    # bumpy edge, attached
    b += '<text x="220" y="210" font-size="14" font-weight="700" fill="%s">With bumps, same angle</text>' % INK
    b += airfoil(310, 270, True)
    b += '<path d="M220,262 H300 C330,240 380,250 420,268 C460,286 500,300 560,318" stroke="%s" stroke-width="2" fill="none" marker-end="url(#ar-sky)"/>' % SKY
    b += '<path d="M220,240 H300 C335,214 390,226 440,246 C480,262 520,278 580,296" stroke="%s" stroke-width="2" fill="none" marker-end="url(#ar-sky)"/>' % SKY
    for cx, cy in ((352, 240), (392, 250)):
        b += '<path d="M%d,%d a7,7 0 1 1 -14,0 a5,5 0 1 1 10,2" stroke="%s" stroke-width="2" fill="none"/>' % (cx, cy, STEEL)
    b += label(480, 206, 2, ["Bumps make", "small swirls"])
    b += '<path d="M468,214 L400,242" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' % INK
    b += label(232, 336, 3, ["Flow stays on, so lift keeps going"])
    return svg(b, "A humpback whale flipper has bumps on its front edge; they make small swirls that keep flow attached at steep angles", "vw")


VISUALS = {
    "bumps-that-attract-water-on-a-surface-that-repels-it": beetle,
    "night-air-flushing-with-chimneys-and-heavy-thermal-mass": termite,
    "bumpy-leading-edge-that-delays-stall": whale,
}

if __name__ == "__main__":
    out = {}
    for slug, fn in VISUALS.items():
        out[slug] = fn()
        with open(os.path.join(HERE, slug + ".svg"), "w", encoding="utf-8") as f:
            f.write(out[slug])
    if "--save" in sys.argv:
        sys.path.insert(0, os.path.dirname(HERE))
        from common import Supabase
        db = Supabase()
        for slug, s in out.items():
            db.update("mechanisms", {"slug": slug}, {"visual_svg": s})
        print("saved", len(out), "visuals to mechanisms.visual_svg")
    print("wrote", len(out), "svgs")
