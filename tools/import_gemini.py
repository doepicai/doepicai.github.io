"""Cut Gemini renders from gemini-raw/ into the light low-poly scene set the site uses.

Usage:  python tools/import_gemini.py       (needs Pillow, numpy, scipy)
Reads   gemini-raw/<name>.(png|jpg|webp)
Writes  img/lp/*.webp  and  scene.json
Missing files are skipped, so layers can be added one by one. Prompts: docs/gemini/PROMPTS.md

The set (all low-poly, small after compression):
  sun-lp                       black background, blended with CSS `screen`  -> img/lp/sun.webp
  hills-lp                     blue chroma key                              -> img/lp/hills.webp
  city-far-lp, city-near-lp    blue chroma key                              -> img/lp/city-far.webp, city-near.webp
  shore-lp-<season>            blue chroma key, 4 seasons                   -> img/lp/shore-<season>.webp
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "gemini-raw"
OUT = ROOT / "img" / "lp"
SEASONS = ("spring", "summer", "autumn", "winter")
# target widths: enough for a 1440 px screen at the scale the page uses, nothing more
W_SHORE, W_CITY, W_HILLS, W_SUN = 1500, 1400, 1400, 512


def load(name):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = RAW / (name + ext)
        if p.exists():
            return Image.open(p).convert("RGB")
    print(f"skip  {name} (not found)")
    return None


def fit(im, width):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def save(im, name, quality=80):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.webp"
    im.save(path, "WEBP", quality=quality, method=6, alpha_quality=85)
    print(f"write {path.relative_to(ROOT)}  {im.size}  {path.stat().st_size // 1024} KB")
    return f"img/lp/{path.name}"


def key_auto(im, crop=None, strict=False):
    """Key out a flat background of any colour (blue here), without a key-coloured halo.
    1. key colour = median of the frame border; alpha from the colour distance;
    2. colours are un-mixed from the key; blue-tinted pixels (old background shining through
       soft edges) are cut (strict) or limited (not strict: ice and violet shadows keep some blue);
    3. semi-transparent pixels take the colour of the nearest solid pixel;
    4. the matte is eroded a little and softened.
    crop='v' crops empty rows above/below the content."""
    a = np.asarray(im).astype(np.float32)
    b = 6
    border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3),
                             a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    key = np.median(border, axis=0)
    d = np.linalg.norm(a - key, axis=2)
    a0 = np.clip((d - 50) / 70, 0, 1)
    a0 = a0 * a0 * (3 - 2 * a0)
    safe = np.maximum(a0, 1e-3)[..., None]
    rgb = np.clip((a - (1 - a0)[..., None] * key) / safe, 0, 255)
    kc = int(np.argmax(key))
    others = [i for i in range(3) if i != kc]
    ex = rgb[..., kc] - np.maximum(rgb[..., others[0]], rgb[..., others[1]])
    lo, span, lim = (12, 70, 8) if strict else (70, 60, 70)
    a0 = a0 * np.clip(1 - (ex - lo) / span, 0, 1)
    rgb[..., kc] = np.minimum(rgb[..., kc], np.maximum(rgb[..., others[0]], rgb[..., others[1]]) + lim)
    solid = a0 > 0.92
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    filled = rgb[idx[0], idx[1]]
    for c in range(3):
        filled[..., c] = ndimage.gaussian_filter(filled[..., c], 1.5)
    wr = np.clip((1 - a0) * 1.8, 0, 1)[..., None] * (~solid)[..., None]
    rgb = np.clip(rgb * (1 - wr) + filled * wr, 0, 255)
    alpha = ndimage.minimum_filter(a0, size=3)
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    alpha = np.clip((alpha - 0.12) / 0.88, 0, 1)
    out = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    if crop == "v":
        bbox = out.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        if bbox:
            out = out.crop((0, bbox[1], out.width, bbox[3]))
    return out


def main():
    layers, seasons = {}, {}

    if (im := load("sun-lp")):
        layers["sun"] = save(fit(im, W_SUN), "sun", 82)        # black stays black, CSS blends with `screen`
    if (im := load("hills-lp")):
        layers["hills"] = save(key_auto(fit(im, W_HILLS), "v"), "hills")
    if (im := load("city-far-lp")):
        layers["city-far"] = save(key_auto(fit(im, W_CITY), "v"), "city-far")
    if (im := load("city-near-lp")):
        layers["city-near"] = save(key_auto(fit(im, W_CITY), "v"), "city-near")
    for s in SEASONS:
        if (im := load(f"shore-lp-{s}")):
            seasons[s] = {"shore": save(key_auto(fit(im, W_SHORE), "v", strict=s != "winter"), f"shore-{s}")}

    (ROOT / "scene.json").write_text(json.dumps({"layers": layers, "seasons": seasons}, indent=1), encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.glob("*.webp")) if OUT.exists() else 0
    print(f"scene.json updated. img/lp total: {total // 1024} KB")


if __name__ == "__main__":
    main()
