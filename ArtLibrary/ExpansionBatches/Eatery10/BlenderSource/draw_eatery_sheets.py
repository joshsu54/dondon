"""Design sheets for the eatery before modelling: 01 elevations (front, right), 02 plans (ground, upper).
Run: python3 draw_eatery_sheets.py   -> ../DesignSheets/Eatery_01_elevations.png, Eatery_02_plans.png
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eatery_specs import *

OUT = HERE.parent / 'DesignSheets'
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
PAPER, INK, WALL, WOOD, ROOF, DIM, GLASS, FIRE = (244, 240, 228), (40, 52, 46), (222, 214, 194), (120, 78, 48), (78, 92, 96), (150, 60, 40), (210, 190, 140), (70, 50, 40)


def font(s): return ImageFont.truetype(FONT, s)


class Pane:
    def __init__(self, d, box, ux, vy, title):
        self.d = d; x0, y0, x1, y1 = box
        self.s = min((x1 - x0) * .86 / (ux[1] - ux[0]), (y1 - y0 - 60) * .82 / (vy[1] - vy[0]))
        self.ox = (x0 + x1) / 2 - (ux[0] + ux[1]) / 2 * self.s
        self.oy = (y0 + 50 + y1) / 2 + (vy[0] + vy[1]) / 2 * self.s
        d.text((x0, y0), title, fill=INK, font=font(30))

    def p(self, u, v): return (self.ox + u * self.s, self.oy - v * self.s)

    def rect(self, u0, v0, u1, v1, fill=WALL, w=2):
        a, b = self.p(min(u0, u1), max(v0, v1)), self.p(max(u0, u1), min(v0, v1))
        self.d.rectangle([a, b], fill=fill, outline=INK, width=w)

    def poly(self, pts, fill=WALL, w=2):
        q = [self.p(*t) for t in pts]; self.d.polygon(q, fill=fill, outline=INK)
        self.d.line(q + [q[0]], fill=INK, width=w)

    def circle(self, u, v, r, fill=WOOD):
        self.d.ellipse([self.p(u - r, v + r), self.p(u + r, v - r)], fill=fill, outline=INK, width=2)

    def text(self, u, v, t, size=20, fill=INK):
        f = font(size); tw = self.d.textlength(t, font=f); x, y = self.p(u, v); self.d.text((x - tw / 2, y - size / 2), t, fill=fill, font=f)

    def dim(self, a, b, off, label=None):
        pa, pb = self.p(*a), self.p(*b); dx, dy = pb[0] - pa[0], pb[1] - pa[1]; n = math.hypot(dx, dy)
        nx, ny = -dy / n, dx / n; o = off * self.s
        qa, qb = (pa[0] + nx * o, pa[1] + ny * o), (pb[0] + nx * o, pb[1] + ny * o)
        for p, q in ((pa, qa), (pb, qb)): self.d.line([p, q], fill=DIM, width=1)
        self.d.line([qa, qb], fill=DIM, width=2)
        for q in (qa, qb): self.d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=DIM)
        t = label or f'{math.dist(a, b):.2f} m'; f = font(20); tw = self.d.textlength(t, font=f)
        mx, my = (qa[0] + qb[0]) / 2 + nx * 16 * math.copysign(1, o), (qa[1] + qb[1]) / 2 + ny * 16 * math.copysign(1, o)
        self.d.text((mx - tw / 2, my - 11), t, fill=DIM, font=f)


def roof_v(t):
    """Roof height at fraction t from ridge (0) to eave (1); gentle concave curve with upturned eave."""
    return Z_TOP - .1 + RISE * (1 - t) ** 1.35 + .18 * t ** 8


def sheet(name, title, panes, notes):
    img = Image.new('RGB', (2000, 1300), PAPER); d = ImageDraw.Draw(img)
    d.text((50, 30), f'{NAME_ZH}  {NAME}  ·  {title}', fill=INK, font=font(46))
    d.text((50, 92), '食肆客棧 10 · 建模設計圖（單位 m，正面 = Blender -Y，原點 = 石台底部中心）', fill=INK, font=font(24))
    for box, fn in panes: fn(d, box)
    y = 1150
    for line in notes: d.text((60, y), '· ' + line, fill=INK, font=font(22)); y += 32
    d.rectangle([20, 20, 1980, 1280], outline=INK, width=3)
    OUT.mkdir(exist_ok=True); img.save(OUT / name); print('SHEET', name)


def front(d, box):
    v = Pane(d, box, (-6.2, 6.2), (-.2, Z_RIDGE + .4), '正立面 Front (X-Z)')
    v.rect(-W / 2 - .1, 0, W / 2 + .1, PLINTH, fill=(170, 176, 172))
    v.rect(-W / 2, PLINTH, W / 2, Z_UP, fill=WALL)
    v.rect(-W / 2, Z_UP, W / 2, Z_TOP)
    for a, b in OPEN_BAYS: v.rect(a + .12, PLINTH, b - .12, PLINTH + DOOR_H, fill=FIRE)
    for cx in (-3.75, 3.75): v.rect(cx - .6, PLINTH + 1.0, cx + .6, PLINTH + 2.3, fill=GLASS)
    for cx in (-3.3, 3.3): v.rect(cx - .6, Z_UP + .9, cx + .6, Z_UP + 2.1, fill=GLASS)
    v.rect(-.55, Z_UP, .55, Z_UP + 2.2, fill=WOOD)
    for x in COLUMNS_X: v.rect(x - .12, PLINTH, x + .12, Z_UP + 1.05, fill=WOOD)
    v.rect(-W / 2 - .1, Z_UP - .2, W / 2 + .1, Z_UP, fill=WOOD)
    v.rect(-W / 2, Z_UP + .95, W / 2, Z_UP + 1.05, fill=WOOD)
    for i in range(41): x = -5 + i * .25; v.d.line([v.p(x, Z_UP), v.p(x, Z_UP + 1.0)], fill=WOOD, width=2)
    v.rect(-SIGN['w'] / 2, SIGN['z'], SIGN['w'] / 2, SIGN['z'] + SIGN['h'], fill=(160, 110, 60))
    for x in LANTERNS_X: v.circle(x, 2.6, .22, fill=(200, 80, 50))
    gx = W / 2 + GABLE_OVER
    v.poly([(-gx, roof_v(1) - .1), (-gx, roof_v(1) + .1), (-gx + .2, Z_RIDGE), (gx - .2, Z_RIDGE), (gx, roof_v(1) + .1), (gx, roof_v(1) - .1)], fill=ROOF)
    v.dim((-W / 2, 0), (W / 2, 0), -.6)
    v.dim((W / 2 + .7, 0), (W / 2 + .7, Z_RIDGE), -.4, f'屋脊 {Z_RIDGE:.2f} m')
    v.dim((-W / 2 - .7, PLINTH), (-W / 2 - .7, Z_UP), .4, f'一樓 {Z_UP - PLINTH:.2f}')
    v.dim((-W / 2 - .7, Z_UP), (-W / 2 - .7, Z_TOP), .4, f'二樓 {F2:.2f}')
    v.dim((-2.38, PLINTH + DOOR_H + .1), (2.38, PLINTH + DOOR_H + .1), .25, '開放門面 2 開間（摺門全開）')


def right(d, box):
    v = Pane(d, box, (-6.4, 5.0), (-.2, Z_RIDGE + .4), '右側立面 Right (Y-Z)，左 = 正面')
    # Mirror so the front (-Y) is on the left of the drawing.
    def P(y): return y
    v.rect(-D / 2 - VERANDA - .1, 0, D / 2 + .1, PLINTH, fill=(170, 176, 172))
    v.rect(-D / 2, PLINTH, D / 2, Z_TOP)
    v.rect(-D / 2 - VERANDA, Z_UP - .2, -D / 2, Z_UP, fill=WOOD)
    v.rect(-D / 2 - VERANDA - .12, PLINTH, -D / 2 - VERANDA + .12, Z_UP + 1.05, fill=WOOD)
    v.rect(-D / 2 - VERANDA, Z_UP + .95, -D / 2, Z_UP + 1.05, fill=WOOD)
    v.rect(.8, PLINTH + 1.1, 2.2, PLINTH + 2.2, fill=GLASS)
    v.rect(-1.0, Z_UP + .9, .2, Z_UP + 2.1, fill=GLASS)
    pts = [(-D / 2 - EAVE + (D + 2 * EAVE) * i / 40, 0) for i in range(41)]
    prof = [(y, roof_v(abs(y) / (D / 2 + EAVE))) for y, _ in pts]
    v.poly(prof + [(y, z - .25) for y, z in prof[::-1]], fill=ROOF)
    v.poly([(-D / 2, Z_TOP)] + [(y, z - .25) for y, z in prof if -D / 2 <= y <= D / 2] + [(D / 2, Z_TOP)], fill=WALL)
    v.rect(CHIMNEY['y0'], Z_TOP - .5, CHIMNEY['y1'], CHIMNEY['top'], fill=(150, 150, 150))
    for i in range(2): v.rect(-D / 2 - VERANDA - .3 - i * .3, 0, -D / 2 - VERANDA - i * .3, PLINTH * (1 - i / 2), fill=(170, 176, 172))
    v.dim((-D / 2 - VERANDA, 0), (D / 2, 0), -.6, f'{D + VERANDA:.1f} m（含簷廊 {VERANDA} m）')
    v.text(-D / 2 - VERANDA / 2, Z_UP + 1.5, '陽台', 22, DIM)
    v.text(CHIMNEY['y0'] - .6, CHIMNEY['top'] - .2, '煙囪', 22, DIM)


def ground(d, box):
    v = Pane(d, box, (-5.6, 5.6), (-5.9, 3.9), '一樓平面 Ground floor')
    v.rect(-W / 2 - .1, -D / 2 - VERANDA, W / 2 + .1, D / 2 + .1, fill=(200, 204, 198))
    v.rect(-W / 2, -D / 2, W / 2, D / 2, fill=(236, 226, 204))
    t = WALL_T
    for a, b in [((-W / 2, D / 2 - t), (W / 2, D / 2)), ((-W / 2, -D / 2), (-W / 2 + t, D / 2)), ((W / 2 - t, -D / 2), (W / 2, D / 2)),
                 ((-W / 2, -D / 2), (-2.5, -D / 2 + t)), ((2.5, -D / 2), (W / 2, -D / 2 + t))]:
        v.rect(a[0], a[1], b[0], b[1], fill=INK)
    k = KITCHEN
    v.rect(k['x0'] - .06, k['y0'], k['x0'] + .06, D / 2, fill=INK)
    v.rect(k['x0'], k['y0'] - .06, k['door'][0], k['y0'] + .06, fill=INK)
    v.rect(k['door'][1], k['y0'] - .06, W / 2, k['y0'] + .06, fill=INK)
    v.text(3.1, 1.6, '廚房', 24); v.text(-.3, -1.1, '用餐區', 24)
    v.rect(HEARTH_AT[0] - .6, HEARTH_AT[1] - .4, HEARTH_AT[0] + .6, HEARTH_AT[1] + .4, fill=(190, 180, 160))
    v.circle(HEARTH_AT[0] - .18, HEARTH_AT[1], .25, fill=FIRE)
    v.rect(CHIMNEY['x'] - CHIMNEY['w'] / 2, CHIMNEY['y0'], CHIMNEY['x'] + CHIMNEY['w'] / 2, CHIMNEY['y1'], fill=(150, 150, 150))
    c = COUNTER; v.rect(c['x0'], c['y'] - c['depth'] / 2, c['x1'], c['y'] + c['depth'] / 2, fill=WOOD); v.text((c['x0'] + c['x1']) / 2, c['y'] + .6, '櫃台', 20)
    s = STAIR
    for i in range(s['risers']):
        y = s['y0'] + i * s['tread']; v.rect(s['x0'], y, s['x1'], y + s['tread'], fill=(200, 170, 120), w=1)
    v.text((s['x0'] + s['x1']) / 2, s['y0'] - .35, '上', 22, DIM)
    for x, y in TABLES:
        v.rect(x - .5, y - .5, x + .5, y + .5, fill=(205, 170, 120))
        for dx, dy in ((STOOL_OFFSET, 0), (-STOOL_OFFSET, 0), (0, STOOL_OFFSET), (0, -STOOL_OFFSET)): v.circle(x + dx, y + dy, .16, fill=(170, 120, 80))
    for x in COLUMNS_X: v.rect(x - .12, -D / 2 - VERANDA - .12, x + .12, -D / 2 - VERANDA + .12, fill=WOOD)
    v.rect(BACK_DOOR_X - .5, D / 2 - .3, BACK_DOOR_X + .5, D / 2 + .1, fill=PAPER)
    v.text(0, -D / 2 - VERANDA / 2, '簷廊', 22)
    v.dim((-W / 2, -D / 2 - VERANDA), (W / 2, -D / 2 - VERANDA), -.45)
    v.dim((W / 2, -D / 2), (W / 2, D / 2), -.45)


def upper(d, box):
    v = Pane(d, box, (-5.6, 5.6), (-5.9, 3.9), '二樓平面 Upper floor')
    v.rect(-W / 2, -D / 2 - VERANDA, W / 2, -D / 2, fill=(205, 175, 130))
    v.rect(-W / 2, -D / 2, W / 2, D / 2, fill=(236, 226, 204))
    t = WALL_T
    for a, b in [((-W / 2, D / 2 - t), (W / 2, D / 2)), ((-W / 2, -D / 2), (-W / 2 + t, D / 2)), ((W / 2 - t, -D / 2), (W / 2, D / 2)),
                 ((-W / 2, -D / 2), (W / 2, -D / 2 + t)), ((-W / 2, CORRIDOR_Y - .06), (W / 2, CORRIDOR_Y + .06))]:
        v.rect(a[0], a[1], b[0], b[1], fill=INK)
    for x in ROOM_WALLS_X: v.rect(x - .06, -D / 2, x + .06, CORRIDOR_Y, fill=INK)
    for i, cx in enumerate([-3.3, 0, 3.3]):
        v.text(cx, -1.6, f'客房 {i + 1}', 24); v.rect(cx - .45, CORRIDOR_Y - .07, cx + .45, CORRIDOR_Y + .07, fill=PAPER)
    v.rect(-.55, -D / 2 - .02, .55, -D / 2 + t + .02, fill=PAPER)
    x0, x1, y0, y1 = STAIRWELL; v.rect(x0, y0, x1, y1, fill=(200, 170, 120)); v.text((x0 + x1) / 2, (y0 + y1) / 2, '梯', 22)
    v.rect(CHIMNEY['x'] - CHIMNEY['w'] / 2, CHIMNEY['y0'], CHIMNEY['x'] + CHIMNEY['w'] / 2, CHIMNEY['y1'], fill=(150, 150, 150))
    v.text(1.0, 2.0, '走廊', 24); v.text(0, -D / 2 - VERANDA / 2, '陽台（欄杆高 1.0 m）', 22)
    v.dim((-W / 2, CORRIDOR_Y), (-W / 2, D / 2), .45, f'走廊 {D / 2 - CORRIDOR_Y:.1f} m')


sheet('Eatery_01_elevations.png', '立面', [((40, 140, 1000, 1130), front), ((1020, 140, 1980, 1130), right)],
      ['一樓兩開間摺門全開為用餐區入口；左右開間為格窗。二樓前牆三扇格窗，中間為陽台門。',
       f'地坪 {PLINTH} m 石台；一樓地面至二樓 {Z_UP - PLINTH:.1f} m（17 級 × 0.20 m）；二樓牆高 {F2} m；雙坡曲面瓦頂，前後出簷 {EAVE} m。',
       '空白木招牌與兩盞紅燈籠掛在簷廊梁下，門高 2.6 m 足供 1.8 m 角色通行。'])
sheet('Eatery_02_plans.png', '平面', [((40, 140, 1000, 1130), ground), ((1020, 140, 1980, 1130), upper)],
      ['一樓：4 張食肆方桌（各 4 張圓凳）、櫃台、西牆直跑樓梯；東北角廚房含柴火爐灶與穿屋頂煙囪，後牆有後門。',
       '二樓：三間客房朝南，北側走廊連接樓梯口；樓梯開口確保樓梯下方淨高 ≥ 2.0 m。',
       '家具直接沿用 KitchenWare09 的 DiningTable、RoundStool、CookingHearth、IronWok、BambooSteamer、碗盤。'])
