"""Design sheets for FreshIngredients13 from fresh_specs.py.
Run: python3 draw_fresh_sheets.py  -> ../DesignSheets/<Item>_design.png
"""
import math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fresh_specs import *
from sheet_kit import *

OUT = HERE.parent / 'DesignSheets'
SACK, RICE, MEAT, FATC, RADISH, CARROT, LEAF, EGGC, FISHC, BASKETC = (190, 165, 120), (240, 236, 222), (130, 50, 35), (235, 210, 180), (245, 242, 230), (230, 120, 40), (90, 140, 60), (235, 215, 180), (150, 150, 140), (200, 170, 110)


def go(aid, ext, front, side, top, notes): sheet(OUT, '生鮮食材 13', aid, NAMES[aid], DETAILS[aid], ext, lambda a, b, c: (front(a), side(b), top(c)), notes)


def basket_front(v, sx, sz):
    b = BASKET; v.poly([(-b['bottom_r'] * sx, .03 * sz), (b['bottom_r'] * sx, .03 * sz), (b['top_r'] * sx, b['h'] * sz), (-b['top_r'] * sx, b['h'] * sz)], BASKETC)
    v.rect(-b['bottom_r'] * sx, 0, b['bottom_r'] * sx, .03 * sz, WOOD)


def sack():
    s = SPECS['RiceSack']
    prof = [(s['base_r'] * .85, 0), (s['base_r'], .03), (s['belly_r'], s['h'] * .45), (s['neck_r'], s['h'] * .9), (s['cuff_r'], s['h'])]
    def front(v):
        v.poly([(-r, z) for r, z in prof] + [(r, z) for r, z in prof[::-1]], SACK)
        v.poly([(-s['cuff_r'] + .01, s['h'])] + [(-(s['cuff_r'] - .01) * math.cos(a), s['h'] + (s['rice_top'] - s['h']) * math.sin(a)) for a in [i * math.pi / 12 for i in range(13)]], RICE)
        v.rect(-s['cuff_r'] - .02, s['h'] - .05, s['cuff_r'] + .02, s['h'], SACK)
        v.line((.05, s['rice_top'] - .01), (.15, s['rice_top'] + .12), 5, WOOD)
        v.dim((-s['belly_r'], 0), (s['belly_r'], 0), -.05, f'Ø{round(s["belly_r"] * 2000)}'); v.dim((s['belly_r'] + .05, 0), (s['belly_r'] + .05, s['rice_top']), -.04)
    def top(v): v.circle(0, 0, s['belly_r'], SACK); v.circle(0, 0, s['cuff_r'] + .02, SACK); v.circle(0, 0, s['cuff_r'] - .01, RICE)
    go('RiceSack', [((-.3, .3), (0, .8)), ((-.3, .3), (0, .8)), ((-.3, .3), (-.3, .3))], front, front, top,
       ['麻袋側面加隨機皺褶；袋口反折一圈，露出米面。', '木米勺斜插在米中。'])


def rack():
    s = SPECS['CuredMeatRack']; W, D, H = s['width'], s['depth'], s['h']
    def front(v):
        for x in (-W / 2, W / 2): v.rect(x - .03, 0, x + .03, H, WOOD)
        v.rect(-W / 2, s['bar_z'] - .02, W / 2, s['bar_z'] + .02, WOOD)
        for i in range(s['strips']): x = -.3 + i * .14; v.line((x, s['bar_z']), (x, s['bar_z'] - .08), 1); v.rect(x - .03, s['bar_z'] - .34, x + .03, s['bar_z'] - .08, MEAT)
        for i in range(s['sausage_strings']):
            x = .28 + i * .06
            for k in range(4): v.circle(x, s['bar_z'] - .08 - k * .07, .015, MEAT)
        v.dim((-W / 2, 0), (W / 2, 0), -.06); v.dim((W / 2 + .1, 0), (W / 2 + .1, H), -.05)
    def side(v):
        v.poly([(-D / 2, 0), (-D / 2 + .05, 0), (0, H), (-.03, H)], WOOD); v.poly([(D / 2, 0), (D / 2 - .05, 0), (0, H), (.03, H)], WOOD)
        v.rect(-.02, s['bar_z'] - .34, .02, s['bar_z'] - .08, MEAT); v.dim((-D / 2, 0), (D / 2, 0), -.06)
    def top(v): v.rect(-W / 2, -D / 2, W / 2, D / 2, None); v.rect(-W / 2, -.02, W / 2, .02, WOOD)
    go('CuredMeatRack', [((-.6, .6), (0, 1.05)), ((-.6, .6), (0, 1.05)), ((-.6, .6), (-.3, .3))], front, side, top,
       [f'{s["strips"]} 條臘肉（瘦肉帶肥邊）＋ {s["sausage_strings"]} 串臘腸，以麻繩吊在橫桿上。', '兩側 A 字腳架，可放在廚房或屋簷下。'])


def crate():
    s = SPECS['RadishCrate']; X, Y = .6, .45
    def front(v):
        v.rect(-X / 2, 0, X / 2, .45, WOOD)
        for i in range(5): v.poly([(-.25 + i * .12, .4), (-.25 + i * .12 + .03, .58), (-.25 + i * .12 + .06, .4)], LEAF)
        v.dim((-X / 2, 0), (X / 2, 0), -.05)
    def top(v):
        v.rect(-X / 2, -Y / 2, X / 2, Y / 2, WOOD); v.rect(-.26, -.185, .26, .185, FILL)
        for i in range(s['radishes']): y = -.15 + (i % 5) * .075; v.rect(-.2 + (i // 5) * .2, y - .03, .1 + (i // 5) * .1, y + .03, RADISH)
    go('RadishCrate', [((-.4, .4), (0, .7)), ((-.4, .4), (0, .7)), ((-.4, .4), (-.3, .3))], front, front, top,
       ['沿用街道道具 11 的木箱，不帶箱蓋。', f'{s["radishes"]} 根白蘿蔔斜放兩排、葉子朝上露出箱口，上面加 {s["carrots"]} 根紅蘿蔔。'])


def vbasket():
    sx, sz = CONTAINERS['VegetableBasket'][1][0], CONTAINERS['VegetableBasket'][1][2]; tr = BASKET['top_r'] * sx; h = BASKET['h'] * sz
    def front(v):
        basket_front(v, sx, sz)
        v.poly([(-.18, h - .03), (-.16, h + .1), (0, h + .12), (.02, h - .03)], (200, 225, 170)); v.poly([(0, h - .03), (.03, h + .09), (.17, h + .08), (.18, h - .03)], (200, 225, 170))
        v.dim((-tr, h + .02), (tr, h + .02), .2, f'籃口 Ø{round(tr * 2000)}'); v.dim((tr + .04, 0), (tr + .04, h), -.04)
    def top(v):
        v.circle(0, 0, tr, BASKETC); v.d.ellipse([v.p(-.18, .1), v.p(.02, -.05)], fill=(200, 225, 170), outline=INK); v.d.ellipse([v.p(-.02, .08), v.p(.18, -.06)], fill=(200, 225, 170), outline=INK)
        for i in range(4): v.line((-.1 + i * .05, -.12), (-.02 + i * .05, -.02), 5, CARROT)
    go('VegetableBasket', [((-.3, .3), (0, .4)), ((-.3, .3), (0, .4)), ((-.3, .3), (-.25, .25))], front, front, top,
       ['竹簍壓低成淺籃（高 0.4 倍），去掉背帶。', '兩顆大白菜、紅蘿蔔與一束青蔥。'])


def ebasket():
    sx, sz = CONTAINERS['EggBasket'][1][0], CONTAINERS['EggBasket'][1][2]; tr = BASKET['top_r'] * sx; h = BASKET['h'] * sz; ex, ez = SPECS['EggBasket']['egg']
    def front(v):
        basket_front(v, sx, sz)
        for i, (x, z) in enumerate([(-.06, h - .01), (-.02, h), (.03, h + .005), (.07, h - .01), (0, h + .035), (-.04, h + .03), (.04, h + .03)]):
            v.d.ellipse([v.p(x - ex, z + ez), v.p(x + ex, z - ez)], fill=EGGC, outline=INK)
        v.dim((-tr, h), (tr, h), .1, f'籃口 Ø{round(tr * 2000)}')
    def top(v):
        v.circle(0, 0, tr, BASKETC)
        for i in range(SPECS['EggBasket']['eggs']): a = i * 2.4; r = .02 + .0065 * i; v.d.ellipse([v.p(r * math.cos(a) - ex, r * math.sin(a) + ez), v.p(r * math.cos(a) + ex, r * math.sin(a) - ez)], fill=EGGC, outline=INK)
    go('EggBasket', [((-.2, .2), (0, .25)), ((-.2, .2), (0, .25)), ((-.2, .2), (-.16, .16))], front, front, top,
       ['竹簍縮小成小淺籃，籃底鋪乾草。', f'{SPECS["EggBasket"]["eggs"]} 顆蛋堆成小丘。'])


def tub():
    sx, sz = CONTAINERS['FishTub'][1][0], CONTAINERS['FishTub'][1][2]; b = BUCKET; s = SPECS['FishTub']
    def front(v):
        v.poly([(-.135 * sx, 0), (.135 * sx, 0), (.16 * sx, b['h'] * sz), (-.16 * sx, b['h'] * sz)], WOOD)
        v.rect(-.14 * sx, s['water_z'] - .004, .14 * sx, s['water_z'], WATER)
        v.dim((-.16 * sx, b['h'] * sz), (.16 * sx, b['h'] * sz), .05, f'盆口 Ø{round(.32 * sx * 1000)}'); v.dim((.16 * sx + .04, 0), (.16 * sx + .04, b['h'] * sz), -.04)
    def top(v):
        v.circle(0, 0, .16 * sx, WOOD); v.circle(0, 0, b['top_r'] * sx, WATER)
        for i in range(s['fish']): a = i * math.tau / 3; v.d.ellipse([v.p(.1 * math.cos(a) - .07, .1 * math.sin(a) + .02), v.p(.1 * math.cos(a) + .07, .1 * math.sin(a) - .02)], fill=FISHC, outline=INK)
    go('FishTub', [((-.35, .35), (0, .3)), ((-.35, .35), (0, .3)), ((-.35, .35), (-.3, .3))], front, front, top,
       ['木水桶放寬 1.7 倍、壓低成淺木盆，去掉提把。', f'{s["fish"]} 條鮮魚在水中，魚長約 {round(s["fish_len"] * 1000)} mm。'])


sack(); rack(); crate(); vbasket(); ebasket(); tub()
