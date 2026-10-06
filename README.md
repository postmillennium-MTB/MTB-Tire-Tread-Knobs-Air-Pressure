# MTB-Tire-Tread-Knobs
Dressel, A.; Sadauckas, J

Interactive MTB tire simulator (Pacejka Magic Formula + FastBike twisting-torque polynomial) based on:
Dressel & Sadauckas, *Characterization and Modelling of Various Sized Mountain Bike Tires and the Effects of Tire Tread Knobs and Inflation Pressure*, Appl. Sci. 2020, 10, 3156. https://doi.org/10.3390/app10093156

The whole tool is one file: `index.html`.

## Color schemes

The **Theme** button cycles through three schemes, in this order:

1. **Win98 (light)** — default. Classic `#c0c0c0` window on a teal desktop.
2. **Win98 (grey)** — the same layout, darker, on a seamless stone-texture window. The texture is a generated 384px tile embedded in the CSS (`--w-tex`); `python3 scripts/make-stone-tile.py` regenerates it (change the constants at the top for a different stone) and prints the CSS to paste.
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

- Nominal tire width is limited to 1.9–2.6". The model scales grip linearly with width, so values outside the range the paper tested would be extrapolation.
- The 32" wheel size is marked `*` as extrapolated beyond the paper's tested sizes.
