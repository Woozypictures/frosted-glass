"""Render graphite-glass icons: translucent white disc with horizontal alpha gradient,
brighter rim, and a white glyph with a soft diagonal shade. Proportions measured
from the reference style at 169px and scaled."""
import sys, os, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import cairosvg
from mapping import MAP

SRC = sys.argv[1]          # material symbols rounded dir
OUT = sys.argv[2]
S = 192                    # output size
SS = 4                     # supersample
N = S * SS
REF = 169.0

os.makedirs(OUT, exist_ok=True)

yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
c = (N - 1) / 2
r = np.hypot(xx - c, yy - c) / (N / REF)       # radius in reference px
u = xx / (N - 1)                                # 0 left -> 1 right

R_OUT, R_IN = 77.6, 75.0
disc = np.clip(R_OUT - r + 0.5, 0, 1)           # anti-aliased disc
rim = np.clip(R_OUT - r + 0.5, 0, 1) * np.clip(r - R_IN + 0.5, 0, 1)
fill_a = 14 + (55 - 14) * u                     # 0-255
rim_a = 58 + (96 - 58) * u
base_a = disc * fill_a * (1 - rim) + rim * rim_a

def base():
    a = np.clip(base_a, 0, 255)
    img = np.zeros((N, N, 4), np.uint8)
    img[..., :3] = 255
    img[..., 3] = a.astype(np.uint8)
    return img

GLYPH_BOX = 55 / REF * 1.2                      # svg 24 box -> ~20 glyph

def glyph_mask(name):
    svg = open(os.path.join(SRC, name + "-fill.svg")).read()
    svg = re.sub(r'<svg ', '<svg fill="#ffffff" ', svg, count=1)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1024, output_height=1024)
    im = Image.open(io.BytesIO(png)).convert("RGBA").split()[3]
    im = im.crop(im.getbbox())
    target = N * 61 / REF                       # max glyph side, as measured
    k = target / max(im.size)
    im = im.resize((max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))), Image.LANCZOS)
    full = Image.new("L", (N, N), 0)
    full.paste(im, ((N - im.size[0]) // 2, (N - im.size[1]) // 2))
    return np.array(full).astype(np.float32) / 255

shade = 255 - 25 * ((xx + yy) / (2 * (N - 1)))   # top-left 255 -> bottom-right 230

def compose(mask):
    b = base().astype(np.float32)
    ba = b[..., 3] / 255
    ga = mask
    out_a = ga + ba * (1 - ga)
    col = (shade * ga + 255 * ba * (1 - ga)) / np.maximum(out_a, 1e-6)
    img = np.zeros((N, N, 4), np.float32)
    img[..., 0] = img[..., 1] = img[..., 2] = col
    img[..., 3] = out_a * 255
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")
    return im.resize((S, S), Image.LANCZOS)

def drawable_name(pkg):
    return "ic_" + re.sub(r"[^a-z0-9]", "_", pkg.lower())

for pkg, (label, g) in MAP.items():
    compose(glyph_mask(g)).save(os.path.join(OUT, drawable_name(pkg) + ".png"), optimize=True)

# blank base for apps not in the list
Image.fromarray(base(), "RGBA").resize((S, S), Image.LANCZOS).save(os.path.join(OUT, "iconback.png"))
print("rendered", len(MAP) + 1)
