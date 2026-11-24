"""Link NASA PeTaL papers to mechanisms, then work out confidence scores.

Confidence answers "how sure are we that it works?" It is built only from
evidence we hold, using fixed rules, so anyone can see why a record got its
label. Points:

  Maturity (from the AI pass)    on market +3, pilot +2, lab +1, concept 0
  Products listed in the record  +1
  Named company                  +1
  Measured results (numbers in key metrics)  +1
  Done again by others: 2 or more companies use the same mechanism  +2
  Peer-reviewed papers on the organism (NASA PeTaL): 3 or more +2, 1 to 2 +1
  Granted patents                not checked yet (day 3), 0 for now

  High    6 or more points AND the two AI passes agree
  Medium  3 to 5 points, or 6 or more when the passes disagree
  Low     2 or fewer points

Usage: python scripts/explora/confidence.py
"""
import re
import time

from common import Supabase

MATURITY_POINTS = {"on market": 3, "pilot": 2, "lab": 1, "concept": 0}
MATURITY_WORDS = {"on market": "On the market", "pilot": "In pilot or early use",
                  "lab": "Lab results only", "concept": "Concept only"}


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", (s or "").lower())).strip()


def link_papers(db, mechanisms, organisms, mech_orgs):
    """Link NASA PeTaL papers to mechanisms. Rebuilt in full on every run.

    An exact species name (two words) links on its own. A genus or common-name
    match only links when the paper also shares a PeTaL function (or its parent
    family) with the mechanism, so broad names like "insects" do not flood it.
    """
    papers = db.select("evidence", {"select": "id,species", "source": "eq.nasa-petal"})
    funcs = {f["id"]: f for f in db.select("functions", {"select": "id,parent_id"})}

    def family(fids):
        return set(fids) | {funcs[f]["parent_id"] for f in fids if funcs.get(f, {}).get("parent_id")}

    paper_funcs = {}
    for r in db.select("evidence_functions", {"select": "evidence_id,function_id"}):
        paper_funcs.setdefault(r["evidence_id"], set()).add(r["function_id"])
    mech_funcs = {}
    for r in db.select("mechanism_functions", {"select": "mechanism_id,function_id"}):
        mech_funcs.setdefault(r["mechanism_id"], set()).add(r["function_id"])
    index = {}
    for p in papers:
        for s in p["species"] or []:
            index.setdefault(norm(s), set()).add(p["id"])
    links = []
    for mech_id, org_ids in mech_orgs.items():
        mfam = family(mech_funcs.get(mech_id, ()))
        for org_id in org_ids:
            org = organisms[org_id]
            sci, common = norm(org["scientific_name"]), norm(org["common_name"])
            found = {}

            def shares_function(pid):
                return bool(mfam & family(paper_funcs.get(pid, ())))

            if sci and " " in sci:
                for pid in index.get(sci, ()):
                    found[pid] = "species name matches: " + org["scientific_name"]
            if sci:
                genus = sci.split()[0]
                if len(genus) > 3:
                    for name, ids in index.items():
                        if name.split(" ")[0] == genus:
                            for pid in ids:
                                if pid not in found and shares_function(pid):
                                    found[pid] = "same genus (%s) and a shared function" % genus.title()
            if common and len(common) > 4:
                for pid in index.get(common, ()):
                    if pid not in found and shares_function(pid):
                        found[pid] = "common name (%s) and a shared function" % org["common_name"]
            links += [{"mechanism_id": mech_id, "evidence_id": pid, "match_reason": why} for pid, why in found.items()]
    # Rebuild: these links are derived data, made only by this script.
    # Source-paper links (made by extract_papers.py) are kept.
    db.delete("mechanism_evidence", {"match_reason": "not.like.Source paper*"})
    for i in range(0, len(links), 500):
        db.insert_ignore("mechanism_evidence", links[i:i + 500], "mechanism_id,evidence_id")
    return links


def has_numbers(metrics):
    if not metrics:
        return False
    text = " ".join(str(v) for m in metrics if isinstance(m, dict) for v in m.values())
    return bool(re.search(r"\d", text))


def score(maturity, products, company, metrics, companies_on_mechanism, n_papers, agree):
    points, reasons = 0, []
    if maturity:
        points += MATURITY_POINTS[maturity]
        reasons.append("%s (+%d)" % (MATURITY_WORDS[maturity], MATURITY_POINTS[maturity]))
    if products:
        points += 1
        reasons.append("Products are listed (+1)")
    if company:
        points += 1
        reasons.append("Named company: %s (+1)" % company)
    if metrics:
        points += 1
        reasons.append("Has measured results (+1)")
    if companies_on_mechanism >= 2:
        points += 2
        reasons.append("Done again by others: %d companies use this mechanism (+2)" % companies_on_mechanism)
    if n_papers >= 3:
        points += 2
        reasons.append("%d peer-reviewed papers on this organism in NASA PeTaL (+2)" % n_papers)
    elif n_papers:
        points += 1
        reasons.append("%d peer-reviewed paper%s on this organism in NASA PeTaL (+1)" % (n_papers, "" if n_papers == 1 else "s"))
    else:
        reasons.append("No linked papers yet")
    reasons.append("Patents not checked yet")
    if agree:
        reasons.append("Two independent AI passes agree")
    else:
        reasons.append("The two AI passes disagree, so this cannot be High")

    if points >= 6 and agree:
        level = "High"
    elif points >= 3:
        level = "Medium"
    else:
        level = "Low"
    return level, points, reasons


def main():
    db = Supabase()
    mechanisms = {m["id"]: m for m in db.select("mechanisms", {"select": "id,slug,origin,passes_agree"})}
    organisms = {o["id"]: o for o in db.select("organisms", {"select": "id,scientific_name,common_name"})}
    mech_orgs = {}
    for r in db.select("mechanism_organisms", {"select": "mechanism_id,organism_id"}):
        mech_orgs.setdefault(r["mechanism_id"], []).append(r["organism_id"])

    links = link_papers(db, mechanisms, organisms, mech_orgs)
    papers_per_mech = {}
    for l in db.select("mechanism_evidence", {"select": "mechanism_id,evidence_id"}):
        papers_per_mech.setdefault(l["mechanism_id"], set()).add(l["evidence_id"])
    print("paper links made this run:", len(links), "| mechanisms with papers:", len(papers_per_mech))

    enriched = db.select("case_study_enrichment", {"select": "case_study_id,mechanism_id,maturity,passes_agree"})
    cases = {c["id"]: c for c in db.select("biomimicry-examples", {"select": "id,company,products,key_metrics"})}

    companies = {}
    for e in enriched:
        co = (cases[e["case_study_id"]].get("company") or "").strip().lower()
        if co:
            companies.setdefault(e["mechanism_id"], set()).add(co)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    by_mech = {}
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for e in enriched:
        case = cases[e["case_study_id"]]
        level, points, reasons = score(
            e["maturity"], (case.get("products") or "").strip(), (case.get("company") or "").strip(),
            has_numbers(case.get("key_metrics")), len(companies.get(e["mechanism_id"], ())),
            len(papers_per_mech.get(e["mechanism_id"], ())), bool(e["passes_agree"]))
        counts[level] += 1
        db.update("case_study_enrichment", {"case_study_id": e["case_study_id"]},
                  {"confidence_level": level, "confidence_points": points,
                   "confidence_reasons": reasons, "updated_at": now})
        best = by_mech.get(e["mechanism_id"])
        # A mechanism takes its strongest case study, but only if every pass on it agrees.
        if best is None or points > best[1]:
            by_mech[e["mechanism_id"]] = (level, points, reasons, e["passes_agree"])
    all_agree = {}
    for e in enriched:
        all_agree[e["mechanism_id"]] = all_agree.get(e["mechanism_id"], True) and bool(e["passes_agree"])
    for mech_id, (level, points, reasons, _) in by_mech.items():
        if level == "High" and not all_agree[mech_id]:
            level = "Medium"
        db.update("mechanisms", {"id": mech_id},
                  {"confidence_level": level, "confidence_points": points, "confidence_reasons": reasons,
                   "passes_agree": all_agree[mech_id], "updated_at": now})
    print("case study confidence:", counts)

    # Solutions read from papers: nothing built yet, so lab results plus papers.
    paper_counts = {"High": 0, "Medium": 0, "Low": 0}
    for mech_id, m in mechanisms.items():
        if m.get("origin") != "paper":
            continue
        level, points, reasons = score("lab", "", "", False, 0, len(papers_per_mech.get(mech_id, ())),
                                       bool(m.get("passes_agree")))
        paper_counts[level] += 1
        db.update("mechanisms", {"id": mech_id}, {"confidence_level": level, "confidence_points": points,
                                                  "confidence_reasons": reasons, "updated_at": now})
    print("paper solution confidence:", paper_counts)


if __name__ == "__main__":
    main()
