"""TownKitchen10 design specs: cooking props, tableware, ingredients, sacks, fence corner.

Same conventions and pipeline as town09_shapes (metres, Z up, front -Y,
bottom-centre origin). Run with TL_SPEC=town10_shapes.
"""
import math

import numpy as np

from town09_shapes import (VIEWS, VIEW_PHRASE, Asset, beam, box, cyl, lathe, merge, rod,  # noqa: F401
                           tube)
import town09_shapes as T9

PALETTE = dict(T9.PALETTE, **{
    'brick':     ((.30, .11, .06), (150, 84, 64)),
    'porcelain': ((.62, .68, .66), (206, 214, 210)),
    'rice':      ((.80, .78, .70), (232, 228, 214)),
    'greens':    ((.10, .28, .05), (82, 140, 58)),
    'cabbage':   ((.36, .52, .20), (164, 190, 120)),
    'carrot':    ((.62, .17, .03), (206, 110, 40)),
    'radish':    ((.78, .78, .72), (228, 228, 218)),
    'fish':      ((.32, .36, .38), (152, 160, 164)),
    'burlap':    ((.40, .29, .15), (172, 146, 104)),
    'broth':     ((.45, .28, .09), (180, 138, 80)),
    'bun':       ((.82, .76, .62), (234, 224, 200)),
})


# ------------------------------------------------------------- helpers
def xf(geo, scale=(1, 1, 1), rot=(0, 0, 0), t=(0, 0, 0)):
    """Scale, rotate (x, y, z radians, applied in that order) and translate a geometry."""
    v, f = geo
    v = np.asarray(v, float) * scale
    rx, ry, rz = rot
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return v @ (Rz @ Ry @ Rx).T + t, f


def sphere(r=1.0, n=16, rings=8):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe((0, 0, 0), prof, n)


def bowl(c, r, h, th=.008, n=24, foot=.35):
    """Open bowl/plate shell standing on a foot ring; r = rim radius, h = height."""
    rf = r * foot
    outer = [(rf, 0), (rf, h * .12)] + [(rf + (r - rf) * math.sin(math.pi / 2 * k / 6), h * .12 + (h * .88) * (1 - math.cos(math.pi / 2 * k / 6)))
                                         for k in range(1, 7)]
    inner = [(x - th, z + (th if i < len(outer) - 1 else 0)) for i, (x, z) in enumerate(outer)][::-1]
    prof = [(0, 0)] + outer + inner[:-2] + [(0, h * .12 + th)]
    return lathe(c, prof, n)


# ------------------------------------------------------------- assets
def cooking_wok():
    A = Asset()
    R, rim = .5, .36
    a_max = math.asin(rim / R)
    outer = [(R * math.sin(a_max * k / 10), R * (1 - math.cos(a_max * k / 10))) for k in range(11)]
    inner = [(max(r - .012, 0), z + .012) for r, z in outer][::-1]
    A.add('Wok_Bowl', lathe((0, 0, .1), outer + inner, 40), 'iron', smooth=True, bevel=False)
    A.add('Wok_Rim', tube((0, 0, .1 + outer[-1][1] - .01), rim + .008, rim - .01, .02, 40), 'iron', smooth=True)
    for sx in (-1, 1):
        x0 = sx * rim
        A.add('Wok_Ear_Handle', merge([beam((x0, -.06, .25), (x0 + sx * .08, -.05, .27), .022, .022),
                                       beam((x0 + sx * .08, -.05, .27), (x0 + sx * .08, .05, .27), .022, .022),
                                       beam((x0 + sx * .08, .05, .27), (x0, .06, .25), .022, .022)]), 'iron')
    A.add('Wok_Stand_Ring', tube((0, 0, 0), .24, .2, .1, 32), 'iron', smooth=True)
    for k in range(6):
        a = k * math.pi / 3
        A.add('Wok_Stand_Vent', box((.22 * math.cos(a), .22 * math.sin(a), .05), (.05, .045, .05), rz=a), 'stone', detail=True)
    A.add('Wok_Spatula_Blade', xf(box((0, 0, 0), (.12, .1, .006)), rot=(0, .35, .4), t=(.05, -.05, .14)), 'iron')
    A.add('Wok_Spatula_Handle', rod((.1, -.02, .16), (.42, .14, .44), .014, 8), 'board', smooth=True)
    # wooden lid resting beside the wok
    A.add('Wok_Lid', lathe((.25, -.62, 0), [(0, 0), (.3, 0), (.3, .03), (.2, .1), (0, .12)], 32), 'board', smooth=True)
    A.add('Wok_Lid_Knob', merge([box((.18, -.62, .135), (.03, .03, .05)), box((.32, -.62, .135), (.03, .03, .05)),
                                 box((.25, -.62, .16), (.17, .035, .03))]), 'timber')
    return A


def bamboo_steamer():
    A = Asset()
    r, h = .21, .085
    for tier in range(3):
        z = tier * (h + .004)
        A.add(f'Steamer_Tier_{tier}_Wall', tube((0, 0, z), r, r - .014, h, 36), 'bamboo', smooth=True)
        A.add(f'Steamer_Tier_{tier}_Band', tube((0, 0, z + h - .016), r + .006, r - .002, .014, 36), 'board', smooth=True, detail=True)
        A.add(f'Steamer_Tier_{tier}_Band', tube((0, 0, z + .004), r + .006, r - .002, .014, 36), 'board', smooth=True, detail=True)
        for k in range(9):
            y = -r + .03 + k * (2 * r - .06) / 8
            w = 2 * math.sqrt(max(r * r - y * y, 0)) - .03
            A.add(f'Steamer_Tier_{tier}_Slat', box((0, y, z + .012), (w, .028, .008)), 'straw', detail=tier > 0)
    zt = 3 * (h + .004)
    A.add('Steamer_Lid', lathe((0, 0, zt), [(0, 0), (r + .004, 0), (r + .004, .03), (r * .72, .085), (.04, .1), (0, .1)], 36), 'straw', smooth=True)
    for k in range(4):
        rr = r * (.95 - k * .18)
        A.add('Steamer_Lid_Weave', tube((0, 0, zt + .028 + k * .016), rr + .004, rr - .008, .01, 36), 'bamboo', smooth=True, detail=True)
    A.add('Steamer_Lid_Knot', cyl((0, 0, zt + .1), .03, .025, 12), 'board', smooth=True)
    # two buns waiting on a small plate beside the steamer
    A.add('Steamer_Side_Plate', bowl((.36, -.16, 0), .12, .025), 'porcelain', smooth=True, bevel=False)
    for x in (.31, .41):
        A.add('Steamer_Bun', xf(sphere(.045, 16, 8), scale=(1, 1, .7), t=(x, -.16, .052)), 'bun', smooth=True, bevel=False)
    return A


def brick_stove():
    A = Asset()
    W, D, H = 1.7, .95, .8
    A.add('Stove_Plinth', box((0, 0, .06), (W + .1, D + .1, .12)), 'stone')
    A.add('Stove_Body', box((0, 0, .12 + (H - .12) / 2), (W, D, H - .12)), 'brick')
    A.add('Stove_Top_Plaster', box((0, 0, H + .03), (W + .06, D + .06, .06)), 'plaster')
    for k in range(5):
        A.add('Stove_Brick_Course', box((0, -D / 2 - .004, .2 + k * .13), (W - .02, .008, .012)), 'plaster', detail=True)
    for sx in (-.42, .42):
        A.add('Stove_Fire_Mouth', box((sx, -D / 2 + .05, .32), (.34, .12, .26)), 'iron')
        A.add('Stove_Fire_Mouth_Arch', box((sx, -D / 2 - .01, .47), (.44, .04, .06)), 'stone')
        A.add('Stove_Ash_Glow', box((sx, -D / 2 + .1, .22), (.26, .06, .04)), 'lantern', detail=True)
        # embedded wok
        A.add('Stove_Hob_Ring', tube((sx, -.05, H + .055), .33, .29, .03, 32), 'stone', smooth=True)
        A.add('Stove_Wok', lathe((sx, -.05, H - .12), [(0, 0), (.15, .02), (.29, .14), (.3, .175), (.285, .175), (.14, .035), (0, .015)], 32), 'iron', smooth=True)
    A.add('Stove_Wok_Lid', lathe((.42, -.05, H + .085), [(0, 0), (.31, 0), (.31, .025), (.2, .09), (0, .1)], 32), 'board', smooth=True)
    A.add('Stove_Wok_Lid_Knob', box((.42, -.05, H + .2), (.16, .035, .035)), 'timber')
    A.add('Stove_Chimney', box((0, D / 2 - .18, H + .65), (.36, .3, 1.3)), 'brick')
    A.add('Stove_Chimney_Cap', box((0, D / 2 - .18, H + 1.33), (.5, .42, .06)), 'tile')
    A.add('Stove_Ledge', box((0, D / 2 - .05, H + .1), (W - .2, .1, .08)), 'plaster')
    for i, x in enumerate((-.65, -.55, .6)):
        A.add('Stove_Ledge_Jar', lathe((x, D / 2 - .05, H + .14), [(0, 0), (.04, 0), (.05, .06), (.03, .1), (0, .1)], 12), 'glaze' if i else 'clay', smooth=True)
    # firewood waiting in front
    for k in range(4):
        A.add('Stove_Firewood', rod((-.25 + k * .07, -D / 2 - .35, .04 + (k % 2) * .06), (-.2 + k * .07, -D / 2 - .05, .04 + (k % 2) * .06), .035, 8), 'board', smooth=True)
    return A


def chopping_block():
    A = Asset()
    A.add('Block_Top', cyl((0, 0, .62), .26, .16, 28), 'board', smooth=True)
    A.add('Block_EndGrain', cyl((0, 0, .78), .245, .006, 28), 'straw', smooth=True, bevel=False)
    for k in range(3):
        a = k * 2 * math.pi / 3 + math.pi / 6
        A.add('Block_Leg', beam((.32 * math.cos(a), .32 * math.sin(a), 0), (.14 * math.cos(a), .14 * math.sin(a), .63), .06, .06), 'timber')
    A.add('Block_Leg_Ring', tube((0, 0, .26), .25, .21, .04, 28), 'timber', smooth=True)
    # cleaver resting on top
    A.add('Block_Cleaver_Blade', box((.02, -.04, .795), (.2, .09, .008), rz=.3), 'iron')
    A.add('Block_Cleaver_Handle', rod((.11, .0, .80), (.24, .06, .80), .016, 10), 'timber', smooth=True)
    # sliced scallions and a radish
    for k in range(6):
        A.add('Block_Scallion', rod((-.16 + k * .02, .06, .79), (-.06 + k * .02, .17, .79), .007, 6), 'greens', smooth=True, bevel=False)
    A.add('Block_Radish', xf(sphere(.05, 16, 8), scale=(1, 1, 1.5), rot=(0, math.pi / 2, .4), t=(-.08, -.1, .83)), 'radish', smooth=True, bevel=False)
    return A


def tableware_set():
    A = Asset()
    A.add('Tray_Base', box((0, 0, .015), (.62, .42, .03)), 'lacquer')
    for (c, s) in [((0, -.2, .045), (.62, .02, .03)), ((0, .2, .045), (.62, .02, .03)),
                   ((-.3, 0, .045), (.02, .42, .03)), ((.3, 0, .045), (.02, .42, .03))]:
        A.add('Tray_Rim', box(c, s), 'lacquer')
    for x in (-.16, .0):
        A.add('Tableware_Bowl', bowl((x, -.08, .03), .065, .055), 'porcelain', smooth=True, bevel=False)
    for x in (.16,):
        A.add('Tableware_Plate', bowl((x, -.08, .03), .09, .02, foot=.5), 'porcelain', smooth=True, bevel=False)
    A.add('Tableware_Rice', xf(sphere(.055, 16, 8), scale=(1, 1, .45), t=(-.16, -.08, .07)), 'rice', smooth=True, bevel=False)
    for dx in (-.008, .008):
        A.add('Tableware_Chopstick', beam((-.26 + dx, .02, .036), (-.1 + dx, .12, .036), .008, .008), 'board')
    A.add('Tableware_Chopstick_Rest', box((-.24, .03, .036), (.04, .02, .012)), 'porcelain', bevel=False)
    # teapot and two cups
    A.add('Teapot_Body', lathe((.12, .09, .03), [(0, 0), (.05, 0), (.075, .04), (.07, .085), (.035, .105), (0, .105)], 24), 'glaze', smooth=True)
    A.add('Teapot_Lid', lathe((.12, .09, .135), [(0, 0), (.038, 0), (.03, .02), (.008, .03), (0, .038)], 16), 'glaze', smooth=True)
    A.add('Teapot_Spout', rod((.19, .09, .07), (.24, .09, .12), .011, 8), 'glaze', smooth=True)
    A.add('Teapot_Handle', merge([beam((.05, .09, .1), (.02, .09, .08), .014, .014), beam((.02, .09, .08), (.05, .09, .05), .014, .014)]), 'glaze')
    for x in (.0, .24):
        A.add('Tea_Cup', bowl((x, .1 + (.02 if x else 0), .03), .028, .035), 'porcelain', smooth=True, bevel=False)
    return A


def grain_sacks():
    A = Asset()
    closed = [(0, 0), (.22, 0), (.27, .1), (.28, .45), (.24, .6), (.14, .68), (.11, .71), (.14, .76), (.08, .79), (0, .79)]
    open_ = [(0, 0), (.2, 0), (.27, .12), (.27, .44), (.24, .55), (.255, .6), (.24, .6), (.22, .55), (0, .55)]
    A.add('Sack_Open', xf(lathe((0, 0, 0), open_, 28), scale=(1, .85, 1), t=(-.2, .1, 0)), 'burlap', smooth=True)
    A.add('Sack_Open_Rice', xf(sphere(.22, 24, 8), scale=(1, .85, .25), t=(-.2, .1, .56)), 'rice', smooth=True, bevel=False)
    A.add('Sack_Open_Scoop', xf(bowl((0, 0, 0), .06, .04), rot=(.4, 0, 0), t=(-.12, .02, .6)), 'board', smooth=True, bevel=False)
    A.add('Sack_Open_Scoop_Handle', rod((-.12, -.03, .63), (-.1, -.2, .7), .012, 8), 'board', smooth=True)
    for i, (y, z, rz) in enumerate([(-.05, .0, .1), (.32, .0, -.12)]):
        A.add(f'Sack_Lying_{i}', xf(lathe((0, 0, 0), closed, 28), scale=(.62, 1, 1), rot=(0, math.pi / 2, rz), t=(.12, y, .174)), 'burlap', smooth=True)
        A.add(f'Sack_Lying_{i}_Tie', xf(tube((0, 0, .68), .125, .1, .04, 16), scale=(.62, 1, 1), rot=(0, math.pi / 2, rz), t=(.12, y, .174)), 'rope', smooth=True)
    A.add('Sack_Stamp_Patch', box((-.2, -.13, .3), (.14, .006, .12)), 'paper', bevel=False, detail=True)
    return A


def fence_corner():
    A = Asset()
    L = 1.0
    posts = [(-L, 0), (0, 0), (0, L)]
    for i, (x, y) in enumerate(posts):
        r = .08 if i == 1 else .06
        A.add('Corner_Post', cyl((x, y, 0), r, 1.3 if i == 1 else 1.25, 10), 'timber', smooth=True)
        A.add('Corner_Post_Cap', cyl((x, y, 1.3 if i == 1 else 1.25), r + .01, .05, 10, .03), 'timber', smooth=True)

    def run(a, b, off):
        a, b = np.array(a, float), np.array(b, float)
        d = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([d[1], -d[0]]) * off
        for z in (.35, .85):
            A.add('Corner_Rail', rod((*(a + nrm * .6), z), (*(b + nrm * .6), z), .03, 8), 'bamboo', smooth=True)
        n = 9
        for k in range(n):
            p = a + (b - a) * (.1 + .8 * k / (n - 1)) + nrm
            h = 1.05 + .06 * math.sin(k * 1.7)
            A.add('Corner_Picket', cyl((p[0], p[1], 0), .022, h, 8), 'bamboo', smooth=True)
            A.add('Corner_Picket_Node', tube((p[0], p[1], h * .55), .026, .02, .015, 8), 'straw', smooth=True, detail=True)
        for z in (.32, .82):
            A.add('Corner_Rail_Tie', tube((*(a + nrm * .6), z), .075, .06, .06, 10), 'rope', smooth=True, detail=True)

    run((-L, 0), (0, 0), .1)
    run((0, 0), (0, L), .1)
    A.add('Corner_Lashing', tube((0, 0, .6), .1, .08, .08, 12), 'rope', smooth=True)
    return A


def food_platter():
    A = Asset()
    A.add('Platter_Tray', cyl((0, 0, 0), .38, .03, 40), 'lacquer', smooth=True)
    A.add('Platter_Tray_Rim', tube((0, 0, .03), .38, .355, .025, 40), 'lacquer', smooth=True)
    # steamed fish on an oval plate
    A.add('Fish_Plate', xf(bowl((0, 0, 0), .16, .025, foot=.55), scale=(1.5, 1, 1), t=(-.04, .1, .03)), 'porcelain', smooth=True, bevel=False)
    A.add('Fish_Body', xf(sphere(.1, 20, 10), scale=(1.5, .45, .35), t=(-.06, .1, .075)), 'fish', smooth=True, bevel=False)
    A.add('Fish_Tail', xf(cyl((0, 0, 0), .05, .01, 3), scale=(1, 1.2, 1), rot=(math.pi / 2, 0, 0), t=(.15, .1, .07)), 'fish', bevel=False)
    for k in range(5):
        A.add('Fish_Scallion', rod((-.16 + k * .04, .08, .108), (-.13 + k * .04, .12, .108), .005, 6), 'greens', smooth=True, bevel=False)
    A.add('Fish_Sauce', xf(cyl((0, 0, 0), .14, .004, 24), scale=(1.45, .9, 1), t=(-.04, .1, .042)), 'broth', smooth=True, bevel=False)
    # rice bowl, buns, greens, soup
    A.add('Rice_Bowl', bowl((.2, -.1, .03), .065, .055), 'porcelain', smooth=True, bevel=False)
    A.add('Rice_Mound', xf(sphere(.055, 16, 8), scale=(1, 1, .5), t=(.2, -.1, .075)), 'rice', smooth=True, bevel=False)
    A.add('Bun_Plate', bowl((-.14, -.17, .03), .09, .02, foot=.5), 'porcelain', smooth=True, bevel=False)
    for (x, y) in [(-.17, -.15), (-.11, -.15), (-.14, -.2)]:
        A.add('Steamed_Bun', xf(sphere(.035, 16, 8), scale=(1, 1, .75), t=(x, y, .065)), 'bun', smooth=True, bevel=False)
    A.add('Greens_Dish', bowl((.22, .14, .03), .085, .025, foot=.5), 'glaze', smooth=True, bevel=False)
    for k in range(6):
        a = k * math.pi / 3
        A.add('Greens_Leaf', xf(sphere(.035, 10, 5), scale=(1.4, .7, .25), rot=(0, 0, a), t=(.22 + .03 * math.cos(a), .14 + .03 * math.sin(a), .055)), 'greens', smooth=True, bevel=False)
    A.add('Soup_Bowl', bowl((.04, -.2, .03), .07, .05), 'glaze', smooth=True, bevel=False)
    A.add('Soup_Broth', cyl((.04, -.2, .07), .058, .004, 24), 'broth', smooth=True, bevel=False)
    A.add('Soup_Spoon', xf(bowl((0, 0, 0), .02, .012), scale=(1.4, 1, 1), t=(.07, -.17, .076)), 'porcelain', smooth=True, bevel=False)
    return A


def ingredient_crate():
    A = Asset()
    W, D, H = .9, .6, .28
    A.add('Crate_Floor', box((0, 0, .03), (W, D, .03)), 'board')
    for z in (.08, .17, .25):
        for (c, s) in [((0, -D / 2, z), (W, .02, .07)), ((0, D / 2, z), (W, .02, .07)),
                       ((-W / 2, 0, z), (.02, D, .07)), ((W / 2, 0, z), (.02, D, .07))]:
            A.add('Crate_Slat', box(c, s), 'board')
    for x in (-1, 1):
        for y in (-1, 1):
            A.add('Crate_Corner', box((x * (W / 2 - .02), y * (D / 2 - .02), H / 2 + .01), (.05, .05, H + .02)), 'timber')
    for (x, y) in [(-.26, -.12), (-.24, .13)]:
        A.add('Cabbage', xf(sphere(.13, 18, 9), scale=(1, 1, .85), t=(x, y, .15)), 'cabbage', smooth=True, bevel=False)
        for k in range(4):
            a = k * math.pi / 2 + .4
            A.add('Cabbage_Leaf', xf(sphere(.1, 12, 6), scale=(1, .9, .35), rot=(.5, 0, a), t=(x + .07 * math.cos(a), y + .07 * math.sin(a), .16)), 'greens', smooth=True, bevel=False, detail=True)
    for k in range(3):
        y = -.16 + k * .14
        A.add('Radish', xf(sphere(.05, 14, 7), scale=(1, 1, 2.6), rot=(0, math.pi / 2, .15 * k), t=(.04, y, .12)), 'radish', smooth=True, bevel=False)
        A.add('Radish_Leaves', rod((-.1, y, .12), (-.2, y + .03, .2), .02, 6), 'greens', smooth=True, bevel=False)
    for k in range(4):
        y = -.18 + k * .11
        A.add('Carrot', xf(cyl((0, 0, 0), .025, .2, 10, .004), rot=(0, math.pi / 2, 0), t=(.2, y, .1 + (k % 2) * .03)), 'carrot', smooth=True, bevel=False)
    # whole raw fish laid across the top on a leaf
    A.add('Crate_Fish_Leaf', xf(sphere(.2, 16, 6), scale=(1.4, .5, .05), t=(.15, .02, .27)), 'greens', smooth=True, bevel=False)
    A.add('Crate_Fish', xf(sphere(.1, 20, 10), scale=(1.8, .45, .4), t=(.13, .02, .3)), 'fish', smooth=True, bevel=False)
    A.add('Crate_Fish_Tail', xf(cyl((0, 0, 0), .055, .01, 3), scale=(1, 1.2, 1), rot=(math.pi / 2, 0, 0), t=(.33, .02, .3)), 'fish', bevel=False)
    return A


ASSETS = {
    'CookingWok': dict(name_zh='鐵鍋', build=cooking_wok, category='料理道具',
                       desc='Round-bottom cast-iron wok with two ear handles on a vented iron ring stand, an iron spatula inside and a domed wooden lid resting beside it.',
                       size='Wok 0.72 m across; set approx. 0.9 x 1.0 x 0.45 m.'),
    'BambooSteamer': dict(name_zh='蒸籠', build=bamboo_steamer, category='料理道具',
                          desc='Three stacked round bamboo steamer tiers with slatted bases and wooden bands, woven domed lid with knot, and a small plate of two steamed buns beside it.',
                          size='Steamer 0.43 m across, 0.37 m tall; set approx. 0.6 x 0.45 m.'),
    'BrickStove': dict(name_zh='雙灶爐台', build=brick_stove, category='料理道具',
                       desc='Kitchen stove of red brick with lime-plastered top, two arched fire mouths with ember glow, two embedded woks (one with wooden lid), rear chimney, back ledge with seasoning jars and firewood in front.',
                       size='1.7 x 0.95 m body, 0.86 m working height, chimney to 2.2 m.'),
    'ChoppingBlock': dict(name_zh='砧板台', build=chopping_block, category='料理道具',
                          desc='Thick round end-grain chopping block on a three-legged braced stand, with a cleaver, sliced scallions and a white radish on top.',
                          size='0.52 m across, 0.8 m working height.'),
    'TablewareSet': dict(name_zh='碗盤茶具組', build=tableware_set, category='料理道具',
                         desc='Red lacquer tray with celadon rice bowl, empty bowl, plate, chopsticks on a rest, small green-glazed teapot and two cups.',
                         size='Tray 0.62 x 0.42 m; teapot 0.14 m tall.'),
    'GrainSacks': dict(name_zh='米糧麻袋', build=grain_sacks, category='通用道具',
                       desc='Burlap sack pile: one open sack full of rice with a wooden scoop, two tied sacks lying beside it, and a blank paper label.',
                       size='Approx. 1.0 x 0.9 x 0.65 m; each sack 0.8 m long.'),
    'BambooFenceCorner': dict(name_zh='竹籬笆轉角段', build=fence_corner, category='庭院與圍欄',
                              desc='L-shaped bamboo fence corner: thicker corner post, two 1 m arms with rails, rope ties and bamboo pickets, matching the BambooFence segment.',
                              size='1.1 x 1.1 x 1.35 m; arm ends at (-1, 0) and (0, +1) m for tiling with BambooFence.'),
    'FoodPlatter': dict(name_zh='料理成品拼盤', build=food_platter, category='料理成品',
                        desc='Round lacquer serving tray with steamed fish on an oval plate in sauce, a bowl of rice, a plate of three steamed buns, a dish of greens and a bowl of soup with spoon.',
                        size='Tray 0.76 m across; tallest item 0.13 m.'),
    'IngredientCrate': dict(name_zh='食材木箱', build=ingredient_crate, category='食材',
                            desc='Shallow slatted produce crate holding two cabbages, three white radishes with leaves, four carrots and a whole raw fish laid on a leaf across the top.',
                            size='0.9 x 0.6 x 0.28 m crate; approx. 0.35 m tall with produce.'),
}

BATCH_ID = 'TownKitchen10'
BATCH_TITLE = '小鎮廚房 10'
BATCH_DATE = '2026-10-17'
BATCH_INTRO = '小鎮待辦的第二批：食肆用的料理道具、碗盤、米糧與食材，加上籬笆轉角段，共 9 組。'
STATUS = {}
BATCH_NOTES = """## 內容

- 料理道具：鐵鍋（含鍋架、鍋鏟、木鍋蓋）、三層蒸籠、雙灶爐台、砧板台、碗盤茶具組。
- 料理成品：清蒸魚、白飯、饅頭、青菜、湯，放在同一個漆盤上；可拆成單品使用。
- 食材：米糧麻袋（開口袋裝米）、食材木箱（白菜、白蘿蔔、紅蘿蔔、整條魚）。
- 竹籬笆轉角段可接 TownLife09 的 BambooFence：兩臂端點在 (-1, 0) 與 (0, +1) m。

## 尚未完成

UV／貼圖烘焙、碰撞、LOD 與 Unreal 匯入驗證都還沒做。爐火、蒸氣、湯面熱氣等特效未製作；食物是外觀模型，沒有烹飪狀態變化。"""


def prompt_for(aid, view):
    a = ASSETS[aid]
    return ('Use case: stylized-concept. Asset type: Blender modeling reference for a xianxia (Chinese immortal-cultivation) '
            f'open-world town kitchen, single game asset: {a["name_zh"]} ({aid}). Design: {a["desc"]} Scale: {a["size"]} '
            'Style: softly beveled stylized 3D game art matching the existing dondon town (warm cedar timber, blue-grey stone, '
            'celadon porcelain, red lacquer, restrained jade and ochre accents). '
            f'View: {VIEW_PHRASE[view]}, entire object visible on a light grey seamless studio background with soft contact shadow. '
            'No characters, no scenery, no text or lettering, no watermark.')
