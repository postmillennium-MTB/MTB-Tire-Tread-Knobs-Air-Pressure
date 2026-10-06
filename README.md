# MTB-Tire-Tread-Knobs
Dressel, A.; Sadauckas, J

Interactive MTB tire simulator (Pacejka Magic Formula + FastBike twisting-torque polynomial) based on:
Dressel & Sadauckas, *Characterization and Modelling of Various Sized Mountain Bike Tires and the Effects of Tire Tread Knobs and Inflation Pressure*, Appl. Sci. 2020, 10, 3156. https://doi.org/10.3390/app10093156

## Background: the two tire models

**Pacejka Magic Formula.** An empirical curve fit for the force a tire generates, developed by Hans B. Pacejka (Delft University of Technology) and the standard starting point for tire modelling in vehicle dynamics. It describes lateral force as a smooth, saturating function of slip angle using four fitted coefficients: B (stiffness), C (shape), D (peak) and E (curvature). More on its author: [Hans B. Pacejka (Wikipedia)](https://en.wikipedia.org/wiki/Hans_B._Pacejka).

**FastBike twisting-torque polynomial.** FastBike is multibody simulation software for motorcycles and bicycles from Dynamotion, Padova, Italy ([FastBike software](https://www.dynamotion.it/en/software/fastbike-software/)). In [Dressel & Sadauckas (2020)](https://doi.org/10.3390/app10093156) (PDF in this repo: `applsci-10-03156-v2.pdf`) it is used for the *twisting torque due to camber*: the moment about the tire's vertical axis that appears when a single-track vehicle leans, driven mainly by the difference in peripheral velocities across the tire's toroidal shape. The paper fits it with FastBike's non-linear polynomial (its Eq. 5):

```
M_ZTW(φ) = m_r · φ · N · (1 + t_w · φ²)       φ = camber angle (rad)   N = normal load (N)
                                              m_r = linear coefficient   t_w = non-linear coefficient
```

Pacejka's Motorcycle Magic Formula is fitted to the lateral force (versus slip angle and versus camber) and to the self-aligning moment (versus slip angle).

**What this tool computes** (functions `pFy` and `fbMz` in `index.html`):

```
Fy = D·sin( C·atan( B·α' − E·( B·α' − atan(B·α') ) ) )      α' = α + camber shift
Mz = −t(α)·Fy + c0 + c1·α + c2·α²                           t(α) = t0·cos( Ct·atan(Bt·α) )
```

The first line is the Magic Formula for lateral force. The second is a pneumatic-trail formulation of the *self-aligning moment* with a slip-angle polynomial residual. It is a different construction from the paper's twisting-torque equation above. See `CLAUDE.md` ("Model integrity") before describing any output as the paper's.

The whole tool is one file: `index.html`.

## Color schemes

The **Theme** button cycles through three schemes, in this order:

1. **Win98 (light)** — default. Classic `#c0c0c0` window on a teal desktop.
2. **Win98 (grey)** — the same layout, darker, on a seamless stone-texture window. The texture is a 320px seamless tile cut from a stone photo and embedded in the CSS (`--w-tex`). The tool never loads the photo, so `image.png` can be deleted from the repo (restore it for regenerating with `git show 0d923a4:image.png > image.png`). `python3 scripts/make-stone-tile.py` regenerates it (crop and contrast constants at the top) and prints the CSS value to paste.
3. **Contrast** — high-contrast dark scheme (yellow on near-black).

Two more schemes are kept in the file but are **not in the cycle** for now:

- **Win00** — the original dark scheme (amber on navy-black), the look the tool had before the Win98 schemes. Internal id: `trail`.
- **Frost** — dark scheme with blue accents.

To switch them back on, find `THEME_ORDER` in the script and add their ids:

```js
const THEME_ORDER = ['win98','win98g','contrast','trail','frost'];
```

Every scheme is one entry in the `THEMES` registry in the script. The Win98 look (window, title bar, taskbar) is scoped to the `html.w98` class, so the dark schemes render exactly as they did before.

## Phones and touch devices

- A sticky **result bar** (peak Fy, contact area, μy and a Charts/Controls jump button) stays at the top while you drag sliders.
- The footprint chart comes first; the coefficient, derived-output and equation groups start collapsed (tap to open).
- Header, menu bar and taskbar are trimmed to save screen height.
- Touch devices (`pointer: coarse`) get 44px buttons and sliders, bigger checkboxes and type, in every color scheme. Mouse users get the original sizing.
- Pinch-zoom is allowed.

`scripts/mobile-check.mjs` is the automated mobile check (see `CLAUDE.md`): `node scripts/mobile-check.mjs index.html --cycle '#themeBtn' --cycles 3`.

## Known limits

- The paper tested five tires (Table 1): 29×2.3", 29×2.5", 29×3.0", 27.5×2.8" and 26×4.0", at a fixed 418 N normal load, mostly on a 25 mm inner-width rim (22 mm briefly), at 10–50 psi. Anything outside those conditions — other loads, rim widths, the 32" size, or width/size combinations the paper did not measure — is the tool's own interpolation or extrapolation, not measured data.
- The 32" wheel size is marked `*` as extrapolated beyond the paper's tested sizes.
