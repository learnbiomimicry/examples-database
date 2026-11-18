// Cloudflare Pages Function: the only server code on this site.
// The pages themselves stay static HTML; this endpoint just records a sign-up in Kajabi
// and sets a long-lived first-party cookie so the visitor is never asked again.
//
// POST /api/unlock  { name, email, audience?, organisation?, source?, page? }  -> sign up, set cookie
// POST /api/unlock  { mode: "returning", email }                              -> set cookie only
// GET  /api/unlock?mark=1                                                     -> set cookie only (links in Kajabi emails)
//
// Environment variables (Cloudflare Pages > Settings > Variables and Secrets, encrypted):
//   KAJABI_CLIENT_ID, KAJABI_CLIENT_SECRET  a Kajabi User API Key (Settings > Security > User API Keys)
//   KAJABI_FORM_ID                          the shared "Explora Open Access" form
// Without them the visitor is still unlocked; the sign-up just isn't sent to Kajabi.

const COOKIE = "lb_access";
const TWO_YEARS = 60 * 60 * 24 * 365 * 2;
const KAJABI = "https://api.kajabi.com";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

let token = null; // cached per isolate: { value, expires }

function accessCookie(host) {
  // Scope to the whole domain so every *.learnbiomimicry.com site shares one unlock.
  const domain = host.endsWith("learnbiomimicry.com") ? "; Domain=.learnbiomimicry.com" : "";
  return `${COOKIE}=1; Path=/; Max-Age=${TWO_YEARS}; Secure; SameSite=Lax${domain}`;
}

function json(body, status, host) {
  const headers = { "Content-Type": "application/json", "Cache-Control": "no-store" };
  if (status < 300) headers["Set-Cookie"] = accessCookie(host);
  return new Response(JSON.stringify(body), { status, headers });
}

async function kajabiToken(env) {
  if (token && token.expires > Date.now() + 60_000) return token.value;
  const res = await fetch(`${KAJABI}/v1/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "client_credentials", client_id: env.KAJABI_CLIENT_ID, client_secret: env.KAJABI_CLIENT_SECRET }),
  });
  if (!res.ok) throw new Error(`token ${res.status}`);
  const t = await res.json();
  token = { value: t.access_token, expires: Date.now() + (t.expires_in || 3600) * 1000 };
  return token.value;
}

async function submitToKajabi(env, attrs) {
  const bearer = await kajabiToken(env);
  const send = (attributes) =>
    fetch(`${KAJABI}/v1/forms/${env.KAJABI_FORM_ID}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/vnd.api+json", Authorization: `Bearer ${bearer}` },
      body: JSON.stringify({ data: { type: "form_submissions", attributes } }),
    });
  const { name, email, ...custom } = attrs;
  let res = await send(attrs);
  // If the form doesn't have the custom fields yet, still capture name and email.
  if (!res.ok && Object.keys(custom).length && res.status !== 401 && res.status !== 403) res = await send({ name, email });
  if (!res.ok) throw new Error(`submit ${res.status}`);
}

export async function onRequestGet({ request }) {
  const host = new URL(request.url).hostname;
  return json({ ok: true }, 200, host);
}

export async function onRequestPost({ request, env }) {
  const host = new URL(request.url).hostname;
  let body;
  try { body = await request.json(); } catch { return json({ ok: false, error: "bad_request" }, 400, host); }

  const email = String(body.email || "").trim().toLowerCase().slice(0, 200);
  if (!EMAIL_RE.test(email)) return json({ ok: false, error: "email" }, 422, host);

  // Returning visitor on a new device: no password, no lookup, just unlock.
  if (body.mode === "returning") return json({ ok: true, returning: true }, 200, host);

  const name = String(body.name || "").trim().slice(0, 120);
  if (!name) return json({ ok: false, error: "name" }, 422, host);

  const attrs = { name, email };
  // custom_1..3 map to the form's custom fields: Source, Exploring for, Organisation.
  if (body.source) attrs.custom_1 = String(body.source).slice(0, 60);
  if (body.audience) attrs.custom_2 = body.audience === "organisation" ? "My organisation" : "Myself";
  if (body.organisation) attrs.custom_3 = String(body.organisation).trim().slice(0, 120);

  let recorded = false;
  if (env.KAJABI_CLIENT_ID && env.KAJABI_CLIENT_SECRET && env.KAJABI_FORM_ID) {
    try { await submitToKajabi(env, attrs); recorded = true; }
    catch (err) { console.error("Kajabi submit failed:", err.message); }
  } else {
    console.warn("Kajabi credentials not set; visitor unlocked without a CRM record.");
  }
  // Never punish the visitor for our plumbing: unlock either way.
  return json({ ok: true, recorded }, 200, host);
}
