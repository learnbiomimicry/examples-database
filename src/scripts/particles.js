// Particle banner, ported from Explora's ParticleBanner component.
// Particles scatter across the canvas, bloom into an image silhouette over 4.5 s,
// then float, sparkle and spring away from the cursor.
const BLOOM_DURATION = 4500;
const REPEL_RADIUS = 42;
const REPEL_STRENGTH = 3.2;
const SPRING_K = 0.018;
const DAMPING = 0.78;
const rnd = (lo, hi) => lo + Math.random() * (hi - lo);

function parseColor(c) {
  const m = c.match(/^#([0-9a-f]{6})$/i);
  if (m) { const h = parseInt(m[1], 16); return [(h >> 16) & 255, (h >> 8) & 255, h & 255]; }
  const r = c.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
  return r ? [+r[1], +r[2], +r[3]] : [10, 69, 100];
}

export function particleBanner(canvas, { src, color = "#0A4564", density = 3 }) {
  const ctx = canvas.getContext("2d");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let particles = [];
  let start = null;
  let raf = 0;
  let w = 0, h = 0;
  let rgb = parseColor(color);
  let mouse = { x: -9999, y: -9999 };
  let current = src;

  function build() {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min((w * 0.52) / img.naturalWidth, (h * 0.94) / img.naturalHeight);
      const iw = Math.max(1, Math.round(img.naturalWidth * scale));
      const ih = Math.max(1, Math.round(img.naturalHeight * scale));
      const off = document.createElement("canvas");
      off.width = iw; off.height = ih;
      const o = off.getContext("2d");
      o.drawImage(img, 0, 0, iw, ih);
      const px = o.getImageData(0, 0, iw, ih).data;
      const ox = w * (w < 640 ? 0.6 : 0.68) - iw / 2;
      const oy = (h - ih) / 2;
      const out = [];
      for (let y = 0; y < ih; y += density) {
        for (let x = 0; x < iw; x += density) {
          const i = (y * iw + x) * 4;
          if (px[i + 3] < 60) continue;
          // Skip near-white backgrounds (the silhouettes are JPEGs, as in Explora).
          if (px[i] > 205 && px[i + 1] > 205 && px[i + 2] > 210) continue;
          const depth = 0.3 + (1 - y / ih) * 0.7;
          const t = Math.random();
          const radius = t < 0.35 ? rnd(0.7, 1.2) : t < 0.8 ? rnd(1.3, 2.2) * (0.75 + depth * 0.5) : rnd(2.4, 3.6) * (0.65 + depth * 0.45);
          out.push({
            sx: Math.random() * w, sy: Math.random() * h,
            rx: ox + x, ry: oy + y,
            tx: Math.random() * w, ty: Math.random() * h,
            vx: 0, vy: 0, radius, depth,
            base: 0.28 + depth * 0.52, cur: 0,
            fp: Math.random() * Math.PI * 2, fax: rnd(0.12, 0.4), fay: rnd(0.08, 0.28),
            fsx: rnd(0.000035, 0.000075), fsy: rnd(0.000025, 0.00006),
            sp: Math.random() * Math.PI * 2, ss: rnd(0.00035, 0.0011), sa: rnd(0.04, 0.13),
            pp: Math.random() * Math.PI * 2, ps: rnd(0.000018, 0.000055), pa: rnd(0.06, 0.16),
          });
        }
      }
      particles = out;
      start = null;
    };
    img.src = current;
  }

  function size() {
    const r = canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = r.width; h = r.height;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
  }

  function draw(ts) {
    if (start === null) start = ts;
    const prog = reduce ? 1 : Math.min((ts - start) / BLOOM_DURATION, 1);
    const ease = prog < 0.5 ? 4 * prog ** 3 : 1 - (-2 * prog + 2) ** 3 / 2;
    ctx.clearRect(0, 0, w, h);
    const [cr, cg, cb] = rgb;
    for (const p of particles) {
      const hx = p.rx + Math.sin(ts * p.fsx + p.fp) * p.fax;
      const hy = p.ry + Math.cos(ts * p.fsy + p.fp * 0.73) * p.fay;
      const dx = p.tx - mouse.x, dy = p.ty - mouse.y;
      const d = Math.hypot(dx, dy);
      let rx = 0, ry = 0;
      if (d < REPEL_RADIUS && d > 0.1) { const f = REPEL_STRENGTH * (1 - d / REPEL_RADIUS); rx = (dx / d) * f; ry = (dy / d) * f; }
      p.vx = (p.vx + (hx - p.tx) * SPRING_K + rx) * DAMPING;
      p.vy = (p.vy + (hy - p.ty) * SPRING_K + ry) * DAMPING;
      p.tx += p.vx; p.ty += p.vy;
      const nx = p.sx + (p.tx - p.sx) * ease;
      const ny = p.sy + (p.ty - p.sy) * ease;
      p.cur += (p.base * ease - p.cur) * (reduce ? 1 : 0.038);
      if (p.cur < 0.006) continue;
      const spark = 0.5 + 0.35 * Math.sin(ts * p.ss + p.sp) + 0.15 * Math.sin(ts * p.ss * 1.73 + p.sp * 2.1);
      const pulse = 0.5 + 0.5 * Math.sin(ts * p.ps + p.pp);
      const op = p.cur * (1 - p.sa + p.sa * spark) * (1 - p.pa + p.pa * pulse);
      if (op < 0.005) continue;
      // Lighter, bluer tint towards the top, as in Explora.
      const r = Math.round(cr + (52 - cr) * p.depth * 0.38);
      const g = Math.round(cg + (152 - cg) * p.depth * 0.33);
      const b = Math.round(cb + (219 - cb) * p.depth * 0.28);
      if (p.radius > 1.2 && p.depth > 0.6 && op > 0.1) {
        const hr = p.radius * 3.4;
        const grad = ctx.createRadialGradient(nx, ny, 0, nx, ny, hr);
        grad.addColorStop(0, `rgba(${r},${g},${b},${(op * 0.22).toFixed(3)})`);
        grad.addColorStop(1, `rgba(${r},${g},${b},0)`);
        ctx.beginPath(); ctx.arc(nx, ny, hr, 0, Math.PI * 2); ctx.fillStyle = grad; ctx.fill();
      }
      ctx.beginPath(); ctx.arc(nx, ny, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r},${g},${b},${op.toFixed(3)})`; ctx.fill();
    }
    raf = requestAnimationFrame(draw);
  }

  canvas.addEventListener("mousemove", (e) => { const r = canvas.getBoundingClientRect(); mouse = { x: e.clientX - r.left, y: e.clientY - r.top }; });
  canvas.addEventListener("mouseleave", () => { mouse = { x: -9999, y: -9999 }; });
  window.addEventListener("resize", size);
  size();
  raf = requestAnimationFrame(draw);

  return {
    set(nextSrc, nextColor) {
      current = nextSrc;
      if (nextColor) rgb = parseColor(nextColor);
      build();
    },
    stop() { cancelAnimationFrame(raf); },
  };
}
