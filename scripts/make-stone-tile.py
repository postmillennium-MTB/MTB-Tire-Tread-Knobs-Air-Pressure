#!/usr/bin/env python3
"""Generates the seamless grey stone tile used by the Win98 (grey) scheme.

  python3 scripts/make-stone-tile.py [out.jpg]      (needs: pip install pillow numpy)

Prints the CSS data-URI to paste into `--w-tex` in index.html, and writes a JPEG
(+ a 3x3 preview PNG next to it) so the tiling can be checked by eye.

Why generated, not photographed: a photo is rarely seamless, and FFT-filtered noise
is periodic by construction, so every layer below wraps at the tile edge (np.roll /
modulo drawing) and the tile repeats with no visible seam.
Tuning constants are named below; change them and re-run."""
import base64, io, sys
import numpy as np
from PIL import Image

SIZE        = 384     # px; also the CSS background-size. Larger = less visible repeat, bigger data URI
SEED        = 98      # change for a different (still seamless) stone
MEAN_GREY   = 160     # average level; MUST match --w-face in the grey scheme (#a0a0a0) so flat buttons blend in
CLOUD_AMP   = 6.5     # large soft mottling, +/- levels
BLOTCH_AMP  = 8.0     # mid-size darker patches
GRAIN_AMP   = 6.5     # fine speckle
PIT_COUNT   = 260     # tiny dark pits
CRACKS      = 5       # hairline cracks
CRACK_DEPTH = 30      # how much darker a crack pixel gets
MIN_LEVEL   = 136     # floor: keeps dark text (#1a1a1a) above 4.5:1 contrast on the darkest pixel
JPEG_QUALITY = 58

rng = np.random.default_rng(SEED)

def fft_noise(power, blur=0.0):
    """Zero-mean unit-std noise with a 1/f^power spectrum. Periodic by construction."""
    f = np.fft.fftfreq(SIZE)
    fx, fy = np.meshgrid(f, f)
    r = np.sqrt(fx**2 + fy**2); r[0, 0] = 1
    spec = (np.fft.fft2(rng.standard_normal((SIZE, SIZE))) / r**power)
    if blur: spec *= np.exp(-(r * SIZE * blur) ** 2 / 2)
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    return (n - n.mean()) / n.std()

img = np.full((SIZE, SIZE), float(MEAN_GREY))
img += CLOUD_AMP  * fft_noise(2.2)
blotch = fft_noise(1.4, blur=0.02)
img += BLOTCH_AMP * np.clip(blotch - 0.4, -1, 2.5)          # only the high tail -> distinct darker/lighter patches
img += GRAIN_AMP  * fft_noise(0.2)

for _ in range(PIT_COUNT):                                    # pits: a dark pixel with a faint halo, wrapped
    y, x = rng.integers(0, SIZE, 2); d = rng.uniform(10, 26)
    img[y, x] -= d
    img[(y + 1) % SIZE, x] -= d * .35; img[y, (x + 1) % SIZE] -= d * .35

def crack():                                                   # meandering hairline, coordinates wrap with modulo
    y, x = rng.uniform(0, SIZE, 2); ang = rng.uniform(0, 2 * np.pi)
    for _ in range(int(rng.integers(70, 150))):
        ang += rng.normal(0, 0.35); y += np.sin(ang); x += np.cos(ang)
        iy, ix = int(y) % SIZE, int(x) % SIZE
        img[iy, ix] -= CRACK_DEPTH
        img[(iy + 1) % SIZE, ix] -= CRACK_DEPTH * .3
for _ in range(CRACKS): crack()

img = np.clip(img, MIN_LEVEL, 255).astype(np.uint8)
im = Image.fromarray(img, 'L')
out = sys.argv[1] if len(sys.argv) > 1 else 'stone-tile.jpg'
im.save(out, 'JPEG', quality=JPEG_QUALITY, optimize=True)
prev = Image.new('L', (SIZE * 3, SIZE * 3))
for i in range(3):
    for j in range(3): prev.paste(im, (i * SIZE, j * SIZE))
prev.save(out.rsplit('.', 1)[0] + '-preview3x3.png')
data = open(out, 'rb').read()
print(f'{len(data)} bytes jpeg, mean={img.mean():.1f} min={img.min()} max={img.max()}', file=sys.stderr)
print('url("data:image/jpeg;base64,' + base64.b64encode(data).decode() + '")')
