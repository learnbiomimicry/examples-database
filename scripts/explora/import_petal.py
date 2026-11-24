"""Build SQL to load NASA PeTaL data into Explora.

Inputs (from public-domain NASA PeTaL repos, The Unlicense):
  taxonomy.csv  github.com/nasa-petal/PeTaL-labeller  scripts/dag-formatter/taxonomy.csv
  golden.json   github.com/nasa-petal/data-collection-and-prep  golden.json

We keep DOIs, titles, function labels and species names only. Abstracts are
never stored: publishers own them. Only papers PeTaL marked as biomimicry
(isBiomimicry = Y, about 1,430) are loaded.

Usage:
  python3 scripts/explora/import_petal.py --load GOLDEN_JSON
      Load the papers into Supabase over REST (uses .env keys).
  python3 scripts/explora/import_petal.py TAXONOMY_CSV GOLDEN_JSON OUT_DIR
      Write OUT_DIR/01_functions.sql and OUT_DIR/02_evidence_NN.sql (in chunks)
      instead, each safe to run more than once.
"""
import ast
import csv
import json
import os
import re
import sys

CREDIT = "NASA PeTaL project (NASA Glenn Research Center), github.com/nasa-petal"
LICENCE = "The Unlicense (public domain)"


def slugify(name):
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", name.strip().lower())).strip("_")


def q(value):
    if value is None:
        return "null"
    return "'" + str(value).replace("'", "''") + "'"


def arr(values):
    if not values:
        return "null"
    return "array[" + ",".join(q(v) for v in values) + "]::text[]"


def parse_list(raw):
    if not raw:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw]
    try:
        out = ast.literal_eval(raw)
        return [str(x) for x in out] if isinstance(out, (list, tuple)) else []
    except (ValueError, SyntaxError):
        return []


def load_taxonomy(path):
    """Return list of (slug, name, level, parent_slug)."""
    rows, l1, l2 = [], None, None
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for cells in reader:
            cells = [c.strip() for c in cells] + ["", "", ""]
            a, b, c = cells[:3]
            if a:
                l1 = slugify(a)
                rows.append((l1, a, 1, None))
            if b:
                l2 = slugify(b)
                rows.append((l2, b, 2, l1))
            if c:
                rows.append((slugify(c), c, 3, l2))
    seen, unique = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            unique.append(r)
    return unique


def functions_sql(tax):
    lines = ["-- NASA PeTaL function taxonomy. " + CREDIT]
    for level in (1, 2, 3):
        for slug, name, lvl, parent in tax:
            if lvl != level:
                continue
            parent_sql = (
                "(select id from public.functions where slug = %s)" % q(parent) if parent else "null"
            )
            lines.append(
                "insert into public.functions (slug, name, level, parent_id, source) values "
                "(%s, %s, %d, %s, 'nasa-petal') on conflict (slug) do nothing;"
                % (q(slug), q(name), lvl, parent_sql)
            )
    return "\n".join(lines) + "\n"


def evidence_chunks(golden, known_slugs, chunk_size=250):
    papers = [p for p in golden if p.get("isBiomimicry") == "Y" and p.get("doi")]
    unmatched = set()
    chunks = []
    for start in range(0, len(papers), chunk_size):
        lines = []
        for p in papers[start:start + chunk_size]:
            doi = p["doi"].strip().lower()
            labels = parse_list(p.get("level3")) + parse_list(p.get("level2"))
            labels = [slugify(x) for x in labels]
            matched = [x for x in labels if x in known_slugs]
            unmatched.update(x for x in labels if x not in known_slugs)
            species = sorted({s.strip().lower() for s in parse_list(p.get("species")) if s.strip()})
            url = p.get("url") or ("https://doi.org/" + doi)
            lines.append(
                "insert into public.evidence (source, source_id, doi, title, url, function_labels, species, credit, licence) values "
                "('nasa-petal', %s, %s, %s, %s, %s, %s, %s, %s) "
                "on conflict (source, doi) do update set title = excluded.title, function_labels = excluded.function_labels, species = excluded.species;"
                % (q(p.get("paper")), q(doi), q((p.get("title") or "").strip()), q(url),
                   arr(labels), arr(species), q(CREDIT), q(LICENCE))
            )
            for slug in sorted(set(matched)):
                lines.append(
                    "insert into public.evidence_functions (evidence_id, function_id) "
                    "select e.id, f.id from public.evidence e, public.functions f "
                    "where e.source = 'nasa-petal' and e.doi = %s and f.slug = %s on conflict do nothing;"
                    % (q(doi), q(slug))
                )
        chunks.append("\n".join(lines) + "\n")
    return chunks, len(papers), unmatched


def load_rest(golden):
    """Load the papers straight into Supabase over REST (needs .env keys)."""
    from common import Supabase
    db = Supabase()
    func_ids = {f["slug"]: f["id"] for f in db.select("functions", {"select": "id,slug"})}
    papers, seen = [], set()
    for p in golden:
        doi = (p.get("doi") or "").strip().lower()
        if p.get("isBiomimicry") == "Y" and doi and doi not in seen:
            seen.add(doi)
            papers.append(p)
    for start in range(0, len(papers), 200):
        batch = papers[start:start + 200]
        rows = []
        for p in batch:
            doi = p["doi"].strip().lower()
            rows.append({
                "source": "nasa-petal", "source_id": p.get("paper"), "doi": doi,
                "title": (p.get("title") or "").strip(),
                "url": p.get("url") or "https://doi.org/" + doi,
                "function_labels": [slugify(x) for x in parse_list(p.get("level3")) + parse_list(p.get("level2"))],
                "species": sorted({s.strip().lower() for s in parse_list(p.get("species")) if s.strip()}),
                "credit": CREDIT, "licence": LICENCE,
            })
        saved = db.upsert("evidence", rows, "source,doi")
        links = [{"evidence_id": e["id"], "function_id": func_ids[s]}
                 for e in saved for s in set(e["function_labels"] or []) if s in func_ids]
        db.insert_ignore("evidence_functions", links, "evidence_id,function_id")
        print("  loaded %d of %d papers" % (start + len(batch), len(papers)), flush=True)


def main():
    if "--load" in sys.argv:
        golden_path = sys.argv[sys.argv.index("--load") + 1]
        with open(golden_path, encoding="utf-8") as f:
            load_rest(json.load(f))
        return
    tax_path, golden_path, out_dir = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    tax = load_taxonomy(tax_path)
    with open(os.path.join(out_dir, "01_functions.sql"), "w", encoding="utf-8") as f:
        f.write(functions_sql(tax))
    with open(golden_path, encoding="utf-8") as f:
        golden = json.load(f)
    chunks, n, unmatched = evidence_chunks(golden, {t[0] for t in tax})
    for i, sql in enumerate(chunks, 1):
        with open(os.path.join(out_dir, "02_evidence_%02d.sql" % i), "w", encoding="utf-8") as f:
            f.write(sql)
    print("functions:", len(tax), "| papers:", n, "| chunks:", len(chunks))
    if unmatched:
        print("labels with no taxonomy match:", sorted(unmatched))


if __name__ == "__main__":
    main()
