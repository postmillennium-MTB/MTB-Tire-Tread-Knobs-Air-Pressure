# CLAUDE.md — MTB Tire Simulator (Post Millennium Renaissance)

Single-file tool: everything lives in `index.html` (markup, CSS, JS, data). It runs by
double-clicking it, has no build step, and loads only Chart.js from a CDN.
Served at postmillenniumrenaissance.com/tire-sim/ inside a full-viewport iframe.

Jon edits through GitHub's web UI, not a git CLI: deliver complete files, never "add this to your CSS".

## Standard

This repo follows the PMR build standard (the `pmr-build-standard` skill): one file, data above
`END OF DATA`, registries for anything that repeats, mobile-first, iframe-aware.
Every change is checked against the **seven audit dimensions**:

1. Data separation  2. Repetition  3. Hard-coded values  4. Comment coverage
5. Naming  6. Extensibility  7. **Automated mobile check** (below)

## 7. Automated mobile check

Mobile is not a judgment call per app. Every change that touches layout, CSS, markup or controls
runs the script below and passes **before it is pushed**.

```
node scripts/mobile-check.mjs index.html --cycle '#themeBtn' --cycles 2
```

It loads the page at 360×740, 390×844, 430×932 and 844×390 (landscape) with touch emulation,
once per color scheme, and **fails** on any of:

| Check | Limit |
|---|---|
| Horizontal overflow | none (page no wider than the viewport) |
| Touch targets (buttons, summaries, sliders, checkbox labels) | ≥ 40px on the short side (44px for primary controls) |
| DOM text | ≥ 11px (canvas text and `<sub>`/`<sup>` exempt) |
| First control (portrait) | starts within 75% of the viewport height — no wall of chrome |
| Pinch-zoom | never blocked (`user-scalable=no` / `maximum-scale=1` fail) |
| JavaScript errors | none |

Needs Playwright installed **globally** (`npm i -g playwright`) — the repo has no `package.json`.
Offline sandboxes: set `CHARTJS_LOCAL=/path/to/chart.umd.js` and `CHROMIUM_PATH=/path/to/chromium`.
Screenshots land in `mobile-check-out/` (one per viewport × scheme) — look at them; the script
cannot judge whether a layout is good, only whether it is broken.
A new color scheme is covered automatically by raising `--cycles` (one cycle per scheme in `THEME_ORDER`).

### Rules the check enforces (and the ones it cannot)

Enforced by the script: the table above. **Still the author's job** — the script cannot see these:

1. **Result next to control.** The primary output must be visible, or mirrored in a sticky strip
   (`#liveBar` here), while any control is being changed. Never make the user scroll past the
   controls to find out what they did.
2. **Payoff first, reference last.** Secondary content (equations, coefficient tables) goes in
   `<details>`, closed on phones, open on desktop. Order panels by what a phone user needs first.
3. **Small first screen.** Decorative chrome (fake menus, taskbars, subtitles) is hidden on phones.
4. **Size controls by pointer, not width:** `@media (pointer:coarse)` for touch sizing;
   `@media (max-width:…)` only for layout. Wrap `:hover` styling in `@media (hover:hover)`.
5. **Sliders:** `touch-action:pan-y` (horizontal drag = slider, vertical = scroll), thumb ≥ 26px,
   hit area = the thumb row, not the 4–6px track. Buttons get `touch-action:manipulation`.
6. **`order` needs flex/grid.** A `display:block` parent silently ignores `order` (this broke
   "footprint first" for months). Use `display:flex;flex-direction:column` when reordering.
7. **No fixed-position chrome on phones.** It eats screen height and misbehaves in iframes.
   Pad any fixed/bottom element with `env(safe-area-inset-bottom)`.
8. **Charts:** explicit height on phones, redraw on resize, no hover-only information.
9. **Footers/long text:** stack lines; never leave separators dangling at line ends.
10. **Real device:** Jon checks one phone before anything goes live. Emulation misses the
    browser toolbars, safe areas and touch feel.

### Pitfalls found the hard way (keep these)

- Playwright `page.screenshot({fullPage:true})` in a mobile context **permanently turns
  `pointer:coarse` off** for that page, so later measurements silently become desktop. The
  script takes screenshots last, in throwaway pages. Never take a full-page shot mid-run.
- ES-module scripts ignore `NODE_PATH`; the script falls back to `npm root -g` for Playwright.
- A CSS rule like `.ftr>span{display:block}` outranks `.ftr-dot{display:none}` — hide with the
  same specificity (`.ftr>.ftr-dot`).
- `100vh` on iOS Safari includes the area behind the browser toolbars. The **wrapper page**
  (not in this repo) uses `iframe{height:100vh}`, which hides the bottom ~100px of the tool on
  iPhones. The wrapper should use `height:100dvh` (with `100vh` as the fallback line before it).

## Color schemes

`THEMES` registry in the script; the Theme button cycles `THEME_ORDER`
(`win98`, `contrast`). Win00 (`trail`) and Frost (`frost`) stay defined but are out of
the cycle. The Win98 look is scoped under `html.w98`; the dark schemes must keep rendering as
they did before it. Mind the specificity trap in the standard: the default theme's CSS block goes first. See README for how to re-enable a scheme. The darker stone-textured "Win98 (grey)" was removed (git history: commit `2e03c03`).

## Model integrity

The tool **has no physics model of its own.** It shows the paper's numbers (`applsci-10-03156-v2.pdf`, in the repo) and nothing else. Read the PDF before making any claim about what "the paper says".

- All data lives in the `PAPER DATA` block of `index.html` (`CONFIGS`). Every value carries a tier — **printed** (typed in the paper: Fig. 3 baseline coefficients, Fig. 5 patch sizes), **read** (digitized from Fig. 16/17, ±3–5 %), **estimated** (`t_w` of non-baseline tires, from Fig. 6d/12d), **assumed** (reused outside the condition measured). The UI states the tier next to the numbers; keep it honest.
- Method, calibrations and scripts: `scripts/paper-data/`. To correct a value, edit the table there, re-run `gen_configs.py`, paste the block, and re-check it against the printed numbers.
- What the paper tested (offer nothing else): 29×2.3″ knobby & bald, 29×2.5″ file-tread & bald (25 mm rim; 22 mm for the knobby/file-tread at 10 and 25 psi), 29×3.0″ knobby (45 mm), 27.5×2.8″ knobby (38 mm), 26×4.0″ knobby (86 mm). One normal load, **418 N**. Nominal pressures 25 / 20 / 20 / 15 psi; the 29×2.3″ was swept 10–50 psi, the others measured at two pressures.
- The paper's FastBike equation is `M_ZTW(φ)=m_r·φ·N·(1+t_w·φ²)` in **camber** (Eq. 5). Pacejka's Magic Formula is fitted to lateral force (slip and camber) and self-aligning moment (slip).
- Slip was measured only to about ±2° (±1° on the 26×4″): the peak and curvature are not identified. Draw only the straight-line stiffness inside the measured range (and only as far as it agrees with the fitted curve: see `LINEAR_SLIP_*_DEG`). The Magic Formula curve exists for the baseline tire only.
- Do **not** add invented physics back (size factors, width scaling, knob factors, A = Fz/p patches): the old surrogate disagreed with the paper (e.g. it gave a 16 cm² patch where the paper measured 34.5 cm²). If the paper has no data for an option, the option should not exist.
- Test friction was non-skid tape on a small treadmill: say "relative comparison", never "grip on the trail".
