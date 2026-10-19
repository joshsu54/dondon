"""Pillow helpers for dimensioned design sheets (front / side / top), shared by prop batches from StreetProps11 on."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
W, H = 1800, 1100
PAPER, INK, FILL, CUT, DIM = (244, 240, 228), (40, 52, 46), (214, 206, 186), (92, 70, 52), (150, 60, 40)
WOOD, STONE, TILE, PAPERY, ROPE, WATER = (150, 100, 60), (170, 176, 172), (90, 110, 112), (236, 228, 200), (190, 160, 110), (70, 90, 100)


def font(size): return ImageFont.truetype(FONT, size)


class View:
    """Maps metres in a view plane to a pixel box; v axis points up."""

    def __init__(self, draw, box, ext_u, ext_v, title, scale):
        self.d, self.s = draw, scale; x0, y0, x1, y1 = box
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2 + 20; self.ou, self.ov = ext_u, ext_v
        draw.text((x0, y0), title, fill=INK, font=font(30))

    def p(self, u, v):
        return (self.cx + (u - (self.ou[0] + self.ou[1]) / 2) * self.s, self.cy - (v - (self.ov[0] + self.ov[1]) / 2) * self.s)

    def rect(self, u0, v0, u1, v1, fill=FILL, width=2):
        self.d.rectangle([self.p(min(u0, u1), max(v0, v1)), self.p(max(u0, u1), min(v0, v1))], fill=fill, outline=INK, width=width)

    def poly(self, pts, fill=FILL, width=2):
        q = [self.p(*t) for t in pts]; self.d.polygon(q, fill=fill, outline=INK); self.d.line(q + [q[0]], fill=INK, width=width)

    def circle(self, u, v, r, fill=FILL, width=2):
        self.d.ellipse([self.p(u - r, v + r), self.p(u + r, v - r)], fill=fill, outline=INK, width=width)

    def line(self, a, b, width=2, fill=INK):
        self.d.line([self.p(*a), self.p(*b)], fill=fill, width=width)

    def dim(self, a, b, offset, label=None):
        pa, pb = self.p(*a), self.p(*b); dx, dy = pb[0] - pa[0], pb[1] - pa[1]; n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n; o = offset * self.s; sg = math.copysign(1, o) if o else 1
        qa, qb = (pa[0] + nx * o, pa[1] + ny * o), (pb[0] + nx * o, pb[1] + ny * o)
        for p, q in ((pa, qa), (pb, qb)): self.d.line([p, q], fill=DIM, width=1)
        self.d.line([qa, qb], fill=DIM, width=2)
        for q in (qa, qb): self.d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=DIM)
        text = label or f'{round(math.dist(a, b) * 1000)} mm'; f = font(22); tw = self.d.textlength(text, font=f)
        mx, my = (qa[0] + qb[0]) / 2 + nx * 18 * sg, (qa[1] + qb[1]) / 2 + ny * 18 * sg
        self.d.text((mx - tw / 2, my - 12), text, fill=DIM, font=f)


def lathe_front(v, profile, outer_count, fill=FILL):
    """Left half silhouette, right half section through the wall."""
    outer = profile[:outer_count]
    v.poly([(0, outer[0][1])] + [(-r, z) for r, z in outer] + [(0, outer[-1][1])], fill)
    v.poly([(r, z) for r, z in profile], CUT)


def sheet(out_dir, batch_title, aid, name_zh, detail, extents, draw_fn, notes):
    img = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(img)
    d.text((50, 30), f'{name_zh}  {aid}', fill=INK, font=font(48))
    d.text((50, 95), f'{batch_title} · 建模設計圖（單位 mm，正面 = Blender -Y，原點 = 底部中心）', fill=INK, font=font(24))
    boxes = [(60, 170, 860, 640), (940, 170, 1740, 640), (60, 650, 860, 1080)]
    scale = min(min((b[2] - b[0]) * .78 / (e[0][1] - e[0][0]), (b[3] - b[1] - 60) * .78 / (e[1][1] - e[1][0])) for b, e in zip(boxes, extents))
    views = [View(d, b, e[0], e[1], t, scale) for b, e, t in zip(boxes, extents, ['正視圖 Front (X-Z)', '側視圖 Right (Y-Z)', '俯視圖 Top (X-Y)'])]
    draw_fn(*views)
    y = 700; d.text((940, y), '製作說明', fill=INK, font=font(30))
    for line in [detail] + notes:
        cur = ''
        for ch in line:
            if d.textlength(cur + ch, font=font(22)) > 780: y += 34; d.text((940, y), cur, fill=INK, font=font(22)); cur = ''
            cur += ch
        y += 34; d.text((940, y), cur, fill=INK, font=font(22)); y += 8
    d.rectangle([20, 20, W - 20, H - 20], outline=INK, width=3)
    Path(out_dir).mkdir(exist_ok=True); img.save(Path(out_dir) / f'{aid}_design.png'); print('SHEET', aid)
