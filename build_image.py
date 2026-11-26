#!/usr/bin/env python3
"""Draw entry.png: the world news of Wednesday 25 November 2026 in one picture.

A 1024x1024 broadsheet-style front page rendered with Pillow:
a masthead naming the day, one hero story with a small drawn scene,
then a labelled grid of 44 more stories grouped by region chips.

Deterministic: no randomness, no network, stdlib + PIL only.
Run:  python3 build_image.py   (writes entry.png next to this file)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

W = H = 1024
MARGIN = 26

PAPER = (247, 243, 234)
INK = (26, 24, 22)
SOFT = (92, 86, 76)
RULE = (26, 24, 22)
CARD_BG = (255, 253, 248)
CARD_EDGE = (210, 202, 186)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- stories ---
# (region, headline, source) -- events of 25 November 2026.
# The hero story is drawn separately; these 44 fill the grid.
STORIES = [
    # Middle East
    ("MIDDLE EAST", "Houthis claim strike on Saudi Ras Tanura refinery", "Daily Fox News"),
    ("MIDDLE EAST", "Houthi strike on Riyadh tower wounds 11", "Reuters"),
    ("MIDDLE EAST", "Israel kills Hamas interior security chief in Gaza", "Daily Fox News"),
    ("MIDDLE EAST", "Netanyahu declares his trial has 'fallen apart'", "Breitbart"),
    ("MIDDLE EAST", "UN aid chief in Yemen warns war blocks food, medicine", "UN News"),
    ("MIDDLE EAST", "UN rights chief warns of atrocity crimes in Gaza", "UN News"),
    # Europe
    ("EUROPE", "30+ countries urge Russia to stop chemical agents", "Standard Topic"),
    ("EUROPE", "Ukrainian drones strike two refineries in Samara region", "Open Chronicle"),
    ("EUROPE", "Russian strike on Odesa kills two, injures three", "Daily Fox News"),
    ("EUROPE", "Spain heads to snap election Sunday; Socialists trail", "Reuters"),
    ("EUROPE", "Puigdemont to return to Catalonia 12 December", "The Times"),
    ("EUROPE", "Hungary and Ukraine make 'fresh start' in trade talks", "Reuters"),
    ("EUROPE", "BBC: 490,334 Russian soldiers killed since 2022", "BBC analysis"),
    ("EUROPE", "Pope Leo XIV voices concern as COP31 ends no deal", "Daily Fox News"),
    # North America
    ("NORTH AMERICA", "Huawei convicted in US trial on trade secrets, fraud", "Reuters"),
    ("NORTH AMERICA", "CIA and ODNI suffer cybersecurity breach", "Reuters"),
    ("NORTH AMERICA", "Jensen Huang returns as Nvidia CEO after Trump move", "Standard Topic"),
    ("NORTH AMERICA", "US to unveil new tariffs on 14 trading partners", "Reuters"),
    ("NORTH AMERICA", "Wall Street slides: S&P -2.2%, Nasdaq -3.2%", "Investopedia"),
    ("NORTH AMERICA", "US Army detonates 5 tons of lead azide in Iowa", "CNN"),
    ("NORTH AMERICA", "US consumer confidence strongest in nearly two years", "Open Chronicle"),
    # South America
    ("SOUTH AMERICA", "Armed men take 30 hostages in Cartagena; all freed", "Open Chronicle"),
    ("SOUTH AMERICA", "Ecuador rains kill 27", "Latin American Pulse"),
    ("SOUTH AMERICA", "Chile mourns actress Delfina Guzman, dead at 98", "Latin American Pulse"),
    ("SOUTH AMERICA", "Argentine peso hits 1,592 per dollar; risk over 1,100", "Latin American Pulse"),
    ("SOUTH AMERICA", "Machado: Gonzalez will return to Venezuela soon", "Pollar"),
    ("SOUTH AMERICA", "Venezuela discloses $237.5bn debt before restructuring", "Open Chronicle"),
    # Africa
    ("AFRICA", "RSF drone strikes kill 19 civilians in two cities", "Daily Fox News"),
    ("AFRICA", "Fuel tanker crash on Cairo ring road kills at least 30", "Standard Topic"),
    ("AFRICA", "DR Congo: Ebola workers evacuated; Gavi buys doses", "UN News"),
    ("AFRICA", "Ramaphosa wins court challenge over Farmgate report", "Open Chronicle"),
    ("AFRICA", "Ethiopia offers to host Sudan talks; Khartoum wary", "Open Chronicle"),
    # Asia
    ("ASIA", "Shenzhou-24 launches with Pakistan's first astronaut", "AP"),
    ("ASIA", "Bangladesh raises garment workers' wage 36%", "Reuters"),
    ("ASIA", "China and Cambodia begin Golden Dragon drills", "Standard Topic"),
    ("ASIA", "Asian stocks slide as AI shares sell off", "Standard Topic"),
    ("ASIA", "China orders 50 Boeing aircraft in $7.4bn deal", "Open Chronicle"),
    ("ASIA", "North Korea orders Swiss diplomatic office closed", "Open Chronicle"),
    ("ASIA", "Shanghai party chief Chen Jining investigated", "Open Chronicle"),
    ("ASIA", "Taiwan comedian gets security detail over China jokes", "Reuters"),
    ("ASIA", "Hong Kong marks one year since deadly fire", "Reuters"),
    # Oceania
    ("OCEANIA", "Australia-Solomon Islands treaty bars foreign bases", "Open Chronicle"),
    ("OCEANIA", "Australia passes Digital Duty of Care Act for Big Tech", "Raj Global Studies"),
    ("OCEANIA", "Qantas jet aborts Sydney landing as Air NZ crosses runway", "Aviation A2Z"),
]

REGION_COLORS = {
    "MIDDLE EAST": (176, 62, 44),
    "EUROPE": (44, 74, 128),
    "NORTH AMERICA": (20, 122, 116),
    "SOUTH AMERICA": (52, 128, 60),
    "AFRICA": (166, 110, 30),
    "ASIA": (104, 62, 148),
    "OCEANIA": (36, 116, 176),
}

HERO_KICKER = "MIDDLE EAST — STRAIT OF HORMUZ"
HERO_HEADLINE = "Iran says tankers hit mines in the Strait of Hormuz"
HERO_BODY = [
    "Tehran's Revolutionary Guards say oil tankers struck naval mines,",
    "exploded and caught fire in the strait; the US military disputes",
    "the account, and reports differ on how many vessels were hit.",
    "Oil prices climb as the world's busiest energy chokepoint shakes.",
]


# ---------------------------------------------------------------- helpers ---

def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def centered(draw, cx, y, s, fnt, fill):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, max_w, max_lines=2):
    """Greedy word wrap; last line gets an ellipsis if text remains."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if len(lines) < max_lines and cur:
        lines.append(cur)
    if len(lines) == max_lines:
        joined = " ".join(lines)
        if joined != s:
            last = lines[-1]
            while last and text_w(draw, last + "…", fnt) > max_w:
                last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
            lines[-1] = last + "…"
    return lines


def chip(draw, x, y, label, color, fnt):
    """Small filled region tag; returns its width."""
    w = int(text_w(draw, label, fnt)) + 12
    draw.rounded_rectangle([x, y, x + w, y + 15], radius=3, fill=color)
    draw.text((x + 6, y + 2), label, font=fnt, fill=(255, 255, 255))
    return w


# --------------------------------------------------------------- masthead ---

def draw_masthead(draw):
    cx = W // 2
    draw.line([MARGIN, 18, W - MARGIN, 18], fill=RULE, width=2)
    centered(draw, cx, 24, "WORLD NEWS IN ONE IMAGE", font(SANS_BOLD, 15), SOFT)
    centered(draw, cx, 44, "WEDNESDAY 25 NOVEMBER 2026", font(SERIF_BOLD, 34), INK)
    centered(draw, cx, 86, "45 stories from 7 regions — one day, one picture",
             font(SANS, 14), SOFT)
    draw.line([MARGIN, 110, W - MARGIN, 110], fill=RULE, width=2)
    return 110


# -------------------------------------------------------------- hero scene ---

def tanker(draw, x, y, length, hull, smoke=False):
    """Simple side-view tanker silhouette sitting on the waterline y."""
    top = y - 16
    draw.polygon([(x, top), (x + length, top),
                  (x + length - 10, y), (x + 8, y)], fill=hull)
    # deck cargo tanks
    for i in range(3):
        tx = x + 10 + i * (length // 3)
        draw.rounded_rectangle([tx, top - 7, tx + length // 3 - 8, top],
                               radius=3, fill=hull)
    # bridge block and funnel at the stern
    bx = x + length - 26
    draw.rectangle([bx, top - 20, bx + 16, top - 7], fill=hull)
    draw.rectangle([bx + 3, top - 28, bx + 9, top - 20], fill=hull)
    if smoke:
        for i, (dx, dy, r) in enumerate([(0, -36, 6), (7, -44, 8), (16, -52, 10)]):
            draw.ellipse([bx + 6 + dx - r, top + dy - r, bx + 6 + dx + r, top + dy + r],
                         fill=(120, 116, 108))
        # flame at the bow
        fx = x + 12
        draw.polygon([(fx, top - 8), (fx + 7, top - 24), (fx + 14, top - 8)],
                     fill=(224, 110, 32))
        draw.polygon([(fx + 3, top - 8), (fx + 7, top - 17), (fx + 11, top - 8)],
                     fill=(244, 178, 52))


def mine(draw, cx, cy, r=7):
    dark = (38, 40, 44)
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-0.7, -0.7), (0.7, 0.7),
                   (-0.7, 0.7), (0.7, -0.7)]:
        draw.line([cx, cy, cx + dx * (r + 5), cy + dy * (r + 5)], fill=dark, width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(200, 60, 44))


def hero_scene(draw, box):
    """Stylised Strait of Hormuz: two shores, tankers, mines, low sun."""
    x0, y0, x1, y1 = box
    sea_y = y0 + int((y1 - y0) * 0.62)
    # sky
    draw.rectangle(box, fill=(246, 222, 178))
    # sun
    sx, sy = x0 + 52, y0 + 34
    draw.ellipse([sx - 17, sy - 17, sx + 17, sy + 17], fill=(240, 170, 60))
    # far shore (Iran side) and near shore (Oman side)
    draw.polygon([(x0, sea_y), (x0, y0 + 46), (x0 + 90, y0 + 30),
                  (x0 + 170, y0 + 52), (x0 + 240, sea_y)], fill=(196, 150, 96))
    draw.polygon([(x1, sea_y), (x1, y0 + 58), (x1 - 70, y0 + 44),
                  (x1 - 130, sea_y)], fill=(176, 130, 84))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(62, 120, 150))
    for i in range(5):
        wy = sea_y + 10 + i * 11
        for wx in range(x0 + 12 + (i % 2) * 18, x1 - 30, 46):
            draw.arc([wx, wy, wx + 24, wy + 8], 180, 360, fill=(150, 195, 215), width=2)
    # tankers and mines
    tanker(draw, x0 + 70, sea_y + 16, 150, (52, 54, 60), smoke=True)
    tanker(draw, x1 - 190, sea_y + 34, 120, (84, 88, 96))
    mine(draw, x0 + 130, sea_y + 30)
    mine(draw, x1 - 90, sea_y + 14, r=6)
    # frame + caption
    draw.rectangle(box, outline=RULE, width=2)
    draw.rectangle([x0, y1 - 20, x1, y1], fill=(26, 24, 22))
    centered(draw, (x0 + x1) // 2, y1 - 16, "STRAIT OF HORMUZ",
             font(SANS_BOLD, 11), (255, 255, 255))


def draw_hero(draw, top):
    bottom = top + 184
    x0, x1 = MARGIN, W - MARGIN
    draw.rectangle([x0, top + 8, x1, bottom], fill=CARD_BG, outline=CARD_EDGE, width=1)
    text_x = x0 + 16
    chip(draw, text_x, top + 20, HERO_KICKER, REGION_COLORS["MIDDLE EAST"], font(SANS_BOLD, 11))
    headline_f = font(SERIF_BOLD, 26)
    lines = wrap(draw, HERO_HEADLINE, headline_f, 560, max_lines=2)
    y = top + 43
    for ln in lines:
        draw.text((text_x, y), ln, font=headline_f, fill=INK)
        y += 31
    body_f = font(SANS, 13)
    y += 3
    for ln in HERO_BODY:
        draw.text((text_x, y), ln, font=body_f, fill=(52, 48, 42))
        y += 18
    hero_scene(draw, (x1 - 342, top + 20, x1 - 16, bottom - 12))
    draw.line([x0, bottom + 8, x1, bottom + 8], fill=RULE, width=1)
    return bottom + 8


# ------------------------------------------------------------------- grid ---

def draw_card(draw, box, region, headline, source):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD_BG, outline=CARD_EDGE, width=1)
    color = REGION_COLORS[region]
    draw.rectangle([x0, y0, x0 + 4, y1], fill=color)
    pad = 9
    chip(draw, x0 + pad, y0 + 5, region, color, font(SANS_BOLD, 9))
    src_f = font(SANS, 9)
    draw.text((x1 - pad - text_w(draw, source, src_f), y0 + 7),
              source, font=src_f, fill=SOFT)
    head_f = font(SANS_BOLD, 12)
    lines = wrap(draw, headline, head_f, (x1 - x0) - 2 * pad, max_lines=2)
    y = y0 + 24
    for ln in lines:
        draw.text((x0 + pad, y), ln, font=head_f, fill=INK)
        y += 15


def draw_grid(draw, top):
    cols, rows, gap = 4, 11, 7
    x0, x1 = MARGIN, W - MARGIN
    bottom_limit = H - 44
    card_w = (x1 - x0 - (cols - 1) * gap) / cols
    card_h = (bottom_limit - top - (rows - 1) * gap) / rows
    assert len(STORIES) == cols * rows, f"grid holds {cols*rows}, have {len(STORIES)}"
    for i, (region, headline, source) in enumerate(STORIES):
        r, c = divmod(i, cols)
        cx = x0 + c * (card_w + gap)
        cy = top + r * (card_h + gap)
        draw_card(draw, (cx, cy, cx + card_w, cy + card_h), region, headline, source)
    return bottom_limit


# ----------------------------------------------------------------- footer ---

def draw_footer(draw, y):
    draw.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
    left = "Sources: Reuters · AP · BBC · UN News · CNN · Open Chronicle · Daily Fox News · Standard Topic"
    draw.text((MARGIN, y + 8), left, font=font(SANS, 11), fill=SOFT)
    right = "make.fun · news-image-20261125"
    draw.text((W - MARGIN - text_w(draw, right, font(SANS, 11)), y + 8),
              right, font=font(SANS, 11), fill=SOFT)


# ------------------------------------------------------------------- main ---

def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_masthead(draw)
    y = draw_hero(draw, y)
    y = draw_grid(draw, y + 10)
    draw_footer(draw, y + 8)
    img.save(OUT, format="PNG", optimize=True)
    size = OUT.stat().st_size
    print(f"wrote {OUT.name}: {size} bytes, {img.size[0]}x{img.size[1]}, "
          f"{1 + len(STORIES)} stories")


if __name__ == "__main__":
    main()
