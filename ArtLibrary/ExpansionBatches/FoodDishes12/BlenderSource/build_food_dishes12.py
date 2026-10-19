"""FoodDishes12: six cooked dishes in KitchenWare09 containers, plus a table-setting preview.
Run: blender --background --factory-startup -t 4 --python build_food_dishes12.py [-- DishID ...]
Containers are appended from <project>/Models/<Container>/v001 and kept as editable objects under a Container_* empty.
"""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = next(p for p in [ROOT, *ROOT.parents] if (p / 'Deliverables').is_dir())
sys.path.insert(0, str(HERE))
from food_specs import *
import prop_kit as K


def make_materials():
    global rice, broth, noodle, meat, fat, skin, white, yolk, green, stem, bun, fishskin, sauce, scallion, ginger, chop, garlic
    rice = K.mat('Steamed_Rice', (.92, .90, .84), rough=.6, noise=180, bump=1.0)
    broth = K.mat('Clear_Broth', (.55, .33, .10), rough=.08, noise=20, bump=.02)
    noodle = K.mat('Wheat_Noodle', (.86, .74, .45), rough=.45)
    meat = K.mat('Braised_Lean', (.36, .10, .05), rough=.35, noise=60, bump=.2); fat = K.mat('Pork_Fat', (.85, .70, .55), rough=.4)
    skin = K.mat('Glazed_Pork_Skin', (.30, .08, .03), rough=.15)
    white = K.mat('Egg_White', (.92, .90, .84), rough=.35); yolk = K.mat('Egg_Yolk', (.95, .62, .12), rough=.4)
    green = K.mat('Bok_Choy_Leaf', (.12, .32, .07), rough=.35, noise=50, bump=.15); stem = K.mat('Bok_Choy_Stem', (.62, .74, .45), rough=.4)
    bun = K.mat('Steamed_Bun_Dough', (.93, .90, .82), rough=.75, noise=90, bump=.08)
    fishskin = K.mat('Steamed_Fish_Skin', (.68, .64, .56), rough=.3, noise=200, bump=.15)
    sauce = K.mat('Soy_Sauce', (.20, .09, .03), rough=.08, noise=10, bump=.01)
    scallion = K.mat('Scallion', (.25, .55, .15), rough=.4); ginger = K.mat('Ginger_Shred', (.85, .72, .38), rough=.5)
    chop = K.mat('Chopstick_Wood', (.30, .16, .07), rough=.5); garlic = K.mat('Garlic_Bits', (.90, .86, .70), rough=.5)


def container(dish):
    """Append the KitchenWare09 container objects under a (possibly scaled) Container empty."""
    aid, scale, skip = CONTAINERS[dish]
    src = PROJECT / 'Models' / aid / 'v001' / f'{aid}_v001.blend'
    with bpy.data.libraries.load(str(src), link=False) as (s, d):
        d.objects = [n for n in s.objects if not n.startswith(skip + (aid + '_ROOT', 'Reference_Camera', 'Key', 'Fill', 'Rim'))]
    ce = bpy.data.objects.new(f'Container_{aid}', None); K.assets.objects.link(ce); ce.parent = K.root; ce.scale = scale
    ce['source'] = str(src.relative_to(PROJECT)); ce['note'] = 'KitchenWare09 container copy; edit the source asset for shared changes.'
    for o in d.objects:
        if o is None or o.type != 'MESH': continue
        K.assets.objects.link(o); o.parent = ce; o.matrix_parent_inverse = Matrix.Identity(4)
    for o in list(bpy.data.objects):          # source roots pulled in as parents of the appended meshes
        if o.name.startswith(aid + '_ROOT'): bpy.data.objects.remove(o)
    return scale


def inner_r(inner, z):
    for (r0, z0), (r1, z1) in zip(inner, inner[1:]):
        if z1 <= z <= z0: return r1 + (r0 - r1) * (z - z1) / (z0 - z1)
    return inner[0][0]


def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts): p.co = (*co, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH'); o.select_set(False)
    return K.place(o, name, m, smooth=True)


def dome(name, r, h, m, p, segs=48, power=.8):
    prof = [(r * math.cos(a), h * math.sin(a) ** power) for a in [i * math.pi / 2 / 12 for i in range(13)]]
    return K.lathe(name, [(0, 0)] + prof, m, p, segs)


def leaf(name, p, ang, length, width, lift, m, curl=.25):
    """Curved oval leaf lying radially (angle ang) with its tip lifted by `lift`."""
    v = []; nu, nv = 7, 4
    for i in range(nu + 1):
        t = i / nu; w = width * math.sin(math.pi * t) ** .8
        for j in range(nv + 1):
            s = (j / nv - .5) * 2
            x, y, z = length * t, s * w / 2, lift * t ** 1.5 + curl * w * s * s
            v.append((p[0] + x * math.cos(ang) - y * math.sin(ang), p[1] + x * math.sin(ang) + y * math.cos(ang), p[2] + z))
    f = [(i * (nv + 1) + j, i * (nv + 1) + j + 1, (i + 1) * (nv + 1) + j + 1, (i + 1) * (nv + 1) + j) for i in range(nu) for j in range(nv)]
    o = K.mesh(name, v, f, m, smooth=True); o.modifiers.new('Leaf_Thickness', 'SOLIDIFY').thickness = .0015; return o


# ---------------------------------------------------------------- dishes
def rice_bowl():
    container('RiceBowl'); s = SPECS['RiceBowl']; r0 = inner_r(BOWL_INNER, s['mound_base_z']) + .001
    dome('Rice_Mound', r0, s['mound_top'] - s['mound_base_z'], rice, (0, 0, s['mound_base_z']), 64, .9)


def noodle_soup():
    sx, sy, sz = container('NoodleSoup'); s = SPECS['NoodleSoup']; z = s['broth_z']; rb = inner_r(BOWL_INNER, z / sz) * sx + .001
    K.cyl('Broth_Surface', (0, 0, z - .002), rb, .004, broth, 64, bevel=0)
    rng = random.Random(12)
    for k in range(7):
        cx, cy = .045 * math.cos(k * 1.1), .045 * math.sin(k * 1.1) * .9; rr = .028 + .008 * (k % 3)
        pts = [(cx + rr * math.cos(a) * (1 - .25 * a / 9), cy + rr * math.sin(a) * (1 - .25 * a / 9), z + .002 + .002 * math.sin(a * 2)) for a in [i * .3 for i in range(31)]]
        pts = [(x, y, zz) for x, y, zz in pts if math.hypot(x, y) < rb - .006]
        if len(pts) > 3: tube('Swirled_Noodle', pts, s['noodle_r'], noodle)
    for i, (x, y, rot) in enumerate([(-.045, .03, .4), (-.02, .055, -.3)]):
        K.box('Pork_Slice', (x, y, z + .004), (.05, .032, .005), meat, .002, rot=(.08, 0, rot))
        K.box('Pork_Slice_Fat_Edge', (x + .022 * math.cos(rot), y + .022 * math.sin(rot), z + .0045), (.006, .032, .0055), fat, 0, rot=(.08, 0, rot))
    er = s['egg_r']; ex, ey = .04, -.03
    K.lathe('Half_Egg_White', [(0, -.014)] + [(er * math.sin(a), -.014 * math.cos(a)) for a in [i * math.pi / 2 / 10 for i in range(1, 11)]] + [(0, 0)], white, (ex, ey, z + .006), 40)
    K.cyl('Half_Egg_Yolk', (ex, ey, z + .0065), er * .5, .003, yolk, 32, bevel=0)
    for i in range(2): leaf('Greens_Leaf', (-.01 + i * .02, -.06, z + .002), 2.6 + i * .6, .06, .035, .01, green, .1)
    for i in range(12):
        a = rng.uniform(0, math.tau); d = rng.uniform(.0, rb - .015)
        K.torus('Scallion_Ring', (d * math.cos(a), d * math.sin(a), z + .004), .004, .0012, scallion, seg=12)
    rim = .0725 * sz; y0 = .05; xr = math.sqrt((.08 * sx) ** 2 - y0 ** 2)
    for dy in (0, .014):
        K.beam('Chopstick', (-.13, y0 + dy, rim + .004 + .004 * (-.13 + xr) / .04), (.11, y0 + dy + .01, rim + .004), .0035, chop, 8)


def steamed_buns():
    container('SteamedBuns'); s = SPECS['SteamedBuns']; r, h = s['bun_r'], s['bun_h']
    spots = [(0, 0)] + [(s['ring_r'] * math.cos(k * math.tau / 6 + .3), s['ring_r'] * math.sin(k * math.tau / 6 + .3)) for k in range(6)]
    for x, y in spots:
        dome('Steamed_Bun', r, h, bun, (x, y, STEAMER_FLOOR_Z), 40, .75)
        for k in range(10):
            a = k * math.tau / 10
            K.beam('Bun_Pleat', (x + .006 * math.cos(a), y + .006 * math.sin(a), STEAMER_FLOOR_Z + h - .001), (x + .03 * math.cos(a + .35), y + .03 * math.sin(a + .35), STEAMER_FLOOR_Z + h * .8), .0022, bun, 5)
        K.torus('Bun_Top_Knot', (x, y, STEAMER_FLOOR_Z + h - .001), .006, .003, bun, seg=12)


def steamed_fish():
    sx, sy, sz = container('SteamedFish'); s = SPECS['SteamedFish']; base = .0115
    o = K.cyl('Soy_Sauce_Pool', (0, 0, base), 1, .002, sauce, 64, bevel=0); o.scale = (s['sauce_r'][0], s['sauce_r'][1], 1)
    L, H, W = s['length'], s['height'], s['width']; bl = L - .07; cx = -L / 2 + bl / 2
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, radius=1, location=(cx, 0, base + H / 2))
    o = K.place(bpy.context.object, 'Fish_Body', fishskin, smooth=True); o.scale = (bl / 2, W / 2, H / 2)
    tail = [(cx + bl / 2 - .012, 0, base + H * .5), (L / 2, .042, base + H * .62), (L / 2 - .012, 0, base + H * .55), (L / 2, -.042, base + H * .62)]
    o = K.mesh('Fish_Tail', tail, [(0, 1, 2), (0, 2, 3)], fishskin); o.modifiers.new('Fin_Thickness', 'SOLIDIFY').thickness = .003
    dors = [(cx - .06, 0, base + H * .95), (cx + .05, 0, base + H * .95), (cx - .01, 0, base + H * 1.3)]
    o = K.mesh('Fish_Dorsal_Fin', dors, [(0, 1, 2)], fishskin); o.modifiers.new('Fin_Thickness', 'SOLIDIFY').thickness = .002
    for sgn in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=.0055, location=(cx - bl / 2 + .028, sgn * W * .36, base + H * .62))
        K.place(bpy.context.object, 'Fish_Eye', sauce, smooth=True)
    for i in range(5):
        x = cx - .05 + i * .025
        K.beam('Fish_Score_Cut', (x, -W * .3, base + H * .93), (x + .012, W * .3, base + H * .93), .0012, sauce, 4)
    rng = random.Random(3)
    for i in range(12):
        x = cx + rng.uniform(-.07, .07); a = rng.uniform(-.6, .6)
        K.beam('Scallion_Shred', (x - .02 * math.cos(a), -.02 * math.sin(a), base + H + .002), (x + .02 * math.cos(a), .02 * math.sin(a), base + H + .002), .0016, scallion, 5)
    for i in range(6):
        x = cx + rng.uniform(-.06, .06); a = rng.uniform(-.8, .8)
        K.beam('Ginger_Shred', (x - .015 * math.cos(a), -.015 * math.sin(a), base + H + .004), (x + .015 * math.cos(a), .015 * math.sin(a), base + H + .004), .0014, ginger, 5)


def stir_fry_greens():
    container('StirFryGreens'); s = SPECS['StirFryGreens']; base = .0115; rng = random.Random(5)
    for i in range(10):
        a = i * math.tau / 10 + rng.uniform(-.1, .1)
        K.box('Bok_Choy_Stem', (.03 * math.cos(a), .03 * math.sin(a), base + .006), (.055, .018, .008), stem, .003, rot=(0, -.15, a))
    for i in range(s['leaves']):
        layer = i // 8; a = i * math.tau / 8 + layer * .4 + rng.uniform(-.1, .1)
        start = (.012 * math.cos(a), .012 * math.sin(a), base + .01 + layer * .018)
        leaf('Bok_Choy_Leaf', start, a, .085 - layer * .02, .05, -.01 + layer * .006, green, .2)
    for i in range(14):
        a = rng.uniform(0, math.tau); d = rng.uniform(0, .06)
        K.box('Garlic_Bit', (d * math.cos(a), d * math.sin(a), base + .03 + rng.uniform(0, .02)), (.005, .005, .004), garlic, 0, rot=(rng.uniform(0, 3), 0, rng.uniform(0, 3)))
    dome('Greens_Heap_Core', .06, s['heap_h'] - .02, green, (0, 0, base), 32, .9)


def braised_pork():
    container('BraisedPork'); s = SPECS['BraisedPork']; c = s['cube']; z = s['sauce_z']; rs = inner_r(BOWL_INNER, z) + .001
    K.cyl('Braising_Sauce', (0, 0, z - .002), rs, .004, sauce, 64, bevel=0)
    rng = random.Random(9)
    spots = [(0, 0, 0)] + [(.034 * math.cos(k * math.tau / 4 + .4), .034 * math.sin(k * math.tau / 4 + .4), 0) for k in range(4)] + \
            [(.018 * math.cos(k * math.tau / 4 + 1.2), .018 * math.sin(k * math.tau / 4 + 1.2), 1) for k in range(4)]
    for x, y, layer in spots[:s['count']]:
        zb = z - .012 + layer * c * .85; rot = rng.uniform(0, math.pi)
        for name, z0, z1, m in (('Pork_Lean', 0, .55, meat), ('Pork_Fat_Layer', .55, .8, fat), ('Pork_Skin', .8, 1, skin)):
            K.box(name, (x, y, zb + c * (z0 + z1) / 2), (c, c, c * (z1 - z0)), m, .003, rot=(rng.uniform(-.08, .08), rng.uniform(-.08, .08), rot))
    top = z - .012 + c * .85 + c                  # top face of the upper layer of cubes
    for i in range(6):
        a = rng.uniform(0, math.tau); d = rng.uniform(0, .02)   # stay over the upper layer
        K.beam('Scallion_Piece', (d * math.cos(a), d * math.sin(a), top + .002), (d * math.cos(a) + .012, d * math.sin(a) + .004, top + .002), .002, scallion, 6)


BUILDERS = {'RiceBowl': rice_bowl, 'NoodleSoup': noodle_soup, 'SteamedBuns': steamed_buns, 'SteamedFish': steamed_fish,
            'StirFryGreens': stir_fry_greens, 'BraisedPork': braised_pork}
ids = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None
K.build_all(ROOT, BUILDERS, NAMES, DETAILS, SPECS, 'FoodDishes12', make_materials, ids)

# ---------------------------------------------------------------- table-setting preview (all dishes on the KitchenWare09 table)
if not ids:
    bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene


    def append_asset(path, loc):
        with bpy.data.libraries.load(str(path), link=False) as (s, d): d.collections = ['01_Editable_Asset']
        c = d.collections[0]; scene.collection.children.link(c)
        root = next(o for o in c.objects if o.name.endswith('_ROOT') or '_ROOT.' in o.name); root.location = loc
        return c


    append_asset(PROJECT / 'Models/DiningTable/v001/DiningTable_v001.blend', (0, 0, 0))
    for dx, dy in ((.7, 0), (-.7, 0), (0, .7), (0, -.7)): append_asset(PROJECT / 'Models/RoundStool/v001/RoundStool_v001.blend', (dx, dy, 0))
    for dish, (x, y) in TABLE_SETTING: append_asset(ROOT / 'Models' / dish / 'v001' / f'{dish}_v001.blend', (x, y, .75))
    cam = bpy.data.objects.new('Preview_Camera', bpy.data.cameras.new('Preview_Camera')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.55; cam.location = (1.5, -2.0, 2.4)
    cam.rotation_euler = (Vector((0, 0, .7)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    for name, d, e in [('Key', (-2, -3, 4), 300), ('Fill', (3, -1, 2), 120), ('Rim', (0, 3, 3), 180)]:
        ld = bpy.data.lights.new(name, 'AREA'); ld.energy = e; ld.size = 2.5
        o = bpy.data.objects.new(name, ld); scene.collection.objects.link(o); o.location = d
        o.rotation_euler = (Vector((0, 0, .7)) - o.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world = bpy.data.worlds.new('Warm_Gray_Studio'); scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.19, .21, .20, 1); bg.inputs[1].default_value = .7
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 48; scene.cycles.use_denoising = True; scene.view_settings.view_transform = 'AgX'
    scene.render.resolution_x = 1600; scene.render.resolution_y = 1100
    scene.render.filepath = str(ROOT / 'table_setting_preview.png'); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'table_setting_preview.blend'))
    print('PREVIEW_COMPLETE', flush=True)
