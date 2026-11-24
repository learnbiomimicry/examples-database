// One place for links and names used across the site.
export const SITE = {
  name: "Biomimicry Examples Database",
  brand: "Learn Biomimicry",
  url: "https://examples.learnbiomimicry.com",
  home: "https://www.learnbiomimicry.com",
};

// Nature's solutions: a separate static site built by scripts/explora/demo_site.py --site.
export const EXPLORA = {
  url: "https://explora.learnbiomimicry.com",
};

// Soft email gate on case study pages (see src/components/Gate.astro, functions/api/unlock.js).
// Shared with Nature's Solutions: same Supabase `signup` function, fields and Kajabi route.
export const GATE = {
  free: 3,                  // full case studies a visitor reads before the sign-up card
  signupUrl: "https://johscicbgjmvxbwlzyat.supabase.co/functions/v1/signup",
  source: "examples",       // stored in public.signups.source
  cookieUrl: "/api/unlock", // Cloudflare Pages Function that sets the two-year lb_access cookie
  // Keys the signup function maps to Kajabi's "Area of Interest" options. Keep in step with it.
  interests: [
    ["product-design", "Product design"],
    ["built-environment", "Built environment and architecture"],
    ["biomaterials", "Biomaterials"],
    ["education", "Education"],
    ["ecological-restoration", "Ecological restoration"],
    ["business", "Business and innovation"],
    ["other", "Something else"],
  ],
};

// Company pilot page (/company-pilot/). Add the scheduling link here and the
// "Book a 20-minute call" buttons appear; until then the page shows the enquiry form only.
export const PILOT = {
  bookCall: "",
};

export const CTA = {
  fieldGuide: {
    href: "https://www.learnbiomimicry.com/fieldguide",
    title: "Free: the Field Guide to Biomimicry",
    text: "The eBook and 7-day email course that teach you to find and use strategies like these.",
    button: "Get the Field Guide",
  },
  // Replaces the Opportunity Map on the retired Lovable app (24 Nov 2026 strategy).
  companyPilot: {
    href: "/company-pilot/",
    title: "For R&D teams: a company pilot",
    text: "Bring us one stuck problem. In four weeks, a mentor takes your team from challenge to nature-inspired concepts and a spec.",
    button: "See the company pilot",
  },
  courses: {
    href: "https://www.learnbiomimicry.com/short-courses",
    button: "Biomimicry short courses",
  },
};

// Supabase is read at build time only, with the public (publishable) key.
export const SUPABASE = {
  url: import.meta.env.SUPABASE_URL || "https://johscicbgjmvxbwlzyat.supabase.co",
  key: import.meta.env.SUPABASE_ANON_KEY || "sb_publishable_MB5kuJONlklys9duAH7hIg_RO48XwNU",
  table: "biomimicry-examples",
  imageBase: "https://johscicbgjmvxbwlzyat.supabase.co/storage/v1/object/public/example-images",
};
