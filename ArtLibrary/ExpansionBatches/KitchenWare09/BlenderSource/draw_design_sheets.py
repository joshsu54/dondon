"""Draw dimensioned design sheets (front / side / top) for KitchenWare09 before modelling.
Run: python3 draw_design_sheets.py   (Pillow; writes ../DesignSheets/<Asset>_design.png)
Lathe items are drawn half elevation (left) / half section (right) so wall thickness is visible.
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kitchen_specs import NAMES, DETAILS, SPECS, BOWL_PROFILE, PLATE_PROFILE

OUT = HERE.parent / 'DesignSheets'
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
W, H = 1800, 1100
PAPER, INK, FILL, CUT, DIM = (244, 240, 228), (40, 52, 46), (214, 206, 186), (92, 70, 52), (150, 60, 40)


def font(size):
    return ImageFont.truetype(FONT, size)


class View:
    """Maps metres in a view plane to a pixel box; v axis points up."""

    def __init__(self, draw, box, extent_u, extent_v, title, scale):
        self.d, self.box, self.s = draw, box, scale
        x0, y0, x1, y1 = box
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2 + 20
        self.ou, self.ov = extent_u, extent_v
        draw.text((x0, y0), title, fill=INK, font=font(30))

    def p(self, u, v):
        return (self.cx + (u - self.ou[0]) * self.s - (self.ou[1] - self.ou[0]) * self.s / 2,
                self.cy - (v - self.ov[0]) * self.s + (self.ov[1] - self.ov[0]) * self.s / 2)

    def rect(self, u0, v0, u1, v1, fill=FILL, width=3):
        a, b = self.p(u0, v1), self.p(u1, v0)
        self.d.rectangle([a, b], fill=fill, outline=INK, width=width)

    def poly(self, pts, fill=FILL, width=3):
        q = [self.p(*pt) for pt in pts]
        self.d.polygon(q, fill=fill, outline=INK)
        self.d.line(q + [q[0]], fill=INK, width=width)

    def circle(self, u, v, r, fill=FILL, width=3):
        a, b = self.p(u - r, v + r), self.p(u + r, v - r)
        self.d.ellipse([a, b], fill=fill, outline=INK, width=width)

    def line(self, a, b, width=2, fill=INK):
        self.d.line([self.p(*a), self.p(*b)], fill=fill, width=width)

    def dim(self, a, b, offset, label=None):
        """Dimension line between a and b, pushed `offset` metres perpendicular (screen space)."""
        pa, pb = self.p(*a), self.p(*b)
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        o = offset * self.s
        qa, qb = (pa[0] + nx * o, pa[1] + ny * o), (pb[0] + nx * o, pb[1] + ny * o)
        for p, q in ((pa, qa), (pb, qb)):
            self.d.line([p, (q[0] + nx * 8 * math.copysign(1, o), q[1] + ny * 8 * math.copysign(1, o))], fill=DIM, width=1)
        self.d.line([qa, qb], fill=DIM, width=2)
        for q, sgn in ((qa, 1), (qb, -1)):
            ux, uy = dx / n * sgn, dy / n * sgn
            self.d.polygon([q, (q[0] + ux * 14 + nx * 5, q[1] + uy * 14 + ny * 5), (q[0] + ux * 14 - nx * 5, q[1] + uy * 14 - ny * 5)], fill=DIM)
        text = label or f'{round(math.dist(a, b) * 1000)} mm'
        f = font(22)
        tw = self.d.textlength(text, font=f)
        mx, my = (qa[0] + qb[0]) / 2 + nx * 18 * math.copysign(1, o), (qa[1] + qb[1]) / 2 + ny * 18 * math.copysign(1, o)
        self.d.text((mx - tw / 2, my - 12), text, fill=DIM, font=f)


def lathe_front(v, profile, outer_count):
    """Left half: silhouette; right half: section through the wall."""
    outer = profile[:outer_count]
    v.poly([(0, outer[0][1])] + [(-r, z) for r, z in outer] + [(0, outer[-1][1])])
    v.poly([(r, z) for r, z in profile], fill=CUT)
    v.line((0, -.01), (0, max(z for _, z in profile) + .01), width=1)


def sheet(aid, extents, scale, draw_fn, notes):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.text((50, 30), f'{NAMES[aid]}  {aid}', fill=INK, font=font(48))
    d.text((50, 95), '食肆用具 09 · 建模設計圖（單位 mm，正面 = Blender -Y，原點 = 底部中心）', fill=INK, font=font(24))
    boxes = [(60, 170, 860, 640), (940, 170, 1740, 640), (60, 650, 860, 1080)]
    titles = ['正視圖 Front (X–Z)', '側視圖 Right (Y–Z)', '俯視圖 Top (X–Y)']
    # One shared scale that fits every view inside its box (the passed scale is an upper bound).
    scale = min([scale] + [min((b[2] - b[0]) * .78 / (e[0][1] - e[0][0]), (b[3] - b[1] - 60) * .78 / (e[1][1] - e[1][0])) for b, e in zip(boxes, extents)])
    views = [View(d, b, e[0], e[1], t, scale) for b, e, t in zip(boxes, extents, titles)]
    draw_fn(*views)
    y = 700
    d.text((940, y), '製作說明', fill=INK, font=font(30))
    for line in [DETAILS[aid]] + notes:
        words, cur = line, ''
        for ch in words:
            if d.textlength(cur + ch, font=font(22)) > 780:
                y += 34; d.text((940, y), cur, fill=INK, font=font(22)); cur = ''
            cur += ch
        y += 34; d.text((940, y), cur, fill=INK, font=font(22)); y += 8
    d.rectangle([20, 20, W - 20, H - 20], outline=INK, width=3)
    OUT.mkdir(exist_ok=True)
    img.save(OUT / f'{aid}_design.png')
    print('SHEET', aid)


def hearth():
    s = SPECS['CookingHearth']; X, Y, Z = s['size']; fm, vent = s['fire_mouth'], s['vent']; hx, hr = s['wok_hole_x'], s['wok_hole_r']

    def front(v):
        v.rect(-X / 2 - .02, 0, X / 2 + .02, s['plinth_h'])
        v.rect(-X / 2, s['plinth_h'], X / 2, Z - s['top_h'])
        v.rect(-X / 2 - .015, Z - s['top_h'], X / 2 + .015, Z, fill=CUT)
        w, h, z = fm['w'], fm['h'], fm['z']
        v.poly([(hx - w / 2, z), (hx - w / 2, z + h - w / 2)] + [(hx - w / 2 * math.cos(t * math.pi / 12), z + h - w / 2 + w / 2 * math.sin(t * math.pi / 12)) for t in range(13)] + [(hx + w / 2, z)], fill=(70, 50, 40))
        v.dim((-X / 2, 0), (X / 2, 0), -.10)
        v.dim((X / 2 + .02, 0), (X / 2 + .02, Z), -.10)
        v.dim((hx - w / 2, z), (hx + w / 2, z), .06, f'火口 {round(w * 1000)}')

    def side(v):
        v.rect(-Y / 2 - .02, 0, Y / 2 + .02, s['plinth_h'])
        v.rect(-Y / 2, s['plinth_h'], Y / 2, Z - s['top_h'])
        v.rect(-Y / 2 - .015, Z - s['top_h'], Y / 2 + .015, Z, fill=CUT)
        v.rect(Y / 2 - .01, vent['z'], Y / 2 + .005, vent['z'] + vent['h'], fill=(70, 50, 40))
        v.dim((-Y / 2, 0), (Y / 2, 0), -.10)
        v.d.text(v.p(-Y / 2 - .05, Z + .06), '前 -Y', fill=DIM, font=font(22))

    def top(v):
        v.rect(-X / 2 - .015, -Y / 2 - .015, X / 2 + .015, Y / 2 + .015)
        v.circle(hx, .02, hr + .012, fill=(90, 90, 90))
        v.circle(hx, .02, hr, fill=(60, 45, 38))
        v.dim((hx - hr, .02), (hx + hr, .02), .0, f'鍋口 Ø{round(hr * 2000)}')
        v.dim((-X / 2, -Y / 2), (-X / 2, Y / 2), .10)
    sheet('CookingHearth', [((-.7, .7), (0, .8)), ((-.5, .5), (0, .8)), ((-.7, .7), (-.45, .45))], 520,
          lambda a, b, c: (front(a), side(b), top(c)),
          ['鍋口 Ø500 mm，鐵鍋 Ø550 mm 的鍋緣擱在鑄鐵承圈上。', '爐面為深色石板；火口拱形、內置三根柴；背面有排煙口。', '台面右側為備料平台，高 800 mm 供站立操作。'])


def wok():
    s = SPECS['IronWok']; r, dz, t = s['mouth_d'] / 2, s['depth'], s['wall']
    R = (r * r + dz * dz) / (2 * dz)
    outer = [(R * math.sin(a), R - R * math.cos(a)) for a in [i / 16 * math.asin(r / R) for i in range(17)]]
    inner = [(max(0, (R - t) * math.sin(a)), t + (R - t) - (R - t) * math.cos(a)) for a in [i / 16 * math.asin(r / R) for i in range(17)]][::-1]
    prof = outer + inner

    def front(v):
        lathe_front(v, prof, len(outer))
        for sgn in (-1, 1):
            v.d.ellipse([v.p(sgn * (r + .03) - .035, dz - .005 + .015), v.p(sgn * (r + .03) + .035, dz - .005 - .015)], outline=INK, width=4)
        v.dim((-r, dz), (r, dz), .06, f'Ø{round(r * 2000)}')
        v.dim((r + .09, 0), (r + .09, dz), -.04)

    def side(v):
        v.poly([(0, 0)] + [(-x, z) for x, z in outer] + [(x, z) for x, z in outer[::-1]])
        v.dim((-r, 0), (r, 0), -.06)

    def top(v):
        v.circle(0, 0, r + .007); v.circle(0, 0, r - .004, fill=(120, 118, 112))
        for sgn in (-1, 1):
            v.d.ellipse([v.p(sgn * (r + .03) - .035, .02), v.p(sgn * (r + .03) + .035, -.02)], outline=INK, width=4)
        v.dim((-r - .065, 0), (r + .065, 0), -.32, '含耳寬')
    sheet('IronWok', [((-.36, .36), (0, .2)), ((-.36, .36), (0, .2)), ((-.36, .36), (-.3, .3))], 1000,
          lambda a, b, c: (front(a), side(b), top(c)),
          [f'球冠鍋身，壁厚 {round(t * 1000)} mm；右半剖面顯示內外壁。', '兩側環形鍋耳，鍋緣捲邊。', '另出內部俯視與底面圖。'])


def steamer():
    s = SPECS['BambooSteamer']; r = s['d'] / 2; th = s['tier_h']; n = s['tiers']; lz = n * th
    top_z = lz + s['lid_ring_h'] + s['lid_dome_h']

    def elev(v):
        for i in range(n):
            v.rect(-r, i * th, r, (i + 1) * th)
            for zz in (.015, .075):
                v.line((-r, i * th + zz), (r, i * th + zz), 2)
        v.rect(-r - .004, lz, r + .004, lz + s['lid_ring_h'], fill=(200, 180, 130))
        v.poly([(-r, lz + s['lid_ring_h'])] + [(-r * math.cos(a * math.pi / 24), lz + s['lid_ring_h'] + s['lid_dome_h'] * math.sin(a * math.pi / 24)) for a in range(25)], fill=(200, 180, 130))
        v.dim((-r, 0), (r, 0), -.05, f'Ø{round(r * 2000)}')
        v.dim((r + .02, 0), (r + .02, top_z), -.05)
        v.dim((-r - .02, 0), (-r - .02, th), .05, f'單層 {round(th * 1000)}')

    def top(v):
        v.circle(0, 0, r + .004, fill=(200, 180, 130))
        for k in range(1, 6):
            v.circle(0, 0, (r - .01) * k / 6, fill=None, width=1)
        v.rect(-.06, -.012, .06, .012, fill=CUT)
    sheet('BambooSteamer', [((-.27, .27), (0, .27)), ((-.27, .27), (0, .27)), ((-.27, .27), (-.24, .24))], 1300,
          lambda a, b, c: (elev(a), elev(b), top(c)),
          ['兩層籠身與籠蓋分件，可上下疊放與取下。', '籠底為竹條與兩根托梁；籠身外圍兩道竹篾束帶。', '另出開蓋圖與底面圖，確認籠底竹條。'])


def board():
    s = SPECS['PrepBoard']; X, Y, Z = s['size']

    def front(v):
        v.rect(-X / 2, 0, X / 2, Z); v.dim((-X / 2, 0), (X / 2, 0), -.04); v.dim((X / 2, 0), (X / 2, Z), -.04)

    def side(v):
        v.rect(-Y / 2, 0, Y / 2, Z); v.dim((-Y / 2, 0), (Y / 2, 0), -.04)

    def top(v):
        cr = s['corner_r']
        v.d.rounded_rectangle([v.p(-X / 2, Y / 2), v.p(X / 2, -Y / 2)], radius=cr * v.s, fill=FILL, outline=INK, width=3)
        v.circle(s['hole_x'], 0, s['hole_r'], fill=PAPER)
        for k in range(1, 7):
            v.line((-X / 2 + .03, -Y / 2 + k * Y / 7), (X / 2 - .06, -Y / 2 + k * Y / 7), 1)
        v.dim((-X / 2, -Y / 2), (-X / 2, Y / 2), .04)
        v.dim((s['hole_x'] - s['hole_r'], 0), (s['hole_x'] + s['hole_r'], 0), -.05, f'掛孔 Ø{round(s["hole_r"] * 2000)}')
    sheet('PrepBoard', [((-.26, .26), (0, .06)), ((-.26, .26), (0, .06)), ((-.26, .26), (-.18, .18))], 1400,
          lambda a, b, c: (front(a), side(b), top(c)),
          ['厚實木砧板，圓角 30 mm。', '右端掛孔可掛於牆釘；表面帶刀痕紋理（材質層）。'])


def bowl_like(aid, prof, outer_count, ext, scale, notes):
    r = max(p[0] for p in prof); h = max(p[1] for p in prof); foot = SPECS[aid].get('foot_d', 0) / 2

    def front(v):
        lathe_front(v, prof, outer_count)
        v.dim((-r, h), (r, h), .03, f'口徑 Ø{round(r * 2000)}')
        v.dim((r + .02, 0), (r + .02, h), -.02)
        v.dim((-foot, 0), (foot, 0), -.025, f'圈足 Ø{round(foot * 2000)}')

    def side(v):
        v.poly([(0, prof[0][1])] + [(-x, z) for x, z in prof[:outer_count]] + [(x, z) for x, z in prof[:outer_count][::-1]])

    def top(v):
        v.circle(0, 0, r); v.circle(0, 0, prof[outer_count + 1][0], fill=(226, 220, 204)); v.circle(0, 0, foot * .8, fill=None, width=1)
    sheet(aid, ext, scale, lambda a, b, c: (front(a), side(b), top(c)), notes)


def table():
    s = SPECS['DiningTable']; X, Y, Z = s['size']; t, L, ins, ah, sz = s['top_t'], s['leg'], s['leg_inset'], s['apron_h'], s['stretcher_z']

    def elev(v, span):
        v.rect(-span / 2, Z - t, span / 2, Z)
        for sgn in (-1, 1):
            c = sgn * (span / 2 - ins - L / 2)
            v.rect(c - L / 2, 0, c + L / 2, Z - t)
        v.rect(-span / 2 + ins + L, Z - t - ah, span / 2 - ins - L, Z - t)
        v.rect(-span / 2 + ins + L, sz - .02, span / 2 - ins - L, sz + .02)
        v.dim((-span / 2, Z), (span / 2, Z), .06)
        v.dim((span / 2, 0), (span / 2, Z), -.06)

    def top(v):
        for i in range(4):
            v.rect(-X / 2 + i * X / 4, -Y / 2, -X / 2 + (i + 1) * X / 4, Y / 2)
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = (sx * (X / 2 - ins - L / 2), sy * (Y / 2 - ins - L / 2))
                v.d.rectangle([v.p(c[0] - L / 2, c[1] + L / 2), v.p(c[0] + L / 2, c[1] - L / 2)], outline=DIM, width=2)
        v.dim((-X / 2, -Y / 2), (-X / 2, Y / 2), .06)
    sheet('DiningTable', [((-.6, .6), (0, .85)), ((-.6, .6), (0, .85)), ((-.6, .6), (-.55, .55))], 520,
          lambda a, b, c: (elev(a, X), elev(b, Y), top(c)),
          ['四片桌板拼接；腿 70 mm 見方，距邊 60 mm。', '牙板高 80 mm，下橫撐離地 150 mm，可坐四人。', '俯視虛框為桌腳位置。'])


def stool():
    s = SPECS['RoundStool']; H_, r = s['h'], s['seat_d'] / 2

    def elev(v):
        v.rect(-r, H_ - s['seat_t'], r, H_)
        for sgn in (-1, 1):
            v.poly([(sgn * s['leg_top'] - .018, H_ - s['seat_t']), (sgn * s['leg_top'] + .018, H_ - s['seat_t']), (sgn * s['leg_foot'] + .018, 0), (sgn * s['leg_foot'] - .018, 0)])
        rz = s['leg_top'] + (s['leg_foot'] - s['leg_top']) * (H_ - s['seat_t'] - s['ring_z']) / (H_ - s['seat_t'])
        v.rect(-rz, s['ring_z'] - .011, rz, s['ring_z'] + .011, fill=CUT)
        v.dim((-r, H_), (r, H_), .04, f'Ø{round(r * 2000)}')
        v.dim((r + .03, 0), (r + .03, H_), -.04)
        v.dim((-s['leg_foot'] - .018, 0), (s['leg_foot'] + .018, 0), -.04, '腳距')

    def top(v):
        v.circle(0, 0, r)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            v.circle(s['leg_foot'] * math.cos(a), s['leg_foot'] * math.sin(a), .02, fill=None, width=2)
    sheet('RoundStool', [((-.25, .25), (0, .5)), ((-.25, .25), (0, .5)), ((-.25, .25), (-.2, .2))], 850,
          lambda a, b, c: (elev(a), elev(b), top(c)),
          ['四腳外撇，斜置於 45° 方向；圓環橫撐離地 140 mm。', '座高 450 mm，搭配 750 mm 方桌。'])


hearth(); wok(); steamer(); board()
bowl_like('CeramicBowl', BOWL_PROFILE, 9, [((-.11, .11), (0, .09)), ((-.11, .11), (0, .09)), ((-.11, .11), (-.1, .1))], 2600,
          ['右半剖面：內外壁分開建模，壁厚約 4–6 mm。', '空碗為基底，之後加入米飯、湯麵等料理變體。'])
bowl_like('CeramicPlate', PLATE_PROFILE, 7, [((-.15, .15), (0, .05)), ((-.15, .15), (0, .05)), ((-.15, .15), (-.14, .14))], 2000,
          ['淺盤，盤心平坦可擺放料理成品。', '與粗陶碗共用釉色。'])
table(); stool()
