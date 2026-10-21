"""FreshIngredients13: rice sack, cured meat rack, radish crate, vegetable basket, egg basket and fish tub.
Run: blender --background --factory-startup -t 4 --python build_fresh13.py [-- ItemID ...]
Container items append StreetProps11 assets from <project>/Models (see fresh_specs.CONTAINERS).
"""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector, Matrix, Euler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = next(p for p in [ROOT, *ROOT.parents] if (p / 'Deliverables').is_dir())
sys.path.insert(0, str(HERE))
from fresh_specs import *
import prop_kit as K


def make_materials():
    global hemp, rice, wood, rope, lean, fat, skin, sausage, radish, carrot, leafg, napa, napaw, scal, scalw, straw, egg1, egg2, water, fishback, fishbelly, dark
    hemp = K.mat('Hemp_Sack_Cloth', (.50, .40, .26), rough=.95, noise=260, bump=.45); rice = K.mat('Raw_Rice', (.90, .88, .80), rough=.7, noise=200, bump=1.0)
    wood = K.mat('Dark_Chestnut', (.20, .09, .045)); rope = K.mat('Hemp_Rope', (.48, .36, .19), rough=.9, noise=120, bump=.2)
    lean = K.mat('Cured_Lean', (.30, .07, .04), rough=.4, noise=80, bump=.15); fat = K.mat('Cured_Fat', (.80, .62, .42), rough=.45)
    skin = K.mat('Cured_Skin', (.22, .10, .04), rough=.3); sausage = K.mat('Chinese_Sausage', (.42, .08, .05), rough=.35, noise=150, bump=.3)
    radish = K.mat('White_Radish', (.88, .87, .80), rough=.4, noise=60, bump=.08); carrot = K.mat('Carrot', (.85, .30, .06), rough=.5, noise=90, bump=.2)
    leafg = K.mat('Leafy_Top', (.14, .36, .08), rough=.4, noise=50, bump=.15); napa = K.mat('Napa_Leaf', (.62, .78, .45), rough=.45, noise=70, bump=.25)
    napaw = K.mat('Napa_Core', (.86, .88, .74), rough=.5); scal = K.mat('Scallion_Green', (.22, .52, .14), rough=.4); scalw = K.mat('Scallion_White', (.88, .90, .80), rough=.4)
    straw = K.mat('Dry_Straw', (.72, .60, .32), rough=.8, noise=120, bump=.2)
    egg1 = K.mat('Egg_Shell_Brown', (.78, .58, .40), rough=.5, noise=300, bump=.03); egg2 = K.mat('Egg_Shell_Cream', (.88, .82, .70), rough=.5, noise=300, bump=.03)
    water = K.mat('Tub_Water', (.05, .12, .12), rough=.04, noise=6, bump=.02)
    fishback = K.mat('Carp_Back', (.25, .27, .20), rough=.3, noise=220, bump=.15); fishbelly = K.mat('Carp_Belly', (.75, .72, .62), rough=.35)
    dark = K.mat('Eye_Dark', (.02, .02, .02), rough=.1)


def wrinkled_shell(name, profile, m, segs=48, seed=1, amp=.035):
    """Closed-bottom lathe with vertical cloth folds: radius modulated per vertex."""
    rng = random.Random(seed); ph = [rng.uniform(0, math.tau) for _ in range(3)]
    v = [(0, 0, 0)]; rows = []
    for r, z in profile:
        row = []
        for i in range(segs):
            a = i * math.tau / segs
            k = 1 + amp * (math.sin(5 * a + ph[0]) * .6 + math.sin(9 * a + ph[1] + z * 8) * .4) * min(1, z / .08) + rng.uniform(-.006, .006)
            row.append(len(v)); v.append((r * k * math.cos(a), r * k * math.sin(a), z))
        rows.append(row)
    f = [(0, rows[0][(i + 1) % segs], rows[0][i]) for i in range(segs)]
    for ra, rb in zip(rows, rows[1:]): f += [(ra[i], ra[(i + 1) % segs], rb[(i + 1) % segs], rb[i]) for i in range(segs)]
    return K.mesh(name, v, f, m, smooth=True)


def rooted(name, prof, m, loc, rot):
    """Lathe a root vegetable along local +Z, then place it; returns (object, world tip of the top end)."""
    o = K.lathe(name, prof, m, (0, 0, 0), 24); o.rotation_euler = rot; o.location = loc
    top = Vector(loc) + Euler(rot).to_matrix() @ Vector((0, 0, prof[-1][1])); return o, top


def radish_prof(L, r): return [(0, 0), (r * .25, L * .12), (r * .6, L * .35), (r * .95, L * .7), (r, L * .9), (r * .7, L * .98), (0, L)]


def leaf_tuft(prefix, top, n, rng, length=.18, m=None):
    for k in range(n):
        a = rng.uniform(0, math.tau)
        K.leaf(prefix + '_Leaf', top, a, length * rng.uniform(.8, 1.1), .045, .02, m or leafg, .15, pitch=rng.uniform(.9, 1.6))


# ---------------------------------------------------------------- items
def rice_sack():
    s = SPECS['RiceSack']; h = s['h']
    prof = [(s['base_r'] * .9, .0), (s['base_r'], .03), (s['belly_r'] * .97, h * .25), (s['belly_r'], h * .45), (s['belly_r'] * .95, h * .65), (s['neck_r'], h * .9), (s['cuff_r'] - .01, h)]
    wrinkled_shell('Hemp_Sack_Body', prof, hemp)
    K.torus('Rolled_Cuff', (0, 0, h - .015), s['cuff_r'], .03, hemp, seg=48)
    K.dome('Rice_Surface', s['cuff_r'] - .012, s['rice_top'] - h + .01, rice, (0, 0, h - .01), 48, .9)
    K.beam('Scoop_Handle', (.05, -.02, s['rice_top'] - .015), (.17, -.06, s['rice_top'] + .14), .012, wood, 8)
    K.ellipsoid('Scoop_Bowl_Buried', (.04, -.015, s['rice_top'] - .012), (.04, .03, .012), wood, (0, .3, .3))
    K.beam('Side_Seam', (s['base_r'] + .003, 0, .03), (s['neck_r'] + .03, 0, h * .9), .003, rope, 4)


def cured_rack():
    s = SPECS['CuredMeatRack']; W, D, H, bz = s['width'], s['depth'], s['h'], s['bar_z']; rng = random.Random(13)
    for x in (-W / 2, W / 2):
        for y in (-D / 2, D / 2): K.beam('A_Frame_Leg', (x, y, 0), (x, 0, H), .022, wood, 6)
        K.beam('Leg_Spreader', (x, -D / 2 + .1, .25), (x, D / 2 - .1, .25), .015, wood, 6)
    K.beam('Hanging_Bar', (-W / 2 - .04, 0, bz), (W / 2 + .04, 0, bz), .025, wood, 10)
    for i in range(s['strips']):
        x = -.3 + i * .14; ln = .24 + rng.uniform(-.03, .03); zc = bz - .08 - ln / 2; rot = (0, rng.uniform(-.05, .05), rng.uniform(-.15, .15))
        K.beam('Hanging_Rope', (x, 0, bz - .02), (x, 0, bz - .08), .004, rope, 4)
        for nm, y, t, m in (('Cured_Skin', -.011, .004, skin), ('Cured_Fat', -.0065, .005, fat), ('Cured_Lean', .001, .010, lean)):
            K.box(nm, (x, y, zc), (.055, t, ln), m, .002, rot=rot)
    for i in range(s['sausage_strings']):
        x = .25 + i * .07; z = bz - .03
        K.beam('Sausage_String', (x, 0, bz - .02), (x, 0, z - .015), .003, rope, 4)
        for k in range(4):
            K.ellipsoid('Chinese_Sausage_Link', (x + rng.uniform(-.004, .004), 0, z - .05 - k * .07), (.015, .015, .032), sausage, (0, rng.uniform(-.1, .1), 0), 16)
            K.torus('Sausage_Tie', (x, 0, z - .015 - k * .07), .006, .002, rope, seg=10)


def radish_crate():
    K.container(PROJECT, CONTAINERS['RadishCrate']); s = SPECS['RadishCrate']; rng = random.Random(21); fz = CRATE['floor_z']
    for i in range(s['radishes']):
        # Two rows: roots against the front and back walls, tops leaning in toward the middle (+X rotation tips +Z toward -Y).
        row, k = divmod(i, 5); x = -.2 + k * .1 + rng.uniform(-.01, .01)
        tilt = math.radians(rng.uniform(32, 42))
        loc = (x, .14 if row else -.14, fz + .012)
        o, top = rooted('White_Radish', radish_prof(s['radish_len'], s['radish_r']), radish, loc, ((tilt if row else -tilt), 0, 0))
        leaf_tuft('Radish', top, 4, rng)
    for i in range(s['carrots']):
        o, top = rooted('Carrot', radish_prof(.16, .02), carrot, (-.12 + i * .11, -.04, .29), (math.radians(80), 0, math.radians(rng.uniform(60, 120))))
        leaf_tuft('Carrot', top, 2, rng, .08)


def vegetable_basket():
    sx, sy, sz = K.container(PROJECT, CONTAINERS['VegetableBasket']); s = SPECS['VegetableBasket']; rng = random.Random(31); fz = BASKET['floor_z'] * sz
    for i, (x, y, yaw) in enumerate([(-.06, .04, .35), (.07, -.02, -.25)][:s['cabbages']]):
        c = Vector((x, y, fz + .065)); ax = Vector((math.cos(yaw), math.sin(yaw), .25)).normalized()
        K.ellipsoid('Napa_Cabbage_Core', c, (.12, .062, .058), napaw, (0, -.24, yaw), 24)
        base = c - ax * .12
        for k in range(5):
            side = (k - 2) * .4
            K.leaf('Napa_Outer_Leaf', (base.x - math.sin(yaw) * side * .05, base.y + math.cos(yaw) * side * .05, base.z + .03 + .01 * abs(side)),
                   yaw + side * .12, .25, .11, .03, napa, .35, pitch=.12)
    for i in range(s['carrots']):
        # Lying along +X near the front of the basket (rotate +Z to -Y, then to +X), inside the rim.
        o, top = rooted('Carrot', radish_prof(.17, .019), carrot, (-.085, -.1 + i * .03, fz + .06 + i * .012), (math.pi / 2, 0, math.pi / 2 + rng.uniform(-.1, .1)))
        leaf_tuft('Carrot', top, 2, rng, .08)
    for i in range(9):
        y = .1 + (i % 3) * .008; z = fz + .14 + (i // 3) * .008
        K.beam('Scallion_White', (-.17, y, z), (-.06, y, z + .005), .0045, scalw, 6); K.beam('Scallion_Green', (-.06, y, z + .005), (.14, y + .01 * (i % 3 - 1), z + .02), .004, scal, 6)
    K.torus('Scallion_Tie', (-.08, .108, fz + .148), .016, .004, straw, rot=(0, math.pi / 2, 0), seg=16)


def egg_basket():
    sx, sy, sz = K.container(PROJECT, CONTAINERS['EggBasket']); s = SPECS['EggBasket']; rng = random.Random(41); fz = BASKET['floor_z'] * sz
    for i in range(36):
        a = rng.uniform(0, math.tau); r = rng.uniform(0, .1); z = fz + .003 + rng.uniform(0, .01) + (r / .1) ** 2 * .02
        K.beam('Straw_Lining', (r * math.cos(a) - .03, r * math.sin(a), z), (r * math.cos(a) + .03, r * math.sin(a) + rng.uniform(-.02, .02), z + .005), .0015, straw, 4)
    ex, ez = s['egg']; spots = [(0, 0, 0)] + [(.055 * math.cos(k * math.tau / 7), .055 * math.sin(k * math.tau / 7), 0) for k in range(7)] + \
        [(.03 * math.cos(k * math.tau / 5 + .4), .03 * math.sin(k * math.tau / 5 + .4), 1) for k in range(5)] + [(.0, .0, 2)]
    for i, (x, y, layer) in enumerate(spots[:s['eggs']]):
        z = fz + .012 + ex + layer * ex * 1.55 + (math.hypot(x, y) / .055) * .006
        K.ellipsoid('Egg', (x, y, z), (ex, ex, ez), egg1 if i % 3 else egg2, (math.radians(80 + rng.uniform(-10, 10)), 0, rng.uniform(0, math.pi)), 24)


def fish_tub():
    sx, sy, sz = K.container(PROJECT, CONTAINERS['FishTub']); s = SPECS['FishTub']; b = BUCKET; rng = random.Random(51)
    zu = s['water_z'] / sz; ru = b['bottom_r'] + (b['top_r'] - b['bottom_r']) * (zu - b['floor_z']) / (b['h'] - b['floor_z'])
    K.cyl('Water_Surface', (0, 0, s['water_z'] - .002), ru * sx - .002, .004, water, 64, bevel=0)
    L = s['fish_len']
    for i in range(s['fish']):
        a = i * math.tau / s['fish'] + .4; r = .1; c = Vector((r * math.cos(a), r * math.sin(a), s['water_z'] - .006)); hd = a + math.pi / 2 + rng.uniform(-.3, .3)
        K.ellipsoid('Carp_Body', c, (L * .36, .022, .03), fishback, (0, 0, hd), 24)
        K.ellipsoid('Carp_Belly', c + Vector((0, 0, -.008)), (L * .33, .02, .022), fishbelly, (0, 0, hd), 16)
        fwd = Vector((math.cos(hd), math.sin(hd), 0)); side = Vector((-math.sin(hd), math.cos(hd), 0))
        tb = c - fwd * L * .34; tt = c - fwd * L * .52
        o = K.mesh('Carp_Tail', [tuple(tb), tuple(tt + side * .03 + Vector((0, 0, .005))), tuple(tt - fwd * -.01), tuple(tt - side * .03 + Vector((0, 0, .005)))], [(0, 1, 2), (0, 2, 3)], fishback)
        o.modifiers.new('Fin_Thickness', 'SOLIDIFY').thickness = .002
        d0, d1 = c + fwd * .02 + Vector((0, 0, .028)), c - fwd * .04 + Vector((0, 0, .028))
        o = K.mesh('Carp_Dorsal_Fin', [tuple(d0), tuple(d1), tuple(c - fwd * .01 + Vector((0, 0, .045)))], [(0, 1, 2)], fishback); o.modifiers.new('Fin_Thickness', 'SOLIDIFY').thickness = .0015
        for sg in (-1, 1): K.ellipsoid('Carp_Eye', c + fwd * L * .27 + side * sg * .016 + Vector((0, 0, .008)), (.004, .004, .004), dark, segs=10)


BUILDERS = {'RiceSack': rice_sack, 'CuredMeatRack': cured_rack, 'RadishCrate': radish_crate, 'VegetableBasket': vegetable_basket,
            'EggBasket': egg_basket, 'FishTub': fish_tub}
ids = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None
K.build_all(ROOT, BUILDERS, NAMES, DETAILS, SPECS, 'FreshIngredients13', make_materials, ids)
