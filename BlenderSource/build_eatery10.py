"""Eatery10: two-storey eatery / inn shell built from eatery_specs.py, furnished with KitchenWare09 props.
Run: blender --background --factory-startup -t 4 --python build_eatery10.py
Writes Models/Eatery/v001 (.blend, .fbx, model_info.json) and ArtLibrary/Turnarounds/Eatery_v001 (ten views + cutaways).
The FBX holds the building only; the furnishing props stay editable in the .blend under 30_Furnishing_KitchenWare09.
Skips if views.json already exists.
"""
import bpy, math, json, sys, random
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Project root (holds Models/<Prop> for the KitchenWare09 furnishing); works from the batch or the project BlenderSource.
PROJECT = next(p for p in [ROOT, *ROOT.parents] if (p / 'Deliverables').is_dir())
sys.path.insert(0, str(HERE))
from eatery_specs import *

VIEWS = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_rear', (0, 1, 0)), ('04_left', (-1, 0, 0)),
         ('05_front_right', (1, -1, .45)), ('06_rear_right', (1, 1, .45)), ('07_rear_left', (-1, 1, .45)),
         ('08_front_left', (-1, -1, .45)), ('09_top', (0, 0, 1)), ('10_high_front', (0, -1, 1))]
# Extra layout views: hide groups to look inside. Not part of the ten basic views.
EXTRA = [('11_cutaway_ground', (1, -1, .9), ['Roof', 'Walls_Upper', 'Frame_Upper', 'Floor_Upper', 'Balcony']),
         ('12_plan_ground', (0, 0, 1), ['Roof', 'Walls_Upper', 'Frame_Upper', 'Floor_Upper', 'Balcony']),
         ('13_plan_upper', (0, 0, 1), ['Roof']),
         ('14_cutaway_upper', (1, -1, .9), ['Roof'])]
rng = random.Random(10)
OUT = ROOT / 'Models' / NAME / 'v001'; REFS = ROOT / 'ArtLibrary/Turnarounds' / f'{NAME}_v001'
if (REFS / 'views.json').exists(): print('ALREADY_COMPLETE', NAME); sys.exit(0)
OUT.mkdir(parents=True, exist_ok=True); REFS.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1.0
asset = bpy.data.collections.new('01_Editable_Asset'); scene.collection.children.link(asset)
root = bpy.data.objects.new(NAME + '_ROOT', None); asset.objects.link(root)
root['stage'] = 'Editable appearance prototype; not game-ready; no baked textures, LOD, collision or navigation.'
GROUPS = {}


def group(name):
    if name not in GROUPS:
        c = bpy.data.collections.new(name); asset.children.link(c); GROUPS[name] = c
    return GROUPS[name]


def mat(name, c, rough=.75, noise=30, bump=.15, metal=0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*c, 1); m.use_nodes = True
    n = m.node_tree.nodes; bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*c, 1); bs.inputs['Roughness'].default_value = rough; bs.inputs['Metallic'].default_value = metal
    t = n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = noise; t.inputs['Detail'].default_value = 4
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = .02
    m.node_tree.links.new(t.outputs['Fac'], b.inputs['Height']); m.node_tree.links.new(b.outputs['Normal'], bs.inputs['Normal'])
    return m


plaster = mat('Warm_Lime_Plaster', (.68, .63, .50), .9, 12, .25)
timber = mat('Aged_Chestnut_Timber', (.18, .075, .035))
board = mat('Worn_Floor_Boards', (.27, .15, .07))
stone = [mat(f'Blue_Stone_{i}', (.22 + i * .02, .26 + i * .02, .27 + i * .02), .85) for i in range(4)]
tiles = [mat(f'Celadon_Grey_Tile_{i}', (.065 + i * .01, .13 + i * .012, .14 + i * .012), .6) for i in range(5)]
paper = mat('Warm_Window_Paper', (.66, .54, .34), .8, 60, .05)
brick = mat('Smoked_Brick', (.24, .2, .18), .9, 25, .3)
soot = mat('Soot', (.02, .018, .016), 1)
signwood = mat('Signboard_Timber', (.36, .19, .08))
lantern = mat('Red_Paper_Lantern', (.55, .08, .04), .7, 40, .05)
lantern.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, .35, .12, 1)
lantern.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.2
jar = mat('Clay_Jar', (.23, .14, .09))


def finish(o, name, m, grp, bevel):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    group(grp).objects.link(o); o.parent = root
    if m: o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Soft_edges', 'BEVEL'); mod.width = bevel; mod.segments = 2; mod.limit_method = 'ANGLE'
    return o


def box(name, p, s, m, grp, bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p); o = bpy.context.object; o.dimensions = s
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, m, grp, bevel if min(s) > 3 * bevel else 0)


def span(name, x0, y0, z0, x1, y1, z1, m, grp, bevel=.012):
    return box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), m, grp, bevel)


def cyl(name, p, r, d, m, grp, verts=16, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=p, rotation=rot)
    return finish(bpy.context.object, name, m, grp, 0)


def rod(name, a, b, r, m, grp, verts=8):
    a, b = Vector(a), Vector(b); o = cyl(name, (a + b) / 2, r, (b - a).length, m, grp, verts)
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); return o


def mesh(name, v, f, m, grp):
    d = bpy.data.meshes.new(name + '_Mesh'); d.from_pydata(v, [], f); d.update(); d.validate()
    o = bpy.data.objects.new(name, d); group(grp).objects.link(o); o.parent = root; d.materials.append(m); return o


# ---------------------------------------------------------------- walls with openings
class Wall:
    """Axis-aligned wall. axis 'x' runs along X at y=fixed; 'y' runs along Y at x=fixed. out = +1/-1 exterior side."""

    def __init__(self, name, grp, axis, fixed, a0, a1, z0, z1, t=WALL_T, out=-1):
        self.__dict__.update(name=name, grp=grp, axis=axis, fixed=fixed, a0=a0, a1=a1, z0=z0, z1=z1, t=t, out=out)

    def box(self, label, along, off, z, sa, st, sz, m=plaster, bevel=.012):
        if self.axis == 'x': return box(f'{self.name}_{label}', (along, self.fixed + off, z), (sa, st, sz), m, self.grp, bevel)
        return box(f'{self.name}_{label}', (self.fixed + off, along, z), (st, sa, sz), m, self.grp, bevel)

    def build(self, openings):
        cur = self.a0
        for i, (c, w, sill, head, kind) in enumerate(sorted(openings)):
            l, r = c - w / 2, c + w / 2
            if l > cur + .001: self.box(f'Pier_{i}', (cur + l) / 2, 0, (self.z0 + self.z1) / 2, l - cur, self.t, self.z1 - self.z0)
            if sill > self.z0 + .001: self.box(f'Below_{i}', c, 0, (self.z0 + sill) / 2, w, self.t, sill - self.z0)
            if head < self.z1 - .001: self.box(f'Above_{i}', c, 0, (head + self.z1) / 2, w, self.t, self.z1 - head)
            if kind == 'window': self.window(i, c, sill, w, head - sill)
            elif kind in ('door', 'lattice_door'): self.door(i, c, sill, w, head - sill, kind == 'lattice_door')
            elif kind == 'hatch': self.box(f'Hatch_Sill_{i}', c, 0, sill - .02, w + .1, self.t + .16, .05, board)
            cur = r
        if cur < self.a1 - .001: self.box('Pier_End', (cur + self.a1) / 2, 0, (self.z0 + self.z1) / 2, self.a1 - cur, self.t, self.z1 - self.z0)

    def window(self, i, c, sill, w, h):
        o = self.out * (self.t / 2 + .04); n = f'Window_{i}'
        self.box(n + '_Paper', c, 0, sill + h / 2, w - .06, .03, h - .06, paper, 0)
        for s in (-1, 1): self.box(n + '_Jamb', c + s * w / 2, o, sill + h / 2, .1, .1, h + .1, timber)
        for z in (sill, sill + h): self.box(n + '_Rail', c, o, z, w + .1, .11, .1, timber)
        self.box(n + '_Stone_Sill', c, o * 1.6, sill - .07, w + .24, .2, .08, stone[2])
        for j in range(1, 6): self.box(n + '_Lattice_V', c - w / 2 + j * w / 6, o * .8, sill + h / 2, .025, .04, h - .06, timber, 0)
        for j in range(1, 5): self.box(n + '_Lattice_H', c, o * .8, sill + j * h / 5, w - .06, .04, .025, timber, 0)

    def door(self, i, c, sill, w, h, lattice):
        n = f'Door_{i}'; o = self.out * (self.t / 2 + .04)
        for s in (-1, 1): self.box(n + '_Jamb', c + s * w / 2, o, sill + h / 2, .1, .12, h, timber)
        self.box(n + '_Lintel', c, o, sill + h + .05, w + .2, .12, .1, timber)
        if lattice:
            self.box(n + '_Lower_Panel', c, 0, sill + .45, w - .04, .05, .9, board)
            self.box(n + '_Paper', c, 0, sill + .9 + (h - .9) / 2, w - .08, .03, h - .94, paper, 0)
            for j in range(1, 5): self.box(n + '_Lattice_V', c - w / 2 + j * w / 5, o * .5, sill + .9 + (h - .9) / 2, .025, .04, h - .94, timber, 0)
            for j in range(1, 6): self.box(n + '_Lattice_H', c, o * .5, sill + .9 + j * (h - .9) / 6, w - .08, .04, .025, timber, 0)
        else:
            for j in range(4): self.box(n + '_Plank', c - w / 2 + (j + .5) * w / 4, 0, sill + h / 2, w / 4 - .01, .05, h - .02, board, .004)
            self.box(n + '_Batten', c, -o * .4, sill + h * .25, w - .1, .04, .08, timber, 0)
            self.box(n + '_Batten', c, -o * .4, sill + h * .75, w - .1, .04, .08, timber, 0)


# ---------------------------------------------------------------- foundation, floors, steps
X2, Y2, YF = W / 2, D / 2, -D / 2 - VERANDA
span('Plinth_Core', -X2 - .1, YF - .1, 0, X2 + .1, Y2 + .1, PLINTH - .04, stone[0], 'Foundation', .03)
k = 0
for x0 in [-X2 - .1 + i * 1.02 for i in range(10)]:
    for y in (YF - .1, Y2 + .1):
        span('Plinth_Edge_Stone', x0, y - .1, 0, x0 + 1.0, y + .1, PLINTH - .03, stone[k % 4], 'Foundation', .02); k += 1
for y0 in [YF - .1 + i * 1.07 for i in range(8)]:
    for x in (-X2 - .1, X2 + .1):
        span('Plinth_Edge_Stone', x - .1, y0, 0, x + .1, y0 + 1.05, PLINTH - .03, stone[k % 4], 'Foundation', .02); k += 1
for i in range(28):
    y0 = -Y2 + i * D / 28
    span('Floor_Board', -X2 + .1, y0 + .004, PLINTH - .04, X2 - .1, y0 + D / 28 - .004, PLINTH, board, 'Foundation', .004)
for i in range(10):
    x0 = -X2 + i * W / 10
    for j in range(3):
        span('Veranda_Paving', x0 + .01, YF + j * .5 + .01, PLINTH - .04, x0 + W / 10 - .01, YF + (j + 1) * .5 - .01, PLINTH, stone[(i + j) % 4], 'Foundation', .008)
for s, (h, dy) in enumerate([(.30, .34), (.15, .68)]):
    span('Front_Step', -1.6 - s * .2, YF - .1 - dy, 0, 1.6 + s * .2, YF - .1 - dy + .34, h, stone[s + 1], 'Foundation', .015)
span('Back_Door_Step', BACK_DOOR_X - .7, Y2 + .1, 0, BACK_DOOR_X + .7, Y2 + .45, .22, stone[2], 'Foundation', .015)

# ---------------------------------------------------------------- ground walls
ZG0, ZG1 = PLINTH, PLINTH + F1
t = WALL_T; fy, ry, ex, wx = -Y2 + t / 2, Y2 - t / 2, X2 - t / 2, -X2 + t / 2
Wall('Ground_Front', 'Walls_Ground', 'x', fy, -X2, X2, ZG0, ZG1).build(
    [(-3.75, 1.2, ZG0 + 1.0, ZG0 + 2.3, 'window'), (3.75, 1.2, ZG0 + 1.0, ZG0 + 2.3, 'window'),
     (-1.25, 2.26, ZG0, ZG0 + DOOR_H, 'open'), (1.25, 2.26, ZG0, ZG0 + DOOR_H, 'open')])
Wall('Ground_Rear', 'Walls_Ground', 'x', ry, -X2, X2, ZG0, ZG1, out=1).build(
    [(BACK_DOOR_X, 1.0, ZG0, ZG0 + 2.2, 'door'), (-3.0, .9, ZG0 + 1.4, ZG0 + 2.2, 'window'), (-.4, .9, ZG0 + 1.4, ZG0 + 2.2, 'window')])
Wall('Ground_East', 'Walls_Ground', 'y', ex, -Y2 + t, Y2 - t, ZG0, ZG1, out=1).build(
    [(1.5, 1.4, ZG0 + 1.1, ZG0 + 2.2, 'window'), (-2.0, 1.2, ZG0 + 1.0, ZG0 + 2.3, 'window')])
Wall('Ground_West', 'Walls_Ground', 'y', wx, -Y2 + t, Y2 - t, ZG0, ZG1, out=-1).build([(-2.6, 1.2, ZG0 + 1.0, ZG0 + 2.3, 'window')])
kt = .12; kc = KITCHEN
Wall('Kitchen_West', 'Kitchen', 'y', kc['x0'], kc['y0'] - kt / 2, Y2 - t, ZG0, ZG1, kt, 1).build([])
Wall('Kitchen_South', 'Kitchen', 'x', kc['y0'], kc['x0'] + kt / 2, X2 - t, ZG0, ZG1, kt, -1).build(
    [((kc['door'][0] + kc['door'][1]) / 2, kc['door'][1] - kc['door'][0], ZG0, ZG0 + 2.2, 'open'),
     ((kc['hatch'][0] + kc['hatch'][1]) / 2, kc['hatch'][1] - kc['hatch'][0], ZG0 + 1.0, ZG0 + 1.6, 'hatch')])

# Folding lattice doors, folded open against the piers of each open bay.
def folded_door(name, x_edge, direction):
    for j in range(2):
        y = -Y2 + t + .04 + j * .055
        box(f'{name}_Leaf_{j}_Frame', (x_edge + direction * .28, y, ZG0 + 1.27), (.52, .045, 2.5), timber, 'Doors', .006)
        box(f'{name}_Leaf_{j}_Paper', (x_edge + direction * .28, y + .01, ZG0 + 1.6), (.4, .03, 1.5), paper, 'Doors', 0)
        for q in range(1, 4): box(f'{name}_Leaf_{j}_Lattice', (x_edge + direction * (.28 - .2 + q * .1), y - .01, ZG0 + 1.6), (.02, .03, 1.5), timber, 'Doors', 0)


for a, b in OPEN_BAYS:
    folded_door(f'Folding_Door_{a}', a + .12, 1); folded_door(f'Folding_Door_{b}', b - .12, -1)

# ---------------------------------------------------------------- timber frame
# Posts are split at the upper floor so cutaway views can hide the upper storey frame.
posts = [(x, y) for x in COLUMNS_X for y in (-Y2, Y2)] + [(x, 0) for x in (-X2, X2)]
for x, y in posts:
    span('Frame_Post', x - .13, y - .13, ZG0, x + .13, y + .13, ZG1, timber, 'Frame', .015)
    span('Frame_Post_Upper', x - .13, y - .13, Z_UP, x + .13, y + .13, Z_TOP, timber, 'Frame_Upper', .015)
for z0, z1, grp in ((ZG0, ZG0 + .16, 'Frame'), (ZG1, Z_UP, 'Frame'), (Z_TOP - .18, Z_TOP, 'Frame_Upper')):
    for y in (-Y2, Y2): span('Frame_Beam_X', -X2 - .14, y - .14, z0, X2 + .14, y + .14, z1, timber, grp, .015)
    for x in (-X2, X2): span('Frame_Beam_Y', x - .14, -Y2, z0, x + .14, Y2, z1, timber, grp, .015)

# ---------------------------------------------------------------- upper floor slab with stairwell
hx0, hx1, hy0, hy1 = STAIRWELL
for name, (x0, y0, x1, y1) in {'Front': (-X2, -Y2, X2, hy0), 'West_Strip': (-X2, hy0, hx0, hy1), 'East': (hx1, hy0, X2, hy1), 'Rear': (-X2, hy1, X2, Y2)}.items():
    span(f'Upper_Slab_{name}', x0, y0, ZG1, x1, y1, Z_UP - .03, timber, 'Floor_Upper', .01)
    n = max(1, round((y1 - y0) / .25))
    for i in range(n): span('Upper_Floor_Board', x0 + .02, y0 + i * (y1 - y0) / n + .004, Z_UP - .03, x1 - .02, y0 + (i + 1) * (y1 - y0) / n - .004, Z_UP, board, 'Floor_Upper', .003)
span('Ceiling_Beam', -X2, -1.6, ZG1 - .22, X2, -1.4, ZG1, timber, 'Floor_Upper', .015)
span('Ceiling_Beam', hx1, 1.5, ZG1 - .22, X2, 1.7, ZG1, timber, 'Floor_Upper', .015)
for i in range(9):
    x = -4.0 + i
    if not (hx0 - .1 < x < hx1 + .1): span('Ceiling_Joist', x - .06, -Y2, ZG1 - .12, x + .06, Y2, ZG1, timber, 'Floor_Upper', .006)

# ---------------------------------------------------------------- stair, counter, shelves
s = STAIR; zr = s['riser']
for i in range(s['risers']):
    y0 = s['y0'] + i * s['tread']; ztop = ZG0 + (i + 1) * zr
    span('Stair_Tread', s['x0'] + .06, y0 - .02, ztop - .05, s['x1'] - .06, y0 + s['tread'], ztop, board, 'Stair', .006)
    span('Stair_Riser', s['x0'] + .06, y0 - .02, ztop - zr, s['x1'] - .06, y0, ztop - .05, timber, 'Stair', 0)
for x in (s['x0'] + .03, s['x1'] - .03):
    rod('Stair_Stringer', (x, s['y0'] - .05, ZG0 + .05), (x, STAIR_TOP_Y, Z_UP - .1), .05, timber, 'Stair', 4)
for i in range(5):
    y = s['y0'] + i * (STAIR_TOP_Y - s['y0']) / 4; z = ZG0 + (y - s['y0']) / (STAIR_TOP_Y - s['y0']) * (Z_UP - ZG0)
    span('Stair_Handrail_Post', s['x1'] - .05, y - .04, z, s['x1'] + .03, y + .04, z + .95, timber, 'Stair', .006)
rod('Stair_Handrail', (s['x1'] - .01, s['y0'], ZG0 + .95), (s['x1'] - .01, STAIR_TOP_Y, Z_UP + .95), .03, timber, 'Stair')
span('Stairwell_Rail', hx1 - .05, hy0, Z_UP + .9, hx1 + .03, hy1, Z_UP + .98, timber, 'Walls_Upper', .006)
for y in (hy0 + .3, (hy0 + hy1) / 2, hy1 - .1): span('Stairwell_Rail_Post', hx1 - .05, y - .04, Z_UP, hx1 + .03, y + .04, Z_UP + .9, timber, 'Walls_Upper', .006)

c = COUNTER; cy0, cy1 = c['y'] - c['depth'] / 2, c['y'] + c['depth'] / 2
span('Counter_Body', c['x0'], cy0 + .04, ZG0, c['x1'], cy1, ZG0 + c['h'] - .05, timber, 'Counter', .01)
span('Counter_Top', c['x0'] - .05, cy0 - .03, ZG0 + c['h'] - .05, c['x1'] + .05, cy1 + .03, ZG0 + c['h'], board, 'Counter', .008)
for i in range(8): span('Counter_Front_Panel', c['x0'] + .05 + i * (c['x1'] - c['x0'] - .1) / 8 + .01, cy0, ZG0 + .1, c['x0'] + .05 + (i + 1) * (c['x1'] - c['x0'] - .1) / 8 - .01, cy0 + .05, ZG0 + c['h'] - .12, board, 'Counter', .004)
for x in (c['x0'] + .05, c['x1'] - .05):
    span('Shelf_Upright', x - .03, ry - t / 2 - .38, ZG0, x + .03, ry - t / 2, ZG0 + 2.1, timber, 'Counter', .004)
for z in (.45, 1.0, 1.55, 2.05):
    span('Wall_Shelf', c['x0'], ry - t / 2 - .38, ZG0 + z, c['x1'], ry - t / 2, ZG0 + z + .04, board, 'Counter', .004)
for i, x in enumerate([-2.55, -2.2, -1.8, -1.4, -1.0]):
    for z in (1.04, 1.59):
        cyl('Wine_Jar', (x, ry - t / 2 - .19, ZG0 + z + .13 + (i % 2) * .02), .11, .26 + (i % 2) * .04, jar, 'Counter', 16)

# ---------------------------------------------------------------- upper walls and rooms
ZU0, ZU1 = Z_UP, Z_TOP
Wall('Upper_Front', 'Walls_Upper', 'x', fy, -X2, X2, ZU0, ZU1).build(
    [(-3.3, 1.2, ZU0 + .9, ZU0 + 2.1, 'window'), (3.3, 1.2, ZU0 + .9, ZU0 + 2.1, 'window'), (0, 1.1, ZU0, ZU0 + 2.2, 'lattice_door')])
Wall('Upper_Rear', 'Walls_Upper', 'x', ry, -X2, X2, ZU0, ZU1, out=1).build(
    [(-2.5, 1.0, ZU0 + 1.0, ZU0 + 2.0, 'window'), (.9, 1.0, ZU0 + 1.0, ZU0 + 2.0, 'window')])
Wall('Upper_East', 'Walls_Upper', 'y', ex, -Y2 + t, Y2 - t, ZU0, ZU1, out=1).build([(-1.6, 1.2, ZU0 + .9, ZU0 + 2.1, 'window')])
Wall('Upper_West', 'Walls_Upper', 'y', wx, -Y2 + t, Y2 - t, ZU0, ZU1, out=-1).build([(-1.6, 1.2, ZU0 + .9, ZU0 + 2.1, 'window')])
Wall('Corridor', 'Walls_Upper', 'x', CORRIDOR_Y - .06, -X2 + t, X2 - t, ZU0, ZU1, .12, 1).build(
    [(cx, .9, ZU0, ZU0 + 2.1, 'door') for cx in (-3.3, 0, 3.3)])
for x in ROOM_WALLS_X: Wall(f'Room_Partition_{x}', 'Walls_Upper', 'y', x, -Y2 + t, CORRIDOR_Y - .12, ZU0, ZU1, .12).build([])
for i, cx in enumerate((-3.3, 0, 3.3)):
    span('Guest_Bed_Frame', cx - 1.0, -Y2 + t + .1, ZU0, cx + 1.0 - .1, -Y2 + t + 1.1, ZU0 + .45, timber, 'Walls_Upper', .01)
    span('Guest_Bed_Quilt', cx - .95, -Y2 + t + .15, ZU0 + .45, cx + .85, -Y2 + t + 1.05, ZU0 + .55, paper, 'Walls_Upper', .03)

# Gable infill follows the roof underside.
def roof_z(y):
    t_ = min(1, abs(y) / (Y2 + EAVE)); return Z_TOP - .1 + RISE * (1 - t_) ** 1.35 + .18 * t_ ** 8


for x in (-X2 + t / 2, X2 - t / 2):
    prof = [(-Y2 + i * D / 30, roof_z(-Y2 + i * D / 30) - .2) for i in range(31)]
    poly = [(Y2, Z_TOP), (-Y2, Z_TOP)] + prof; n = len(poly)
    v = [(x + dd, y, z) for dd in (-t / 2, t / 2) for y, z in poly]
    f = [tuple(reversed(range(n))), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh('Gable_Plaster', v, f, plaster, 'Roof')
    for j in range(30):
        a, b = prof[j], prof[j + 1]; rod('Gable_Rake_Timber', (x + math.copysign(.14, x), a[0], a[1] - .02), (x + math.copysign(.14, x), b[0], b[1] - .02), .07, timber, 'Roof', 6)
    rod('Gable_King_Post', (x + math.copysign(.14, x), 0, Z_TOP), (x + math.copysign(.14, x), 0, roof_z(0) - .2), .08, timber, 'Roof', 6)

# ---------------------------------------------------------------- roof
RX = X2 + GABLE_OVER; RY = Y2 + EAVE
for side in (-1, 1):
    v = []
    for ix in range(45):
        x = -RX + ix * 2 * RX / 44
        for j in range(17): tt = j / 16; v.append((x, side * tt * RY, roof_z(tt * RY) - .07))
    f = [(i * 17 + j, i * 17 + j + 1, (i + 1) * 17 + j + 1, (i + 1) * 17 + j) for i in range(44) for j in range(16)]
    if side > 0: f = [tuple(reversed(q)) for q in f]
    o = mesh(f'Roof_Underlay_{side}', v, f, timber, 'Roof'); o.modifiers.new('Underlay_Thickness', 'SOLIDIFY').thickness = .12
    nstrip = 46
    for i in range(nstrip):
        xc = -RX + .12 + i * (2 * RX - .24) / (nstrip - 1); v = []; f = []
        for row in range(13):
            t0 = row / 13; t1 = min(1, (row + 1.1) / 13); st = len(v)
            for tt in (t0, t1):
                for j in range(7):
                    a = math.pi * j / 6; x = xc + .115 * math.cos(a)
                    v.append((x, side * tt * RY, roof_z(tt * RY) + .055 * math.sin(a) + .018 * (1 - tt)))
            for j in range(6): f.append((st + j, st + j + 1, st + j + 8, st + j + 7))
        if side > 0: f = [tuple(reversed(q)) for q in f]
        o = mesh(f'Roof_Tile_Strip_{side}_{i:02}', v, f, tiles[rng.randrange(5)], 'Roof'); o.modifiers.new('Ceramic_Thickness', 'SOLIDIFY').thickness = .025
    for x in (-RX - .03, RX + .03):
        for j in range(16):
            a, b = j / 16 * RY, (j + 1) / 16 * RY
            rod('Roof_Fascia', (x, side * a, roof_z(a) - .12), (x, side * b, roof_z(b) - .12), .07, timber, 'Roof', 6)
    for i in range(23):
        x = -RX + .3 + i * (2 * RX - .6) / 22
        rod('Eave_Rafter', (x, side * (RY - .9), roof_z(RY - .9) - .2), (x, side * RY, roof_z(RY) - .17), .055, timber, 'Roof', 6)
for i in range(30):
    x = -RX + i * 2 * RX / 30; rod('Ridge_Cap', (x, 0, roof_z(0) + .02), (x + 2 * RX / 30, 0, roof_z(0) + .02), .14, tiles[2], 'Roof', 8)
for sgn in (-1, 1):
    rod('Ridge_End_Upturn', (sgn * RX, 0, roof_z(0) + .02), (sgn * (RX + .35), 0, roof_z(0) + .35), .12, tiles[2], 'Roof', 8)

# ---------------------------------------------------------------- chimney
ch = CHIMNEY
span('Chimney_Stack', ch['x'] - ch['w'] / 2, ch['y0'], ZG0, ch['x'] + ch['w'] / 2, ch['y1'], ch['top'], brick, 'Kitchen', .01)
span('Chimney_Cap', ch['x'] - ch['w'] / 2 - .08, ch['y0'] - .08, ch['top'], ch['x'] + ch['w'] / 2 + .08, ch['y1'] + .08, ch['top'] + .1, stone[3], 'Kitchen', .01)
span('Chimney_Flue_Soot', ch['x'] - .17, (ch['y0'] + ch['y1']) / 2 - .12, ch['top'] + .05, ch['x'] + .17, (ch['y0'] + ch['y1']) / 2 + .12, ch['top'] + .101, soot, 'Kitchen', 0)
for z in [ZG0 + .5 + i * .6 for i in range(13)]:
    if z < ch['top'] - .2: span('Chimney_Brick_Course', ch['x'] - ch['w'] / 2 - .005, ch['y0'] - .005, z, ch['x'] + ch['w'] / 2 + .005, ch['y1'] + .005, z + .025, stone[1], 'Kitchen', 0)

# ---------------------------------------------------------------- veranda, balcony, signage
for x in COLUMNS_X:
    cyl('Veranda_Stone_Socket', (x, YF + .02, PLINTH + .1), .2, .2, stone[1], 'Veranda', 8)
    cyl('Veranda_Column', (x, YF + .02, (PLINTH + .2 + Z_UP + 1.05) / 2), .12, Z_UP + 1.05 - PLINTH - .2, timber, 'Veranda', 16)
    for sgn in (-1, 1):
        if -X2 < x + sgn * .5 < X2: rod('Veranda_Bracket', (x, YF + .02, ZG1 - .65), (x + sgn * .55, YF + .02, ZG1 - .1), .05, timber, 'Veranda', 6)
span('Veranda_Header', -X2 - .15, YF - .1, ZG1 - .1, X2 + .15, YF + .14, Z_UP - .02, timber, 'Veranda', .015)
for x in (-X2, X2): span('Veranda_Side_Beam', x - .12, YF, ZG1 - .1, x + .12, -Y2, Z_UP - .02, timber, 'Veranda', .015)
span('Balcony_Deck', -X2, YF - .06, ZG1 - .02, X2, -Y2, Z_UP - .04, timber, 'Balcony', .01)
for i in range(40): span('Balcony_Board', -X2 + i * W / 40 + .005, YF - .06, Z_UP - .04, -X2 + (i + 1) * W / 40 - .005, -Y2, Z_UP, board, 'Balcony', .003)
for z in (Z_UP + .1, Z_UP + .95):
    span('Balcony_Rail_Front', -X2, YF - .02, z, X2, YF + .06, z + .08, timber, 'Balcony', .006)
    for x in (-X2, X2): span('Balcony_Rail_Side', x - .04, YF, z, x + .04, -Y2, z + .08, timber, 'Balcony', .006)
for i in range(1, 40):
    x = -X2 + i * W / 40
    if all(abs(x - cx) > .15 for cx in COLUMNS_X): span('Balcony_Baluster', x - .02, YF, Z_UP + .18, x + .02, YF + .04, Z_UP + .95, timber, 'Balcony', 0)
for x in (-X2, X2):
    for j in range(1, 6): y = YF + j * VERANDA / 6; span('Balcony_Baluster', x - .02, y - .02, Z_UP + .18, x + .02, y + .02, Z_UP + .95, timber, 'Balcony', 0)
sg = SIGN
span('Blank_Signboard', -sg['w'] / 2, YF - .14, sg['z'], sg['w'] / 2, YF - .08, sg['z'] + sg['h'], signwood, 'Signage', .015)
span('Signboard_Frame_Top', -sg['w'] / 2 - .06, YF - .16, sg['z'] + sg['h'], sg['w'] / 2 + .06, YF - .06, sg['z'] + sg['h'] + .06, timber, 'Signage', .01)
span('Signboard_Frame_Bottom', -sg['w'] / 2 - .06, YF - .16, sg['z'] - .06, sg['w'] / 2 + .06, YF - .06, sg['z'], timber, 'Signage', .01)
for x in (-sg['w'] / 2 + .2, sg['w'] / 2 - .2): rod('Signboard_Hanger', (x, YF - .11, sg['z'] + sg['h']), (x, YF - .11, ZG1 - .1), .015, timber, 'Signage', 6)
for x in LANTERNS_X:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.22, location=(x, YF - .1, 2.65))
    o = finish(bpy.context.object, 'Paper_Lantern', lantern, 'Signage', 0); o.scale.z = 1.25
    for f in o.data.polygons: f.use_smooth = True
    cyl('Lantern_Cap', (x, YF - .1, 2.65 + .28), .09, .05, timber, 'Signage', 12)
    cyl('Lantern_Cap', (x, YF - .1, 2.65 - .28), .09, .05, timber, 'Signage', 12)
    rod('Lantern_Cord', (x, YF - .1, 2.95), (x, YF - .1, ZG1 - .1), .008, timber, 'Signage', 4)
    rod('Lantern_Tassel', (x, YF - .1, 2.35), (x, YF - .1, 2.12), .02, lantern, 'Signage', 6)

# ---------------------------------------------------------------- recentre on plinth footprint (not the eaves)
bpy.context.view_layer.update()
asset_meshes = [o for o in asset.all_objects if o.type == 'MESH']


def bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objs:
        e = o.evaluated_get(dg); m = e.to_mesh(); pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


# The plinth (incl. veranda) is the placement footprint; origin = its bottom centre.
plinth = [o for o in asset_meshes if o.name.startswith(('Plinth_', 'Front_Step'))]
plo, phi = bounds([o for o in plinth if o.name.startswith('Plinth_')])
shift = Vector(((plo.x + phi.x) / 2, (plo.y + phi.y) / 2, plo.z))
root.location -= shift; bpy.context.view_layer.update()

# ---------------------------------------------------------------- furnishing (KitchenWare09 props, kept out of the FBX)
furn = bpy.data.collections.new('30_Furnishing_KitchenWare09'); scene.collection.children.link(furn)
froot = bpy.data.objects.new('Furnishing_ROOT', None); furn.objects.link(froot); froot.location = root.location.copy()
froot['note'] = 'Appended copies of KitchenWare09 props for layout preview; source assets live in Models/<Prop>/v001.'


def place(aid, loc, rot=0.0):
    path = PROJECT / 'Models' / aid / 'v001' / f'{aid}_v001.blend'
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if not n.startswith(('Reference_Camera', 'Key', 'Fill', 'Rim', 'Under'))]
    pr = None
    for o in dst.objects:
        if o is None or o.type in ('CAMERA', 'LIGHT'): continue
        furn.objects.link(o)
        if o.name.startswith(aid + '_ROOT'): pr = o
    pr.parent = froot; pr.location = Vector(loc); pr.rotation_euler.z = rot; pr['source'] = str(path.relative_to(PROJECT))
    bpy.context.view_layer.update(); return pr


def obj_bounds(pr):
    return bounds([o for o in pr.children_recursive if o.type == 'MESH'])


F0 = PLINTH
h = place('CookingHearth', (HEARTH_AT[0], HEARTH_AT[1], F0))
lo_, hi_ = bounds([o for o in h.children_recursive if o.name.startswith('Stone_Plinth')])
h.location.y += (CHIMNEY['y0'] - .02) - (hi_.y - root.location.y)
h.location.x += HEARTH_AT[0] - ((lo_.x + hi_.x) / 2 - root.location.x); bpy.context.view_layer.update()
seat = next(o for o in h.children_recursive if o.name.startswith('Cast_Iron_Wok_Seat'))
sp = seat.matrix_world.translation - root.location
place('IronWok', (sp.x, sp.y, sp.z + .012 - .139))  # wok surface meets the seat ring at r = 0.262 m
pb = next(o for o in h.children_recursive if o.name.startswith('Prep_Surface_Board'))
lo_, hi_ = bounds([pb]); place('BambooSteamer', ((lo_.x + hi_.x) / 2 - root.location.x, (lo_.y + hi_.y) / 2 - root.location.y, hi_.z - root.location.z))
place('PrepBoard', ((COUNTER['x0'] + COUNTER['x1']) / 2 + .5, COUNTER['y'], F0 + COUNTER['h']), .2)
place('CeramicBowl', ((COUNTER['x0'] + COUNTER['x1']) / 2 - .6, COUNTER['y'] - .05, F0 + COUNTER['h']))
for i, (x, y) in enumerate(TABLES):
    place('DiningTable', (x, y, F0))
    for dx, dy in ((STOOL_OFFSET, 0), (-STOOL_OFFSET, 0), (0, STOOL_OFFSET), (0, -STOOL_OFFSET)): place('RoundStool', (x + dx, y + dy, F0))
    place('CeramicBowl', (x - .18, y + .1, F0 + .75)); place('CeramicPlate', (x + .2, y - .1, F0 + .75))

# ---------------------------------------------------------------- export, info
bpy.context.view_layer.update()
lo, hi = bounds(asset_meshes); centre = (lo + hi) / 2; extent = hi - lo
bpy.ops.object.select_all(action='DESELECT')
for o in [root] + asset_meshes: o.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.fbx(filepath=str(OUT / f'{NAME}_v001.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'}, add_leaf_bones=False,
                         axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_anim=False)

studio = bpy.data.collections.new('90_Studio_Not_Exported'); scene.collection.children.link(studio)
cam = bpy.data.objects.new('Reference_Camera', bpy.data.cameras.new('Reference_Camera')); studio.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.clip_start = .01; cam.data.clip_end = 1000; L = extent.length; cam.data.ortho_scale = L * 1.12
k = L / 1.6
for name, d, power, size in [('Key', (-3, -4, 6), 520, 4), ('Fill', (4, -1, 3), 260, 4), ('Rim', (0, 4, 5), 420, 3)]:
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power * k * k; ld.shape = 'DISK'; ld.size = size * k
    o = bpy.data.objects.new(name, ld); studio.objects.link(o); o.location = centre + Vector(d) * k
    o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
scene.world = bpy.data.worlds.new('Warm_Gray_Studio'); scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.19, .21, .20, 1); bg.inputs[1].default_value = .8
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 16; scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = 1024; scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'{NAME}_v001.blend'))

props = [o for o in froot.children]
info = {'asset': NAME, 'name_zh': NAME_ZH, 'batch': 'Eatery10', 'stage': 'appearance_prototype', 'units': 'meters', 'front': '-Y',
        'origin': 'bottom centre of the stone plinth incl. veranda (roof eaves and steps extend beyond it)',
        'dimensions_m': [round(c, 3) for c in extent], 'plinth_footprint_m': [round(phi.x - plo.x, 3), round(phi.y - plo.y, 3)],
        'mesh_objects': len(asset_meshes), 'levels_m': {'ground_floor': PLINTH, 'upper_floor': Z_UP, 'wall_top': Z_TOP, 'ridge': round(roof_z(0), 3)},
        'stair': {'risers': STAIR['risers'], 'riser_m': STAIR['riser'], 'tread_m': STAIR['tread'], 'width_m': STAIR['x1'] - STAIR['x0']},
        'door_clear_height_m': DOOR_H, 'groups': sorted(GROUPS), 'design_sheets': ['DesignSheets/Eatery_01_elevations.png', 'DesignSheets/Eatery_02_plans.png'],
        'furnishing_in_blend_only': sorted({o.get('source', '') for o in props}), 'furnishing_instances': len(props),
        'modeling_method': 'procedural editable mesh built from eatery_specs.py; views rendered from the same model',
        'uv_baked': False, 'collision': False, 'lod': False, 'navigation': False, 'unreal_import_verified': False}
(OUT / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2))

from bpy_extras.object_utils import world_to_camera_view


def position(d):
    cam.location = centre + Vector(d).normalized() * L * 3
    cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()


def render(name, d):
    position(d)
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [world_to_camera_view(scene, cam, e.matrix_world @ Vector(p)) for o in asset_meshes for e in [o.evaluated_get(dg)] for p in e.bound_box]
    assert all(.003 < p.x < .997 and .003 < p.y < .997 and p.z > 0 for p in pts), (name, 'cropped')
    scene.render.filepath = str(REFS / (name + '.png')); bpy.ops.render.render(write_still=True); print('VIEW_COMPLETE', name, flush=True)
    return {'file': name + '.png', 'camera_location': [round(c, 3) for c in cam.location], 'direction': d, 'projection': 'orthographic', 'framing_checked': True}


records = [render(n, d) for n, d in VIEWS]
extras = []
for n, d, hide in EXTRA:
    hidden = [o for g in hide for o in GROUPS[g].all_objects]
    for o in hidden: o.hide_render = True
    r = render(n, d); r['hidden_groups'] = hide; extras.append(r)
    for o in hidden: o.hide_render = False
(REFS / 'views.json').write_text(json.dumps({'asset': NAME, 'source': f'Models/{NAME}/v001/{NAME}_v001.blend', 'same_geometry': True,
                                             'views': records, 'extra_views': extras}, indent=2))
print('ASSET_COMPLETE', NAME, flush=True)
