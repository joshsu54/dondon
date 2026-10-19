"""Design sheets for FoodDishes12 from food_specs.py: container half-section with the food on top.
Run: python3 draw_food_sheets.py  -> ../DesignSheets/<Dish>_design.png
"""
import math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from food_specs import *
from sheet_kit import *

OUT = HERE.parent / 'DesignSheets'
RICE, BROTH, NOODLE, MEAT, GREEN, BUN, FISH, SAUCE, EGG = (240, 236, 222), (200, 150, 80), (236, 210, 140), (130, 60, 40), (90, 140, 60), (245, 238, 220), (215, 205, 185), (120, 70, 35), (250, 220, 120)
BOWL = [(0, .006), (.030, .006), (.031, 0), (.038, 0), (.040, .010), (.052, .022), (.066, .040), (.076, .058), (.080, .070), (.0795, .0725)] + BOWL_INNER
PLATE = [(0, .004), (.050, .004), (.052, 0), (.060, 0), (.062, .007), (.100, .018), (.120, .028), (.1200, .0305)] + PLATE_INNER


def scaled(prof, sx, sz): return [(r * sx, z * sz) for r, z in prof]


def inner_r(inner, z):
    for (r0, z0), (r1, z1) in zip(inner, inner[1:]):
        if z1 <= z <= z0: return r1 + (r0 - r1) * (z - z1) / (z0 - z1)
    return inner[0][0]


def go(aid, ext, front, top, notes):
    sheet(OUT, '料理成品 12', aid, NAMES[aid], DETAILS[aid], ext, lambda a, b, c: (front(a), front(b), top(c)), notes)


def bowl_dish(aid, sx, sz, food_front, food_top, notes, ext):
    prof = scaled(BOWL, sx, sz); n = 10
    def front(v):
        lathe_front(v, prof, n, (200, 190, 170)); food_front(v)
        v.dim((-.08 * sx, .0725 * sz), (.08 * sx, .0725 * sz), .03, f'碗口 Ø{round(160 * sx)}')
    def top(v):
        v.circle(0, 0, .08 * sx, (200, 190, 170)); food_top(v)
    go(aid, ext, front, top, notes)


def rice():
    s = SPECS['RiceBowl']; r0 = inner_r(BOWL_INNER, s['mound_base_z'])
    bowl_dish('RiceBowl', 1, 1, lambda v: v.poly([(-r0, s['mound_base_z'])] + [(-r0 * math.cos(a), s['mound_base_z'] + (s['mound_top'] - s['mound_base_z']) * math.sin(a)) for a in [i * math.pi / 16 for i in range(17)]], RICE),
              lambda v: v.circle(0, 0, r0, RICE), [f'飯面高出碗口約 {round((s["mound_top"] - .0725) * 1000)} mm，呈圓丘。', '米粒以材質凹凸表現，不逐粒建模。'],
              [((-.12, .12), (0, .11)), ((-.12, .12), (0, .11)), ((-.12, .12), (-.1, .1))])


def noodle():
    s = SPECS['NoodleSoup']; sx, sz = 1.35, 1.25; rb = inner_r(BOWL_INNER, s['broth_z'] / sz) * sx
    def ff(v):
        v.rect(-rb, s['broth_z'] - .002, rb, s['broth_z'], BROTH)
        for i in range(5): v.circle(-rb * .6 + i * rb * .3, s['broth_z'] + .004, .006, NOODLE, 1)
        v.circle(rb * .35, s['broth_z'] + .008, s['egg_r'], EGG); v.rect(-rb * .5, s['broth_z'], -rb * .1, s['broth_z'] + .01, MEAT)
        v.line((-.13, .095), (.12, .088), 4, (110, 70, 40))
    def ft(v):
        v.circle(0, 0, rb, BROTH)
        for k in range(6): a = k * math.tau / 6; v.circle(.035 * math.cos(a), .035 * math.sin(a), .02, None, 1)
        v.circle(.04, -.03, s['egg_r'], EGG); v.rect(-.06, .01, -.02, .05, MEAT); v.line((-.13, .05), (.12, .07), 4, (110, 70, 40))
    bowl_dish('NoodleSoup', sx, sz, ff, ft, ['大碗：沿用粗陶碗放大 1.35 倍（高 1.25 倍）。', '湯面、捲麵、叉燒兩片、半顆蛋、青菜、蔥花，筷子架在碗口。'],
              [((-.16, .16), (0, .12)), ((-.16, .16), (0, .12)), ((-.16, .16), (-.13, .13))])


def buns():
    s = SPECS['SteamedBuns']; r, h = s['bun_r'], s['bun_h']
    def bun_front(v, x):
        v.poly([(x - r, STEAMER_FLOOR_Z)] + [(x - r * math.cos(a), STEAMER_FLOOR_Z + h * math.sin(a) ** .8) for a in [i * math.pi / 16 for i in range(17)]], BUN)
    def front(v):
        v.rect(-.2, 0, .2, .09, (200, 170, 110)); v.rect(-.188, .012, .188, .088, (236, 228, 205))
        for x in (-s['ring_r'], 0, s['ring_r']): bun_front(v, x)
        v.dim((-.2, .09), (.2, .09), .03, '蒸籠 Ø400'); v.dim((.22, STEAMER_FLOOR_Z), (.22, STEAMER_FLOOR_Z + h), -.03, f'包子高 {round(h * 1000)}')
    def top(v):
        v.circle(0, 0, .2, (200, 170, 110)); v.circle(0, 0, .188, (236, 228, 205)); v.circle(0, 0, r, BUN)
        for k in range(6): a = k * math.tau / 6 + .3; v.circle(s['ring_r'] * math.cos(a), s['ring_r'] * math.sin(a), r, BUN)
    go('SteamedBuns', [((-.26, .26), (0, .12)), ((-.26, .26), (0, .12)), ((-.26, .26), (-.23, .23))], front, top,
       ['只沿用蒸籠下層，蓋子與上層不帶入。', f'{s["count"]} 顆包子：中間 1 顆、外圈 6 顆，頂部有摺紋。'])


def fish():
    s = SPECS['SteamedFish']; L, Hh, Wd = s['length'], s['height'], s['width']
    def front(v):
        lathe_front(v, scaled(PLATE, 1.6, 1), 8, (200, 190, 170))
        v.poly([(-L / 2 + .05, .02)] + [(-L / 2 + .05 + (L - .11) * t, .02 + Hh * math.sin(math.pi * t) ** .7) for t in [i / 16 for i in range(17)]] + [(L / 2 - .06, .02)], FISH)
        v.poly([(L / 2 - .06, .03), (L / 2, .06), (L / 2, .0)], FISH); v.dim((-L / 2, .09), (L / 2, .09), .02, f'魚長 {round(L * 1000)}')
    def top(v):
        v.d.ellipse([v.p(-.192, .126), v.p(.192, -.126)], fill=(200, 190, 170), outline=INK, width=2)
        v.d.ellipse([v.p(-s['sauce_r'][0], s['sauce_r'][1]), v.p(s['sauce_r'][0], -s['sauce_r'][1])], fill=SAUCE, outline=INK, width=1)
        v.d.ellipse([v.p(-L / 2 + .05, Wd / 2), v.p(L / 2 - .06, -Wd / 2)], fill=FISH, outline=INK, width=2)
        v.poly([(L / 2 - .07, 0), (L / 2, .04), (L / 2, -.04)], FISH)
        for i in range(6): v.line((-.08 + i * .03, -.02), (-.06 + i * .03, .025), 2, GREEN)
    go('SteamedFish', [((-.22, .22), (0, .1)), ((-.22, .22), (0, .1)), ((-.22, .22), (-.15, .15))], front, top,
       ['魚盤：粗陶盤拉長為 384 × 252 mm 的橢圓盤。', '淺色醬汁鋪底，魚身上放蔥絲與薑絲；頭朝 -X、尾朝 +X。'])


def greens():
    s = SPECS['StirFryGreens']
    def front(v):
        lathe_front(v, PLATE, 8, (200, 190, 170))
        v.poly([(-.09, .012)] + [(-.09 * math.cos(a), .012 + s['heap_h'] * math.sin(a)) for a in [i * math.pi / 16 for i in range(17)]], GREEN)
        v.dim((.13, .012), (.13, .012 + s['heap_h']), -.02, f'堆高 {round(s["heap_h"] * 1000)}')
    def top(v):
        v.circle(0, 0, .12, (200, 190, 170))
        for k in range(s['leaves']): a = k * math.tau / s['leaves']; v.d.ellipse([v.p(.05 * math.cos(a) - .03, .05 * math.sin(a) + .02), v.p(.05 * math.cos(a) + .03, .05 * math.sin(a) - .02)], fill=GREEN, outline=INK)
    go('StirFryGreens', [((-.16, .16), (0, .1)), ((-.16, .16), (0, .1)), ((-.16, .16), (-.14, .14))], front, top,
       [f'{s["leaves"]} 片青江菜葉與淺綠菜梗，中間堆高，加少量蒜末。'])


def pork():
    s = SPECS['BraisedPork']; c = s['cube']; rs = inner_r(BOWL_INNER, s['sauce_z'])
    def ff(v):
        v.rect(-rs, s['sauce_z'] - .002, rs, s['sauce_z'], SAUCE)
        for x, z in [(-.035, s['sauce_z']), (0, s['sauce_z']), (.035, s['sauce_z']), (-.017, s['sauce_z'] + c), (.017, s['sauce_z'] + c)]: v.rect(x - c / 2, z - .01, x + c / 2, z + c - .01, MEAT)
    def ft(v):
        v.circle(0, 0, rs, SAUCE)
        for k in range(6): a = k * math.tau / 6; v.rect(.035 * math.cos(a) - c / 2, .035 * math.sin(a) - c / 2, .035 * math.cos(a) + c / 2, .035 * math.sin(a) + c / 2, MEAT)
    bowl_dish('BraisedPork', 1, 1, ff, ft, [f'{s["count"]} 塊 {round(c * 1000)} mm 五花肉塊，兩層堆疊，帶肥瘦分層。', '醬汁面在碗內，表面加蔥段。'],
              [((-.12, .12), (0, .11)), ((-.12, .12), (0, .11)), ((-.12, .12), (-.1, .1))])


rice(); noodle(); buns(); fish(); greens(); pork()
