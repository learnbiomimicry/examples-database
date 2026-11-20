# Explora demo: from mechanism-first to function-first

**Brief for the next build session (Claude Code or Cowork)**
Owner: Alistair Daynes, Learn Biomimicry
Date: 18 November 2026

---

## 0. Where this fits: the four-step journey

Explora's end-to-end process is:

| Step | What goes in | What comes out | What exists today | Main gap |
|---|---|---|---|---|
| **1. Find problems worth solving** | An industry, a product or a messy challenge | A sharp challenge statement ("How might nature help us…?"), root causes, a **requirements list**, and the functions to search | Biomimicry Project Finder v0.2, Biomimicry Project Playbook | Root-cause analysis and a requirements list |
| **2. Explore nature's solutions** | Functions | A shortlist of about 5 biological models and 3 design strategies, with confidence and evidence | 185 nature's solutions, NASA PeTaL papers, function doors (this brief) | Breadth beyond 185, patents (day 3) |
| **3. Design concepts** | Shortlisted solutions plus the requirements | 3 to 4 concepts, each with biological model, design principles, materials, manufacturing route and existing technology | Practitioner curriculum (abstraction), case studies as "existing technology" | The concept generator itself |
| **4. Engineer specs** | The chosen concept | A one-page spec: concepts scored against the requirements, key parameters and target values, a prototype and test plan, a patent check and the Life-friendly score | Nothing yet | All of it, and it's where Explora can lead |

This brief covers the front door to **Step 2**. Steps 1, 3 and 4 get their own briefs.

## 1. The change in one line

Today the demo opens with 185 nature's solutions, organised by mechanism. People arrive with a problem, not a mechanism. So the front door becomes **"How might nature help us…?"**, with a set of plain-English **"I need to…"** doors. The mechanism pages stay as the detail layer underneath.

## 2. Why

- R&D teams, Practitioners and Sprinters think in functions: "keep this cool", "stop dust building up", "make this lighter".
- The paying projects so far cluster around a few functions: thermal efficiency, self-cleaning surfaces, and packaging and materials.
- The "In Claude" mock-up already answers "How might nature help us cool a battery pack?". The website should work the same way the connector does.

## 3. What already exists (keep all of it)

Each mechanism page already has:

- A plain-English title and summary
- "How it works" in three steps
- Confidence (High / Medium / Low) with evidence points
- Proof level (for example "Proven in a product")
- Life-friendly score out of 30
- **Functions tags** (taxonomy terms such as "Protect from temperature", "Store energy", "Maintain homeostasis")
- The case study it came from, and the organism

The functions tags are what makes this change possible. We are **(re)grouping existing data**, not creating new content.

## 4. New structure

### 4.1 Home page

1. **Hero:** a single search box: "How might nature help us…" with example prompts underneath ("cool a battery pack", "keep solar panels clean", "make packaging without plastic").
2. **"I need to…" doors:** 8 cards, each with an icon, a plain-English name, and a count of solutions.
3. **Call to action** (see section 6).
4. Secondary link: "Browse all 185 solutions" (the current mechanism list, kept as is).

### 4.2 The eight "I need to…" doors (v1)

Each door maps to a group of existing functions tags. Final wording to be agreed; simple English first.

| Door | Plain English | Maps to functions tags like |
|---|---|---|
| 1 | **Keep things cool (or warm)** | Protect from temperature, Maintain homeostasis, Modify temperature, Store energy |
| 2 | **Keep surfaces clean and dry** | Manage liquids, Prevent fouling, Self-clean, Protect from microbes |
| 3 | **Find, hold and clean water** | Capture/absorb water, Filter, Store resources |
| 4 | **Be strong but light** | Manage structural forces, Distribute load, Prevent fracture |
| 5 | **Stick, grip and join** | Attach, Adhere, Hold in place |
| 6 | **Move through air or water with less effort** | Manage drag/turbulence, Move, Fly, Swim |
| 7 | **Make materials kindly and turn waste into value** | Process resources, Break down, Assemble, Cycle nutrients |
| 8 | **Organise teams, systems and places** | Coordinate, Communicate, Cooperate, Self-organise |

Rules:

- A solution can sit behind more than one door.
- Every solution must sit behind at least one door. Anything left over goes into a "Not yet sorted" list for Alistair to check.
- Optional later doors: "Sense and signal", "Protect and defend", "Heal and grow back".

### 4.3 Door page (for example "Keep things cool")

- Heading framed as a challenge: **"How might nature help us keep things cool?"**
- One line on why this matters to industry
- **Solutions, best first:** sorted by confidence, then proof level, then Life-friendly score
- **Filters:** industry, proof level (Proven / Tested / Idea), Life-friendly score, "Is it open?" (once patents land on day 3)
- **Linked doors:** "Teams with this problem also look at: Find, hold and clean water"
- The call to action at the bottom (section 6)

### 4.4 Mechanism page (small changes)

- Add a **"Helps you…"** row of chips near the top, linking back to each door it sits behind.
- Keep everything else.

## 5. Search (v1 simple, v2 smart)

- **v1:** keyword and synonym matching to doors. A small synonym list per door, for example Keep things cool: overheating, heat, thermal, cooling, battery, HVAC, air conditioning, insulation. A search shows the best door first, then the matching solutions.
- **v2:** let Claude (or embeddings) match free text to solutions, the same way the connector will. Not needed for the demo.
- **Empty search state:** "Not sure what your problem is yet?" leads straight to the call to action.

## 6. Call to action: "Find a problem worth solving, naturally"

Wording:

> **Find a problem worth solving, naturally**
> Most innovation fails before it starts, with the wrong problem. Our Biomimicry Project Finder helps you pick one worth solving, then shows you where nature has already solved it.
> [ Find your problem ]

Where it appears:

1. Home page, just under the doors
2. Bottom of every door page
3. In the "Apply this" section of every mechanism page
4. The empty search state

Button destination: **[link to be confirmed: Biomimicry Project Finder page, or the Practitioner Programme page]**.

## 7. Data clean-up before launch

**Merge these near-duplicates** (keep the strongest page and point the others to it):

- Fungal threads binding waste: `fungal-threads-growing-through-waste-to-bind-it`, `fungal-threads-that-grow-through-and-bind-loose-waste`, `fungal-threads-that-grow-through-waste-and-bind-it` (also check `grown-mat-of-interlocking-fungal-threads` and `self-interlocking-fungal-threads-grown-into-strong-sheets`)
- Protein fibres with hard crystals: `protein-chains-with-hard-crystals-and-stretchy-links`, `protein-fibre-with-hard-crystals-and-stretchy-links`, `protein-fibres-with-hard-crystals-in-a-stretchy-matrix`
- Tiny gripping hairs: `tiny-branching-hairs-that-grip-by-molecular-attraction`, `tiny-branching-hairs-that-stick-by-close-contact`, `tiny-hairs-that-grip-by-close-contact`
- Cell-like lattices: `cell-like-lattice-for-strength-with-little-material`, `cell-like-lattice-that-spreads-load-with-little-material`
- Waste feeds the next stage: `closed-loop-cascade-where-waste-feeds-the-next-process`, `closed-loop-material-cycles-where-waste-becomes-food`, `closed-loops-where-every-output-becomes-an-input`, `waste-from-one-stage-feeds-the-next`, `linked-network-where-one-member-s-waste-feeds-another`
- Buildings as living systems: `building-that-cycles-energy-water-and-waste-like-an-ecosystem`, `buildings-that-run-like-self-sufficient-living-systems`, `living-ecosystems-built-into-a-building`
- Spinning winged seeds: `spinning-winged-seed-shape-that-forms-a-lifting-vortex`, `spinning-winged-seed-vortex-flow-for-rotors`
- Water-repelling fibre films: `thin-molecular-water-repelling-film-on-single-fibres`, `thin-water-repelling-molecule-layer-bonded-to-fibres`
- Fog-harvesting surfaces: `patchy-surface-that-catches-fog-and-drains-water`, `patterned-water-loving-and-water-repelling-surfaces-that-harvest-fog`

**Drop or fix:** `unspecified-nature-inspired-biological-process` (placeholder).

**Check:** a number of mechanism pages are much smaller than the rest (about 40 KB against 150 to 600 KB). They may be missing images, evidence or a full case study.

## 8. Data model (Supabase, the single source of truth)

- New table `function_doors`: id, slug, name, plain-English line, icon, sort order, synonyms (text array)
- New table `door_functions`: door_id, function_tag (many to many with the existing functions tags)
- Solutions behind a door are worked out from their functions tags, not tagged by hand
- Merged duplicates: keep a `merged_into` field so old links still work

## 9. Done when

- [ ] The home page leads with "How might nature help us…" and eight "I need to…" doors
- [ ] Every one of the solutions sits behind at least one door; "Not yet sorted" is empty or checked by Alistair
- [ ] Door pages sort best evidence first and filter by industry and proof level
- [ ] Mechanism pages show "Helps you…" chips linking back to their doors
- [ ] Near-duplicates are merged and the placeholder is gone
- [ ] "Find a problem worth solving, naturally" appears in all four places, and the button works
- [ ] Searching "cool a battery pack", "clean solar panels" and "plastic-free packaging" each land on the right door

## 10. Order of work

1. Data clean-up (section 7) and the two new tables (section 8)
2. Door pages
3. New home page with search and the call to action
4. "Helps you…" chips on mechanism pages
5. Test the three searches in section 9

## 11. Prompt to start the build session

> Read `docs/function-first-brief.md`. We're changing the Explora demo from mechanism-first to function-first. Start in plan mode: list the files you'll change and the Supabase changes, then wait for my go-ahead. Do section 7 (data clean-up) first and show me the merge list before changing any data.
