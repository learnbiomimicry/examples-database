"""Export random enriched records to markdown for a human spot-check.

Usage: python scripts/explora/export_spotcheck.py [N] [OUT_FILE]
Default: 10 records to explora-spotcheck.md in the repo root.
"""
import os
import random
import sys
import time

from common import ROOT, Supabase

CRIT = [("lf_biomimicry_link", "rating_biomimicry_link", "Biomimicry link"),
        ("lf_ease_of_application", "rating_ease_of_application", "Ease of application"),
        ("lf_wide_applicability", "rating_wide_applicability", "Wide applicability"),
        ("lf_life_friendly_fit", "rating_life_principles", "Life-friendly fit"),
        ("lf_benefit_to_humanity", "rating_benefit_to_humanity", "Benefit to humanity")]


def fmt(v):
    if v in (None, ""):
        return "-"
    f = float(v)
    return str(int(f)) if f == int(f) else "%.1f" % f


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "explora-spotcheck.md")
    db = Supabase()
    enriched = db.select("case_study_enrichment", {"select": "*"})
    pick = random.sample(enriched, min(n, len(enriched)))
    cases = {c["id"]: c for c in db.select("biomimicry-examples", {
        "select": "id,title,slug,organism,company,rating_biomimicry_link,rating_ease_of_application,"
                  "rating_wide_applicability,rating_life_principles,rating_benefit_to_humanity"})}
    mechs = {m["id"]: m for m in db.select("mechanisms", {"select": "id,name,summary,how_it_works"})}
    funcs = {f["id"]: f for f in db.select("functions", {"select": "id,name,parent_id"})}
    mf = {}
    for r in db.select("mechanism_functions", {"select": "mechanism_id,function_id"}):
        mf.setdefault(r["mechanism_id"], []).append(r["function_id"])
    orgs = {o["id"]: o for o in db.select("organisms", {"select": "id,scientific_name,common_name,habitat"})}
    mo = {}
    for r in db.select("mechanism_organisms", {"select": "mechanism_id,organism_id"}):
        mo.setdefault(r["mechanism_id"], []).append(r["organism_id"])
    papers = {}
    for r in db.select("mechanism_evidence", {"select": "mechanism_id,match_reason,evidence(doi,title)"}):
        papers.setdefault(r["mechanism_id"], []).append(r)

    lines = [
        "# Explora spot-check: %d random enriched records" % len(pick),
        "",
        "Made %s from Supabase. Claude scores are the mean of two independent passes; 'your score' is the score you gave by hand, already in the database." % time.strftime("%d %B %Y"),
        "Please mark each record OK or note what is wrong. Paper evidence: NASA PeTaL (public domain), credit NASA.",
        "",
    ]
    for i, e in enumerate(pick, 1):
        case, mech = cases[e["case_study_id"]], mechs.get(e["mechanism_id"], {})
        ag = e.get("agreement") or {}
        lines += ["## %d. %s" % (i, case["title"]), "",
                  "- **Case study:** `%s` (company: %s)" % (case["slug"], case.get("company") or "-"),
                  "- **Mechanism:** %s" % mech.get("name", "-"),
                  "- **Summary:** %s" % mech.get("summary", "-"),
                  "- **How it works:**"]
        lines += ["  %d. %s" % (k, s) for k, s in enumerate(mech.get("how_it_works") or [], 1)]
        fn = []
        for fid in mf.get(e["mechanism_id"], []):
            f = funcs[fid]
            parent = funcs.get(f["parent_id"], {}).get("name")
            fn.append("%s > %s" % (parent, f["name"]) if parent else f["name"])
        lines.append("- **Functions (PeTaL):** %s" % ("; ".join(fn) or "-"))
        for oid in mo.get(e["mechanism_id"], []):
            o = orgs[oid]
            lines.append("- **Organism:** %s (*%s*)%s  (record says: %s)" % (
                o.get("common_name") or "-", o.get("scientific_name") or "-",
                ", " + o["habitat"] if o.get("habitat") else "", case.get("organism") or "-"))
        lines.append("- **Maturity:** %s" % (e.get("maturity") or "-"))
        lines.append("- **Two passes agree:** %s (organism %s, functions %s, mechanism %s, scores within 1 point %s)" % (
            "Yes" if e.get("passes_agree") else "No",
            *["yes" if ag.get(k) else "no" for k in ("organism", "functions", "mechanism", "scores_within_1")]))
        if ag.get("mechanism_reason"):
            lines.append("  - Judge: %s" % ag["mechanism_reason"])
        lines.append("- **Life-friendly score:** %s / 30" % fmt(e.get("lf_total")))
        for new, old, label in CRIT:
            lines.append("  - %s: %s (your score %s)" % (label, fmt(e.get(new)), fmt(case.get(old))))
        vs = e.get("lf_vs_existing") or {}
        if vs.get("mean_abs_gap") is not None:
            lines.append("  - Average gap from your scores: %s points" % vs["mean_abs_gap"])
        lines.append("- **Confidence:** %s (%s points)" % (e.get("confidence_level") or "-", e.get("confidence_points") or 0))
        lines += ["  - %s" % r for r in (e.get("confidence_reasons") or [])]
        ps = papers.get(e["mechanism_id"], [])
        if ps:
            lines.append("- **Linked papers (NASA PeTaL):** %d" % len(ps))
            for p in ps[:3]:
                ev = p.get("evidence") or {}
                lines.append("  - %s. https://doi.org/%s (%s)" % (ev.get("title"), ev.get("doi"), p["match_reason"]))
        lines += ["- **Your check:** ", ""]
    text = "\n".join(lines).replace("—", ", ")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
