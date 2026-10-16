"""Shared design specs for TownLife09 (town props + inn).

Pure Python/numpy; no bpy. Each asset is a list of parts built from simple
primitives. The concept sketcher draws the non-detail parts as ten-angle
reference images first; the Blender builder then models every part (adds
detail, bevels and materials) on top of those references.

Conventions: metres, Z up, front faces Blender -Y, origin at bottom centre.
"""
import math
import numpy as np

# name -> (linear RGB for Blender, sRGB-ish for sketches)
PALETTE = {
    'stone':   ((.20, .23, .22), (118, 128, 124)),
    'pale':    ((.42, .43, .39), (176, 176, 164)),
    'plaster': ((.62, .58, .50), (214, 205, 186)),
    'timber':  ((.12, .055, .025), (92, 58, 38)),
    'board':   ((.30, .16, .075), (150, 102, 66)),
    'lacquer': ((.30, .045, .03), (150, 48, 38)),
    'tile':    ((.07, .08, .09), (66, 72, 80)),
    'bamboo':  ((.42, .36, .16), (184, 166, 104)),
    'straw':   ((.50, .40, .19), (198, 172, 110)),
    'clay':    ((.36, .15, .07), (166, 104, 70)),
    'glaze':   ((.10, .14, .12), (82, 100, 92)),
    'paper':   ((.72, .68, .56), (232, 222, 196)),
    'rope':    ((.38, .30, .17), (170, 148, 108)),
    'iron':    ((.06, .06, .06), (60, 60, 62)),
    'brass':   ((.45, .32, .10), (196, 160, 84)),
    'cloth':   ((.12, .22, .17), (90, 128, 108)),
    'lantern': ((.62, .08, .04), (210, 66, 48)),
    'water':   ((.05, .10, .12), (60, 88, 98)),
}


class Part:
    def __init__(self, name, verts, faces, color, smooth=False, detail=False, bevel=True):
        self.name, self.color, self.smooth, self.detail, self.bevel = name, color, smooth, detail, bevel
        self.verts = np.asarray(verts, float)
        self.faces = [list(f) for f in faces]


# ---------------------------------------------------------------- primitives
def _rz(v, a):
    c, s = math.cos(a), math.sin(a)
    v = np.asarray(v, float)
    return np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c, v[:, 2]], 1)


HEX_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def hexa(corners):
    """8 corners: bottom loop (ccw from above) then top loop."""
    return corners, HEX_FACES


def box(c, s, rz=0.0):
    x, y, z = s[0] / 2, s[1] / 2, s[2] / 2
    v = np.array([(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
                  (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)])
    return _rz(v, rz) + c, HEX_FACES


def beam(a, b, w, h=None, up=(0, 0, 1)):
    """Rectangular bar from a to b; w across, h along `up`."""
    h = w if h is None else h
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    d /= np.linalg.norm(d)
    u = np.asarray(up, float)
    if abs(np.dot(u, d)) > .95:
        u = np.array([1., 0, 0]) if abs(d[0]) < .9 else np.array([0, 1., 0])
    side = np.cross(d, u)
    side /= np.linalg.norm(side)
    u = np.cross(side, d)
    sw, sh = side * w / 2, u * h / 2
    ring = [-sw - sh, sw - sh, sw + sh, -sw + sh]
    v = [a + r for r in ring] + [b + r for r in ring]
    faces = [(0, 1, 2, 3)[::-1], (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return np.array(v), faces


def lathe(c, profile, n=24, start=0.0):
    """Revolve closed (r, z) loop about the Z axis through c."""
    verts, faces, m = [], [], len(profile)
    for i in range(n):
        a = start + 2 * math.pi * i / n
        for r, z in profile:
            verts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2] + z))
    for i in range(n):
        j = (i + 1) % n
        for k in range(m):
            kk = (k + 1) % m
            faces.append((i * m + k, j * m + k, j * m + kk, i * m + kk))
    return np.array(verts), faces


def cyl(c, r, h, n=16, r2=None):
    r2 = r if r2 is None else r2
    return lathe(c, [(0, 0), (r, 0), (r2, h), (0, h)], n)


def tube(c, r_out, r_in, h, n=24):
    return lathe(c, [(r_in, 0), (r_out, 0), (r_out, h), (r_in, h)], n)


def rod(a, b, r, n=8):
    a, b = np.asarray(a, float), np.asarray(b, float)
    v, f = cyl((0, 0, 0), r, np.linalg.norm(b - a), n)
    d = (b - a) / np.linalg.norm(b - a)
    z = np.array([0, 0, 1.])
    ax = np.cross(z, d)
    s, cth = np.linalg.norm(ax), np.dot(z, d)
    if s < 1e-9:
        R = np.eye(3) if cth > 0 else np.diag([1, -1, -1])
    else:
        ax /= s
        K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        R = np.eye(3) + s * K + (1 - cth) * K @ K
    return v @ R.T + a, f


def prism(c, w, d, h, ridge='x'):
    """Solid gable-end prism: rectangle w (x) by d (y) rising to a ridge."""
    x, y = w / 2, d / 2
    if ridge == 'x':
        v = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0), (-x, 0, h), (x, 0, h)]
        f = [(0, 3, 2, 1), (0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    else:
        v = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0), (0, -y, h), (0, y, h)]
        f = [(0, 3, 2, 1), (1, 2, 5, 4), (3, 0, 4, 5), (0, 1, 4), (2, 3, 5)]
    return np.array(v) + c, f


# ------------------------------------------------------------ asset builder
class Asset:
    def __init__(self):
        self.parts = []

    def add(self, name, geo, color, **kw):
        v, f = geo
        self.parts.append(Part(name, v, f, color, **kw))

    def gable_roof(self, name, c, w, d, h, th=.12, color='tile', ribs=.28, ridge_cap=True, curl=0.0):
        """Two sloped slabs, ridge along x, eaves at c.z (outer bottom)."""
        cx, cy, cz = c
        for sgn in (-1, 1):
            e0, e1 = np.array([0, sgn * d / 2, 0.]), np.array([0, 0, h])
            n = np.array([0, sgn * h, d / 2])
            n /= np.linalg.norm(n)
            t = n * th
            bot = [(-w / 2, *(e0[1:])), (w / 2, *(e0[1:])), (w / 2, *(e1[1:])), (-w / 2, *(e1[1:]))]
            bot = np.array(bot)
            top = bot + t
            if sgn > 0:
                bot, top = bot[[1, 0, 3, 2]], top[[1, 0, 3, 2]]
            self.add(f'{name}_Slope_{"N" if sgn > 0 else "S"}',
                     hexa(np.vstack([bot, top]) + c), color)
            if ribs:
                k = int(w / ribs)
                for i in range(k + 1):
                    x = -w / 2 + .1 + i * (w - .2) / k
                    a = np.array([x, e0[1], e0[2]]) + t * 1.4 + c
                    b = np.array([x, e1[1], e1[2]]) + t * 1.4 + c
                    self.add(f'{name}_TileRow', rod(a, b, .045, 6), color, smooth=True, detail=True, bevel=False)
            # fascia board along eave
            self.add(f'{name}_Fascia', beam(np.array([-w / 2, e0[1], e0[2] + th / 2]) + c,
                                            np.array([w / 2, e0[1], e0[2] + th / 2]) + c, th * 1.1, th * 1.4),
                     'timber', detail=True)
        if ridge_cap:
            rc = np.array([0, 0, h + th * 1.3]) + c
            self.add(f'{name}_Ridge', beam(rc - (w / 2 + .05, 0, 0), rc + (w / 2 + .05, 0, 0), th * 2.2, th * 1.6), color)
            if curl:
                for sx in (-1, 1):
                    p = rc + (sx * (w / 2 + .05), 0, 0)
                    self.add(f'{name}_Ridge_Ornament', beam(p, p + (sx * curl * .5, 0, curl), th * 1.8, th * 1.6), color)


# ----------------------------------------------------------------- assets
def town_well():
    A = Asset()
    A.add('Well_Base_Step', tube((0, 0, 0), 1.3, .72, .12, 32), 'pale')
    # stacked stone courses
    for i in range(4):
        A.add(f'Well_Ring_Course_{i}', tube((0, 0, .12 + i * .17), .9 - i * .01, .66, .17, 28), 'stone' if i % 2 == 0 else 'pale')
    A.add('Well_Rim_Cap', tube((0, 0, .80), .96, .62, .1, 32), 'pale')
    A.add('Well_Water', cyl((0, 0, .25), .66, .02, 24), 'water', bevel=False)
    for x in (-1.1, 1.1):
        A.add('Well_Post', box((x, 0, 1.25), (.16, .16, 2.5)), 'timber')
        A.add('Well_Post_Footing', box((x, 0, .25), (.32, .32, .26)), 'stone')
    A.add('Well_Crossbeam', box((0, 0, 2.42), (2.5, .18, .16)), 'timber')
    A.gable_roof('Well_Roof', (0, 0, 2.48), 2.9, 1.7, .62, th=.07, ribs=.22, curl=.18)
    A.add('Well_Roof_Gable', prism((0, 0, 2.48), 2.3, 1.3, .5), 'board')
    # windlass
    A.add('Well_Windlass_Drum', rod((-.8, 0, 1.75), (.8, 0, 1.75), .09, 12), 'board', smooth=True)
    A.add('Well_Windlass_Axle', rod((-1.2, 0, 1.75), (1.2, 0, 1.75), .03, 8), 'iron', smooth=True)
    A.add('Well_Crank_Arm', beam((1.22, 0, 1.75), (1.22, -.32, 1.6), .05, .05), 'timber')
    A.add('Well_Crank_Handle', rod((1.22, -.32, 1.6), (1.42, -.32, 1.6), .025, 8), 'timber', smooth=True)
    for x in np.linspace(-.5, .5, 7):
        A.add('Well_Rope_Coil', rod((x - .03, 0, 1.75), (x + .03, 0, 1.75), .102, 12), 'rope', smooth=True, detail=True)
    A.add('Well_Rope', rod((.15, -.09, 1.75), (.15, -.09, 1.22), .014, 6), 'rope', smooth=True)
    # bucket hanging above the shaft
    A.add('Well_Bucket', lathe((.15, -.09, .92), [(.0, 0), (.15, 0), (.18, .26), (.165, .26), (.135, .03), (0, .03)], 18), 'board', smooth=True)
    for z in (.05, .2):
        A.add('Well_Bucket_Hoop', tube((.15, -.09, .92 + z), .155 + z * .11, .14 + z * .11, .03, 18), 'iron', smooth=True)
    A.add('Well_Bucket_Bail', beam((.0, -.09, 1.18), (.30, -.09, 1.18), .02, .02), 'iron')
    for x in (.0, .30):
        A.add('Well_Bucket_Bail_Side', beam((x, -.09, 1.18), (x + (.02 if x < .1 else -.02), -.09, 1.08), .02, .02), 'iron')
    # spare bucket on the ground
    A.add('Well_Spare_Bucket', lathe((-.75, -1.12, .12), [(0, 0), (.16, 0), (.19, .32), (.175, .32), (.145, .03), (0, .03)], 18), 'board', smooth=True)
    A.add('Well_Spare_Bucket_Hoop', tube((-.75, -1.12, .34), .18, .165, .03, 18), 'iron', smooth=True)
    return A


def notice_board():
    A = Asset()
    for x in (-1.15, 1.15):
        A.add('Board_Post', box((x, 0, 1.3), (.16, .16, 2.6)), 'timber')
        A.add('Board_Post_Base', box((x, 0, .12), (.34, .34, .24)), 'stone')
        A.add('Board_Post_Brace', beam((x, -.35, 0.02), (x, -.05, .6), .08, .08), 'timber')
        A.add('Board_Post_Brace', beam((x, .35, 0.02), (x, .05, .6), .08, .08), 'timber')
    A.add('Board_Panel', box((0, 0, 1.45), (2.16, .07, 1.2)), 'board')
    A.add('Board_Frame_Top', box((0, -.01, 2.08), (2.3, .1, .1)), 'timber')
    A.add('Board_Frame_Bottom', box((0, -.01, .82), (2.3, .1, .1)), 'timber')
    A.add('Board_Ledge', box((0, -.12, .86), (2.2, .2, .04)), 'timber')
    A.gable_roof('Board_Roof', (0, 0, 2.48), 2.9, .95, .32, th=.06, ribs=.2, curl=.12)
    A.add('Board_Roof_Gable', prism((0, 0, 2.48), 2.4, .6, .22), 'board')
    # pinned papers (blank, no lettering)
    sheets = [(-.72, 1.6, .5, .62, 3), (-.12, 1.72, .42, .52, -4), (.48, 1.52, .55, .7, 2),
              (-.45, 1.08, .38, .32, -2), (.2, 1.1, .5, .3, 5), (.78, 1.1, .3, .38, -6)]
    for i, (x, z, w, h, rot) in enumerate(sheets):
        geo = box((0, 0, 0), (w, .006, h))
        v = geo[0] @ np.array([[math.cos(math.radians(rot)), 0, -math.sin(math.radians(rot))], [0, 1, 0],
                               [math.sin(math.radians(rot)), 0, math.cos(math.radians(rot))]]).T
        A.add(f'Notice_Paper_{i}', (v + (x, -.04, z), geo[1]), 'paper', bevel=False)
        A.add(f'Notice_Pin_{i}', rod((x, -.04, z + h / 2 - .04), (x, -.065, z + h / 2 - .04), .016, 8),
              'brass', smooth=True, detail=True, bevel=False)
    return A


def bamboo_basket():
    A = Asset()
    A.add('Basket_Base', cyl((0, 0, 0), .19, .04, 20), 'bamboo', smooth=True)
    n = 28
    for i in range(n):
        a = 2 * math.pi * i / n
        p0 = (.19 * math.cos(a), .19 * math.sin(a), .02)
        p1 = (.26 * math.cos(a), .26 * math.sin(a), .58)
        A.add('Basket_Stave', beam(p0, p1, .03, .012, up=(math.cos(a), math.sin(a), 0)), 'bamboo')
    A.add('Basket_Body_Weave', lathe((0, 0, .02), [(.18, 0), (.193, 0), (.253, .56), (.24, .56)], 28), 'straw', smooth=True)
    for z in np.arange(.08, .55, .07):
        r = .19 + (.26 - .19) * z / .58
        A.add('Basket_Weave_Band', tube((0, 0, z), r + .012, r - .004, .025, 28), 'bamboo', smooth=True, detail=True)
    A.add('Basket_Rim', tube((0, 0, .57), .285, .245, .05, 28), 'board', smooth=True)
    for x in (-.1, .1):
        top = (x, math.sqrt(.253 ** 2 - x * x) + .02, .52)
        bot = (x, math.sqrt(.202 ** 2 - x * x) + .02, .1)
        A.add('Basket_Strap', beam(top, bot, .05, .014, up=(0, 1, 0)), 'rope')
        A.add('Basket_Strap_Loop', beam(top, (x, top[1] + .06, .4), .05, .014, up=(0, 1, 0)), 'rope')
        A.add('Basket_Strap_Loop', beam((x, top[1] + .06, .4), (x, bot[1] + .05, .2), .05, .014, up=(0, 1, 0)), 'rope')
    # herbs bundle peeking out
    for i, (x, y) in enumerate([(-.06, .02), (.07, -.05), (.0, .09)]):
        A.add(f'Basket_Herb_Bundle_{i}', cyl((x, y, .45), .06, .22, 8, .085), 'cloth', smooth=True)
    return A


def wooden_crate():
    A = Asset()
    s = .7
    A.add('Crate_Core', box((0, 0, s / 2), (s - .02, s - .02, s - .02)), 'board')
    for i in range(4):
        z = .09 + i * .17
        for (c, d) in [((0, -s / 2 + .005, z), (s - .1, .02, .14)), ((0, s / 2 - .005, z), (s - .1, .02, .14)),
                       ((-s / 2 + .005, 0, z), (.02, s - .1, .14)), ((s / 2 - .005, 0, z), (.02, s - .1, .14))]:
            A.add('Crate_Plank', box(c, d), 'board', detail=True)
    for x in (-1, 1):
        for y in (-1, 1):
            A.add('Crate_Corner_Post', box((x * (s / 2 - .03), y * (s / 2 - .03), s / 2), (.08, .08, s)), 'timber')
    for z in (.04, s - .04):
        for (c, d) in [((0, -s / 2 + .03, z), (s, .08, .08)), ((0, s / 2 - .03, z), (s, .08, .08)),
                       ((-s / 2 + .03, 0, z), (.08, s, .08)), ((s / 2 - .03, 0, z), (.08, s, .08))]:
            A.add('Crate_Frame', box(c, d), 'timber')
    A.add('Crate_Diagonal_Front', beam((-s / 2 + .07, -s / 2 - .005, .08), (s / 2 - .07, -s / 2 - .005, s - .08), .07, .03, up=(0, -1, 0)), 'timber')
    A.add('Crate_Diagonal_Side', beam((s / 2 + .005, -s / 2 + .07, .08), (s / 2 + .005, s / 2 - .07, s - .08), .07, .03, up=(1, 0, 0)), 'timber')
    A.add('Crate_Lid', box((0, 0, s + .02), (s - .04, s - .04, .04)), 'board')
    A.add('Crate_Rope_Handle', rod((-.2, -s / 2 - .03, s - .16), (.2, -s / 2 - .03, s - .16), .015, 6), 'rope', smooth=True)
    return A


def clay_jar():
    A = Asset()
    prof = [(0, 0), (.16, 0), (.21, .06), (.27, .22), (.28, .34), (.24, .5), (.15, .6), (.14, .64), (.17, .67), (.17, .7),
            (.12, .7), (.11, .64), (0, .64)]
    A.add('Jar_Body', lathe((0, 0, 0), prof, 32), 'clay', smooth=True)
    A.add('Jar_Glaze_Band', tube((0, 0, .26), .292, .268, .1, 32), 'glaze', smooth=True)
    A.add('Jar_Lid_Cloth', lathe((0, 0, .68), [(0, 0), (.2, 0), (.22, -.06), (.2, -.07), (.19, .03), (0, .06)], 24), 'cloth', smooth=True)
    A.add('Jar_Lid_Tie', tube((0, 0, .63), .175, .155, .025, 24), 'rope', smooth=True)
    for a in (0, math.pi):
        A.add('Jar_Lug_Handle', tube((.24 * math.cos(a), .24 * math.sin(a), .48), .05, .03, .03, 10), 'clay', smooth=True, detail=True)
    return A


def firewood_stack():
    A = Asset()
    A.add('Firewood_Sleeper_F', box((0, -.28, .05), (1.5, .1, .1)), 'timber')
    A.add('Firewood_Sleeper_B', box((0, .28, .05), (1.5, .1, .1)), 'timber')
    for x in (-.72, .72):
        A.add('Firewood_End_Stake', box((x, -.36, .55), (.07, .07, 1.1)), 'timber')
        A.add('Firewood_End_Stake', box((x, .36, .55), (.07, .07, 1.1)), 'timber')
    rng = np.random.default_rng(9)
    r = .075
    for row in range(6):
        k = 9 if row % 2 == 0 else 8
        z = .1 + r + row * r * 1.75
        for i in range(k):
            x = -.6 + (i + (0 if row % 2 == 0 else .5)) * (1.2 / 8)
            rr = r * rng.uniform(.82, 1.05)
            jitter = rng.uniform(-.04, .04)
            A.add('Firewood_Log', rod((x, -.34 + jitter, z), (x, .34 + jitter, z), rr, 9), 'board', smooth=True)
            A.add('Firewood_Log_EndGrain', rod((x, -.345 + jitter, z), (x, -.335 + jitter, z), rr * .8, 9), 'straw',
                  smooth=True, detail=True, bevel=False)
    A.add('Firewood_Axe_Block', cyl((.95, -.3, 0), .2, .42, 14), 'board', smooth=True)
    A.add('Firewood_Axe_Handle', beam((.95, -.3, .38), (1.1, -.55, .9), .04, .04), 'timber')
    A.add('Firewood_Axe_Head', box((.97, -.28, .42), (.04, .16, .1), rz=.5), 'iron')
    return A


def bamboo_fence():
    A = Asset()
    L = 2.0
    for x in (-L / 2, L / 2):
        A.add('Fence_Post', cyl((x, 0, 0), .06, 1.25, 10), 'timber', smooth=True)
        A.add('Fence_Post_Cap', cyl((x, 0, 1.25), .07, .05, 10, .03), 'timber', smooth=True)
    for z in (.35, .85):
        A.add('Fence_Rail', rod((-L / 2, -.06, z), (L / 2, -.06, z), .03, 8), 'bamboo', smooth=True)
        A.add('Fence_Rail_Tie', tube((-L / 2, -.06, z - .03), .075, .06, .06, 10), 'rope', smooth=True, detail=True)
        A.add('Fence_Rail_Tie', tube((L / 2, -.06, z - .03), .075, .06, .06, 10), 'rope', smooth=True, detail=True)
    n = 17
    for i in range(n):
        x = -L / 2 + .12 + i * (L - .24) / (n - 1)
        h = 1.05 + .06 * math.sin(i * 1.7)
        A.add('Fence_Picket', cyl((x, -.1, 0), .022, h, 8), 'bamboo', smooth=True)
        A.add('Fence_Picket_Node', tube((x, -.1, h * .55), .026, .02, .015, 8), 'straw', smooth=True, detail=True)
    return A


def fence_gate():
    A = Asset()
    for x in (-1.05, 1.05):
        A.add('Gate_Post', box((x, 0, 1.15), (.16, .16, 2.3)), 'timber')
        A.add('Gate_Post_Base', box((x, 0, .1), (.28, .28, .2)), 'stone')
    A.add('Gate_Lintel', box((0, 0, 2.2), (2.5, .14, .14)), 'timber')
    A.gable_roof('Gate_Roof', (0, 0, 2.3), 2.9, .9, .3, th=.06, ribs=.2, curl=.12)
    A.add('Gate_Roof_Gable', prism((0, 0, 2.3), 2.3, .5, .2), 'board')
    for side in (-1, 1):
        x0 = side * .97
        xm = side * .04
        cx = (x0 + xm) / 2
        w = abs(x0 - xm)
        for z in (.25, 1.35):
            A.add('Gate_Leaf_Rail', box((cx, -.03, z), (w, .05, .07)), 'board')
        A.add('Gate_Leaf_Brace', beam((x0, -.06, .28), (xm, -.06, 1.32), .06, .03, up=(0, -1, 0)), 'board')
        for i in range(6):
            x = x0 + (xm - x0) * (i + .5) / 6
            A.add('Gate_Leaf_Bamboo', cyl((x, -.0, .12), .028, 1.42, 8), 'bamboo', smooth=True)
        A.add('Gate_Hinge', box((x0 - side * .01, -.04, .4), (.05, .06, .06)), 'iron', detail=True)
        A.add('Gate_Hinge', box((x0 - side * .01, -.04, 1.2), (.05, .06, .06)), 'iron', detail=True)
    A.add('Gate_Latch', box((0, -.08, .85), (.18, .03, .04)), 'iron')
    return A


def town_inn():
    A = Asset()
    W, D = 12.0, 9.0
    P = .45            # plinth height
    F1, F2 = 3.4, 3.0   # storey heights
    z1 = P
    z2 = P + F1
    zr = z2 + F2
    A.add('Inn_Plinth', box((0, 0, P / 2), (W + .4, D + .4, P)), 'stone')
    A.add('Inn_Front_Steps', box((0, -D / 2 - .45, P / 4), (4.4, .5, P / 2)), 'pale')
    A.add('Inn_Front_Steps', box((0, -D / 2 - .2, P * .75), (4.4, .5, P / 2)), 'pale')
    A.add('Inn_Ground_Floor', box((0, 0, P + .02), (W - .2, D - .2, .04)), 'board', bevel=False)
    xs = np.linspace(-W / 2 + .1, W / 2 - .1, 6)
    ys = np.linspace(-D / 2 + .1, D / 2 - .1, 5)
    # columns
    for x in xs:
        for y in (ys[0], ys[-1]):
            A.add('Inn_Column', box((x, y, z1 + (F1 + F2) / 2), (.24, .24, F1 + F2)), 'lacquer')
    for y in ys[1:-1]:
        for x in (xs[0], xs[-1]):
            A.add('Inn_Column', box((x, y, z1 + (F1 + F2) / 2), (.24, .24, F1 + F2)), 'lacquer')
    # ground floor walls: back and sides solid plaster with timber frame, front lattice
    t = .14
    A.add('Inn_Wall_Back_G', box((0, D / 2 - .1, z1 + F1 / 2), (W - .2, t, F1)), 'plaster')
    for x in (-W / 2 + .1, W / 2 - .1):
        A.add('Inn_Wall_Side_G', box((x, 0, z1 + F1 / 2), (t, D - .2, F1)), 'plaster')
        A.add('Inn_Side_Window_G', box((x + (-.08 if x < 0 else .08), -1.0, z1 + 1.9), (.04, 1.6, 1.0)), 'timber')
    bay = (W - .2) / 5
    for i in range(5):
        cx = -W / 2 + .1 + bay * (i + .5)
        if i in (1, 2, 3):   # open doorway bays with folded-back lattice doors
            for sx in (-1, 1):
                A.add('Inn_Front_Door_Folded', box((cx + sx * (bay / 2 - .2), -D / 2 + .05, z1 + 1.3), (.3, .06, 2.6)), 'board')
            A.add('Inn_Front_Transom', box((cx, -D / 2 + .1, z1 + 2.95), (bay - .24, .1, .7)), 'board')
        else:
            A.add('Inn_Front_Lower_Wall', box((cx, -D / 2 + .1, z1 + .45), (bay - .24, t, .9)), 'plaster')
            A.add('Inn_Front_Lattice_Window', box((cx, -D / 2 + .1, z1 + 2.05), (bay - .24, .08, 2.3)), 'board')
            for k in range(1, 6):
                A.add('Inn_Lattice_Bar', box((cx - (bay - .24) / 2 + k * (bay - .24) / 6, -D / 2 + .05, z1 + 2.05), (.04, .04, 2.3)), 'timber', detail=True)
            for k in range(1, 6):
                A.add('Inn_Lattice_Bar', box((cx, -D / 2 + .05, z1 + .9 + k * 2.3 / 6), (bay - .24, .04, .04)), 'timber', detail=True)
    # second floor
    A.add('Inn_Floor_Beam_Front', box((0, -D / 2 + .1, z2 - .12), (W, .26, .3)), 'timber')
    A.add('Inn_Floor_Beam_Back', box((0, D / 2 - .1, z2 - .12), (W, .26, .3)), 'timber')
    # slab with a stair opening at the back-left (x -5.9..-1.4, y 2.9..4.4)
    A.add('Inn_Upper_Floor_Main', box((.0, -1.15, z2 + .03), (W - .2, D - .2 - 2.3, .14)), 'board')
    A.add('Inn_Upper_Floor_BackRight', box((2.3, 3.32, z2 + .03), (7.2, 2.16, .14)), 'board')
    A.add('Inn_Upper_Floor_BackLeft_Strip', box((-3.65, 4.25, z2 + .03), (4.5, .3, .14)), 'board')
    # balcony
    A.add('Inn_Balcony_Deck', box((0, -D / 2 - .5, z2 + .02), (W - .4, 1.0, .12)), 'board')
    for x in np.linspace(-W / 2 + .3, W / 2 - .3, 11):
        A.add('Inn_Balcony_Post', box((x, -D / 2 - .95, z2 + .5), (.08, .08, .9)), 'lacquer')
    A.add('Inn_Balcony_Rail', box((0, -D / 2 - .95, z2 + .95), (W - .4, .1, .08)), 'lacquer')
    A.add('Inn_Balcony_Rail_Low', box((0, -D / 2 - .95, z2 + .2), (W - .4, .08, .06)), 'lacquer')
    for x in np.linspace(-W / 2 + .3, W / 2 - .3, 41):
        A.add('Inn_Balcony_Baluster', box((x, -D / 2 - .95, z2 + .58), (.03, .03, .74)), 'timber', detail=True)
    for x in np.linspace(-W / 2 + .3, W / 2 - .3, 6):
        A.add('Inn_Balcony_Bracket', beam((x, -D / 2, z2 - .8), (x, -D / 2 - .9, z2 - .05), .1, .1), 'timber')
    # pent eave over the ground floor front
    A.add('Inn_Pent_Eave', hexa(np.array([(-W / 2 - .3, -D / 2 - 1.5, z2 - .55), (W / 2 + .3, -D / 2 - 1.5, z2 - .55),
                                          (W / 2 + .3, -D / 2 - .05, z2 - .15), (-W / 2 - .3, -D / 2 - .05, z2 - .15),
                                          (-W / 2 - .3, -D / 2 - 1.5, z2 - .48), (W / 2 + .3, -D / 2 - 1.5, z2 - .48),
                                          (W / 2 + .3, -D / 2 - .05, z2 - .08), (-W / 2 - .3, -D / 2 - .05, z2 - .08)])), 'tile')
    # upper walls set back 0.0, lattice windows
    A.add('Inn_Wall_Back_U', box((0, D / 2 - .1, z2 + F2 / 2), (W - .2, t, F2)), 'plaster')
    for x in (-W / 2 + .1, W / 2 - .1):
        A.add('Inn_Wall_Side_U', box((x, 0, z2 + F2 / 2), (t, D - .2, F2)), 'plaster')
    for i in range(5):
        cx = -W / 2 + .1 + bay * (i + .5)
        A.add('Inn_Upper_Front_Lower', box((cx, -D / 2 + .1, z2 + .45), (bay - .24, t, .9)), 'plaster')
        A.add('Inn_Upper_Front_Lattice', box((cx, -D / 2 + .1, z2 + 1.9), (bay - .24, .08, 2.0)), 'board')
        for k in range(1, 4):
            A.add('Inn_Lattice_Bar', box((cx - (bay - .24) / 2 + k * (bay - .24) / 4, -D / 2 + .05, z2 + 1.9), (.04, .04, 2.0)), 'timber', detail=True)
        A.add('Inn_Lattice_Bar', box((cx, -D / 2 + .05, z2 + 1.9), (bay - .24, .04, .04)), 'timber', detail=True)
    for x in (-W / 2 + .1, W / 2 - .1):
        for y in (-2.2, 2.4):
            A.add('Inn_Side_Window_U', box((x + (-.08 if x < 0 else .08), y, z2 + 1.7), (.04, 1.4, .9)), 'timber')
    for i in (0, 2, 4):
        cx = -W / 2 + .1 + bay * (i + .5)
        A.add('Inn_Back_Window_U', box((cx, D / 2 - .02, z2 + 1.7), (1.1, .04, .9)), 'timber')
    # main roof
    A.add('Inn_Top_Beam', box((0, 0, zr - .1), (W, D, .2)), 'timber')
    A.add('Inn_Roof_Gable_Wall', prism((0, 0, zr), W - .2, D - .2, 2.3), 'plaster')
    A.gable_roof('Inn_Roof', (0, 0, zr - .15), W + 1.8, D + 2.0, 2.9, th=.16, ribs=.32, curl=.6)
    # signboard (blank plaque) and lanterns
    A.add('Inn_Signboard', box((0, -D / 2 - .06, z1 + 2.92), (2.2, .08, .6)), 'lacquer')
    A.add('Inn_Signboard_Frame', box((0, -D / 2 - .02, z1 + 2.92), (2.4, .06, .74)), 'brass')
    for sx in (-1, 1):
        x = sx * (bay * 1.5)
        A.add('Inn_Lantern_Cord', rod((x, -D / 2 - 1.3, z2 - .5), (x, -D / 2 - 1.3, z2 - .9), .01, 6), 'rope', smooth=True)
        A.add('Inn_Lantern', lathe((x, -D / 2 - 1.3, z2 - 1.6), [(0, 0), (.16, 0), (.26, .12), (.28, .35), (.24, .58), (.14, .7), (0, .7)], 16), 'lantern', smooth=True)
        A.add('Inn_Lantern_Cap', cyl((x, -D / 2 - 1.3, z2 - .92), .12, .05, 12), 'timber', smooth=True)
        A.add('Inn_Lantern_Base', cyl((x, -D / 2 - 1.3, z2 - 1.65), .12, .05, 12), 'timber', smooth=True)
    # ---- interior: dining hall (front), counter, stairs, kitchen annex
    for (x, y) in [(-3.0, -2.6), (0.0, -2.6), (3.0, -2.6), (-1.5, .2), (1.5, .2)]:
        A.add('Inn_Table_Top', box((x, y, z1 + .78), (1.0, 1.0, .06)), 'board')
        for dx in (-.42, .42):
            for dy in (-.42, .42):
                A.add('Inn_Table_Leg', box((x + dx, y + dy, z1 + .38), (.07, .07, .76)), 'timber', detail=True)
        for (bx, by, bw, bd) in [(x, y - .85, 1.1, .3), (x, y + .85, 1.1, .3)]:
            A.add('Inn_Bench_Seat', box((bx, by, z1 + .44), (bw, bd, .05)), 'board')
            for dx in (-.45, .45):
                A.add('Inn_Bench_Leg', box((bx + dx, by, z1 + .21), (.06, .24, .42)), 'timber', detail=True)
    A.add('Inn_Counter', box((4.3, 1.2, z1 + .55), (2.6, .7, 1.1)), 'timber')
    A.add('Inn_Counter_Top', box((4.3, 1.2, z1 + 1.13), (2.8, .85, .06)), 'board')
    A.add('Inn_Wine_Shelf', box((4.3, 3.9, z1 + 1.2), (2.6, .45, 2.4)), 'timber')
    for i in range(6):
        A.add('Inn_Wine_Jar', lathe((3.3 + i * .4, 3.9, z1 + 1.0), [(0, 0), (.1, 0), (.15, .12), (.12, .28), (.06, .32), (0, .32)], 12), 'clay', smooth=True, detail=True)
    # stairs: 17 risers along +x at back-left, from x=-5.75 to -1.5
    steps = 17
    rise = F1 / steps
    run = .25
    for i in range(steps):
        h = (i + 1) * rise
        A.add(f'Inn_Stair_Step_{i:02d}', box((-5.75 + (i + .5) * run, 3.65, z1 + h - .04), (run + .02, 1.1, .08)), 'board')
    A.add('Inn_Stair_Stringer', beam((-5.75, 3.08, z1), (-5.75 + steps * run, 3.08, z2), .06, .3), 'timber')
    A.add('Inn_Stair_Stringer', beam((-5.75, 4.22, z1), (-5.75 + steps * run, 4.22, z2), .06, .3), 'timber')
    A.add('Inn_Stair_Handrail', beam((-5.75, 3.06, z1 + .95), (-5.75 + steps * run, 3.06, z2 + .95), .06, .06), 'lacquer')
    # upper guest rooms: three rooms along the back half, corridor along the front
    A.add('Inn_Upper_Corridor_Wall', box((1.4, .6, z2 + 1.5), (W - .2 - 2.8 - .1, .1, 3.0)), 'plaster')
    for x in (-1.3, 1.65, 4.6):
        A.add('Inn_Room_Partition', box((x, 2.6, z2 + 1.5), (.1, 4.0, 3.0)), 'plaster')
    for cx in (.17, 3.12, 5.3):
        A.add('Inn_Room_Door', box((cx, .52, z2 + 1.05), (.9, .06, 2.1)), 'board')
    for cx in (.17, 3.12):
        A.add('Inn_Bed_Frame', box((cx - .5, 3.3, z2 + .3), (1.1, 2.0, .45)), 'timber')
        A.add('Inn_Bed_Quilt', box((cx - .5, 3.4, z2 + .58), (1.0, 1.7, .12)), 'cloth')
        A.add('Inn_Bed_Pillow', box((cx - .5, 4.1, z2 + .62), (.6, .25, .12)), 'paper')
    A.add('Inn_Bed_Frame', box((5.4, 3.3, z2 + .3), (.95, 2.0, .45)), 'timber')
    A.add('Inn_Bed_Quilt', box((5.4, 3.4, z2 + .58), (.85, 1.7, .12)), 'cloth')
    # kitchen annex (rear right lean-to with chimney)
    kx, ky = 3.6, D / 2 + 1.7
    A.add('Inn_Kitchen_Plinth', box((kx, ky, P / 2), (4.6, 3.4, P)), 'stone')
    A.add('Inn_Kitchen_Wall_Back', box((kx, ky + 1.55, z1 + 1.4), (4.4, .14, 2.8)), 'plaster')
    for sx in (-1, 1):
        A.add('Inn_Kitchen_Wall_Side', box((kx + sx * 2.15, ky, z1 + 1.4), (.14, 3.2, 2.8)), 'plaster')
    A.add('Inn_Kitchen_Door_Opening_Frame', box((kx, D / 2 - .17, z1 + 1.1), (1.0, .06, 2.2)), 'timber')
    A.add('Inn_Kitchen_Roof', hexa(np.array([(kx - 2.5, D / 2 - .1, z1 + 3.3), (kx + 2.5, D / 2 - .1, z1 + 3.3),
                                             (kx + 2.5, ky + 2.1, z1 + 2.5), (kx - 2.5, ky + 2.1, z1 + 2.5),
                                             (kx - 2.5, D / 2 - .1, z1 + 3.42), (kx + 2.5, D / 2 - .1, z1 + 3.42),
                                             (kx + 2.5, ky + 2.1, z1 + 2.62), (kx - 2.5, ky + 2.1, z1 + 2.62)])), 'tile')
    A.add('Inn_Kitchen_Stove', box((kx + .6, ky + 1.0, z1 + .4), (2.2, .9, .8)), 'stone')
    for dx in (-.4, .5):
        A.add('Inn_Stove_Wok', lathe((kx + .6 + dx, ky + 1.0, z1 + .72), [(0, 0), (.12, .02), (.3, .12), (.3, .14), (.12, .05), (0, .04)], 16), 'iron', smooth=True)
    A.add('Inn_Kitchen_Chimney', box((kx + 1.4, ky + 1.25, z1 + 2.2), (.5, .5, 3.6)), 'stone')
    A.add('Inn_Kitchen_Chimney_Cap', box((kx + 1.4, ky + 1.25, z1 + 4.05), (.7, .7, .1)), 'tile')
    A.add('Inn_Kitchen_Chopping_Table', box((kx - 1.2, ky + .2, z1 + .4), (1.2, .6, .8)), 'board')
    A.add('Inn_Kitchen_Water_Vat', lathe((kx - 1.6, ky + 1.1, z1), [(0, 0), (.25, 0), (.35, .3), (.32, .65), (0, .65)], 16), 'glaze', smooth=True)
    return A


ASSETS = {
    'TownWell': dict(name_zh='小鎮水井', build=town_well, category='小鎮生活道具',
                     desc='Round stone well with timber posts, small tiled roof, windlass drum, rope and a hanging wooden bucket; spare bucket on the ground.',
                     size='Approx. 2.5 x 2.1 x 3.2 m; stone ring 1.8 m across, rim 0.9 m high.'),
    'NoticeBoard': dict(name_zh='小鎮公告板', build=notice_board, category='小鎮生活道具',
                        desc='Two-post timber notice board with braced feet, plank panel, tiny tiled roof and six blank pinned paper notices (no lettering).',
                        size='Approx. 2.9 x 1.0 x 2.9 m; board face 2.2 x 1.2 m.'),
    'BambooBasket': dict(name_zh='竹簍', build=bamboo_basket, category='通用道具',
                         desc='Tapered woven bamboo back basket with staves, weave bands, wooden rim, two rope straps and herb bundles inside.',
                         size='Approx. 0.6 x 0.6 x 0.67 m.'),
    'WoodenCrate': dict(name_zh='木箱', build=wooden_crate, category='通用道具',
                        desc='0.7 m plank crate with dark timber corner posts, frame, diagonal braces, flat lid and rope handle.',
                        size='Approx. 0.72 x 0.76 x 0.74 m.'),
    'ClayJar': dict(name_zh='陶罐', build=clay_jar, category='通用道具',
                    desc='Round-bellied terracotta storage jar with a dark green glaze band, cloth lid tied with rope and two small lugs.',
                    size='Approx. 0.6 x 0.6 x 0.74 m.'),
    'FirewoodStack': dict(name_zh='柴堆', build=firewood_stack, category='通用道具',
                          desc='Six rows of split logs on two sleepers held by four stakes, with a chopping block and axe beside it.',
                          size='Approx. 2.0 x 0.8 x 1.1 m.'),
    'BambooFence': dict(name_zh='竹籬笆段', build=bamboo_fence, category='庭院與圍欄',
                        desc='2 m repeatable fence segment: two round timber posts, two bamboo rails with rope ties and seventeen bamboo pickets.',
                        size='2.1 x 0.2 x 1.3 m; posts at x = +/-1.0 m for tiling.'),
    'FenceGate': dict(name_zh='籬笆院門', build=fence_gate, category='庭院與圍欄',
                      desc='Courtyard gate: two posts on stone bases, lintel with small tiled roof and two bamboo gate leaves with braces, hinges and latch.',
                      size='Approx. 2.9 x 0.9 x 2.8 m; clear opening 1.9 m wide, 2.1 m high.'),
    'TownInn': dict(name_zh='食肆客棧', build=town_inn, category='小鎮建築',
                    desc='Two-storey 12 x 9 m inn: red lacquered columns, open lattice front, dining hall with five tables, counter and wine shelf, straight stair, three upstairs guest rooms with beds, front balcony, blank signboard, two red lanterns, tiled gable roof and a rear kitchen annex with stove, woks and chimney.',
                    size='Approx. 13.8 x 13 x 9.6 m; floor-to-floor 3.4 m; stair 17 risers of 0.2 m.'),
}

VIEWS = [('01_front', (0, -1, 0), '正面'), ('02_right', (1, 0, 0), '右側'), ('03_rear', (0, 1, 0), '背面'),
         ('04_left', (-1, 0, 0), '左側'), ('05_front_right', (1, -1, .45), '右前斜角'), ('06_rear_right', (1, 1, .45), '右後斜角'),
         ('07_rear_left', (-1, 1, .45), '左後斜角'), ('08_front_left', (-1, -1, .45), '左前斜角'), ('09_top', (0, 0, 1), '垂直俯視'),
         ('10_high_front', (0, -1, 1), '正面高角度')]

VIEW_PHRASE = {
    '01_front': 'straight front elevation, camera level, facing the -Y front',
    '02_right': 'straight right side elevation, camera level',
    '03_rear': 'straight rear elevation, camera level',
    '04_left': 'straight left side elevation, camera level',
    '05_front_right': 'front-right three-quarter view, slightly elevated',
    '06_rear_right': 'rear-right three-quarter view, slightly elevated',
    '07_rear_left': 'rear-left three-quarter view, slightly elevated',
    '08_front_left': 'front-left three-quarter view, slightly elevated',
    '09_top': 'top-down plan view',
    '10_high_front': 'high front bird\'s-eye view at 45 degrees',
}


def prompt_for(aid, view):
    a = ASSETS[aid]
    return ('Use case: stylized-concept. Asset type: Blender modeling reference for a xianxia (Chinese immortal-cultivation) '
            f'open-world town, single game asset: {a["name_zh"]} ({aid}). Design: {a["desc"]} Scale: {a["size"]} '
            'Style: softly beveled stylized 3D game art matching the existing dondon town (dark cedar timber, blue-grey stone, '
            'charcoal tile roofs, restrained jade and ochre accents). '
            f'View: {VIEW_PHRASE[view]}, orthographic, entire object visible on a neutral warm paper background. '
            'No characters, no scenery, no text or lettering, no watermark.')
