// Date-aware messages, shared by the build and the browser.
//
// Every message that depends on a date is rendered with data-from / data-until
// attributes. The build hides the ones outside their window (using today's date, or
// NOW=2027-01-15 in the environment for testing), and applyWindows() re-checks in the
// visitor's browser, so a message switches on time even if the site hasn't been rebuilt.
// Add ?now=2027-01-15 to any page address to preview another date.

const envNow = (typeof process !== "undefined" && process.env?.NOW) || import.meta.env?.NOW || "";
export const BUILD_NOW = Date.parse(envNow) || Date.now();

export function inWindow(from, until, t = BUILD_NOW) {
  return (!from || t >= Date.parse(from)) && (!until || t < Date.parse(until));
}

// Attributes for one date-aware element: spread them onto the tag.
export function win(from, until, t = BUILD_NOW) {
  return {
    "data-from": from || undefined,
    "data-until": until || undefined,
    hidden: inWindow(from, until, t) ? undefined : true,
  };
}

// A list of dated items (cohorts, deadlines) becomes consecutive windows: each item
// shows until its own date, and a final fallback (item: null) shows after the last one.
export function steps(items) {
  const out = [];
  let from = null;
  for (const item of items) {
    out.push({ item, from, until: item.date });
    from = item.date;
  }
  out.push({ item: null, from, until: null });
  return out;
}

// Browser side: show or hide every dated element for the visitor's current date.
export function applyWindows(root = document) {
  let t = Date.now();
  try {
    const q = new URLSearchParams(location.search).get("now");
    if (q && !Number.isNaN(Date.parse(q))) t = Date.parse(q);
  } catch {}
  root.querySelectorAll("[data-from], [data-until]").forEach((el) => {
    el.hidden = !inWindow(el.dataset.from, el.dataset.until, t);
  });
  return t;
}
