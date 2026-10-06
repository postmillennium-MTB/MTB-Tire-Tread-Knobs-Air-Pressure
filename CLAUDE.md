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
node scripts/mobile-check.mjs index.html --cycle '#themeBtn' --cycles 3
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
A new color scheme is covered automatically by raising `--cycles`.

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

Win98 (grey) has a stone texture: ONE textured surface (`.window`), every panel above it transparent so there are no seams, buttons/fields/bevels flat. The tile (`--w-tex`, 320px) is cut from a stone photo (`image.png`, deletable — restore with `git show 0d923a4:image.png > image.png`) by `scripts/make-stone-tile.py` (a photo is made seamless there with a two-pass cross-fade; `--procedural` makes a generated stone instead). Keep `SIZE` equal to the CSS `background-size` and `MEAN_GREY` equal to `--w-face`; `MIN_LEVEL` keeps dark text above 4.5:1. The tile is embedded as a data URI so the tool stays one file — The photo is only a source and is never loaded at runtime.

`THEMES` registry in the script; the Theme button cycles `THEME_ORDER`
(`win98`, `win98g`, `contrast`). Win00 (`trail`) and Frost (`frost`) stay defined but are out of
the cycle. The Win98 look is scoped under `html.w98`; the dark schemes must keep rendering as
they did before it. Mind the specificity trap in the standard: the default theme's CSS block goes first. See README for how to re-enable a scheme.

## Model integrity

Source paper: `applsci-10-03156-v2.pdf` (Dressel & Sadauckas 2020, in this repo). Read it before making any claim about what "the paper" says.

What the paper actually contains (checked against the PDF):
- Tires: 29×2.3", 29×2.5", 29×3.0", 27.5×2.8", 26×4.0" (Table 1). Fixed normal load **418 N**; rim **25 mm** inner width (22 mm briefly); pressures 10–50 psi (full sweep on the 29×2.3" only, two levels on the others).
- Pacejka Motorcycle Magic Formula fitted to lateral force (vs slip and vs camber) and to self-aligning moment (vs slip). FastBike's polynomial is fitted to the **twisting torque due to camber**: `M_ZTW(φ) = m_r·φ·N·(1 + t_w·φ²)` (Eq. 5).
- Fitted curves and stiffness trends; **no table of coefficients**, no width-scaling law, no wheel-size or knob-level factors.

Not found anywhere in the paper's text (so their source is unverified): `PACEJKA_COEFF`, the wheel-size factors (`WHEEL_SIZES.sf`), the linear width scaling in `sizeFactor`, the knob-level factors (`KNB`), the rim-width rules of thumb, and `fbMz` (pneumatic trail × Fy plus a slip-angle polynomial, which is not Eq. 5). The comment in `index.html` saying the coefficients "ARE the paper" is **not supported by the paper's text** — their provenance is unverified. Do not describe outputs as measured or "the paper's" results, and do not change the constants to improve a chart. If the UI labels "FastBike Mz" / "FastBike Poly Coefficients" are kept, they refer to this tool's own formulation.

Limits: the width slider is 1.9–2.6" while the paper's widths are 2.3–4.0" on specific wheel sizes; loads other than 418 N, rim widths other than 25/22 mm, and the 32" size are the tool's extrapolation and must be flagged as such.
