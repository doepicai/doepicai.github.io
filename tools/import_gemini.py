"""Cut Gemini renders from gemini-raw/ into the layers the site uses.

Usage:  python tools/import_gemini.py       (needs Pillow + numpy + scipy)
Writes img/scene/*.webp (or .png) and scene.json. Missing files are skipped,
so you can add images one by one. See docs/gemini/PROMPTS.md.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "gemini-raw"
OUT = ROOT / "img" / "scene"
MAXW = 2560


def load(name):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = RAW / (name + ext)
        if p.exists():
            return Image.open(p).convert("RGB")
    print(f"skip  {name} (not found)")
    return None


def shrink(im):
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    return im


def save(im, name, alpha):
    OUT.mkdir(parents=True, exist_ok=True)
    ext = "webp" if alpha or True else "png"
    path = OUT / f"{name}.{ext}"
    im.save(path, quality=88 if ext == "webp" else None, method=6) if ext == "webp" else im.save(path)
    print(f"write {path.relative_to(ROOT)}  {im.size}")
    return f"img/scene/{path.name}"


def key_green(im):
    """Chroma-key a #00FF00 background to alpha, remove green spill, crop to content."""
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    greenness = g - np.maximum(r, b)           # large only for the key colour
    alpha = np.clip(1 - (greenness - 40) / 90, 0, 1)   # soft edge
    # despill: cap green at the max of red/blue on edge pixels
    spill = greenness > 0
    g2 = np.where(spill, np.maximum(r, b) + np.minimum(greenness, 0), g)
    rgba = np.dstack([r, g2, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA")
    bbox = out.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    if bbox:
        # keep the full width, crop the empty top and the empty strip below the ground line
        out = out.crop((0, bbox[1], out.width, bbox[3]))
    return out


def key_auto(im, crop=None, strict=False):
    """Key out a flat background of any colour (blue for the nature assets), without a key-coloured halo.
    1. key colour = median of the frame border; alpha from the colour distance;
    2. colours are un-mixed from the key and the key-coloured spill is removed on semi-transparent pixels;
    3. the matte is eroded a little and softened, so no bright rim of the old background survives;
    4. fully transparent pixels get the colour of the nearest solid pixel (no blue bleeding into the
       edge when the browser scales or the WebP encoder compresses the image).
    crop: None = keep the frame, 'v' = crop empty rows above/below the content."""
    a = np.asarray(im).astype(np.float32)
    b = 6
    border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3),
                             a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    key = np.median(border, axis=0)
    d = np.linalg.norm(a - key, axis=2)
    a0 = np.clip((d - 50) / 70, 0, 1)
    a0 = a0 * a0 * (3 - 2 * a0)                               # smoothstep
    safe = np.maximum(a0, 1e-3)[..., None]
    rgb = np.clip((a - (1 - a0)[..., None] * key) / safe, 0, 255)
    # key-colour excess (blue over red/green for a blue key): blue-tinted pixels are the old background
    # shining through blurred edges. strict = foliage and blossoms (blue is never a real colour there);
    # otherwise ice and violet shadows keep a limited blue cast.
    kc = int(np.argmax(key))
    others = [i for i in range(3) if i != kc]
    ex = rgb[..., kc] - np.maximum(rgb[..., others[0]], rgb[..., others[1]])
    lo, span, lim = (12, 70, 8) if strict else (70, 60, 70)
    a0 = a0 * np.clip(1 - (ex - lo) / span, 0, 1)
    rgb[..., kc] = np.minimum(rgb[..., kc], np.maximum(rgb[..., others[0]], rgb[..., others[1]]) + lim)
    # edge colour: semi-transparent pixels take the colour of the nearest solid pixel (smoothed), so the
    # key colour cannot survive as a halo, whatever the (unknowable) real colour behind the blur was
    solid = a0 > 0.92
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    filled = rgb[idx[0], idx[1]]
    for c in range(3):
        filled[..., c] = ndimage.gaussian_filter(filled[..., c], 1.5)
    wr = np.clip((1 - a0) * 1.8, 0, 1)[..., None] * (~solid)[..., None]
    rgb = np.clip(rgb * (1 - wr) + filled * wr, 0, 255)
    # matte: erode, soften, and cut the faintest fringe
    alpha = ndimage.minimum_filter(a0, size=3)
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    alpha = np.clip((alpha - 0.12) / 0.88, 0, 1)
    out = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    if crop == "v":
        bbox = out.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        if bbox:
            out = out.crop((0, bbox[1], out.width, bbox[3]))
    return out

def black_to_alpha(im):
    """For screen-blended art on black: alpha from brightness, colour un-premultiplied."""
    a = np.asarray(im).astype(np.float32)
    lum = a.max(axis=2)
    alpha = np.clip(lum / 255 * 1.6, 0, 1)
    safe = np.maximum(alpha, 1e-3)[..., None]
    rgb = np.clip(a / safe, 0, 255)
    return Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")


def main():
    manifest = {"layers": {}, "glass": []}

    if (im := load("sky")):
        manifest["layers"]["sky"] = save(shrink(im), "sky", False)

    if (im := load("sun")):
        manifest["layers"]["sun"] = save(shrink(im), "sun", False)   # black stays, CSS uses screen

    for n in ("city-far", "city-mid", "city-near"):
        if (im := load(n)):
            manifest["layers"][n] = save(key_green(shrink(im)), n, True)

    if (im := load("water")):
        manifest["layers"]["water"] = save(shrink(im), "water", False)

    if (im := load("glass")):
        rgba = black_to_alpha(shrink(im))
        mask = np.asarray(rgba.getchannel("A")) > 40
        mask = ndimage.binary_dilation(mask, iterations=6)
        lab, n = ndimage.label(mask)
        k = 0
        for sl in ndimage.find_objects(lab):
            h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if min(h, w) < 40:
                continue
            k += 1
            pad = 6
            box = (max(sl[1].start - pad, 0), max(sl[0].start - pad, 0), sl[1].stop + pad, sl[0].stop + pad)
            manifest["glass"].append(save(rgba.crop(box), f"glass-{k}", True))

    # nature: hills + per-season shore strip and corner branch (blue chroma key)
    if (im := load("hills")):
        manifest["layers"]["hills"] = save(key_auto(shrink(im), "v"), "hills", True)
    manifest["seasons"] = {}
    for s in ("spring", "summer", "autumn", "winter"):
        entry = {}
        if (im := load(f"shore-{s}")):
            entry["shore"] = save(key_auto(shrink(im), "v", strict=s != "winter"), f"shore-{s}", True)
        if (im := load(f"branch-{s}")):
            entry["branch"] = save(key_auto(shrink(im), strict=s != "winter"), f"branch-{s}", True)
        if entry:
            manifest["seasons"][s] = entry
    (ROOT / "scene.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("scene.json updated, open the site to see the new art")


if __name__ == "__main__":
    main()
