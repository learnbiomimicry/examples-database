// Cloudflare Pages Function: the only server code on this site. It serves no page content.
// Sign-ups themselves go from the browser to the shared Supabase `signup` edge function
// (the same one Nature's Solutions uses: Supabase -> Zapier -> Kajabi Free eBook form).
// This endpoint only sets a long-lived first-party cookie after a sign-up, because Safari
// clears script-set storage after 7 days without a visit but keeps server-set cookies.
//
// GET or POST /api/unlock  -> 200 with Set-Cookie: lb_access=1 (two years, *.learnbiomimicry.com)

const TWO_YEARS = 60 * 60 * 24 * 365 * 2;

function unlocked(request) {
  const host = new URL(request.url).hostname;
  // Scope to the whole domain so every *.learnbiomimicry.com site shares one unlock.
  const domain = host.endsWith("learnbiomimicry.com") ? "; Domain=.learnbiomimicry.com" : "";
  return new Response(JSON.stringify({ ok: true }), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
      "Set-Cookie": `lb_access=1; Path=/; Max-Age=${TWO_YEARS}; Secure; SameSite=Lax${domain}`,
    },
  });
}

export const onRequestGet = ({ request }) => unlocked(request);
export const onRequestPost = ({ request }) => unlocked(request);
