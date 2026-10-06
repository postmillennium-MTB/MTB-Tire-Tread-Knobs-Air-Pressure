# MTB-Tire-Tread-Knobs
Dressel, A.; Sadauckas, J

An interactive explorer for the measurements in:
Dressel & Sadauckas, *Characterization and Modelling of Various Sized Mountain Bike Tires and the Effects of Tire Tread Knobs and Inflation Pressure*, Appl. Sci. 2020, 10, 3156. https://doi.org/10.3390/app10093156 (PDF in this repo: `applsci-10-03156-v2.pdf`).

The whole tool is one file: `index.html`.

## What the tool shows

Every option is a tire, rim and pressure the paper actually tested — nothing is interpolated between tires or scaled by a made-up factor.

- **Tires:** 29″ × 2.3″ (knobby, bald), 29″ × 2.5″ (file-tread, bald), 29″ × 3.0″ (knobby), 27.5″ × 2.8″ (knobby), 26″ × 4.0″ (knobby), on the rims and at the pressures the paper used. Pick a wheel size and only the widths tested on it appear.
- **Charts:** lateral force vs slip, lateral force vs camber, self-aligning moment vs slip, twisting torque vs camber (the FastBike polynomial), the contact-patch ellipse drawn to scale, and any measured quantity vs inflation pressure. For the other tires the paper's own fitted curves (Fig. 6 and 12) are digitized and overlaid at the one pressure each was plotted for.
- **Extra panels:** tire cross-section outlines traced from Fig. 4 and 10 (one shared scale, crowns aligned); the knobs-as-springs model (Fig. 14, 18; 29×2.3″ knobby on a 25 mm rim only); static lateral and radial stiffness (Fig. 8, printed values).
- **Solid vs dashed lines:** solid is the range the authors actually measured; dashed is extrapolation, the paper's own convention.

### Where the numbers come from
| Tier | Meaning |
|---|---|
| **printed** | typed in the paper itself (Fig. 3 coefficients of the 29″ × 2.3″ knobby at 25 psi; Fig. 5 contact-patch sizes at nominal pressure). Exact. |
| **read** | digitized from the paper's plots (Fig. 16 patch size, Fig. 17 stiffness vs pressure), then checked against the printed values (agreement about 1–3 %). Treat as ±3–5 %. |
| **estimated** | the FastBike `t_w` of tires other than the baseline, least-squares fitted to the twisting-torque curves in Fig. 6d / 12d (about ±0.3). |
| **curves / outlines** | fitted curves and tire outlines digitized from the figures (about ±3 % of full scale; outlines ±1 mm). |
| **assumed** | a value reused outside the condition it was measured in. The tool says so next to the number. |

The method, calibration numbers and scripts are in `scripts/paper-data/` (new tables, curve and outline tracing in `scripts/paper-data/extra/`).

**Paper inconsistency:** Fig. 4 labels the 27.5×2.8″ rim `584-35`, while Fig. 6 and 17 use 38 mm; the tool follows 38 mm. Fig. 8b prints 60,365 N/m for two different radial bars; kept as printed.

## Background: the two tire models

**Pacejka Magic Formula.** An empirical curve fit for the force a tire generates, developed by Hans B. Pacejka (Delft University of Technology) and the standard starting point for tire modelling in vehicle dynamics. It describes force as a smooth, saturating function of slip or camber angle using four fitted coefficients: B (stiffness), C (shape), D (peak) and E (curvature). More on its author: [Hans B. Pacejka (Wikipedia)](https://en.wikipedia.org/wiki/Hans_B._Pacejka).

**FastBike twisting-torque polynomial.** FastBike is multibody simulation software for motorcycles and bicycles from Dynamotion, Padova, Italy ([FastBike software](https://www.dynamotion.it/en/software/fastbike-software/)). In the paper it models the *twisting torque due to camber*: the moment about the tire's vertical axis that appears when a single-track vehicle leans, driven mainly by the difference in peripheral velocities across the tire's toroidal shape (paper Eq. 5):

```
M_ZTW(φ) = m_r · φ · N · (1 + t_w · φ²)       φ = camber angle (rad)   N = normal load (N)
                                              m_r = linear coefficient   t_w = non-linear coefficient
```

The paper fits the Magic Formula to lateral force (versus slip and versus camber) and to the self-aligning moment (versus slip), and the polynomial above to twisting torque versus camber.

## Color schemes

The **Theme** button cycles through two schemes, in this order:

1. **Win98 (light)** — default. Classic `#c0c0c0` maximized window with a taskbar.
2. **Contrast** — high-contrast dark scheme (yellow on near-black).

Two more schemes are kept in the file but are **not in the cycle** for now:

- **Win00** — the original dark scheme (amber on navy-black). Internal id: `trail`.
- **Frost** — dark scheme with blue accents.

To switch them back on, find `THEME_ORDER` in the script and add their ids:

```js
const THEME_ORDER = ['win98','contrast','trail','frost'];
```

(A darker "Win98 (grey)" scheme with a stone texture existed briefly and was removed; it is in the git history, e.g. commit `2e03c03`, along with `scripts/make-stone-tile.py` and the source photo `image.png`.)

Every scheme is one entry in the `THEMES` registry in the script. The Win98 look (window, title bar, taskbar) is scoped to the `html.w98` class, so the dark schemes render as they did before.

## Phones and touch devices

- A sticky **result bar** (cornering force per degree, contact-patch area, `m_r` and a Charts/Controls jump button) stays at the top while you change tires and pressures.
- The footprint chart comes first; the coefficient, patch and equation groups start collapsed (tap to open).
- Header, menu bar and taskbar are trimmed to save screen height.
- Touch devices (`pointer: coarse`) get 44px buttons, bigger checkboxes and type, in every color scheme. Mouse users get the original sizing.
- Pinch-zoom is allowed.

`scripts/mobile-check.mjs` is the automated mobile check (see `CLAUDE.md`): `node scripts/mobile-check.mjs index.html --cycle '#themeBtn' --cycles 2`.

## Known limits (from the paper itself)

- **Slip range:** the treadmill limited slip to about ±2° (±1° on the 26 × 4″). The paper says the peak and curvature of the lateral-force and self-aligning curves could not be identified, only the slope near zero, so the tool draws that straight-line stiffness inside the measured range. The Magic Formula curve is drawn only for the one tire whose coefficients the paper prints.
- **One load:** every test used 418 N (95 kg rider on an 11 kg bike, 40 % front). Charts are normalized by load; "Newtons at 418 N" just multiplies by it.
- **Friction:** the treadmill was coated with non-skid tape, so absolute grip is not trail grip. Use the data for relative comparisons.
- **Slip and camber were swept separately,** never together, and the curves are drawn symmetric about zero (the paper's fits carry small offsets it does not report).
- **Overlapping markers** in the paper's plots limit the accuracy of a few points (mostly 10 psi and the bald / file-tread tires).

## The paper in one paragraph (for possible future use)

*A plain-language summary written for this project from the paper's results; the authors' own conclusion is Section 4 of the paper.*

Dressel and Sadauckas measured five mountain bike tire sizes — 29×2.3″, 29×2.5″, 27.5×2.8″, 29×3.0″ and 26×4.0″, the 29″ tires also with their tread sanded off — at one 418 N load, each on a rim and at a pressure typical of its use, and fitted Pacejka's Magic Formula and FastBike's twisting-torque polynomial to the forces and moments. Width changed behavior most: the 26×4.0″ fat bike had nearly double the cornering stiffness of the 29×2.3″ and by far the largest twisting torque, consistent with the heavy "autosteer" feel riders report. Yet every knobby tire's contact patch was mostly air, 70–81 % void and only 34–58 cm². Less-treaded tires were stiffer than knobby ones above about 20 psi, and treating knobs as springs in parallel on a carcass spring in series predicted a knobby tire's lateral stiffness within 8 %. Pressure mattered more than rim width: raising it from 10 to 50 psi more than halved the contact patch and cut camber and twisting-torque stiffness steeply, mostly below 30 psi, while moving from a 25 mm to a 22 mm rim changed little. The data suit relative comparison, not absolute grip: the treadmill coated in non-skid tape limited slip to about ±2° (±1° for the fat bike), so only each curve's slope near zero is reliable.

## Credits

- Data and models: Dressel & Sadauckas (2020), CC BY 4.0 (MDPI).
- The Windows 98 look was inspired by [98.css](https://jdan.github.io/98.css/) by Jordan Scales. The CSS here is hand-written for this tool; no 98.css code or assets are used.
