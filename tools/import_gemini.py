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

    (ROOT / "scene.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("scene.json updated, open the site to see the new art")


if __name__ == "__main__":
    main()
