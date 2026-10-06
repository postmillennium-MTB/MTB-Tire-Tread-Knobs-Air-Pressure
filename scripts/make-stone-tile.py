#!/usr/bin/env python3
"""Builds the seamless stone tile used by the Win98 (grey) scheme.

  python3 scripts/make-stone-tile.py                    # from image.png (the photo in the repo root)
  python3 scripts/make-stone-tile.py --procedural       # no photo: generated noise stone instead
  python3 scripts/make-stone-tile.py --photo other.png --out tile.jpg
  needs: pip install pillow numpy

Prints the CSS value to paste into `--w-tex` in index.html, writes the JPEG, and writes a
3x3 preview PNG beside it so the tiling can be checked by eye. SIZE here must equal the
`background-size` on `.window` in the grey scheme; MEAN_GREY must equal `--w-face`.

PHOTO MODE — a photo is not seamless, so a crop is made tileable by cross-fading it with a
copy of itself rolled by half a tile (weight 0 at the tile edge, 1 in the centre), once per
axis. The edge then shows the *interior* of the picture on both sides, so it wraps with no seam.
The blend is variance-compensated, otherwise the mid-blend zones look flatter.
PROCEDURAL MODE — FFT-filtered noise is periodic by construction (see fft_noise)."""
import argparse, base64, sys
import numpy as np
from PIL import Image

SIZE         = 320    # px, square tile. Larger = repeat less visible, bigger data URI
MEAN_GREY    = 160    # tile average level; MUST equal --w-face (#a0a0a0) so flat buttons blend in
CONTRAST     = 1.8    # photo mode: gain on deviations from the photo's mean (the photo is very subtle)
LIGHT_LIMIT  = 30     # photo mode: soft cap on how much lighter than the mean a pixel may get
DARK_LIMIT   = 24     # photo mode: soft cap on how much darker — with MEAN_GREY keeps text readable
MIN_LEVEL    = 136    # hard floor: dark text (#1a1a1a) stays >= 4.5:1 contrast on the darkest pixel
CROP_X, CROP_Y = 120, 35   # photo mode: top-left of the crop (evenest mottling, no strong cracks to ghost at half-tile spacing)
JPEG_QUALITY = 62
SEED         = 98     # procedural mode only

ap = argparse.ArgumentParser()
ap.add_argument('--photo', default='image.png')
ap.add_argument('--procedural', action='store_true')
ap.add_argument('--out', default='stone-tile.jpg')
args = ap.parse_args()

def tone_map(dev):
    """Raise contrast, then softly cap both directions so extremes cannot hurt text legibility."""
    d = dev * CONTRAST
    return np.where(d >= 0, LIGHT_LIMIT * np.tanh(d / LIGHT_LIMIT), DARK_LIMIT * np.tanh(d / DARK_LIMIT))

if not args.procedural:
    import os
    if not os.path.exists(args.photo):
        sys.exit(f'{args.photo} not found. Restore it with:  git show 0d923a4:image.png > image.png   (or run with --procedural)')
    src = np.asarray(Image.open(args.photo).convert('L')).astype(float)
    crop = src[CROP_Y:CROP_Y + SIZE, CROP_X:CROP_X + SIZE]
    assert crop.shape == (SIZE, SIZE), f'crop {crop.shape} does not fit inside {src.shape}; adjust CROP_X/CROP_Y/SIZE'
    dev = crop - crop.mean()
    u = (np.arange(SIZE) + 0.5) / SIZE
    w1 = 1 - np.abs(2 * u - 1)                      # 0 at both tile edges, 1 in the middle
    def seamless_along(a, axis):
        """Cross-fade a with itself rolled half a tile along `axis`. The roll's own wrap line sits at
        the middle, where the weight hides it; the tile edge shows the roll's interior on both sides."""
        w = w1[:, None] if axis == 0 else w1[None, :]
        r = np.roll(a, SIZE // 2, axis)
        return (a * w + r * (1 - w)) / np.sqrt(w**2 + (1 - w)**2)   # variance-preserving
    # TWO 1-D passes (x then y), NOT one 2-D weight: a 2-D weight cannot hide the roll's wrap
    # lines along the whole cross at once and leaves a faint grid of lines in the tiled result.
    blend = seamless_along(seamless_along(dev, 1), 0)
    img = MEAN_GREY + tone_map(blend)
else:
    rng = np.random.default_rng(SEED)
    def fft_noise(power, blur=0.0):
        f = np.fft.fftfreq(SIZE); fx, fy = np.meshgrid(f, f)
        r = np.sqrt(fx**2 + fy**2); r[0, 0] = 1
        spec = np.fft.fft2(rng.standard_normal((SIZE, SIZE))) / r**power
        if blur: spec *= np.exp(-(r * SIZE * blur) ** 2 / 2)
        spec[0, 0] = 0
        n = np.real(np.fft.ifft2(spec)); return (n - n.mean()) / n.std()
    img = MEAN_GREY + 6.5 * fft_noise(2.2) + 8.0 * np.clip(fft_noise(1.4, 0.02) - 0.4, -1, 2.5) + 6.5 * fft_noise(0.2)
    for _ in range(260):
        y, x = rng.integers(0, SIZE, 2); d = rng.uniform(10, 26)
        img[y, x] -= d; img[(y + 1) % SIZE, x] -= d * .35; img[y, (x + 1) % SIZE] -= d * .35

img = np.clip(img, MIN_LEVEL, 255).astype(np.uint8)
im = Image.fromarray(img, 'L')
im.save(args.out, 'JPEG', quality=JPEG_QUALITY, optimize=True)
prev = Image.new('L', (SIZE * 3, SIZE * 3))
for i in range(3):
    for j in range(3): prev.paste(im, (i * SIZE, j * SIZE))
prev.save(args.out.rsplit('.', 1)[0] + '-preview3x3.png')
data = open(args.out, 'rb').read()
# seam check: how different are the two pixels that become neighbours when the tile repeats?
seam = np.abs(img[:, 0].astype(int) - img[:, -1]).mean(), np.abs(img[0, :].astype(int) - img[-1, :]).mean()
inner = np.abs(np.diff(img.astype(int), axis=1)).mean()
print(f'{len(data)} bytes jpeg  mean={img.mean():.1f} min={img.min()} max={img.max()}  '
      f'seam diff L/R={seam[0]:.1f} T/B={seam[1]:.1f} (typical neighbour diff inside tile={inner:.1f})', file=sys.stderr)
print('url("data:image/jpeg;base64,' + base64.b64encode(data).decode() + '")')
