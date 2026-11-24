"""Pilot: read NASA PeTaL papers and turn each into a Nature's Solution.

For every paper in the `evidence` table (source nasa-petal), Claude reads the
title and abstract and decides whether it describes a clear biological
solution. If it does, Claude extracts the organism, PeTaL functions, a plain
name, summary, 3-step "how it works" and a Life-friendly score.

Like the case study enrichment, two independent passes run per paper, and a
small judge call checks whether they describe the same solution. Claude never
sees PeTaL's own human labels, so they are a fair test of its accuracy.

Abstracts come from PeTaL's golden.json on disk and are never stored. Only
Claude's own extraction is saved (table paper_passes), plus the new
solutions (mechanisms with origin = 'paper', published = false).

Usage:
  python scripts/explora/extract_papers.py GOLDEN_JSON --limit 10
  python scripts/explora/extract_papers.py GOLDEN_JSON                 # all papers
  python scripts/explora/extract_papers.py GOLDEN_JSON --compare claude-fable-5-2 --sample 30
Safe to stop and run again: stored passes are reused.
"""
import argparse
import json
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import anthropic

import enrich
from common import Supabase, slugify
from enrich import CRITERIA, JUDGE_SCHEMA, functions_agree, no_em_dash, organism_agrees

MODEL = "claude-opus-5-5"
PROMPT_VERSION = "paper-v1-2026-11-17"
WORKERS = 10
SOURCE_REASON = "Source paper: the solution was read from this paper"


def build_schema(function_slugs):
    base = enrich.build_schema(function_slugs)
    props = dict(base["properties"])
    props.pop("maturity")
    props["has_clear_solution"] = {
        "type": "boolean",
        "description": "True only if the paper explains how a living thing achieves a function well enough to copy."}
    props["why_not"] = {"type": "string", "description": "If has_clear_solution is false, one short reason. Else empty."}
    required = ["has_clear_solution", "why_not"] + [r for r in base["required"] if r != "maturity"]
    return {"type": "object", "additionalProperties": False, "required": required, "properties": props}


def system_prompt(functions):
    lines = [
        "You read biology research papers for Explora, an open database of Nature's Solutions:",
        "ways living things solve problems that people could learn from and copy.",
        "You get a paper's title and abstract. Work only from them, plus well-established textbook biology.",
        "Never invent figures, organisms or results the abstract does not support.",
        "",
        "First decide has_clear_solution. It is true only when the abstract explains HOW a living thing achieves",
        "a function (a structure, material, process or behaviour), clearly enough that an engineer or designer",
        "could learn from it. It is false for papers that only list species, describe genes or ecology without a",
        "mechanism, or are about human-made designs with no clear biology. If false, still fill every field as best",
        "you can, keep text short, and give the reason in why_not.",
        "",
        "Writing rules: British English, simple words a 14 year old understands, short sentences. Never use the em dash.",
        "Name: the solution in general terms, 3 to 8 words, for example 'Ridged scales that cut drag in water'.",
        "Summary: one or two sentences on what it does and why it works.",
        "How it works: exactly 3 steps, each one sentence, in order.",
        "Organism: if the paper covers a group rather than one species, leave the scientific name empty and give the",
        "group as the common name, for example 'Desert beetles'.",
        "Functions: pick 1 to 3 from the NASA PeTaL taxonomy below. Prefer level 3; use level 2 only when no level 3 fits.",
        "In notes, list any biology you added that is not in the abstract.",
        "",
        "Life-friendly score, 1 to 6 for each criterion. Score the potential of a design that copies this solution.",
        "Nothing has been built yet, so be strict on ease of application. Use the whole range:",
    ]
    lines += ["- " + text for _, text in CRITERIA]
    lines += ["", "NASA PeTaL function taxonomy (slug: name, with parent):"]
    lines += ["- %s: %s (%s)" % (f["slug"], f["name"], f["parent"]) for f in functions]
    return "\n".join(lines)


class Claude(enrich.Claude):
    def __init__(self, system, schema, model):
        super().__init__(system, schema)
        self.model = model

    def _ask(self, system, content, schema, effort, max_tokens):
        resp = self.client.messages.create(
            model=self.model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": content}],
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        )
        if resp.stop_reason == "refusal":
            return "refused", None
        if resp.stop_reason == "max_tokens":
            return "error", "hit max_tokens"
        text = next(b.text for b in resp.content if b.type == "text")
        return "ok", no_em_dash(json.loads(text))

    def read_paper(self, paper):
        content = "Title: %s\n\nAbstract: %s" % (paper["title"], paper["abstract"])
        return self._ask(self.system, content, self.schema, "medium", 16000)


def load_abstracts(path):
    data = json.load(open(path, encoding="utf-8"))
    recs = data if isinstance(data, list) else list(data.values())[0]
    out = {}
    for r in recs:
        # Keyed by title: PeTaL's DOIs are shuffled against titles (see fix_dois.py).
        title = _key(r.get("title"))
        ab = (r.get("abstract") or "").strip()
        if title and len(ab) > 50 and str(r.get("isBiomimicry", "")).upper().startswith("Y"):
            out[title] = ab
    return out


def _key(title):
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", (title or "").lower()).split())


def label_match(claude_funcs, human_labels, parent_of):
    """Does Claude share at least one function (or its level 2 family) with PeTaL's human labels?"""
    human = set(human_labels or [])
    mine = set(claude_funcs)
    if mine & human:
        return "exact"
    if ({parent_of.get(x, x) for x in mine} | mine) & ({parent_of.get(x, x) for x in human} | human):
        return "family"
    return "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("golden")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--compare", help="second model to compare on a sample, e.g. claude-fable-5-2")
    ap.add_argument("--sample", type=int, default=30)
    args = ap.parse_args()

    db = Supabase()
    funcs = db.select("functions", {"select": "id,slug,name,level,parent_id", "order": "level,slug"})
    by_id = {f["id"]: f for f in funcs}
    usable = [f for f in funcs if f["level"] in (2, 3)]
    for f in usable:
        f["parent"] = by_id[f["parent_id"]]["name"] if f["parent_id"] else ""
    slug_to_id = {f["slug"]: f["id"] for f in funcs}
    parent_of = {f["slug"]: by_id[f["parent_id"]]["slug"] for f in funcs if f["parent_id"]}

    abstracts = load_abstracts(args.golden)
    papers = db.select("evidence", {"select": "id,doi,title,function_labels", "source": "eq.nasa-petal", "order": "id"})
    for p in papers:
        p["abstract"] = abstracts.get(_key(p["title"]))
    papers = [p for p in papers if p["abstract"]]
    random.Random(17).shuffle(papers)  # fixed order, so --limit picks a fair spread
    print("papers with an abstract:", len(papers))

    system, schema = system_prompt(usable), build_schema([f["slug"] for f in usable])

    if args.compare:
        return compare(db, papers[: args.sample], system, schema, args.compare, parent_of)

    if args.limit:
        papers = papers[: args.limit]
    claude = Claude(system, schema, MODEL)

    done = db.select("paper_passes", {"select": "evidence_id,pass_no,output",
                                      "prompt_version": "eq." + PROMPT_VERSION, "model": "eq." + MODEL,
                                      "status": "eq.ok"})
    stored = {(d["evidence_id"], d["pass_no"]): d["output"] for d in done}
    jobs = [(p, n) for p in papers for n in (1, 2) if (p["id"], n) not in stored]
    print("passes to run:", len(jobs))

    def run(job):
        paper, n = job
        try:
            status, out = claude.read_paper(paper)
            err = out if status == "error" else None
            out = out if status == "ok" else None
        except anthropic.APIError as e:
            status, out, err = "error", None, str(e)[:500]
        db.upsert("paper_passes", [{"evidence_id": paper["id"], "pass_no": n, "prompt_version": PROMPT_VERSION,
                                    "model": MODEL, "status": status, "output": out, "error": err}],
                  "evidence_id,pass_no,prompt_version,model", returning=False)
        if status == "ok":
            stored[(paper["id"], n)] = out
        print("  %-40s pass %d %s" % ((paper["title"] or "")[:40], n, status), flush=True)

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(run, jobs))

    # Write solutions. Slugs must never clash with an existing one, or we would
    # overwrite a case study's solution, so clashes get a number on the end.
    existing = {m["slug"]: m for m in db.select("mechanisms", {"select": "id,slug,origin"})}
    source_links = {r["evidence_id"]: r["mechanism_id"] for r in db.select(
        "mechanism_evidence", {"select": "evidence_id,mechanism_id", "match_reason": "eq." + SOURCE_REASON})}
    lock = threading.Lock()
    stats = {"solution": 0, "no_solution": 0, "agree": 0, "labels_exact": 0, "labels_family": 0, "labels_none": 0}

    def free_slug(name):
        base = slugify(name) or "solution"
        with lock:
            slug, n = base, 2
            while slug in existing:
                slug, n = "%s-%d" % (base, n), n + 1
            existing[slug] = {"origin": "paper"}
            return slug

    def consolidate(paper):
        a, b = stored[(paper["id"], 1)], stored[(paper["id"], 2)]
        match = label_match(a["functions"], paper["function_labels"], parent_of)
        with lock:
            stats["labels_" + match] += 1
        if not (a["has_clear_solution"] and b["has_clear_solution"]):
            with lock:
                stats["no_solution"] += 1
            return
        judge = claude.same_mechanism(a, b)
        agree = organism_agrees(a, b) and functions_agree(a, b, parent_of) and bool(judge["same_mechanism"])
        lf = {c: round((a["life_friendly"][c] + b["life_friendly"][c]) / 2 * 2) / 2 for c, _ in CRITERIA}
        values = {
            "name": a["mechanism_name"], "summary": a["mechanism_summary"], "how_it_works": a["how_it_works"][:3],
            "lf_biomimicry_link": lf["biomimicry_link"], "lf_ease_of_application": lf["ease_of_application"],
            "lf_wide_applicability": lf["wide_applicability"], "lf_life_friendly_fit": lf["life_friendly_fit"],
            "lf_benefit_to_humanity": lf["benefit_to_humanity"], "passes_agree": agree, "origin": "paper",
            "published": False,
        }
        mech_id = source_links.get(paper["id"])
        if mech_id:  # already written on an earlier run: update in place
            db.update("mechanisms", {"id": mech_id}, values)
        else:
            mech_id = db.upsert("mechanisms", [dict(values, slug=free_slug(a["mechanism_name"]))], "slug")[0]["id"]
            db.insert_ignore("mechanism_evidence", [{"mechanism_id": mech_id, "evidence_id": paper["id"],
                                                     "match_reason": SOURCE_REASON}], "mechanism_id,evidence_id")
        org_name = a["organism_scientific_name"] or a["organism_common_name"]
        if org_name:
            slug = slugify(org_name)
            db.insert_ignore("organisms", [{"slug": slug, "scientific_name": a["organism_scientific_name"] or None,
                                            "common_name": a["organism_common_name"] or None,
                                            "habitat": a["organism_habitat"] or None}], "slug")
            org = db.select("organisms", {"select": "id", "slug": "eq." + slug})[0]
            db.insert_ignore("mechanism_organisms", [{"mechanism_id": mech_id, "organism_id": org["id"]}],
                             "mechanism_id,organism_id")
        db.insert_ignore("mechanism_functions",
                         [{"mechanism_id": mech_id, "function_id": slug_to_id[s]} for s in a["functions"] if s in slug_to_id],
                         "mechanism_id,function_id")
        with lock:
            stats["solution"] += 1
            stats["agree"] += agree
        print("  %-40s %s | agree=%s" % ((paper["title"] or "")[:40], a["mechanism_name"][:50], agree), flush=True)

    ready = [p for p in papers if (p["id"], 1) in stored and (p["id"], 2) in stored]
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(consolidate, ready))
    print("papers read:", len(ready), "of", len(papers))
    print(json.dumps(stats))


def compare(db, sample, system, schema, other_model, parent_of):
    """Run one pass of each model on the same sample and score both against PeTaL's human labels."""
    models = [MODEL, other_model]
    clients = {m: Claude(system, schema, m) for m in models}
    stored = {}
    for d in db.select("paper_passes", {"select": "evidence_id,model,output,status",
                                        "prompt_version": "eq." + PROMPT_VERSION, "pass_no": "eq.1"}):
        if d["status"] == "ok":
            stored[(d["evidence_id"], d["model"])] = d["output"]
    jobs = [(p, m) for p in sample for m in models if (p["id"], m) not in stored]
    print("compare passes to run:", len(jobs))

    def run(job):
        paper, m = job
        t = time.time()
        try:
            status, out = clients[m].read_paper(paper)
        except anthropic.APIError as e:
            status, out = "error", str(e)[:500]
        db.upsert("paper_passes", [{"evidence_id": paper["id"], "pass_no": 1, "prompt_version": PROMPT_VERSION,
                                    "model": m, "status": status, "output": out if status == "ok" else None,
                                    "error": None if status == "ok" else out}],
                  "evidence_id,pass_no,prompt_version,model", returning=False)
        if status == "ok":
            stored[(paper["id"], m)] = out
        print("  %-30s %-18s %s %.0fs" % ((paper["title"] or "")[:30], m, status, time.time() - t), flush=True)

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(run, jobs))

    report = {m: {"exact": 0, "family": 0, "none": 0, "has_solution": 0, "n": 0} for m in models}
    rows = []
    for p in sample:
        row = {"doi": p["doi"], "title": p["title"], "petal_labels": p["function_labels"]}
        for m in models:
            out = stored.get((p["id"], m))
            if not out:
                continue
            r = report[m]
            r["n"] += 1
            r[label_match(out["functions"], p["function_labels"], parent_of)] += 1
            r["has_solution"] += out["has_clear_solution"]
            row[m] = {k: out[k] for k in ("has_clear_solution", "why_not", "mechanism_name", "mechanism_summary",
                                          "how_it_works", "functions", "organism_scientific_name",
                                          "organism_common_name", "notes")}
        rows.append(row)
    out_path = "explora-model-compare.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"report": report, "rows": rows}, f, indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=1))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
