"""Shared helpers for the Explora data scripts: settings and Supabase REST."""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_env():
    """Read KEY=VALUE lines from the repo's .env (git-ignored) into os.environ."""
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def need(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit("Missing %s. Add it to .env in the repo root." % name)
    return value


def slugify(text, limit=80):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:limit].rstrip("-")


class Supabase:
    """Tiny PostgREST client. Uses the service role key, so keep it server side.

    public=True uses the publishable key instead: read-only, published rows only
    (row level security). The public site build uses this, so it needs no secret.
    """

    PUBLIC_URL = "https://johscicbgjmvxbwlzyat.supabase.co"
    PUBLIC_KEY = "sb_publishable_MB5kuJONlklys9duAH7hIg_RO48XwNU"  # also in src/lib/config.js

    def __init__(self, public=False):
        load_env()
        if public:
            self.url = os.environ.get("SUPABASE_URL", self.PUBLIC_URL).rstrip("/") + "/rest/v1/"
            key = os.environ.get("SUPABASE_ANON_KEY", self.PUBLIC_KEY)
        else:
            self.url = need("SUPABASE_URL").rstrip("/") + "/rest/v1/"
            key = need("SUPABASE_SERVICE_ROLE_KEY")
        self.headers = {
            "apikey": key,
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        }

    def _call(self, method, table, params=None, body=None, prefer=None):
        url = self.url + urllib.parse.quote(table)
        if params:
            url += "?" + urllib.parse.urlencode(params, safe=",.()*:")
        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise RuntimeError("%s %s failed: %s %s" % (method, table, e.code, e.read().decode()[:500]))

    def select(self, table, params=None, page=1000):
        """Return every row, paging with offset."""
        params = dict(params or {})
        rows, offset = [], 0
        while True:
            params.update({"limit": page, "offset": offset})
            batch = self._call("GET", table, params)
            rows.extend(batch)
            if len(batch) < page:
                return rows
            offset += page

    def upsert(self, table, rows, on_conflict, returning=True):
        if not rows:
            return []
        prefer = "resolution=merge-duplicates," + ("return=representation" if returning else "return=minimal")
        return self._call("POST", table, {"on_conflict": on_conflict}, rows, prefer) or []

    def insert_ignore(self, table, rows, on_conflict):
        if rows:
            self._call("POST", table, {"on_conflict": on_conflict}, rows,
                       "resolution=ignore-duplicates,return=minimal")

    def delete(self, table, params):
        self._call("DELETE", table, params, None, "return=minimal")

    def update(self, table, match, values):
        params = {k: "eq." + str(v) for k, v in match.items()}
        self._call("PATCH", table, params, values, "return=minimal")
