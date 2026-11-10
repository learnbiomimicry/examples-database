// Loads the examples once per build and shapes them for the pages.
import { readFileSync } from "node:fs";
import { SUPABASE } from "./config.js";

const FIELDS = [
  "slug", "title", "organism", "company", "location", "industry_id", "category_id",
  "mimicry_levels", "content_type", "summary", "problem_statement", "natural_model",
  "adaptation_emulated", "innovation", "breakdown_function", "breakdown_mechanism",
  "breakdown_principle", "breakdown_result", "key_metrics", "banner_image1_url",
  "featured", "updated_at", "full_description", "banner_image2_url", "example_type", "products",
  "design_prompts", "rating_score", "rating_biomimicry_link", "rating_ease_of_application",
  "rating_wide_applicability", "rating_life_principles", "rating_benefit_to_humanity",
].join(",");

// Labels for the slugs stored in industry_id and category_id.
const LABELS = {
  architecture: "Architecture", materials: "Materials", manufacturing: "Manufacturing",
  "chemistry-materials": "Chemistry and Materials", "medical-biotechnology": "Medicine and Biotech",
  infrastructure: "Infrastructure", "renewable-energy": "Renewable Energy",
  "food-agriculture": "Food and Agriculture", "software-it": "Software and IT", textiles: "Textiles",
  aerospace: "Aerospace", engineering: "Engineering", "product-design": "Product Design",
  environmental: "Environmental", technology: "Technology", organisational: "Organisational Design",
  robotics: "Robotics", computing: "Computing", water: "Water", construction: "Construction",
  transportation: "Transportation", energy: "Energy", packaging: "Packaging",
};

const COUNTRY_ALIASES = {
  usa: "United States", "united states": "United States", us: "United States",
  uk: "United Kingdom", "united kingdom": "United Kingdom", england: "United Kingdom",
  "canary islands": "Spain",
};

export const LEVELS = ["Form", "Process", "System"];

export function slugify(s) {
  return String(s).normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export function label(slug) {
  if (!slug) return null;
  return LABELS[slug] || slug.split("-").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
}

function country(location) {
  if (!location) return null;
  const last = location.split(",").pop().trim();
  return COUNTRY_ALIASES[last.toLowerCase()] || last;
}

function levels(raw) {
  if (!raw) return [];
  const list = Array.isArray(raw) ? raw : String(raw).replace(/[{}]/g, "").split(",");
  return list.map((s) => s.trim()).filter(Boolean)
    .map((s) => s[0].toUpperCase() + s.slice(1).toLowerCase())
    .filter((s) => LEVELS.includes(s));
}

function prompts(raw) {
  if (!raw) return [];
  const t = String(raw).trim();
  if (t.startsWith("[") && t.endsWith("]")) {
    try { return JSON.parse(t); } catch { return [...t.matchAll(/'([^']+)'/g)].map((m) => m[1]); }
  }
  return t.split("\n").map((x) => x.trim()).filter(Boolean);
}

function image(raw) {
  if (!raw) return null;
  if (/^https?:\/\//.test(raw)) return raw;
  return `${SUPABASE.imageBase}/${encodeURIComponent(raw)}`;
}

export function paragraphs(text) {
  return (text || "").split(/\n\s*\n|\n/).map((p) => p.trim()).filter(Boolean);
}

async function fetchRows() {
  const url = `${SUPABASE.url}/rest/v1/${SUPABASE.table}?select=${FIELDS}&published=eq.true&slug=not.is.null&order=title.asc`;
  try {
    const res = await fetch(url, { headers: { apikey: SUPABASE.key, Authorization: `Bearer ${SUPABASE.key}` } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const rows = await res.json();
    console.log(`[data] ${rows.length} examples from Supabase`);
    return rows;
  } catch (e) {
    // Local builds without network access use the saved snapshot.
    console.warn(`[data] Supabase unavailable (${e.message}); using data/examples.snapshot.json`);
    return JSON.parse(readFileSync(new URL("../../data/examples.snapshot.json", import.meta.url), "utf8"));
  }
}

let cache;
export async function getExamples() {
  if (cache) return cache;
  const rows = await fetchRows();
  cache = rows.map((r) => {
    const c = country(r.location);
    return {
      ...r,
      image: image(r.banner_image1_url),
      image2: image(r.banner_image2_url),
      prompts: prompts(r.design_prompts),
      rating: r.rating_score == null ? null : {
        score: r.rating_score,
        criteria: [
          ["Biomimicry Link", r.rating_biomimicry_link],
          ["Ease of Application", r.rating_ease_of_application],
          ["Wide Applicability", r.rating_wide_applicability],
          ["Life Principles", r.rating_life_principles],
          ["Benefit to Humanity", r.rating_benefit_to_humanity],
        ].filter((c) => c[1] != null),
      },
      levels: levels(r.mimicry_levels),
      industry: r.industry_id ? { slug: r.industry_id, name: label(r.industry_id) } : null,
      interest: r.category_id ? { slug: r.category_id, name: label(r.category_id) } : null,
      country: c ? { slug: slugify(c), name: c } : null,
      metrics: Array.isArray(r.key_metrics) ? r.key_metrics.filter((m) => m && m.value && m.label) : [],
    };
  }).sort((a, b) => (b.rating?.score ?? -1) - (a.rating?.score ?? -1) || (b.featured === true) - (a.featured === true) || a.title.localeCompare(b.title));
  return cache;
}

// Facets that get their own landing pages. A page needs at least MIN examples.
const MIN = 2;
export const FACETS = {
  industry: { path: "industry", noun: "Industry", pick: (e) => (e.industry ? [e.industry] : []) },
  interest: { path: "interest", noun: "Interest", pick: (e) => (e.interest ? [e.interest] : []) },
  country: { path: "country", noun: "Country", pick: (e) => (e.country ? [e.country] : []) },
  level: { path: "level", noun: "Level", pick: (e) => e.levels.map((l) => ({ slug: slugify(l), name: l })) },
};

export function facetValues(examples, key, min = MIN) {
  const map = new Map();
  for (const e of examples) {
    for (const v of FACETS[key].pick(e)) {
      const cur = map.get(v.slug) || { ...v, count: 0, items: [] };
      cur.count++; cur.items.push(e); map.set(v.slug, cur);
    }
  }
  return [...map.values()].filter((v) => v.count >= min).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

export function facetUrl(key, slug) {
  return `/${FACETS[key].path}/${slug}/`;
}
