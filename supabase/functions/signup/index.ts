// Sign-up endpoint for Explora (Nature's Solutions) and the examples site.
// 1. Saves the person in public.signups (Supabase is the source of truth).
// 2. Copies them to Kajabi through a Zapier webhook. The Zap submits the Kajabi
//    Free eBook form (2147692554), so the existing automations send the eBook
//    sequence for their interest and add the interest tags.
//    (Kajabi's Public API is not on our plan, so we go through Zapier.)
// Zap: "Explora sign-up to Kajabi eBook form" (zapier.com/workflow/01a1ee52-9fcc-7778-8743-d15c596819b5).
import { createClient } from "jsr:@supabase/supabase-js@2";

// The webhook URL lives only in the ZAPIER_HOOK_URL secret: this repo is public, and the URL would let anyone add contacts to Kajabi.
const ZAPIER_HOOK_URL = Deno.env.get("ZAPIER_HOOK_URL") ?? "";

// Short keys used by the website, mapped to the exact option text on the Kajabi form.
// The Kajabi automations match on this text, so it must not change.
const INTERESTS: Record<string, string> = {
  "product-design": "Product Design (Consumer, Industrial, Healthcare, etc)",
  "built-environment": "Built Environment (Architects, Interior Designers, Civil Engineers, Urban Planners, etc)",
  "biomaterials": "Biomaterials (Chemical Engineers, Material Scientists, etc)",
  "education": "Education (Teachers, Professors, Lecturers, etc)",
  "ecological-restoration": "Ecological Restoration (Conservation, Bioremediation, Water Management, etc)",
  "business": "Business (Sustainability consulting, Innovation, Management, etc)",
  "other": "Other",
};
const SOURCES = new Set(["natures-solutions", "examples", "company-pilot"]);

// Company pilot enquiries (examples.learnbiomimicry.com/company-pilot/) skip the eBook route.
// Each one is posted to the PILOT_HOOK_URL secret, a Zap that emails Alistair.
const PILOT_HOOK_URL = Deno.env.get("PILOT_HOOK_URL") ?? "";
const clip = (v: unknown, n: number) => String(v ?? "").trim().slice(0, n);

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type, authorization, apikey, x-client-info",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, "Content-Type": "application/json" } });

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});

async function sendToKajabi(name: string, email: string, interest: string, source: string) {
  if (!ZAPIER_HOOK_URL) throw new Error("ZAPIER_HOOK_URL secret is not set");
  const r = await fetch(ZAPIER_HOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, interest_label: INTERESTS[interest], source }),
  });
  if (!r.ok) throw new Error(`zapier ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return { status: "sent" as const, error: null };
}

async function pilotEnquiry(body: any, name: string, email: string) {
  const details = {
    company: clip(body.company, 160),
    role: clip(body.role, 120),
    challenge: clip(body.challenge, 1500),
    page: clip(body.page, 200),
  };
  if (!name) return json({ error: "Please add your name." }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: "Please check your email address." }, 400);
  if (!details.company) return json({ error: "Please add your company." }, 400);
  if (!details.challenge) return json({ error: "Please tell us about your challenge in a line or two." }, 400);
  if (body.consent !== true) return json({ error: "Please tick the box so we can contact you." }, 400);

  // One row per email (already lower-cased); a repeat enquiry updates it.
  const { data: existing } = await db.from("signups").select("id").eq("email", email).eq("source", "company-pilot").maybeSingle();
  const { error } = existing
    ? await db.from("signups").update({ name, details, updated_at: new Date().toISOString() }).eq("id", existing.id)
    : await db.from("signups").insert({ name, email, interest: "other", source: "company-pilot", details, consent: true, kajabi_status: "skipped" });
  if (error) return json({ error: "Could not save, please try again." }, 500);

  if (PILOT_HOOK_URL) {
    try {
      await fetch(PILOT_HOOK_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, email, ...details }) });
    } catch (_) { /* the row is saved; Alistair can still see it in Supabase */ }
  }
  return json({ ok: true });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);

  let body: any;
  try { body = await req.json(); } catch { return json({ error: "Invalid request" }, 400); }

  // Honeypot: real people never fill the hidden "website" field.
  if (body.website) return json({ ok: true });

  const name = String(body.name ?? "").trim().slice(0, 120);
  const email = String(body.email ?? "").trim().toLowerCase().slice(0, 200);
  const interest = String(body.interest ?? "");
  const source = SOURCES.has(body.source) ? body.source : "natures-solutions";
  const viewed = Array.isArray(body.viewed) ? body.viewed.map(String).slice(0, 20).map((s: string) => s.slice(0, 120)) : [];

  if (source === "company-pilot") return pilotEnquiry(body, name, email);

  if (!name) return json({ error: "Please add your name." }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: "Please check your email address." }, 400);
  if (!INTERESTS[interest]) return json({ error: "Please pick an area of interest." }, 400);
  if (body.consent !== true) return json({ error: "Please tick the box to agree to emails." }, 400);

  const { data: existing } = await db.from("signups").select("id, kajabi_status").eq("email", email).eq("source", source).maybeSingle();
  let id = existing?.id;
  if (id) {
    await db.from("signups").update({ name, interest, ...(viewed.length ? { viewed } : {}), consent: true, updated_at: new Date().toISOString() }).eq("id", id);
  } else {
    const { data, error } = await db.from("signups").insert({ name, email, interest, source, viewed, consent: true }).select("id").single();
    if (error) return json({ error: "Could not save, please try again." }, 500);
    id = data.id;
  }

  // Someone already on the list just gets back in; don't restart their emails.
  if (existing?.kajabi_status === "sent") return json({ ok: true, returning: true });

  let result: { status: "pending" | "sent" | "error"; error: string | null };
  try { result = await sendToKajabi(name, email, interest, source); }
  catch (e) { result = { status: "error", error: String(e).slice(0, 500) }; }

  await db.from("signups").update({
    kajabi_status: result.status,
    kajabi_error: result.error,
    kajabi_sent_at: result.status === "sent" ? new Date().toISOString() : null,
  }).eq("id", id);

  // The visitor gets in either way; failed Kajabi copies can be resent later.
  return json({ ok: true });
});
