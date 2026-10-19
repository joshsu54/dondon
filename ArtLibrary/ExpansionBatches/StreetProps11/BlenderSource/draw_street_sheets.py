"""Design sheets for StreetProps11, drawn from street_specs.py before modelling.
Run: python3 draw_street_sheets.py  -> ../DesignSheets/<Asset>_design.png
"""
import math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from street_specs import NAMES, DETAILS, SPECS
from sheet_kit import *

OUT = HERE.parent / 'DesignSheets'
T = '街道道具 11'


def go(aid, ext, fn, notes): sheet(OUT, T, aid, NAMES[aid], DETAILS[aid], ext, fn, notes)


def well():
    s = SPECS['StoneWell']; R, r, h, ar = s['outer_r'], s['inner_r'], s['wall_h'], s['apron_r']; px, ph = s['post_x'], s['post_h']; rf = s['roof']

    def elev(v, half):
        v.rect(-ar, 0, ar, s['apron_h'], STONE)
        v.rect(-R, s['apron_h'], R, h, STONE); v.rect(-R - .02, h, R + .02, h + .06, STONE)
        for k in range(1, 5): v.line((-R, s['apron_h'] + k * (h - s['apron_h']) / 5), (R, s['apron_h'] + k * (h - s['apron_h']) / 5), 1)
        for x in (-px, px): v.rect(x - .05, 0, x + .05, ph, WOOD)
        if half == 'x':
            v.rect(-px, s['roller_z'] - .07, px, s['roller_z'] + .07, WOOD); v.line((px, s['roller_z']), (px + .25, s['roller_z'] - .1), 4)
            v.line((0, s['roller_z']), (0, 1.0), 2, ROPE); v.rect(-.16, .85, .16, 1.0, WOOD)
            v.poly([(-rf['half_x'], rf['eave_z']), (rf['half_x'], rf['eave_z']), (rf['half_x'], rf['ridge_z']), (-rf['half_x'], rf['ridge_z'])], TILE)
        else:
            v.poly([(-rf['half_y'], rf['eave_z']), (0, rf['ridge_z']), (rf['half_y'], rf['eave_z'])], TILE)
            v.circle(0, s['roller_z'], .07, WOOD)
        v.dim((-ar, 0), (ar, 0), -.15, f'台座 Ø{round(ar * 2000)}')
        v.dim((rf['half_x'] + .15, 0), (rf['half_x'] + .15, rf['ridge_z']), -.1)
        v.dim((-R, h + .1), (R, h + .1), .12, f'井口 Ø{round(R * 2000)}')

    def top(v):
        v.circle(0, 0, ar, STONE); v.circle(0, 0, R + .02, STONE); v.circle(0, 0, r, WATER)
        v.rect(-rf['half_x'], -rf['half_y'], rf['half_x'], rf['half_y'], None); v.line((-rf['half_x'], 0), (rf['half_x'], 0), 2)
        v.dim((-r, 0), (r, 0), -.25, f'內徑 Ø{round(r * 2000)}')
    go('StoneWell', [((-1.2, 1.3), (0, 2.6)), ((-1.2, 1.3), (0, 2.6)), ((-1.2, 1.2), (-1, 1))], lambda a, b, c: (elev(a, 'x'), elev(b, 'y'), top(c)),
       ['井欄高 750 mm，供角色倚靠取水；轆轤在 X 方向，搖把在右側。', '屋頂為兩坡小瓦頂，柱子立在台座外側，不擋取水動作。'])


def bucket():
    s = SPECS['WellBucket']; prof = [(0, .012), (s['bottom_r'] - s['wall'], .012), (s['bottom_r'], 0), (s['top_r'], s['h']), (s['top_r'] - s['wall'], s['h']), (s['bottom_r'] - s['wall'] * 1.6, .03), (0, .03)]

    def front(v):
        lathe_front(v, prof, 4, WOOD)
        for z in (.06, .24): v.line((-s['bottom_r'] - (s['top_r'] - s['bottom_r']) * z / s['h'], z), (0, z), 4, INK)
        v.line((-s['top_r'], s['h']), (0, s['h'] + .16), 2, ROPE); v.line((0, s['h'] + .16), (s['top_r'], s['h']), 2, ROPE)
        v.dim((-s['top_r'], s['h']), (s['top_r'], s['h']), .05, f'口徑 Ø{round(s["top_r"] * 2000)}'); v.dim((s['top_r'] + .04, 0), (s['top_r'] + .04, s['h']), -.03)

    def side(v): v.poly([(-s['bottom_r'], 0), (s['bottom_r'], 0), (s['top_r'], s['h']), (-s['top_r'], s['h'])], WOOD)

    def top(v):
        v.circle(0, 0, s['top_r'], WOOD); v.circle(0, 0, s['top_r'] - s['wall'], FILL)
        for k in range(s['staves']): a = k * math.tau / s['staves']; v.line((math.cos(a) * (s['top_r'] - s['wall']), math.sin(a) * (s['top_r'] - s['wall'])), (math.cos(a) * s['top_r'], math.sin(a) * s['top_r']), 1)
    go('WellBucket', [((-.25, .25), (0, .5)), ((-.25, .25), (0, .5)), ((-.25, .25), (-.2, .2))], lambda a, b, c: (front(a), side(b), top(c)),
       [f'{s["staves"]} 片木板拼成，上下兩道鐵箍；繩提把可與石井共用。', '右半剖面顯示內外壁與桶底。'])


def board():
    s = SPECS['NoticeBoard']; bw, bt, bh = s['board']; px, ph, p = s['post_x'], s['post_h'], s['post']; z0 = s['board_z']

    def front(v):
        for x in (-px, px): v.rect(x - .12, 0, x + .12, .2, STONE); v.rect(x - p / 2, 0, x + p / 2, ph, WOOD)
        v.rect(-bw / 2, z0, bw / 2, z0 + bh, WOOD); v.rect(-bw / 2 - .05, z0 - .1, bw / 2 + .05, z0 - .04, WOOD)
        for (x, z, w, h) in [(-.48, 1.25, .36, .48), (-.02, 1.38, .3, .4), (.42, 1.2, .38, .52), (.0, 1.02, .5, .28)]: v.rect(x - w / 2, z, x + w / 2, z + h, PAPERY)
        v.poly([(-s['roof_w'] / 2, ph), (s['roof_w'] / 2, ph), (s['roof_w'] / 2, ph + s['roof_rise']), (-s['roof_w'] / 2, ph + s['roof_rise'])], TILE)
        v.dim((-bw / 2, z0), (bw / 2, z0), .5, f'板面 {round(bw * 1000)}'); v.dim((px + .2, 0), (px + .2, ph + s['roof_rise']), -.15)
        v.dim((-px - .25, z0), (-px - .25, z0 + bh), .1, f'{round(bh * 1000)}')

    def side(v):
        v.rect(-.12, 0, .12, .2, STONE); v.rect(-p / 2, 0, p / 2, ph, WOOD); v.rect(-bt / 2 - .03, z0, bt / 2, z0 + bh, WOOD)
        v.poly([(-s['roof_d'] / 2, ph), (0, ph + s['roof_rise']), (s['roof_d'] / 2, ph)], TILE)
        v.dim((-s['roof_d'] / 2, ph + s['roof_rise'] + .05), (s['roof_d'] / 2, ph + s['roof_rise'] + .05), .1)

    def top(v):
        v.rect(-s['roof_w'] / 2, -s['roof_d'] / 2, s['roof_w'] / 2, s['roof_d'] / 2, TILE); v.line((-s['roof_w'] / 2, 0), (s['roof_w'] / 2, 0))
        v.dim((-s['roof_w'] / 2, -s['roof_d'] / 2), (s['roof_w'] / 2, -s['roof_d'] / 2), -.12)
    go('NoticeBoard', [((-1.2, 1.2), (0, 2.6)), ((-1.2, 1.2), (0, 2.6)), ((-1.2, 1.2), (-.6, .6))], lambda a, b, c: (front(a), side(b), top(c)),
       ['告示紙為空白，不放可讀文字；可替換成任務告示貼圖。', '板面中心高約 1.45 m，角色站立即可閱讀。'])


def crate():
    s = SPECS['WoodenCrate']; X, Y, Z = s['size']

    def elev(v, a):
        for i in range(3): v.rect(-a / 2, i * Z / 3 + .006, a / 2, (i + 1) * Z / 3 - .006, WOOD)
        for x in (-a / 2, a / 2 - .05): v.rect(x, 0, x + .05, Z, CUT)
        v.rect(-a / 2 - .01, Z, a / 2 + .01, Z + s['lid_t'], WOOD)
        v.dim((-a / 2, 0), (a / 2, 0), -.06); v.dim((a / 2 + .04, 0), (a / 2 + .04, Z + s['lid_t']), -.04)

    def top(v):
        for i in range(4): v.rect(-X / 2, -Y / 2 + i * Y / 4 + .005, X / 2, -Y / 2 + (i + 1) * Y / 4 - .005, WOOD)
        for x in (-X / 2 + .08, X / 2 - .08): v.rect(x - .03, -Y / 2, x + .03, Y / 2, CUT)
    go('WoodenCrate', [((-.45, .45), (0, .6)), ((-.45, .45), (0, .6)), ((-.45, .45), (-.3, .3))], lambda a, b, c: (elev(a, X), elev(b, Y), top(c)),
       ['側板三片、角柱補強；箱蓋為獨立物件，可移開放入貨物。', '尺寸可堆疊兩層，與材料袋、竹簍一起擺放。'])


def basket():
    s = SPECS['BambooBasket']; t = s['wall']
    prof = [(0, .03), (s['bottom_r'], .03), (s['top_r'], s['h']), (s['top_r'] - t, s['h']), (s['bottom_r'] - t, .03 + t), (0, .03 + t)]

    def front(v):
        lathe_front(v, prof, 3, (200, 170, 110))
        for k in range(1, 10):
            z = .03 + k * (s['h'] - .03) / 10; r = s['bottom_r'] + (s['top_r'] - s['bottom_r']) * (z - .03) / (s['h'] - .03); v.line((-r, z), (0, z), 1)
        v.rect(-s['bottom_r'], 0, s['bottom_r'], .03, WOOD)
        v.dim((-s['top_r'], s['h']), (s['top_r'], s['h']), .05, f'口徑 Ø{round(s["top_r"] * 2000)}'); v.dim((s['top_r'] + .05, 0), (s['top_r'] + .05, s['h']), -.03)

    def side(v):
        v.poly([(-s['bottom_r'], .03), (s['bottom_r'], .03), (s['top_r'], s['h']), (-s['top_r'], s['h'])], (200, 170, 110)); v.rect(-s['bottom_r'], 0, s['bottom_r'], .03, WOOD)
        v.line((s['top_r'] - .01, s['h'] - .05), (s['bottom_r'] + .06, .15), 5, ROPE); v.d.text(v.p(s['top_r'] + .02, .3), '背帶', fill=DIM, font=font(20))

    def top(v):
        v.circle(0, 0, s['top_r'], (200, 170, 110)); v.circle(0, 0, s['top_r'] - t, FILL)
        for k in range(s['ribs']): a = k * math.tau / s['ribs']; v.circle(math.cos(a) * (s['top_r'] - t / 2), math.sin(a) * (s['top_r'] - t / 2), .006, WOOD, 1)
    go('BambooBasket', [((-.3, .3), (0, .65)), ((-.3, .3), (0, .65)), ((-.3, .3), (-.25, .25))], lambda a, b, c: (front(a), side(b), top(c)),
       [f'{s["ribs"]} 根直向竹骨加橫向編圈；方形木底框防潮。', '兩條背帶在背面 (+Y)，可背在角色身上或放地上當貨簍。'])


def wood():
    s = SPECS['FirewoodStack']; L, D = s['length'], s['depth']; lo, hi = s['cap_z']

    def front(v):
        for x in (-L / 2 - .05, L / 2 + .05): v.rect(x - .05, 0, x + .05, s['post_h'], WOOD)
        rr = (s['log_r'][0] + s['log_r'][1]) / 2
        for row in range(s['rows']):
            n = int(L / (2 * rr)); off = rr if row % 2 else 0
            for i in range(n - (row % 2)): v.circle(-L / 2 + rr + off + i * 2 * rr, .1 + rr + row * rr * 1.75, rr * .95, (190, 150, 100), 1)
        v.poly([(-L / 2 - .15, lo), (L / 2 + .15, lo), (L / 2 + .15, lo + .05), (-L / 2 - .15, lo + .05)], WOOD)
        v.dim((-L / 2, 0), (L / 2, 0), -.12); v.dim((L / 2 + .25, 0), (L / 2 + .25, hi + .04), -.1)

    def side(v):
        v.rect(-D / 2 - .05, .02, D / 2 + .05, .1, WOOD); v.rect(-D / 2, .1, D / 2, .1 + s['rows'] * .065 * 1.75, (190, 150, 100))
        v.poly([(-D / 2 - .12, lo), (D / 2 + .12, hi), (D / 2 + .12, hi + .04), (-D / 2 - .12, lo + .04)], WOOD); v.dim((-D / 2, 0), (D / 2, 0), -.08)

    def top(v):
        v.rect(-L / 2 - .15, -D / 2 - .12, L / 2 + .15, D / 2 + .12, WOOD); v.dim((-L / 2 - .15, -D / 2 - .12), (L / 2 + .15, -D / 2 - .12), -.1)
    go('FirewoodStack', [((-1.0, 1.1), (0, 1.4)), ((-1.0, 1.1), (0, 1.4)), ((-1.0, 1.0), (-.5, .5))], lambda a, b, c: (front(a), side(b), top(c)),
       [f'{s["rows"]} 層交錯堆疊的劈柴，兩端立柱擋住；前低後高的木板遮雨。', '放在食肆後門與廚房旁，也可用在民宅或鐵匠鋪。'])


well(); bucket(); board(); crate(); basket(); wood()
