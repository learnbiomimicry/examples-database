// One place for links and names used across the site.
export const SITE = {
  name: "Biomimicry Examples Database",
  brand: "Learn Biomimicry",
  url: "https://examples.learnbiomimicry.com",
  home: "https://www.learnbiomimicry.com",
};

export const CTA = {
  fieldGuide: {
    href: "https://www.learnbiomimicry.com/fieldguide",
    title: "Free: the Field Guide to Biomimicry",
    text: "The eBook and 7-day email course that teach you to find and use strategies like these.",
    button: "Get the Field Guide",
  },
  opportunityMap: {
    href: "https://explora.network/get-started",
    title: "For R&D teams: your Biomimicry Opportunity Map",
    text: "Enter your company website and see where nature-inspired innovation could help your products.",
    button: "Map my opportunities",
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
