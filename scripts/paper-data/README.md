# How the paper's numbers got into the tool

Source: Dressel & Sadauckas (2020), *Appl. Sci.* **10**, 3156 — `applsci-10-03156-v2.pdf` in the repo root.
The paper prints coefficients for exactly one tire (Fig. 3). Everything else was read off its plots.

| Data | Where in the paper | How |
|---|---|---|
| Baseline coefficients (Magic Formula, FastBike `m_r`, `t_w`) | Fig. 3 | typed by hand from the figure labels — **exact** |
| Contact-patch size at each tire's nominal pressure | Fig. 5 | typed from the figure labels — **exact** |
| Cornering, camber, self-aligning, twisting stiffness vs pressure (9 tire setups) | Fig. 17 a–d | digitized — about ±3–5 % |
| Patch area, void ratio, length, width vs pressure | Fig. 16 a–d | digitized — about ±3–5 % |
| Rim width and pressure of each tire | Fig. 6 legend, Fig. 17 legend | read |
| `t_w` for tires other than the baseline | Fig. 6d, 12d | back-solved from the curve shape — about ±0.3 |
| End of the measured (solid) range of each curve | Fig. 6, 12 | read |

## Procedure (Fig. 16 / 17)
1. Render the figure page at 300 dpi: `pdftoppm -r 300 -f 19 -l 19 -png applsci-10-03156-v2.pdf pg`.
2. `find_plot_frames.py pg-19.png 450` finds each plot frame; gridline rows give the axis calibration
   (e.g. Fig. 17a: y = (1871.5 − px)/24.2 for 0–25 1/rad; x = (px − 559)/10.217 psi).
3. `digitize_markers.py` classifies pixels by marker colour (blue, red, cyan, magenta, green, gold, orange) and returns the
   cluster centre at each tested pressure. Filled and open markers of the same colour are told apart by pixel count.
4. Overlapping markers were resolved by hand: draw the chosen values back onto the figure as rings and check each one by eye.
5. **Check against the printed values** — they agree to ~1–3 % (e.g. Fig. 17a baseline @ 25 psi read 10.7 vs printed 10.488;
   Fig. 16 patch @ 25 psi read 34.7 cm², 122.9 × 36.6 mm vs printed 34.5 cm², 122 × 36 mm).
6. `gen_configs.py` writes the `CONFIGS` block pasted into `index.html`.

Markers hidden under other markers are the weakest points (mostly the 10 psi points and the bald / file-tread tires).
To improve one, re-read it from a zoomed crop and edit the table; the tier labels in `index.html` stay "read".
