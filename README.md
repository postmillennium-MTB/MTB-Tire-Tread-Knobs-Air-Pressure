# MTB-Tire-Tread-Knobs
Dressel, A.; Sadauckas, J

Interactive MTB tire simulator (Pacejka Magic Formula + FastBike twisting-torque polynomial) based on:
Dressel & Sadauckas, *Characterization and Modelling of Various Sized Mountain Bike Tires and the Effects of Tire Tread Knobs and Inflation Pressure*, Appl. Sci. 2020, 10, 3156. https://doi.org/10.3390/app10093156

## Files

| File | What it is |
|---|---|
| `index.html` | The live tool (dark theme). |
| `win98-mockup.html` | The same tool with a selectable Windows 98 look. Same physics and charts; only the styling differs. |

## Color schemes (`win98-mockup.html`)

The **Theme** button cycles through the schemes in this order:

1. **Win98 (light)** — default. Classic `#c0c0c0` window on a teal desktop.
2. **Win98 (grey)** — the same layout with every shade one step darker.
3. **Win00** — the original dark scheme, unchanged (no Win98 window chrome).

**Frost** and **Contrast** (the two other original dark themes) are kept in the file but are not in the cycle for now.
To switch them back on, find `THEME_ORDER` in the script and add them:

```js
const THEME_ORDER = ['win98','win98g','trail','frost','contrast'];
```

(`trail` is the internal id of Win00.) Each scheme is one entry in the `THEMES` registry in the script.

## Touch devices

Phones and tablets (`pointer: coarse`) get larger controls in the Win98 schemes: 44px buttons and sliders, bigger checkboxes and type. Mouse users get the original 1998-sized controls.

## Known limits

- Nominal tire width is limited to 1.9–2.6". The model scales grip linearly with width, so values outside the range the paper tested would be extrapolation.
- The 32" wheel size is marked `*` as extrapolated beyond the paper's tested sizes.
