# Explora V2.0 Strategy

Nov 18, 2026 · @Alistair Daynes

## Summary

Explora V2.0 becomes the open source (machine-readable) biomimicry database that AI tools rely on, plus a four-step workflow that companies pay us to run on their own problems.

**The bet in one line:** give the biomimicry knowledge away, we sell the outcome.

- **Open:** the core database of nature's solutions, its function map and its schema, free to read for people and AI agents under a non-commercial licence.

- **Paid:** the patent and opportunity layer, commercial and high-volume API access, and above all the work of taking a company's challenge through four steps: *Find problems worth solving, Explore nature's solutions, Design concepts, Engineer specs.*

- **Who pays first:** companies, not individuals. Our five biggest customers since 2023 are all organisations, and companies already pay for their people to join the Practitioner Programme.

- **Who builds the database:** Mainly Learn Biomimicry team. Other contributors include our Practitioners and Educators (about 48 a year), mentors, contributors and, over time, AI agents. Every contribution is checked before it goes live.

This memo is the single source of truth for Explora. It goes to the team, to Claude in Cowork, and into the Explora code as docs/STRATEGY.md, so that every build decision traces back to it.

**The decision we are making:** for the next 90 days, Explora is a service with software behind it. We prove that companies pay for the four-step outcome before we build more product.

## Core strategy on one page

We open the knowledge, earn trust and an audience with it, and get paid for helping companies act on it.

1.  **Open the database.** Nature's solutions, the function map and the schema stay free to read for people and AI agents. Every page is real HTML, so search engines and AI tools can find it.

2.  **Turn readers into a list.** Anyone can read 3 solutions or case studies free, then joins with name, email and field. Supabase holds the list; Kajabi sends the eBook emails for their field.

3.  **Grow it from the bottom up.** The team, Practitioners, Educators, mentors and, later, AI agents add to the database. Every contribution is checked before it goes live.

4.  **Sell the work, not the reading.** Companies pay for the patent and opportunity layer, commercial API access, and Team Sprints that take a challenge through Find, Explore, Design and Engineer.

5.  **Let each project feed the next.** Projects add data, data brings demand, and demand brings more projects.

## Core principles

Three principles guide every decision on Explora. When two options look equal, pick the one that is faster, gives people more freedom, or brings more people in.

| Principle                       | What it means                                                               | What it looks like in practice                                                                                                           |
|---------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **Unreasonable speed**          | We move fast and innovate effectively, on timelines that feel unreasonable. | Ship in days, not months. Test with real people before polishing. A working version today beats a perfect one next quarter.              |
| **Freedom**                     | We give our users the freedom to think, act, speculate and experiment.      | Open knowledge, free to read. No permission needed to try an idea. Wild ideas are welcome and safe to test.                              |
| **Bottom-up and collaborative** | Explora grows from the people who use it, not only from the top.            | Practitioners, Educators, mentors and users add to and improve the database. Ideas come from anyone. We build with people, not for them. |

## Why now

Four shifts in 2026 make this the moment, and we already hold the assets most others would need years to build.

1.  **AI agents now read databases directly.** Claude, Gemini and others call tools through connectors (MCP). When an engineer asks "how might nature help us cool a battery pack?", the answer comes from whichever source the agent can read and trust. Today biomimicry has no open, structured source for agents. Asteria is private / closed. AskNature's terms forbid robots, data mining and automated indexing. NASA's PeTaL is a tool for scientists built on about 1,400 labelled papers. The slot is empty.

2.  **Generating ideas has become cheap.** A list of biological models and four concepts, the core of what specialist tools sold two years ago, can now be drafted in minutes. The value has moved to what AI can't fake: checked evidence, real outcomes, and people who can take a concept into a spec.

3.  **We no longer have a tool partner.** The Asteria partnership ended because its cost made the Sprints and the Practitioner Programme unaffordable. We need our own tool either way.

4.  **Buyers have told us what they want.** In June 2026, Daan Reith at Heijmans turned down Explora early access: "hard to free up the budget without any concrete outcomes for our company. If it was up to me, I would do it." The person who uses Explora is not the person with the budget, and the budget holder buys outcomes.

**What we already have:**

| Asset                              | Today                                                                                                          |
|------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Case studies of nature's solutions | 181 published, each scored on 5 criteria, in Supabase                                                          |
| Nature's solutions (mechanisms)    | 1000+ mechanisms in the Explora demo, with confidence, proof level and function tags                           |
| Learner projects                   | About 100 Practitioner projects logged; Creative Commons licences since Sept 2025                              |
| People                             | About 48 Practitioners and Educators a year, plus a mentor team                                                |
| Company relationships              | Logoplaste, Heijmans, ELEKS, Exxaro, HBKU and others                                                           |
| Track record                       | Biomimicry Practitioner Programme is 42% of our business                                                       |
| Living infrastructure              | examples.learnbiomimicry.com (static, on Cloudflare), the Biomimicry Project Finder connector, explora.network |

## What others are getting wrong

Everyone in this space stops one step short of what a company will pay for. Each does something well; none closes the loop from a problem to a spec, with evidence that machines can read.

| Who                                                                                                                       | What they do well                              | Where they stop                                                                                                                                       | What Explora does instead                                                                          |
|---------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| [AskNature](https://asknature.org/innovation/colorful-waterproof-textiles-inspired-by-arthropods/) (Biomimicry Institute) | The best-known library; inspiring stories      | Closed to machines ([terms](https://biomimicry.org/terms/) forbid data mining); innovation pages carry no function tags, development stage or sources | Open, structured records with evidence, confidence and proof level, readable by people and agents  |
| [Asteria](https://asteria.life/use-cases/low-energy-high-density-data-storage)                                            | Polished AI workflow for large R&D teams       | Ends at concepts. Its use cases list needs, then never score the concepts against them, and report no measured outcomes                               | Step 4: concepts scored against the needs list, then target values, a test plan and a patent check |
| [NASA PeTaL](https://nasa-petal.github.io/blog/posts/engineering-elegance-from-nature)                                    | Open source; links biology papers to functions | Built for scientists; no path to a product                                                                                                            | Uses open papers like PeTaL's as evidence inside a practical workflow                              |
| Biomimicry courses (including ours, until now)                                                                            | Teach the method well                          | Learners often start with the wrong problem and stop at a concept                                                                                     | Step 1 (Project Finder) at the start; Explora as the place the project lives on after the course   |

Three mistakes sit underneath:

- **Selling the method, not the job.** Few R&D teams want "biomimicry". Many want to cut energy, drop a toxic chemical or make a part lighter. Explora's front door asks "How might nature help us…?" and is organised by function.

- **Treating the data as the product.** A database alone rarely earns money. It earns trust and attention, and that turns into paid work.

- **Building for the user, selling to nobody.** The engineer loves the tool; the budget holder needs an outcome. We price for the budget holder.

## The strategy

Explora takes one challenge through four steps and hands back a spec. The first two steps are free and open; the last two are where companies pay.

<img src="strategy-media/media/image1.png" style="width:6in;height:2.20536in" alt="Explora&#39;s four-step journey · what each step produces, and where money changes hands" />

Explora's four-step journey · what each step produces, and where money changes hands

The free steps bring people in and teach them our way of working. The paid steps produce what a budget holder can take to a meeting: concepts scored against their needs, target values and a test plan.

**Who pays, in order:**

1.  **Companies that already send people to us.** They get an "In-house Biomimicry Lab" package instead of a single seat.

2.  **R&D teams with a stuck problem.** They buy a Team Sprint: one challenge, all four steps, delivered by a mentor working with Explora.

3.  **Practitioners, Educators and Sprinters.** Explora is part of their programme for 12 months, then optional.

4.  **AI products and agents, later.** They pay for commercial or high-volume access to the database and the patent layer.

| Offer                                | Buyer                  | What they get                                                                                                        | Price                                                            |
|--------------------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| In-house Biomimicry Lab (new)        | Company                | 1 to 3 Practitioner seats, a Team Sprint on the company's own challenge, and an Explora team workspace for 12 months | To set after the discovery calls; target at least USD 10k a year |
| Team Sprint                          | R&D team               | One challenge through all four steps, ending in a dossier and spec                                                   | Target at least USD 10k per challenge                            |
| Practitioner and Educator Programmes | Individual or employer | The programme, with Explora included for 12 months                                                                   | Current prices                                                   |
| Explora Pro                          | Individual             | The workspace after the first 12 months                                                                              | USD 1,300 a year (founder rate USD 795)                          |
| API and agent access (later)         | AI products, companies | Commercial and high-volume use, patent layer                                                                         | Pay per use; set in 2027                                         |

**Pricing rule:** we price outcomes for budget holders, give individuals access through our programmes, and keep the open tier free because it is our marketing.

## Where Explora lives

Learn Biomimicry is where people learn; Explora is where they apply it. Both run on one database.

| Home                                             | What lives there                                                                                                                   | Who it serves                               |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| learnbiomimicry.com                              | Courses, blog, eBook, Practitioner and Educator Programmes                                                                         | Learners and educators                      |
| explora.network                                  | The open database (case studies and nature's solutions, linked and organised by function), use cases, Team Sprint, Opportunity Map | R&D teams, Practitioners at work, AI agents |
| Claude, through the Explora connector and Skills | The workspace where the four steps happen                                                                                          | Anyone running a project                    |

- **Brand:** "Explora, by Learn Biomimicry" until the B2B side stands on its own. Then we drop the "by", and Learn Biomimicry becomes the academy that trains people to use Explora.

- **One database:** Supabase, owned by the Explora US company and licensed to Learn Biomimicry.

- **One site:** the examples site moves to explora.network, with 301 (re)directs from examples.learnbiomimicry.com. The Lovable demo retires once the new site covers it.

- **Who signs up:** the free-reads limit applies to people browsing the site. Agents using the connector and search-engine crawlers always read freely, and every page stays real HTML.

- **Why now:** the examples site only went live in November 2026, so a move costs little search ranking. This replaces our earlier choice to keep the examples on learnbiomimicry.com.

## The open-source strategy

We open the knowledge and keep the outcome: anything that makes Explora the trusted source is open, and anything that turns a source into a result for one company is paid.

| Layer                                                    | Open or paid | Terms                                                        |
|----------------------------------------------------------|--------------|--------------------------------------------------------------|
| Nature's solutions and case study records                | Open         | CC BY-NC 4.0: free to use and share with credit, not to sell |
| Function map and data schema                             | Open         | CC BY 4.0, so others can adopt our structure (proposed)      |
| Website and connector code                               | Open         | MIT licence (proposed)                                       |
| Biomimicry Skills for Claude and Gemini                  | Free         | Email to download                                            |
| MCP connector, read access                               | Free         | Fair-use limits                                              |
| Patent and opportunity layer (Open, Free to use, Proven) | Paid         | Commercial licence                                           |
| Commercial or high-volume API use                        | Paid         | Pay per use                                                  |
| Team workspaces, steps 3 and 4                           | Paid         | Subscription or Team Sprint                                  |

**Why open works for us:**

- **Agents use what they can read.** An open, well-structured record gets cited by AI tools and found by search engines. A closed one is invisible to both.

- **Open data attracts contributors.** People improve what they can see and use.

- **Non-commercial protects the business.** Learners, teachers and scientists use it freely. A company or a tool that wants to sell on top of it buys a licence.

- **The value we sell is not in the records.** It is in the patent layer, the workflow and our people, none of which a copy of the data gives away.

### Can anyone add to it, humans or agents?

Yes. Anyone can propose a change, but nothing goes live without evidence and a check. The model is [iNaturalist](https://www.inaturalist.org), where anyone uploads an observation and it becomes "Research Grade" once others agree on it. Wikidata and OpenStreetMap work the same way.

1.  **Propose.** A person uses a web form; an agent uses a propose_solution tool in the MCP connector. Every proposal cites at least one source: a paper, a patent number or a company page.

2.  **Automatic checks.** Explora looks for duplicates (we already have about 9 groups of near-duplicates), checks that the sources exist, applies the plain-English rules and computes a confidence score from the evidence, as the demo does now.

3.  **Human verification.** A mentor or two verified Practitioners approve it, and it is marked Verified.

4.  **Publish with history.** Every record keeps its versions and credits its contributors, and any change can be undone.

**House rules:** contributors accept the licence when they submit; agents need a key and have rate limits; every change logs who or what made it; AI-written text is labelled until a person verifies it.

**Built-in contributors:** every Practitioner and Educator project ends with "add your nature's solutions to Explora". That is about 48 checked contributions a year before anyone else joins.

**What it means for the build:** Supabase stays the single source of truth. We add a proposals table, a status on every record (proposed, checked, verified, published) and a version history. The static site keeps building from published records only.

## Why this will work in the long term

It works because each finished project makes Explora more useful and easier to sell, and that loop gets stronger every year.

<img src="strategy-media/media/image2.png" style="width:6in;height:2.99107in" alt="Explora&#39;s flywheel · how projects, data and demand feed each other" />

Explora's flywheel · how projects, data and demand feed each other

AI models will keep getting better and cheaper, so the AI itself is no moat. What compounds is what AI cannot produce on its own:

- **Verified evidence.** Every record carries sources, a confidence score and a history of who checked it. That trail takes years to build and is what makes agents and engineers trust an answer.

- **A trained community.** About 48 Practitioners and Educators a year learn our method, use Explora and add to it. A competitor can copy the data; it cannot copy the people.

- **Real outcomes.** Each Team Sprint and Practitioner project, shared with permission, becomes a use case with measured outcomes. Mercy, one of our first Sprinters, used this workflow to file a provisional biomimetic patent in six weeks. Asteria's published use cases show concepts, not outcomes like that.

- **Education and tool together.** We are the only player that trains a company's people *and* gives them the tool. A company that has trained staff keeps using the tool, and the tool keeps the training alive.

The open licence makes the loop turn faster: more people and agents can read Explora, so more of them find us.

## The next 90 days

The 90 days answer one question before anything else: will a company pay for the four-step outcome?

<img src="strategy-media/media/image3.png" style="width:6in;height:1.95536in" alt="Explora V2.0 · 90-day plan, 23 Nov 2026 to 26 Feb 2027" />

Explora V2.0 · 90-day plan, 23 Nov 2026 to 26 Feb 2027

The gate falls on Jan 29, 2027. If a company has paid, or three have committed in writing, Alistair moves from 8 to 16 hours a week on Explora. If not, Explora stays a tool inside our programmes and we (re)think the B2B offer with what the calls taught us.

| Measure                                                                                                   | Target by 26 Feb 2027 |
|-----------------------------------------------------------------------------------------------------------|-----------------------|
| Discovery calls held (alumni sponsors, ELEKS, Canyon, LogoPlaste)                                         | 8                     |
| Companies paying for a Team Sprint pilot                                                                  | At least 1            |
| Use-case pages live, in the four-step format                                                              | 3                     |
| Test searches landing on the right function (battery cooling, clean solar panels, plastic-free packaging) | 3 of 3                |
| Verified contributions through the new flow                                                               | First 10              |

**How we stay aligned with Claude:** this memo is exported to the Explora code as docs/STRATEGY.md, and CLAUDE.md points to it. Every build brief (the first is the function-first demo) names the section it serves. If a task doesn't serve this memo, we don't build it this quarter.

## Risks, open questions and what we need from the team

The biggest risk is time, not technology. That is why the first 90 days are a service, run by hand, with a clear gate.

| Risk                                                        | What we do about it                                                                                        |
|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Alistair has 8 hours a week                                 | Service first; Claude does most of the build; hours rise only after the gate                               |
| Wrong or AI-invented records                                | Sources on every record, verification before publishing, AI text labelled, duplicates merged before launch |
| Spam or low-quality contributions                           | Agent keys, rate limits, nothing live without a check                                                      |
| The Lab package takes sales from the Practitioner Programme | The package includes Practitioner seats; we test it rather than assume                                     |
| The non-commercial licence slows company use                | Commercial licence on request; the schema and function map stay CC BY                                      |
| A larger tool copies the open data                          | Our edge is the people, the outcomes and the patent layer, not the records                                 |

**Open questions to settle by the gate:**

- [ ] What does the In-house Biomimicry Lab cost?

- [ ] CC BY-NC or CC BY-SA for the core records?

- [ ] Do we ask past Practitioners for Creative Commons licences on their projects?

- [ ] Who verifies contributions, and are mentors paid for it?

- [ ] When, if ever, does the Explora US company raise capital?

**What we need from the team:**

- **Mentors:** act as verifiers, and join the pilot Team Sprints.

- **Everyone:** pass every company enquiry to Alistair, and flag any learner whose employer paid.

- **Programme team:** add "add your nature's solutions to Explora" to the final project, starting with the Xenopus cohort in February 2027.

## Sources

- [Asteria use case: Long-term low-energy data storage](https://asteria.life/use-cases/low-energy-high-density-data-storage)

- [Biomimicry Institute terms of use](https://biomimicry.org/terms/)

- [AskNature: Colorful waterproof textiles inspired by arthropods](https://asknature.org/innovation/colorful-waterproof-textiles-inspired-by-arthropods/)

- [NASA PeTaL: Engineering elegance from nature](https://nasa-petal.github.io/blog/posts/engineering-elegance-from-nature)

- [iNaturalist](https://www.inaturalist.org)

- Learn Biomimicry: Xero / top customers since March 2023, Biomimicry Projects Database, Explora demo (18 Nov 2026)
