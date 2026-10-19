"""StreetProps11: well, bucket, notice board, crate, bamboo basket and firewood stack.
Run: blender --background --factory-startup -t 4 --python build_street_props11.py [-- AssetID ...]
Dimensions come from street_specs.py (shared with draw_street_sheets.py). Completed assets are skipped.
"""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from street_specs import NAMES, DETAILS, SPECS
import prop_kit as K


def make_materials():
    global wood, board, stone, stone2, tile, iron, rope, water, paper, bamboo, logwood, logend
    wood = K.mat('Dark_Chestnut', (.20, .09, .045)); board = K.mat('Warm_Timber', (.36, .20, .09))
    stone = K.mat('Blue_Gray_Stone', (.27, .32, .32), rough=.85, noise=18, bump=.3); stone2 = K.mat('Pale_Gray_Stone', (.36, .40, .38), rough=.85, noise=18, bump=.3)
    tile = K.mat('Celadon_Grey_Tile', (.09, .16, .17), rough=.6); iron = K.mat('Dark_Iron', (.06, .06, .06), .85, .45)
    rope = K.mat('Hemp_Rope', (.48, .36, .19), rough=.9, noise=120, bump=.2); water = K.mat('Well_Water', (.02, .05, .06), rough=.05, noise=8, bump=.02)
    paper = K.mat('Blank_Notice_Paper', (.72, .66, .52), rough=.9, noise=50, bump=.03)
    bamboo = K.mat('Woven_Bamboo', (.55, .42, .20), rough=.6, noise=140, bump=.15)
    logwood = K.mat('Split_Log_Bark', (.24, .15, .08), rough=.9, noise=60, bump=.35); logend = K.mat('Split_Log_End', (.62, .45, .26), rough=.8)


def bucket_at(p, prefix='Bucket', bail=True):
    s = SPECS['WellBucket']; x, y, z = p; t = s['wall']
    K.lathe(f'{prefix}_Stave_Body', [(0, .012), (s['bottom_r'] - t, .012), (s['bottom_r'], 0), (s['top_r'], s['h']), (s['top_r'] - t, s['h']),
                                     (s['bottom_r'] - t * 1.6, .03), (0, .03)], board, p, 48)
    for k in range(s['staves']):
        a = k * math.tau / s['staves']
        r0, r1 = s['bottom_r'] + .0015, s['top_r'] + .0015
        K.beam(f'{prefix}_Stave_Joint', (x + r0 * math.cos(a), y + r0 * math.sin(a), z + .005), (x + r1 * math.cos(a), y + r1 * math.sin(a), z + s['h'] - .005), .0022, wood, 4)
    for zz in (.06, .24):
        r = s['bottom_r'] + (s['top_r'] - s['bottom_r']) * zz / s['h'] + .004
        K.torus(f'{prefix}_Iron_Hoop', (x, y, z + zz), r, .006, iron)
    if bail:
        pts = [(x + s['top_r'] * math.cos(a), y, z + s['h'] + .16 * math.sin(a)) for a in [i * math.pi / 10 for i in range(11)]]
        for a_, b_ in zip(pts, pts[1:]): K.beam(f'{prefix}_Rope_Bail', a_, b_, .006, rope, 6)


def well():
    s = SPECS['StoneWell']; R, r, h, ar, ah = s['outer_r'], s['inner_r'], s['wall_h'], s['apron_r'], s['apron_h']
    K.lathe('Stone_Apron', [(0, 0), (ar, 0), (ar, ah), (R + .02, ah), (R + .02, ah), (0, ah)], stone2, segments=48)
    rng = random.Random(11); courses = 5; ch = (h - ah) / courses
    for c in range(courses):
        n = 14; off = (c % 2) * .5
        for i in range(n):
            a0, a1 = (i + off) * math.tau / n + .012, (i + 1 + off) * math.tau / n - .012
            v = []; seg = 4
            for zz in (ah + c * ch + .006, ah + (c + 1) * ch - .006):
                for rr in (r, R + rng.uniform(-.008, .01)):
                    for j in range(seg + 1):
                        a = a0 + (a1 - a0) * j / seg; v.append((rr * math.cos(a), rr * math.sin(a), zz))
            q = seg + 1
            f = []
            for j in range(seg):
                f += [(j, j + 1, q + j + 1, q + j)[::-1], (2 * q + j, 2 * q + j + 1, 3 * q + j + 1, 3 * q + j)]   # bottom, top
                f += [(q + j, q + j + 1, 3 * q + j + 1, 3 * q + j)[::-1], (j, j + 1, 2 * q + j + 1, 2 * q + j)]  # outer, inner
            f += [(0, q, 3 * q, 2 * q), (seg, 2 * q + seg, 3 * q + seg, q + seg)]
            o = K.mesh('Well_Wall_Stone', v, f, stone if (i + c) % 3 else stone2); o.modifiers.new('Stone_Bevel', 'BEVEL').width = .008
    K.lathe('Well_Coping_Ring', [(r - .03, h), (R + .04, h), (R + .04, h + .06), (r - .03, h + .06)], stone2, segments=64, closed=True)
    K.cyl('Well_Water_Surface', (0, 0, s['water_z']), r - .002, .01, water, 48)
    K.lathe('Well_Shaft_Lining', [(r - .001, s['water_z']), (r - .001, h)], stone, segments=48)
    px, ph = s['post_x'], s['post_h']
    for x in (-px, px):
        K.box('Windlass_Post', (x, 0, ph / 2), (.1, .1, ph), wood, .008)
        K.box('Post_Stone_Foot', (x, 0, ah / 2 + .03), (.2, .2, ah + .06), stone2, .01)
        K.beam('Post_Brace', (x, -.32, ah), (x, 0, .9), .025, wood, 6); K.beam('Post_Brace', (x, .32, ah), (x, 0, .9), .025, wood, 6)
    K.cyl('Windlass_Roller', (0, 0, s['roller_z']), .07, 2 * px - .1, wood, 24, rot=(0, math.pi / 2, 0))
    for x in (-px + .2, px - .2): K.torus('Roller_Iron_Band', (x, 0, s['roller_z']), .072, .006, iron, rot=(0, math.pi / 2, 0))
    K.beam('Crank_Axle', (px, 0, s['roller_z']), (px + .1, 0, s['roller_z']), .018, iron, 8)
    K.beam('Crank_Arm', (px + .1, 0, s['roller_z']), (px + .1, -.22, s['roller_z'] - .08), .016, iron, 8)
    K.beam('Crank_Handle', (px + .1, -.22, s['roller_z'] - .08), (px + .26, -.22, s['roller_z'] - .08), .02, wood, 8)
    for i in range(6): K.torus('Rope_Coil', (-.25 + i * .06, 0, s['roller_z']), .078, .009, rope, rot=(0, math.pi / 2, 0), seg=24)
    K.beam('Well_Rope', (0, -.075, s['roller_z']), (0, -.075, 1.18), .008, rope, 6)
    bucket_at((0, -.075, .86), 'Hanging_Bucket')
    rf = s['roof']
    K.box('Roof_Tie_Beam', (0, 0, rf['eave_z'] - .06), (2 * px + .1, .1, .1), wood, .006)
    K.box('Ridge_Beam', (0, 0, rf['ridge_z'] - .05), (2 * rf['half_x'], .09, .09), wood, .006)
    for x in (-px, px): K.box('King_Post', (x, 0, (ph + rf['ridge_z']) / 2 - .04), (.08, .08, rf['ridge_z'] - ph), wood, .006)
    K.gable_roof('Well_Roof', rf['half_x'], rf['half_y'], rf['eave_z'], rf['ridge_z'], tile, wood)


def bucket(): bucket_at((0, 0, 0))


def notice_board():
    s = SPECS['NoticeBoard']; bw, bt, bh = s['board']; px, ph, p = s['post_x'], s['post_h'], s['post']; z0 = s['board_z']
    for x in (-px, px):
        K.box('Stone_Foot', (x, 0, .1), (.24, .24, .2), stone2, .015)
        K.box('Board_Post', (x, 0, ph / 2), (p, p, ph), wood, .01)
    for i in range(6): K.box('Board_Plank', (-bw / 2 + (i + .5) * bw / 6, 0, z0 + bh / 2), (bw / 6 - .006, bt, bh), board, .004)
    for z in (z0, z0 + bh): K.box('Board_Frame_Rail', (0, -bt / 2 - .012, z), (bw + .08, .03, .06), wood, .005)
    for x in (-bw / 2, bw / 2): K.box('Board_Frame_Stile', (x, -bt / 2 - .012, z0 + bh / 2), (.06, .03, bh + .06), wood, .005)
    for x in (-px, px): K.box('Board_Bracket', ((x + math.copysign(bw / 2, x)) / 2, 0, z0 + bh / 2), (abs(px) - bw / 2 + .02, .05, .05), wood, .004)
    K.box('Notice_Ledge', (0, -.07, z0 - .07), (bw + .1, .14, .03), board, .004)
    rng = random.Random(4)
    for (x, z, w, h) in [(-.48, 1.25, .36, .48), (-.02, 1.38, .3, .4), (.42, 1.2, .38, .52), (0, 1.02, .5, .28)]:
        o = K.box('Blank_Notice', (x, -bt / 2 - .004, z + h / 2), (w, .003, h), paper, 0); o.rotation_euler.y = rng.uniform(-.04, .04)
        K.cyl('Notice_Pin', (x, -bt / 2 - .008, z + h - .03), .008, .006, iron, 8, rot=(math.pi / 2, 0, 0), bevel=0)
    K.box('Roof_Tie_Beam', (0, 0, ph - .04), (s['roof_w'] - .1, .08, .08), wood, .005)
    K.gable_roof('Board_Roof', s['roof_w'] / 2, s['roof_d'] / 2, ph + .02, ph + s['roof_rise'], tile, wood)


def crate(lid=True):
    s = SPECS['WoodenCrate']; X, Y, Z = s['size']; g = s['plank_gap']; t = .02
    for i in range(3):
        z = (i + .5) * Z / 3
        for sy in (-1, 1): K.box('Side_Plank_Long', (0, sy * (Y / 2 - t / 2), z), (X - .1, t, Z / 3 - g), board, .003)
        for sx in (-1, 1): K.box('Side_Plank_Short', (sx * (X / 2 - t / 2), 0, z), (t, Y - .1, Z / 3 - g), board, .003)
    for sx in (-1, 1):
        for sy in (-1, 1): K.box('Corner_Batten', (sx * (X / 2 - .025), sy * (Y / 2 - .025), Z / 2), (.05, .05, Z), wood, .005)
    K.box('Crate_Floor', (0, 0, .012), (X - .04, Y - .04, .024), board, .003)
    for i in range(4): K.box('Lid_Plank', (0, -Y / 2 + (i + .5) * Y / 4, Z + s['lid_t'] / 2), (X + .02, Y / 4 - .006, s['lid_t']), board, .003)
    for x in (-X / 2 + .08, X / 2 - .08): K.box('Lid_Cleat', (x, 0, Z + s['lid_t'] + .01), (.05, Y - .02, .02), wood, .003)


def basket():
    s = SPECS['BambooBasket']; t = s['wall']; br, tr, h = s['bottom_r'], s['top_r'], s['h']
    K.lathe('Woven_Basket_Wall', [(0, .03), (br, .03), (tr, h), (tr - t, h), (br - t, .03 + t), (0, .03 + t)], bamboo, segments=48)
    for k in range(1, 11):
        z = .03 + k * (h - .03) / 11; r = br + (tr - br) * (z - .03) / (h - .03) + .002
        K.torus('Weave_Ring', (0, 0, z), r, .0045, bamboo, seg=40)
    K.torus('Rim_Binding', (0, 0, h), tr - t / 2, .009, board, seg=48)
    for k in range(s['ribs']):
        a = k * math.tau / s['ribs']
        K.beam('Bamboo_Rib', ((br + .004) * math.cos(a), (br + .004) * math.sin(a), .03), ((tr + .004) * math.cos(a), (tr + .004) * math.sin(a), h), .0035, wood, 5)
    for sx in (-1, 1): K.box('Foot_Frame', (sx * (br - .02), 0, .015), (.03, 2 * br, .03), wood, .004)
    for sy in (-1, 1): K.box('Foot_Frame', (0, sy * (br - .02), .015), (2 * br, .03, .03), wood, .004)
    for sx in (-1, 1):
        top = (sx * .1, tr * .92, h - .04); bot = (sx * .12, br + .02, .14)
        mid = (sx * .11, tr + .06, (h + .14) / 2)
        K.beam('Shoulder_Strap', top, mid, .012, rope, 6); K.beam('Shoulder_Strap', mid, bot, .012, rope, 6)


def firewood():
    s = SPECS['FirewoodStack']; L, D = s['length'], s['depth']; rng = random.Random(7)
    for y in (-D / 2 + .08, D / 2 - .08): K.box('Base_Rail', (0, y, .04), (L + .2, .08, .08), wood, .006)
    for x in (-L / 2 - .05, L / 2 + .05):
        for y in (-D / 2 + .05, D / 2 - .05): K.box('End_Post', (x, y, s['post_h'] / 2), (.08, .08, s['post_h']), wood, .006)
    rr = sum(s['log_r']) / 2
    for row in range(s['rows']):
        off = rr if row % 2 else 0; n = int(L / (2 * rr)) - (row % 2)
        for i in range(n):
            r = rng.uniform(*s['log_r']); x = -L / 2 + rr + off + i * 2 * rr; z = .08 + rr + row * rr * 1.75
            ln, y0 = D - rng.uniform(0, .06), rng.uniform(-.03, .03); spin = rng.uniform(0, math.tau)
            o = K.cyl('Split_Log', (x, y0, z), r * .97, ln, logwood, 7, bevel=.004)
            o.rotation_euler = (math.pi / 2, spin, 0)          # lie along Y, random spin about its own axis
            for sy in (-1, 1):
                e = K.cyl('Log_End_Grain', (x, y0 + sy * (ln / 2 + .001), z), r * .9, .004, logend, 7, bevel=0); e.rotation_euler = (math.pi / 2, spin, 0)
    lo, hi = s['cap_z']; ang = math.atan2(hi - lo, D + .24)
    for i in range(5):
        x = -L / 2 - .15 + (i + .5) * (L + .3) / 5
        o = K.box('Rain_Cap_Plank', (x, 0, (lo + hi) / 2 + .02), ((L + .3) / 5 - .01, math.hypot(D + .24, hi - lo), .025), board, .003); o.rotation_euler.x = ang
    for x in (-L / 2 - .05, L / 2 + .05): K.beam('Cap_Rafter', (x, -D / 2 - .12, lo), (x, D / 2 + .12, hi), .03, wood, 6)


BUILDERS = {'StoneWell': well, 'WellBucket': bucket, 'NoticeBoard': notice_board, 'WoodenCrate': crate, 'BambooBasket': basket, 'FirewoodStack': firewood}
EXTRA = {'StoneWell': [('11_into_well', (0, -.25, 1))], 'WellBucket': [('11_interior', (0, -.35, 1)), ('12_underside', (.25, -.6, -1))],
         'BambooBasket': [('11_interior', (0, -.35, 1)), ('12_back_straps', (.4, 1, .3))]}
ids = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None
K.build_all(ROOT, BUILDERS, NAMES, DETAILS, SPECS, 'StreetProps11', make_materials, ids, EXTRA)
