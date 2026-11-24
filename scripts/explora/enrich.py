"""Enrich every case study in Supabase with Claude, twice, and store whether the passes agree.

For each row of `biomimicry-examples` Claude extracts:
  mechanism (name, summary, 3-step "how it works" in simple English),
  functions (NASA PeTaL taxonomy), organism, maturity,
  and a Life-friendly score on the five criteria (1 to 6 each).

Two independent passes run per case study (separate requests, same prompt).
Claude never sees the existing hand scores, so its scores are a fair check
against them. A third, small request judges whether the two mechanism
descriptions describe the same thing.

Writes: enrichment_passes, organisms, mechanisms, mechanism_functions,
mechanism_organisms, case_study_mechanisms, case_study_enrichment.
Never writes to `biomimicry-examples`.

Usage:
  python scripts/explora/enrich.py                 # all case studies
  python scripts/explora/enrich.py --limit 5       # try a few first
  python scripts/explora/enrich.py --slug some-slug
Safe to stop and run again: passes already stored are reused.
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import anthropic

from common import Supabase, load_env, need, slugify

MODEL = "claude-opus-5-5"
PROMPT_VERSION = "v3-2026-11-16"
WORKERS = 6

CRITERIA = [
    ("biomimicry_link", "Biomimicry link: how closely the design copies a real, understood strategy in nature. 6 = a clear, documented mechanism copied closely. 1 = a loose likeness or metaphor."),
    ("ease_of_application", "Ease of application: how easy it is for others to use this today (cost, materials, skills, complexity). 6 = simple and cheap to apply now. 1 = very hard or far off."),
    ("wide_applicability", "Wide applicability: how many fields and problems could use it. 6 = many industries. 1 = one narrow use."),
    ("life_friendly_fit", "Life-friendly fit (Life's Principles): benign materials and chemistry, uses little energy and material, local, adapts, can be (re)used or breaks down safely. 6 = strong on most. 1 = works against them."),
    ("benefit_to_humanity", "Benefit to humanity: size of the good it does for people and the planet if widely used. 6 = very large. 1 = very small."),
]

CASE_FIELDS = [
    "title", "company", "organism", "summary", "full_description", "problem_statement",
    "innovation", "natural_model", "adaptation_emulated", "products", "key_metrics",
    "breakdown_function", "breakdown_mechanism", "breakdown_principle", "breakdown_result",
    "mimicry_levels", "location", "example_type",
]


def build_schema(function_slugs):
    score = {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["mechanism_name", "mechanism_summary", "how_it_works", "functions",
                     "organism_scientific_name", "organism_common_name", "organism_habitat",
                     "maturity", "life_friendly", "notes"],
        "properties": {
            "mechanism_name": {"type": "string", "description": "Short, general name for the mechanism, 3 to 8 words, no brand names."},
            "mechanism_summary": {"type": "string", "description": "One or two plain sentences: what the mechanism does and why it works."},
            "how_it_works": {"type": "array", "items": {"type": "string"}, "description": "Exactly 3 short steps in simple English."},
            "functions": {"type": "array", "items": {"type": "string", "enum": function_slugs},
                          "description": "1 to 3 PeTaL functions, most specific level available."},
            "organism_scientific_name": {"type": "string", "description": "Latin name (genus or species). Empty string if not one organism."},
            "organism_common_name": {"type": "string"},
            "organism_habitat": {"type": "string", "description": "Where it lives, a few words. Empty string if unknown."},
            "maturity": {"type": "string", "enum": ["concept", "lab", "pilot", "on market"]},
            "life_friendly": {
                "type": "object",
                "additionalProperties": False,
                "required": [c for c, _ in CRITERIA] + ["reasons"],
                "properties": dict(
                    {c: score for c, _ in CRITERIA},
                    reasons={"type": "string", "description": "One short sentence per criterion."},
                ),
            },
            "notes": {"type": "string", "description": "Anything unclear or missing in the source. Empty string if none."},
        },
    }


JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["same_mechanism", "reason"],
    "properties": {"same_mechanism": {"type": "boolean"}, "reason": {"type": "string"}},
}


def system_prompt(functions):
    lines = [
        "You enrich biomimicry case studies for Explora, an open database that people and AI tools rely on.",
        "Work only from the case study text you are given. Do not invent facts, organisms, figures or papers.",
        "If the source is unclear, give your best reading and say what is unclear in notes.",
        "",
        "Writing rules: British English, simple words a 14 year old understands, short sentences. Never use the em dash.",
        "",
        "Mechanism: the way nature (and the design copying it) achieves the function. Name it in general terms,",
        "for example 'Bumps that attract water on a surface that repels it', not the product name.",
        "How it works: exactly 3 steps, each one sentence, in order.",
        "Biology: you may add well-established biology about the organism (for example, that a cat's tongue has",
        "small backward-facing spines), even if the source does not say it. Only add biology a textbook or review",
        "paper would state; if you are not sure, leave it out.",
        "Product, company and method: use only what the source says. Never add a method, material, machine,",
        "figure or claim about the product or company that the source does not name. If the source does not say",
        "how the design is made, describe it at the level the source gives.",
        "In notes, list any biology you added that is not in the source.",
        "Organism: if the source names no single organism, leave the scientific name empty and give the group",
        "it names as the common name, for example 'Plants (plant cells)'.",
        "Functions: pick 1 to 3 from the NASA PeTaL taxonomy below. Prefer level 3; use level 2 only when no level 3 fits.",
        "Maturity: concept (idea only), lab (research results), pilot (field trials or first customers), on market (sold now).",
        "",
        "Life-friendly score, 1 to 6 for each criterion. Use the whole range and be strict:",
    ]
    lines += ["- " + text for _, text in CRITERIA]
    lines += ["", "NASA PeTaL function taxonomy (slug: name, with parent):"]
    lines += ["- %s: %s (%s)" % (f["slug"], f["name"], f["parent"]) for f in functions]
    return "\n".join(lines)


def case_text(row):
    parts = []
    for field in CASE_FIELDS:
        value = row.get(field)
        if value in (None, "", [], {}):
            continue
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        parts.append("%s: %s" % (field.replace("_", " ").title(), value))
    return "Case study\n\n" + "\n\n".join(parts)


def no_em_dash(obj):
    if isinstance(obj, str):
        return obj.replace(" — ", ", ").replace("—", ", ").replace("–", "-")
    if isinstance(obj, list):
        return [no_em_dash(x) for x in obj]
    if isinstance(obj, dict):
        return {k: no_em_dash(v) for k, v in obj.items()}
    return obj


class Claude:
    def __init__(self, system, schema):
        load_env()
        need("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(max_retries=5)
        self.system = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        self.schema = schema

    def _ask(self, system, content, schema, effort, max_tokens):
        resp = self.client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": content}],
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        )
        if resp.stop_reason == "refusal":
            return "refused", None
        if resp.stop_reason == "max_tokens":
            return "error", "hit max_tokens"
        text = next(b.text for b in resp.content if b.type == "text")
        return "ok", no_em_dash(json.loads(text))

    def extract(self, row):
        return self._ask(self.system, case_text(row), self.schema, "medium", 16000)

    def same_mechanism(self, a, b):
        def show(x):
            return "Name: %s\nSummary: %s\nSteps: %s" % (x["mechanism_name"], x["mechanism_summary"], " / ".join(x["how_it_works"]))
        content = ("Two people described the mechanism in one biomimicry case study. "
                   "Do they describe the same underlying mechanism (wording may differ)?\n\nA\n%s\n\nB\n%s" % (show(a), show(b)))
        status, out = self._ask("You compare two short descriptions. Answer in simple British English.",
                                content, JUDGE_SCHEMA, "low", 4000)
        return out if status == "ok" else {"same_mechanism": False, "reason": "judge " + status}


# ---------- agreement ----------

def _norm(s):
    return re.sub(r"[^a-z ]", "", (s or "").lower()).strip()


def organism_agrees(a, b):
    sa, sb = _norm(a["organism_scientific_name"]), _norm(b["organism_scientific_name"])
    if sa and sb and sa.split()[0] == sb.split()[0]:
        return True
    ca, cb = _norm(a["organism_common_name"]), _norm(b["organism_common_name"])
    if ca and cb and (ca == cb or ca in cb or cb in ca):
        return True
    # No single organism named (e.g. "plant cells", "coral and shells"):
    # agree when the common names share a real word.
    return bool(_words(ca) & _words(cb))


GENERIC = {"natural", "nature", "general", "structure", "structures", "builder", "builders",
           "organism", "organisms", "various", "system", "systems", "cell", "cells"}


def _words(s):
    return {w.rstrip("s") for w in s.split() if len(w) >= 4 and w not in GENERIC}


def functions_agree(a, b, parent_of):
    fa, fb = set(a["functions"]), set(b["functions"])
    if fa & fb:
        return True
    # Same level 2 family counts as agreement (e.g. two kinds of 'protect from non-living threats').
    pa = {parent_of.get(x, x) for x in fa} | fa
    pb = {parent_of.get(x, x) for x in fb} | fb
    return bool(pa & pb)


def score_gaps(a, b):
    return {c: abs(a["life_friendly"][c] - b["life_friendly"][c]) for c, _ in CRITERIA}


EXISTING = {
    "biomimicry_link": "rating_biomimicry_link",
    "ease_of_application": "rating_ease_of_application",
    "wide_applicability": "rating_wide_applicability",
    "life_friendly_fit": "rating_life_principles",
    "benefit_to_humanity": "rating_benefit_to_humanity",
}


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--slug")
    args = ap.parse_args()

    db = Supabase()
    funcs = db.select("functions", {"select": "id,slug,name,level,parent_id", "order": "level,slug"})
    by_id = {f["id"]: f for f in funcs}
    usable = [f for f in funcs if f["level"] in (2, 3)]
    for f in usable:
        f["parent"] = by_id[f["parent_id"]]["name"] if f["parent_id"] else ""
    slug_to_id = {f["slug"]: f["id"] for f in funcs}
    parent_of = {f["slug"]: by_id[f["parent_id"]]["slug"] for f in funcs if f["level"] == 3}

    claude = Claude(system_prompt(usable), build_schema([f["slug"] for f in usable]))

    params = {"select": "id,slug,rating_biomimicry_link,rating_ease_of_application,rating_wide_applicability,"
                        "rating_life_principles,rating_benefit_to_humanity," + ",".join(CASE_FIELDS),
              "order": "slug"}
    if args.slug:
        params["slug"] = "eq." + args.slug
    cases = db.select("biomimicry-examples", params)
    if args.limit:
        cases = cases[: args.limit]
    print("case studies:", len(cases))

    done = db.select("enrichment_passes", {"select": "case_study_id,pass_no,status,output",
                                           "prompt_version": "eq." + PROMPT_VERSION})
    stored = {(d["case_study_id"], d["pass_no"]): d for d in done if d["status"] == "ok"}

    # Phase 1: two independent passes per case study.
    jobs = [(c, p) for c in cases for p in (1, 2) if (c["id"], p) not in stored]
    print("passes to run:", len(jobs))

    def run(job):
        case, pass_no = job
        try:
            status, out = claude.extract(case)
            err = out if status == "error" else None
            out = out if status == "ok" else None
        except anthropic.APIError as e:
            status, out, err = "error", None, str(e)[:500]
        db.upsert("enrichment_passes", [{
            "case_study_id": case["id"], "pass_no": pass_no, "prompt_version": PROMPT_VERSION,
            "model": MODEL, "status": status, "output": out, "error": err,
        }], "case_study_id,pass_no,prompt_version", returning=False)
        if status == "ok":
            stored[(case["id"], pass_no)] = {"output": out}
        print("  %-50s pass %d %s" % (case["slug"][:50], pass_no, status), flush=True)

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(run, jobs))

    # Phase 2: compare passes and write the agreed records.
    ready = [c for c in cases if (c["id"], 1) in stored and (c["id"], 2) in stored]
    print("case studies with both passes:", len(ready), "of", len(cases))

    def consolidate(case):
        a, b = stored[(case["id"], 1)]["output"], stored[(case["id"], 2)]["output"]
        judge = claude.same_mechanism(a, b)
        gaps = score_gaps(a, b)
        agreement = {
            "organism": organism_agrees(a, b),
            "functions": functions_agree(a, b, parent_of),
            "mechanism": bool(judge["same_mechanism"]),
            "mechanism_reason": judge["reason"],
            "scores_within_1": all(g <= 1 for g in gaps.values()),
            "score_gaps": gaps,
        }
        agree = agreement["organism"] and agreement["functions"] and agreement["mechanism"]

        # Scores: mean of the two passes, to the nearest half point.
        lf = {c: round((a["life_friendly"][c] + b["life_friendly"][c]) / 2 * 2) / 2 for c, _ in CRITERIA}
        vs = {}
        for c, col in EXISTING.items():
            old = case.get(col)
            vs[c] = None if old in (None, "", 0, "0") else round(lf[c] - float(old), 2)
        known = [abs(v) for v in vs.values() if v is not None]
        vs["mean_abs_gap"] = round(sum(known) / len(known), 2) if known else None

        # Organism and mechanism come from pass 1.
        org_id = None
        org_name = a["organism_scientific_name"] or a["organism_common_name"]
        if org_name:
            org = db.upsert("organisms", [{
                "slug": slugify(org_name),
                "scientific_name": a["organism_scientific_name"] or None,
                "common_name": a["organism_common_name"] or None,
                "habitat": a["organism_habitat"] or None,
            }], "slug")
            org_id = org[0]["id"]

        mech = db.upsert("mechanisms", [{
            "slug": slugify(a["mechanism_name"]),
            "name": a["mechanism_name"],
            "summary": a["mechanism_summary"],
            "how_it_works": a["how_it_works"][:3],
            "lf_biomimicry_link": lf["biomimicry_link"],
            "lf_ease_of_application": lf["ease_of_application"],
            "lf_wide_applicability": lf["wide_applicability"],
            "lf_life_friendly_fit": lf["life_friendly_fit"],
            "lf_benefit_to_humanity": lf["benefit_to_humanity"],
            "passes_agree": agree,
        }], "slug")
        mech_id = mech[0]["id"]

        db.insert_ignore("mechanism_functions",
                         [{"mechanism_id": mech_id, "function_id": slug_to_id[s]} for s in a["functions"] if s in slug_to_id],
                         "mechanism_id,function_id")
        if org_id:
            db.insert_ignore("mechanism_organisms", [{"mechanism_id": mech_id, "organism_id": org_id}],
                             "mechanism_id,organism_id")
        db.insert_ignore("case_study_mechanisms", [{"case_study_id": case["id"], "mechanism_id": mech_id}],
                         "case_study_id,mechanism_id")
        db.upsert("case_study_enrichment", [{
            "case_study_id": case["id"], "prompt_version": PROMPT_VERSION, "mechanism_id": mech_id,
            "maturity": a["maturity"], "passes_agree": agree, "agreement": agreement,
            "lf_biomimicry_link": lf["biomimicry_link"], "lf_ease_of_application": lf["ease_of_application"],
            "lf_wide_applicability": lf["wide_applicability"], "lf_life_friendly_fit": lf["life_friendly_fit"],
            "lf_benefit_to_humanity": lf["benefit_to_humanity"], "lf_total": sum(lf.values()),
            "lf_vs_existing": vs, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }], "case_study_id", returning=False)
        print("  %-50s agree=%s" % (case["slug"][:50], agree), flush=True)
        return agree

    with ThreadPoolExecutor(WORKERS) as pool:
        results = list(pool.map(consolidate, ready))
    print("passes agree: %d of %d" % (sum(results), len(results)))
    missing = len(cases) - len(ready)
    if missing:
        print("%d case studies are missing a pass (refused or error). Run again to retry." % missing)
        sys.exit(1)


if __name__ == "__main__":
    main()
