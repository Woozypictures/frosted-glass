#!/usr/bin/env python3
"""Render the custom device-specific icons in the pack's graphite-glass style.

Outputs 192x192 RGBA PNGs into icons/. Uses Pillow, NumPy and CairoSVG.
"""
from pathlib import Path
import io
import re
import numpy as np
from PIL import Image
import cairosvg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "icons"
S = 192
SS = 4
N = S * SS
REF = 169.0

SVG = {
    # Epic Games launcher: a neutral storefront and game-controller glyph.
    "com.epicgames.portal": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M4 3.5h16l1.7 5.1v1.1c0 1.5-1.2 2.7-2.7 2.7-.9 0-1.7-.4-2.2-1.1-.5.7-1.3 1.1-2.2 1.1s-1.7-.4-2.2-1.1c-.5.7-1.3 1.1-2.2 1.1s-1.7-.4-2.2-1.1c-.5.7-1.3 1.1-2.2 1.1-1.5 0-2.7-1.2-2.7-2.7V8.6z"/>
      <path d="M5 13.2h14v7.3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1z"/>
      <path fill="#555" d="M8 15.4h8c1 0 1.6.7 1.4 1.6l-.4 1.5c-.2.8-1.1 1.1-1.7.6l-1.3-1H10l-1.3 1c-.6.5-1.5.2-1.7-.6l-.4-1.5c-.2-.9.4-1.6 1.4-1.6Zm1.1.8v.9H10v.8h-.9v.9h-.8v-.9h-.9v-.8h.9v-.9zm4.8.2a.55.55 0 1 0 0 1.1.55.55 0 0 0 0-1.1zm1.2 1.1a.55.55 0 1 0 0 1.1.55.55 0 0 0 0-1.1z"/>
    </svg>''',
    # Meta Edits: editing frame with a diagonal pencil.
    "com.instagram.basel": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M5 3.5h10.8L20 7.7v7.1l-2.1 2.1V8.5h-4.2V4.8H6.2v14.4h6.3l-1.8 1.8H5c-1 0-1.8-.8-1.8-1.8V5.3c0-1 .8-1.8 1.8-1.8Z"/>
      <path d="M7.7 10h7.1v1.7H7.7zm0 3.3h5.3V15H7.7z"/>
      <path d="m14.7 17.2 4.7-4.7 1.8 1.8-4.7 4.7-2.7.9z"/>
    </svg>''',
    # Crossed swords for Brawlhalla.
    "air.com.ubisoft.brawl.halla.platform.fighting.action.pvp": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="m4.1 3.2 1.8.2 14.9 14.9-1.7 1.7L4.2 5.1z"/><path d="m19.9 3.2-1.8.2L3.2 18.3l1.7 1.7L19.8 5.1z"/>
      <path d="m2.8 2.4 3.9 1.1-2.9 2.9zm18.4 0-1 4-2.9-2.9z"/>
      <path d="m8.1 14.8 1.1 1.1-3.6 3.6-1.1-1.1zm7.8 0-1.1 1.1 3.6 3.6 1.1-1.1z"/>
      <path d="M2.8 12.2h6.1v1.6H2.8zm12.3 0h6.1v1.6h-6.1z"/>
    </svg>''',
    # Monogram for Bright Memory: Infinite.
    "com.FYQD.BMI": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M2.8 4h7.4c2.6 0 4.1 1.3 4.1 3.5 0 1.2-.6 2.1-1.7 2.6 1.5.5 2.4 1.6 2.4 3.3 0 2.5-1.8 4-4.8 4H2.8zm2.9 2.5v2.5h4.1c.9 0 1.4-.4 1.4-1.2s-.5-1.3-1.4-1.3zm0 4.9v3.4h4.4c1.1 0 1.7-.6 1.7-1.7s-.6-1.7-1.7-1.7z"/>
      <path d="M14.8 4h2.5l2 5.5 2-5.5h2.4v13.4h-2.6V9.5l-1.3 4.2h-1.2l-1.3-4.2v7.9h-2.5z"/>
      <path d="M2.8 19.3h20v1.5h-20z"/>
    </svg>''',

    # GameNative: controller silhouette with D-pad and buttons.
    "app.gamenative": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M7.1 7h9.8c2.1 0 3.6 1.3 4.1 3.3l1.1 4.4c.4 1.8-1.5 3-2.9 2l-3.2-2.4H8l-3.2 2.4c-1.4 1-3.3-.2-2.9-2L3 10.3C3.5 8.3 5 7 7.1 7Z M6.4 9.1h1.7v1.7h1.7v1.7H8.1v1.7H6.4v-1.7H4.7v-1.7h1.7z M16.1 9.2a1.05 1.05 0 1 0 0 2.1 1.05 1.05 0 0 0 0-2.1z M18.3 11.5a1.05 1.05 0 1 0 0 2.1 1.05 1.05 0 0 0 0-2.1z"/>
    </svg>''',

    # Old School RuneScape: shield with RS monogram.
    "com.jagex.oldscape.android": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M12 2 20 5v6.2c0 5-3.3 8.5-8 10.8-4.7-2.3-8-5.8-8-10.8V5zm0 2.1L6 6.2v5c0 3.8 2.3 6.6 6 8.7 3.7-2.1 6-4.9 6-8.7v-5z"/>
      <path d="M8 8.2h4.1c1.6 0 2.6.8 2.6 2.2 0 1-.5 1.6-1.4 1.9l1.8 3.5h-2.4l-1.5-3.1h-1v3.1H8zm2.2 1.7v1.3h1.7c.5 0 .8-.2.8-.7s-.3-.6-.8-.6z"/>
      <path d="M16.3 8.2h-3v1.7h2.1c.4 0 .6.2.6.5s-.2.5-.6.5h-.8c-1.3 0-2.2.8-2.2 2s.9 1.9 2.2 1.9h2.2v-1.7h-2c-.4 0-.6-.1-.6-.4s.2-.4.6-.4h.8c1.3 0 2.2-.8 2.2-2s-.7-2.1-1.5-2.1Z"/>
    </svg>''',
    # Pizza Boy GBA Pro: handheld console.
    "it.dbtecno.pizzaboygbapro": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M6 2.5h12a2 2 0 0 1 2 2v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-15a2 2 0 0 1 2-2Z M6.4 4.5h11.2v8H6.4z M7.3 15.1h1.7v1.7h1.7v1.7H9v1.7H7.3v-1.7H5.6v-1.7h1.7z M15.1 16.4a1 1 0 1 0 0 2 1 1 0 0 0 0-2z M17.3 18.3a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
    </svg>''',

    # Papa Johns: pizza slice and toppings.
    "uk.co.papajohns.ppjqg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M3 5.1c5.1-2.4 12.9-2.4 18 0l-7.7 15.5c-.4.8-1.2 1-1.8.3z M10 8.3a1 1 0 1 0 0-2 1 1 0 0 0 0 2z M14.4 9.4a1 1 0 1 0 0-2 1 1 0 0 0 0 2z M12.3 13.3a.9.9 0 1 0 0-1.8.9.9 0 0 0 0 1.8z"/>
    </svg>''',

    # Prince of Persia: curved Persian blade.
    "com.ubisoft.princeofpersia.thelostcrown.mobile.action.adventure.platform": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="M4 3c4.5 4.2 9.3 6.9 16.4 6.5-2.4 3.3-6.4 4.7-10.4 3.4l-4.1 5.9-2.1-1.5 4-5.8C5.7 9.7 4.4 6.4 4 3Z"/>
      <path d="m3.1 17.2 3.8 2.6-1.7 2.4-3.8-2.6z"/><path d="m4.4 16.2 2.2 1.5-1 1.4-2.2-1.5z"/>
      <path d="M8.1 9.5c2.4 1.8 5.2 2.8 8.7 2.3-3.1 1.1-6.1.5-8.7-2.3Z" fill="#555"/>
    </svg>''',
    # Sky: radiant star with wing-like arcs.
    "com.tgc.sky.android": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path d="m12 2.2 2.1 6.4 6.7-.1-5.4 3.9 2.1 6.4-5.5-4-5.5 4 2.1-6.4-5.4-3.9 6.7.1z"/>
      <path d="M2.1 17.7c2.5-.2 4.5-1.1 6-2.8l1.1 1.3c-1.7 2-4 3.1-6.8 3.3zm19.8 0c-2.5-.2-4.5-1.1-6-2.8l-1.1 1.3c1.7 2 4 3.1 6.8 3.3z"/>
    </svg>''',
    # X1 Box: controller silhouette with X1 mark.
    "com.izzy2lost.x1box": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M5 5.5h14c1.5 0 2.5 1 2.5 2.5v8c0 1.5-1 2.5-2.5 2.5h-3l-2-2H10l-2 2H5c-1.5 0-2.5-1-2.5-2.5V8C2.5 6.5 3.5 5.5 5 5.5Z M6.8 8.9l1.2-1.2 2 2 2-2 1.2 1.2-2 2 2 2-1.2 1.2-2-2-2 2-1.2-1.2 2-2z M16.5 8.7a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2z M18.1 11a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2z"/>
    </svg>''',

    # SpongeBob BFBB: square sponge face, eyes and smile.
    "com.hg.bfbb": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M5.3 3.2 7 4l2-.8 2 .8 2-.8 2 .8 2-.8 2 .8 1.3-.8.6 3.2-.6 2 .6 2-.6 2 .6 2-.6 2 .6 2-2 .6-2-.6-2 .6-2-.6-2 .6-2-.6-2 .6-2-.6-2 .6-1.2-.6.6-2-.6-2 .6-2-.6-2 .6-2Z M9 7.8a1.8 2.1 0 1 0 0 4.2 1.8 2.1 0 0 0 0-4.2z M15 7.8a1.8 2.1 0 1 0 0 4.2 1.8 2.1 0 0 0 0-4.2z M8 14.7c1.2 1.1 2.5 1.7 4 1.7s2.8-.6 4-1.7v1.6c-1.2 1.2-2.5 1.8-4 1.8s-2.8-.6-4-1.8z M6.5 12.5a.7.7 0 1 0 0 1.4.7.7 0 0 0 0-1.4z M17.5 12.5a.7.7 0 1 0 0 1.4.7.7 0 0 0 0-1.4z M6.7 6.5a.45.45 0 1 0 0 .9.45.45 0 0 0 0-.9z M17.1 6.3a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1z M7.1 17.5a.4.4 0 1 0 0 .8.4.4 0 0 0 0-.8z M17.2 17.5a.4.4 0 1 0 0 .8.4.4 0 0 0 0-.8z"/>
      <circle cx="9" cy="10" r=".5"/><circle cx="15" cy="10" r=".5"/>
    </svg>''',

    # HQ (Woozypictures): the dashboard's four tiles, as on HQ's own launcher icon.
    "uk.woozy.hq": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <rect x="3" y="3" width="8" height="8" rx="1.6"/><rect x="13" y="3" width="8" height="8" rx="1.6"/>
      <rect x="3" y="13" width="8" height="8" rx="1.6"/><rect x="13" y="13" width="8" height="8" rx="1.6"/>
    </svg>''',
    # HQ Fit (Woozypictures): a dumbbell, as on HQ Fit's own launcher icon, tilted so it fills the disc.
    "uk.woozy.fit": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <g transform="rotate(-45 12 12)">
      <rect x="1.2" y="8.4" width="2.6" height="7.2" rx="1.1"/><rect x="4.6" y="5" width="3.6" height="14" rx="1.5"/>
      <rect x="7.6" y="10.6" width="8.8" height="2.8" rx="1"/>
      <rect x="15.8" y="5" width="3.6" height="14" rx="1.5"/><rect x="20.2" y="8.4" width="2.6" height="7.2" rx="1.1"/>
      </g>
    </svg>''',
    # Roblox placeholder for base generation; merge replaces it with original source art.
    "com.roblox.client": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff">
      <path fill-rule="evenodd" d="M5.1 2.8 21.2 7.2 18.9 21.2 2.8 16.8z M9 8.4l5 1.4-.8 5-5-1.4z"/>
    </svg>''',
}

def drawable_name(pkg):
    return "ic_" + re.sub(r"[^a-z0-9]", "_", pkg.lower())

def render(svg):
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    c = (N - 1) / 2
    r = np.hypot(xx - c, yy - c) / (N / REF)
    u = xx / (N - 1)
    r_out, r_in = 77.6, 75.0
    disc = np.clip(r_out - r + 0.5, 0, 1)
    rim = np.clip(r_out - r + 0.5, 0, 1) * np.clip(r - r_in + 0.5, 0, 1)
    fill_a = 14 + (55 - 14) * u
    rim_a = 58 + (96 - 58) * u
    base_a = disc * fill_a * (1 - rim) + rim * rim_a

    glyph_png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=1024, output_height=1024)
    glyph = Image.open(io.BytesIO(glyph_png)).convert("RGBA").split()[3]
    bbox = glyph.getbbox()
    if not bbox:
        raise ValueError("Empty glyph SVG")
    glyph = glyph.crop(bbox)
    target = N * 61 / REF
    k = target / max(glyph.size)
    glyph = glyph.resize((max(1, round(glyph.width * k)), max(1, round(glyph.height * k))), Image.Resampling.LANCZOS)
    mask = Image.new("L", (N, N), 0)
    mask.paste(glyph, ((N - glyph.width)//2, (N - glyph.height)//2))
    ga = np.asarray(mask).astype(np.float32) / 255

    shade = 255 - 25 * ((xx + yy) / (2 * (N - 1)))
    ba = np.clip(base_a, 0, 255) / 255
    out_a = ga + ba * (1 - ga)
    col = (shade * ga + 255 * ba * (1 - ga)) / np.maximum(out_a, 1e-6)
    out = np.zeros((N, N, 4), np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)[..., None]
    out[..., 3] = np.clip(out_a * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA").resize((S, S), Image.Resampling.LANCZOS)


def make_icons():
    OUT.mkdir(parents=True, exist_ok=True)
    for pkg, svg in SVG.items():
        render(svg).save(OUT / f"{drawable_name(pkg)}.png", optimize=True)
    print(f"Rendered {len(SVG)} custom device icons into {OUT}")

if __name__ == "__main__":
    make_icons()
