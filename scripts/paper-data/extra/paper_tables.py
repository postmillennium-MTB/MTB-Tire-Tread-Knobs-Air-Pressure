"""Hand-checked tables transcribed / digitized from Dressel & Sadauckas (2020). See README.md in this folder for method and tiers.
Pressures in psi."""
from fig17_table import T   # Fig. 17 a-d: (cornering 1/rad, camber 1/rad, self-aligning m, twisting m_r m)

# Fig. 16 a-d: (ellipse area cm2, void ratio %, length mm, width mm). Nominal points of the four knobby tires and the
# baseline @25 psi are PRINTED in Fig. 5; the rest are read from the plot.
P = {
 'k23':  {10:(66,81,155,55), 15:(53.5,81.5,137,50), 20:(45,81,134,43), 25:(34.5,78.1,122,36), 30:(30.5,76.5,121,32), 35:(29.5,76.5,119,31), 40:(26.5,75.5,112,30), 50:(24.5,75,108,28.5)},
 'f25':  {10:(55,75.5,165,42.5), 15:(38,69.5,144,33.5), 20:(31.5,67.5,130,31.5), 25:(28,66,116,30.5), 30:(23.5,62,111,27.5), 35:(22,61,104.5,26.5), 40:(19.5,59,101,24.5), 50:(17.5,56.5,96.5,23)},
 'b25':  {10:(50,20,166,38), 15:(37.5,19,145,32.5), 20:(29.8,17.5,129,29), 25:(27.5,19.5,121,27.5), 30:(22.3,16.5,114,25), 40:(17.8,14.5,104,21.5), 50:(15.2,11.5,96,19.5)},
 'b23':  {10:(52,5.5,156,43), 15:(39,3.5,141,35.5), 20:(31,3,132,30.5), 25:(26,2,116,27.5), 30:(22.5,1.5,110.5,26), 40:(18,3.5,100.5,22.5), 50:(15,4,94.5,20)},
 'k23n': {10:(58.7,77,146,51), 25:(32,70.5,115.5,35)},
 'f25n': {10:(43,71.5,161,34), 25:(26.8,71.5,119,29)},
 'k275': {10:(62.5,77,141,56.5), 20:(35.8,76.1,117,39)},
 'k29p': {10:(66.5,74.8,152,55.3), 20:(39.2,69.7,127,39)},
 'k26':  {10:(70,82.2,150,59), 15:(58.4,80.6,130,57)},
}
# key, id, wheel, width, tread, rim, nominal psi, measured slip max (deg), measured camber max (deg), t_w, t_w source, printed points
# t_w: baseline = printed (Fig. 3). Others = least-squares fit of Eq. 5 to the paper's twisting-torque curve (Fig. 6d / 12d) with m_r
# fixed from Fig. 17d (exception: 29x2.5 bald, whose Fig. 17d reading disagreed 12 % with its curve, so m_r came from the curve).
META = [
 ('k23',  'k23_25',  '29',   2.3, 'knobby',     25, 25, 2.4, 20, -2.118, 'printed',   {25:('stiffness','patch')}),
 ('b23',  'b23_25',  '29',   2.3, 'bald',       25, 25, 2.0, 13, -0.05,  'estimated', {}),
 ('k23n', 'k23_22',  '29',   2.3, 'knobby',     22, 25, 2.4, 20, -2.118, 'assumed',   {}),
 ('f25',  'f25_25',  '29',   2.5, 'file-tread', 25, 25, 2.0, 19, -0.42,  'estimated', {}),
 ('b25',  'b25_25',  '29',   2.5, 'bald',       25, 25, 1.7, 19,  0.85,  'estimated', {}),
 ('f25n', 'f25_22',  '29',   2.5, 'file-tread', 22, 25, 2.0, 19, -0.42,  'assumed',   {}),
 ('k29p', 'k29_45',  '29',   3.0, 'knobby',     45, 20, 1.5, 15,  6.92,  'estimated', {20:('patch',)}),
 ('k275', 'k275_38', '27.5', 2.8, 'knobby',     38, 20, 2.3, 22, -1.17,  'estimated', {20:('patch',)}),
 ('k26',  'k26_86',  '26',   4.0, 'knobby',     86, 15, 1.0, 15, -1.02,  'estimated', {15:('patch',)}),
]
# Fig. 8 (PRINTED): static lateral and radial stiffness at each tire's nominal rim and pressure, N/m.
# Note: the paper prints 60,365 for BOTH the 27.5x2.8 and 29x3.0 radial bars; kept as printed.
STATIC = [
 ('k23_25', 27710, 62295), ('k275_38', 30859, 60365), ('k29_45', 36181, 60365), ('k26_86', 59051, 58376),
]
# Fig. 14 / 18 (29x2.3 knobby, 25 mm): knobs-as-springs model.
KNOB = dict(
  k_knob=9837,                                    # N/m per knob, PRINTED (Fig. 14)
  psi=[10,15,20,25,30,40,50],
  n_knobs=[18,16,14,12,11,9,8],                   # knobs in the footprint, read from Fig. 18 (integers)
  carcass=[21800,27100,31500,39912,37100,41600,53700],   # bald-carcass lateral stiffness N/m; 25 psi PRINTED, others read (+/-5 %), cross-checked against Eq. 7
  measured_25=27710,                              # measured total at 25 psi, PRINTED (Fig. 8a, 14)
)
