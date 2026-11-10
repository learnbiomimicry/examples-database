# Brand: Explora layout, Learn Biomimicry look

This site keeps Explora's layout, components and motion, and swaps Explora's own brand (Instrument Serif, DM Sans, steel blue #2D4F73) for the Learn Biomimicry identity. The tokens live at the top of `src/layouts/Base.astro`.

## Colour

From "Brand Identity, Logo Fonts and Colours - Learn Biomimicry.pdf", plus the website blue.

| Role | Token | Hex |
| --- | --- | --- |
| Primary text accent, sidebar, footer | `--lb-deep` | #0A4564 |
| Buttons, active pills, links on hover | `--lb-web` | #3498DB |
| Secondary blue | `--lb-steel` | #33668A |
| Light blue | `--lb-sky` | #87BAD9 |
| Aqua (accents on dark) | `--lb-aqua` | #A8DADC |
| Greens and ochre | `--lb-moss` `--lb-olive` `--lb-ochre` `--lb-amber` | #576E3D #808F42 #B0A64C #F5B23A |
| Reds | `--lb-plum` `--lb-berry` `--lb-rose` `--lb-coral` | #4F003A #891236 #CF4257 #FF6362 |
| Text | `--lb-charcoal` | #231F20 |

Level colours: Form = moss #576E3D, Process = steel #33668A, System = berry #891236.

## Type

| Use | Font | Explora used |
| --- | --- | --- |
| Headings, wordmark | Lato (300 for LEARN, 900 for BIOMIMICRY and headings) | Instrument Serif |
| Body | IBM Plex Sans Light | DM Sans Light |
| Case study titles, organism and problem text | IBM Plex Serif | IBM Plex Serif |
| Subtitles and italic accents | Fira Sans Italic | Instrument Serif Italic |
| Labels and overlines | IBM Plex Mono, uppercase, wide tracking | JetBrains Mono |

Note: the 2021 brand sheet names Fira Sans Italic for subtitles; the website notes mention Georgia Italic. This site follows the brand sheet. Pick one and update both.

## Motion (kept from Explora)

- Cards lift 8px with a soft blue glow; details slide open on hover (500 ms).
- Hero fades up in steps; sections fade up as they scroll into view.
- Category pills stick under the header after the hero; the level tabs stick inside the levels section.
- "View all" expands the grid in place.
- Level banner: particles bloom into a silhouette over 4.5 s and spring away from the cursor.
- Case study: rating counts up when it scrolls into view; criteria expand.
- Everything respects "reduce motion".

## Imagery

Real nature photography, as on learnbiomimicry.com. The level silhouettes in `public/silhouettes/` are stand-ins for Explora's originals (`whale-silhouette`, `mushroom-silhouette`, `planet-silhouette`), which can be copied across once the Explora repository is on GitHub.
