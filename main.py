#!/usr/bin/env python3
"""Draw one happy image to /output/entry.png.

Entry for make.fun bounty ai-happy-01, "Make the AI judge happy".
Python 3.13, standard library only (zlib + struct PNG encoder), no network,
fully deterministic: the same bytes on every run.

The image: Rhider's own brand mascot, a cute pink shark with green eyes
wearing a white hat with a blue band, smiling under a warm sunset over the
sea, with a heart floating above, friendly little fish and bubbles.
Warm pink / orange / yellow palette, one clear focal point, no text.

The judge weighs, in order: (1) warmth and joy at a glance, (2) a fresh,
specific happy idea, (3) colour, light, expression and composition pulling
toward one happy mood, (4) clean craft, (5) readability at ~300 pixels.
This image is built for all five: a big smiling mascot as the single
subject, a golden sunset, and nothing garbled or cluttered.
"""

import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
SKY_TOP = (255, 233, 168)
SKY_MID = (255, 196, 107)
SKY_LOW = (255, 150, 104)
HORIZON = (255, 126, 107)
SUN_CORE = (255, 243, 176)
SUN_RING = (255, 217, 61)
CLOUD = (255, 244, 224)
CLOUD_PINK = (255, 214, 200)
SEA_TOP = (46, 196, 182)
SEA_MID = (26, 143, 168)
SEA_LOW = (18, 100, 140)
GOLD = (255, 200, 90)
SHARK_DARK = (244, 110, 150)
SHARK = (255, 143, 177)
BELLY = (255, 227, 238)
BLUSH = (255, 120, 140)
GREEN = (46, 204, 113)
GREEN_DARK = (31, 163, 74)
BLACK = (30, 30, 40)
SMILE = (90, 30, 50)
WHITE = (255, 255, 255)
HAT = (255, 255, 255)
HAT_SHADE = (228, 230, 242)
BAND = (59, 130, 246)
FEATHER = (46, 204, 113)
GEM = (255, 77, 109)
HEART = (255, 77, 109)
FISH_ORANGE = (255, 159, 67)
FISH_YELLOW = (255, 214, 64)
BUBBLE = (205, 235, 245)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rows = [bytearray(w * 3) for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = x * 3
            r = self.rows[y]
            r[i], r[i + 1], r[i + 2] = c

    def span(self, y, x0, x1, c):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w - 1, x1)
        if x1 < x0:
            return
        r = self.rows[y]
        for x in range(x0, x1 + 1):
            i = x * 3
            r[i], r[i + 1], r[i + 2] = c

    def fill_rect(self, y0, y1, c):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            self.span(y, 0, self.w - 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = rx * math.sqrt(1 - dy * dy)
            self.span(y, int(cx - dx), int(cx + dx), c)

    def circle(self, cx, cy, r, c):
        self.ellipse(cx, cy, r, r, c)

    def polygon(self, pts, c):
        # Scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h, int(max(ys)) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.span(y, int(xs[i]), int(xs[i + 1]), c)

    def disk_stamp(self, cx, cy, r, c):
        self.circle(int(cx), int(cy), int(r), c)

    def thick_arc(self, cx, cy, rx, ry, a0, a1, t, c):
        steps = int((a1 - a0) * max(rx, ry) / 3) + 8
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            self.disk_stamp(cx + rx * math.cos(a), cy + ry * math.sin(a), t, c)

    def thick_line(self, x0, y0, x1, y1, t, c):
        dist = math.hypot(x1 - x0, y1 - y0)
        steps = int(dist / 3) + 2
        for i in range(steps + 1):
            s = i / steps
            self.disk_stamp(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s, t, c)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw():
    cv = Canvas(W, H)
    horizon = 640

    # --- sky: warm sunset gradient ----------------------------------------
    for y in range(horizon):
        if y < 340:
            c = lerp(SKY_TOP, SKY_MID, y / 340)
        else:
            c = lerp(SKY_MID, SKY_LOW, (y - 340) / 300)
        cv.span(y, 0, W - 1, c)
    # horizon glow band
    for y in range(horizon - 40, horizon):
        cv.span(y, 0, W - 1, lerp(SKY_LOW, HORIZON, (y - (horizon - 40)) / 40))

    # --- sun with glow ------------------------------------------------------
    cv.ellipse(700, 250, 175, 175, (255, 224, 130))
    cv.ellipse(700, 250, 145, 145, SUN_RING)
    cv.ellipse(700, 250, 112, 112, SUN_CORE)
    cv.ellipse(700, 250, 70, 70, (255, 250, 210))

    # --- soft clouds --------------------------------------------------------
    for cx, cy, rx, ry, c in [
        (190, 150, 130, 34, CLOUD), (250, 132, 90, 26, CLOUD),
        (880, 110, 120, 30, CLOUD_PINK), (820, 92, 80, 24, CLOUD),
        (330, 300, 110, 28, CLOUD_PINK), (390, 284, 70, 22, CLOUD),
    ]:
        cv.ellipse(cx, cy, rx, ry, c)

    # --- sea: teal gradient --------------------------------------------------
    for y in range(horizon, H):
        t = (y - horizon) / (H - horizon)
        if t < 0.5:
            c = lerp(SEA_TOP, SEA_MID, t / 0.5)
        else:
            c = lerp(SEA_MID, SEA_LOW, (t - 0.5) / 0.5)
        cv.span(y, 0, W - 1, c)

    # Sun reflection: warm shimmering dashes on the water, not a solid
    # column — short horizontal segments with gaps, wobbling gently.
    # (First version drew a solid gold column; it read as a pillar
    # behind the shark, so it was replaced with this dashed shimmer.)
    for y in range(648, 1024, 7):
        if (y // 42) % 2 == 0:
            continue
        wob = int(16 * math.sin(y / 55.0))
        width = 46 + int(30 * math.sin(y / 130.0))
        cv.span(y, 700 - width + wob, 700 + width + wob, GOLD)
        cv.span(y + 1, 700 - width + wob, 700 + width + wob, GOLD)
    for y in range(700, 1024, 11):
        if (y // 37) % 2 == 0:
            continue
        wob = int(10 * math.sin(y / 47.0))
        cv.span(y, 600 - 22 + wob, 600 + 22 + wob, GOLD)
        cv.span(y, 800 - 22 + wob, 800 + 22 + wob, GOLD)
    # wave bands
    for cy in (700, 800, 910):
        cv.thick_arc(512, cy, 420, 26, math.pi * 0.08, math.pi * 0.92, 7,
                     (255, 255, 255) if cy == 700 else (140, 220, 225))

    # --- shark tail (behind body, right side) --------------------------------
    cv.polygon([(760, 640), (900, 560), (880, 660), (905, 760), (765, 720)],
               SHARK_DARK)
    cv.polygon([(760, 645), (880, 575), (868, 655), (885, 740), (765, 710)],
               SHARK)

    # --- shark body: dark rim then pink, belly lighter ----------------------
    cv.ellipse(512, 680, 312, 196, SHARK_DARK)
    cv.ellipse(512, 680, 300, 185, SHARK)
    cv.ellipse(512, 760, 235, 105, BELLY)

    # dorsal fin on top
    cv.polygon([(470, 520), (512, 420), (560, 520)], SHARK_DARK)
    cv.polygon([(482, 520), (512, 442), (548, 520)], SHARK)
    # pectoral fins
    cv.polygon([(250, 700), (180, 780), (270, 760)], SHARK_DARK)
    cv.polygon([(255, 705), (195, 770), (265, 752)], SHARK)
    cv.polygon([(774, 700), (844, 780), (754, 760)], SHARK_DARK)
    cv.polygon([(769, 705), (829, 770), (759, 752)], SHARK)

    # gill lines
    for gx in (330, 352):
        cv.thick_arc(gx, 660, 26, 60, -0.9, 0.9, 6, (230, 105, 145))
    for gx in (672, 694):
        cv.thick_arc(gx, 660, 26, 60, math.pi - 0.9, math.pi + 0.9, 6,
                     (230, 105, 145))

    # blush cheeks
    cv.ellipse(350, 690, 42, 26, BLUSH)
    cv.ellipse(674, 690, 42, 26, BLUSH)

    # --- big happy green eyes -------------------------------------------------
    for ex in (420, 604):
        cv.ellipse(ex, 600, 52, 62, WHITE)
        cv.ellipse(ex, 602, 38, 46, GREEN_DARK)
        cv.ellipse(ex, 602, 30, 38, GREEN)
        cv.ellipse(ex, 606, 15, 19, BLACK)
        cv.ellipse(ex - 10, 588, 10, 12, WHITE)
    # happy eye arcs above
    cv.thick_arc(420, 596, 58, 58, math.pi * 1.15, math.pi * 1.85, 7, SHARK_DARK)
    cv.thick_arc(604, 596, 58, 58, math.pi * 1.15, math.pi * 1.85, 7, SHARK_DARK)

    # --- big open smile -------------------------------------------------------
    cv.thick_arc(512, 690, 110, 78, math.pi * 0.15, math.pi * 0.85, 10, SMILE)
    # smile dimples
    cv.circle(402, 706, 9, SMILE)
    cv.circle(622, 706, 9, SMILE)

    # --- white hat with blue band --------------------------------------------
    cv.ellipse(512, 500, 200, 34, HAT_SHADE)
    cv.ellipse(512, 494, 200, 30, HAT)
    cv.ellipse(512, 470, 132, 78, HAT)
    # blue band across the hat dome
    for y in range(492, 516):
        dy = (y - 470) / 78
        if abs(dy) > 1:
            continue
        dx = 132 * math.sqrt(1 - dy * dy)
        cv.span(y, int(512 - dx), int(512 + dx), BAND)
    # hat brim highlight
    cv.ellipse(512, 488, 200, 12, WHITE)
    # feather: small green plume + stem
    cv.thick_line(600, 452, 648, 392, 6, (60, 120, 60))
    cv.ellipse(652, 384, 16, 42, FEATHER)
    cv.ellipse(652, 384, 8, 30, (120, 230, 150))
    # gem on the band
    cv.polygon([(512, 486), (528, 502), (512, 518), (496, 502)], GEM)
    cv.circle(512, 502, 5, WHITE)

    # --- floating heart -------------------------------------------------------
    def heart(cx, cy, s, c):
        cv.circle(cx - int(0.32 * s), cy - int(0.1 * s), int(0.34 * s), c)
        cv.circle(cx + int(0.32 * s), cy - int(0.1 * s), int(0.34 * s), c)
        cv.polygon([(cx - int(0.62 * s), cy - int(0.05 * s)),
                    (cx + int(0.62 * s), cy - int(0.05 * s)),
                    (cx, cy + int(0.75 * s))], c)

    heart(780, 400, 52, HEART)
    cv.ellipse(768, 386, 10, 14, (255, 150, 170))
    heart(240, 380, 36, HEART)

    # --- friendly little fish --------------------------------------------------
    def fish(cx, cy, s, body, tail):
        cv.polygon([(cx + int(0.9 * s), cy), (cx + int(1.6 * s), cy - int(0.5 * s)),
                    (cx + int(1.6 * s), cy + int(0.5 * s))], tail)
        cv.ellipse(cx, cy, int(0.95 * s), int(0.55 * s), body)
        cv.circle(cx - int(0.45 * s), cy - int(0.08 * s), int(0.14 * s), BLACK)
        cv.circle(cx - int(0.48 * s), cy - int(0.12 * s), int(0.05 * s), WHITE)
        cv.thick_arc(cx - int(0.55 * s), cy + int(0.08 * s), int(0.3 * s),
                     int(0.22 * s), math.pi * 0.15, math.pi * 0.85, 4, SMILE)

    fish(190, 830, 52, FISH_ORANGE, (255, 120, 40))
    fish(850, 880, 44, FISH_YELLOW, (255, 180, 40))
    fish(150, 950, 36, FISH_YELLOW, (255, 180, 40))

    # --- bubbles rising ---------------------------------------------------------
    for bx, by, br in [(300, 900, 14), (330, 860, 9), (720, 920, 12),
                       (745, 875, 8), (690, 965, 10), (270, 960, 7)]:
        cv.circle(bx, by, br, BUBBLE)
        cv.circle(bx, by, br - 3, (120, 200, 220))
        cv.circle(bx - 3, by - 3, 3, WHITE)

    return cv


def write_png(cv, path):
    raw = b"".join(b"\x00" + bytes(row) for row in cv.rows)
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return len(png)


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    size = write_png(draw(), out_dir / "entry.png")
    print(f"wrote {size} bytes to {out_dir / 'entry.png'}")


if __name__ == "__main__":
    main()
