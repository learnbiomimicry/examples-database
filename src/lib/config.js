// One place for links and names used across the site.
export const SITE = {
  name: "Biomimicry Examples Database",
  brand: "Learn Biomimicry",
  url: "https://examples.learnbiomimicry.com",
  home: "https://www.learnbiomimicry.com",
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

// ---------------------------------------------------------------------------
// Offers, events and links. Change dates and links here, not in the templates.
// Dates are ISO strings with the South Africa offset (+02:00). Messages switch on
// their own when a date passes: the build picks the right one, and a small script
// re-checks in the visitor's browser (src/lib/timely.js), so no rebuild is needed.
// Test any date by adding ?now=2027-01-15 to a page address.
// ---------------------------------------------------------------------------
export const OFFERS = {
  shortCourses: {
    name: "Biomimicry Short Course Set",
    href: "https://www.learnbiomimicry.com/short-courses",
  },
  practitioner: {
    name: "Biomimicry Practitioner Programme",
    href: "https://www.learnbiomimicry.com/biomimicry-practitioner-programme",
    price: "$2,799",
    duration: "six months",
    // Each cohort shows until its start date, then the next one takes over.
    cohorts: [
      { month: "February", starts: "1 February", date: "2027-02-01T00:00:00+02:00" },
      { month: "June", starts: "7 June", date: "2027-06-07T00:00:00+02:00" },
    ],
  },
  educator: {
    name: "Biomimicry Educator Programme",
    href: "https://www.learnbiomimicry.com/biomimicry-educator-programme",
    price: "$2,799",
    // Each deadline shows until the end of that day, then the next one takes over.
    deadlines: [
      { closes: "18 December", date: "2026-12-19T00:00:00+02:00" },
    ],
  },
  fieldGuide: {
    name: "Field Guide to Biomimicry",
    href: "https://www.learnbiomimicry.com/fieldguide",
  },
};

export const EVENTS = {
  demo: {
    name: "Biomimicry with Claude",
    day: "Thursday 14 January 2027",
    short: "14 January",
    start: "2027-01-14T15:00:00+02:00",
    end: "2027-01-14T16:00:00+02:00",
    saTime: "15:00 to 16:00 South Africa time",
    // New people need the invite link to join the community first; members go straight in.
    // Never put the Google Meet link on the site.
    register: "https://ecosystem.learnbiomimicry.com/join?inviteKey=c6ee33ef3843a518",
    members: "https://ecosystem.learnbiomimicry.com/home",
  },
  confluence: {
    name: "Biomimicry Confluence Seven",
    when: "3 and 4 March",
    end: "2027-03-05T00:00:00+02:00",
    href: "https://www.learnbiomimicry.com/confluence",
  },
  all: "https://www.learnbiomimicry.com/blog/biomimicry-events",
};

export const TOOLS = {
  explora: { name: "Explora", href: "https://explora.network" },
};

export const BETA = {
  feedback: "mailto:hello@learnbiomimicry.com?subject=Biomimicry%20Examples%20Database%20beta%20feedback",
  // Newsletter links carry ?from=livingloop: those readers never see the email limit.
  bypassParam: ["from", "livingloop"],
};

// Google Analytics 4: the Learn Biomimicry property (also used on learnbiomimicry.com).
export const ANALYTICS = { ga4: "G-91160H2ZSM" };

export const CTA = {
  fieldGuide: {
    href: OFFERS.fieldGuide.href,
    title: "Free: the Field Guide to Biomimicry",
    text: "The eBook and seven-day email course that teach you to find and use strategies like these.",
    button: "Get the Field Guide",
  },
  courses: {
    href: OFFERS.shortCourses.href,
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
