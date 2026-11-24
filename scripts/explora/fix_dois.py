"""Fix the DOIs of NASA PeTaL papers by looking each title up in Crossref.

PeTaL's golden.json has its DOI and URL fields shuffled against the titles
(27 of 29 checked pointed to a different paper). Titles, abstracts and species
do line up, so the title is the safe key.

For each paper: search Crossref by title, take the best hit, and accept it only
if the titles are near identical. PeTaL's original value stays in petal_doi.
doi_check records the result: 'petal ok', 'fixed', or 'not found'.
Papers not found keep no DOI link (doi set to null) so nobody is sent to the wrong paper.

Usage: python scripts/explora/fix_dois.py
"""
import difflib
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from common import Supabase


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|[^a-z0-9 ]", " ", (t or "").lower())).strip()


def similar(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def crossref(path):
    req = urllib.request.Request("https://api.crossref.org/" + path, headers={"User-Agent": "explora-data-check/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]


def check(paper):
    title = paper["title"] or ""
    try:
        if paper["petal_doi"]:
            try:
                t = (crossref("works/" + urllib.parse.quote(paper["petal_doi"])).get("title") or [""])[0]
                if similar(t, title) >= 0.9:
                    return paper, paper["petal_doi"], "petal ok"
            except Exception:
                pass
        q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 5, "select": "DOI,title"})
        best = max(((similar((i.get("title") or [""])[0], title), i["DOI"]) for i in crossref("works?" + q)["items"]),
                   default=(0, None))
        if best[0] >= 0.9:
            return paper, best[1].lower(), "fixed"
        return paper, None, "not found"
    except Exception as e:
        return paper, None, "error: " + str(e)[:80]


def main():
    db = Supabase()
    # Clear unchecked DOIs first (PeTaL's value is kept in petal_doi), so a
    # corrected DOI never clashes with a shuffled one still sitting on another row.
    db._call("PATCH", "evidence", {"source": "eq.nasa-petal", "doi_check": "is.null"}, {"doi": None, "url": None},
             "return=minimal")
    papers = db.select("evidence", {"select": "id,title,petal_doi,doi_check", "source": "eq.nasa-petal"})
    todo = [p for p in papers if not p["doi_check"] or p["doi_check"].startswith("error")]
    print("papers to check:", len(todo))
    taken = {p["doi"] for p in db.select("evidence", {"select": "doi", "doi_check": "in.(petal ok,fixed)"})}
    counts = {}
    with ThreadPoolExecutor(2) as pool:
        for paper, doi, result in pool.map(check, todo):
            if doi and doi in taken:
                doi, result = None, "duplicate"
            if doi:
                taken.add(doi)
            values = {"doi_check": result, "doi": doi,
                      "url": "https://doi.org/" + doi if doi else None}
            if not result.startswith("error"):
                db.update("evidence", {"id": paper["id"]}, values)
            counts[result.split(":")[0]] = counts.get(result.split(":")[0], 0) + 1
            print("  %-12s %s" % (result[:12], (paper["title"] or "")[:70]), flush=True)
    print(counts)


if __name__ == "__main__":
    main()
