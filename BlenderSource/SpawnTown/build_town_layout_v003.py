"""TownLayout v003: extend v002 west with a street holding the eatery, materials shop and herbal stall.
Run: blender --background --factory-startup -t 4 --python BlenderSource/SpawnTown/build_town_layout_v003.py
Layout values come from town_v003_specs.py. v002 is opened as the base and is not modified; output goes to
the next free Models/TownLayout/vNNN folder.
"""
import bpy, json, math, random, sys
from pathlib import Path
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from town_v003_specs import *

BASE = ROOT / 'Models/TownLayout'
version = 1
while (BASE / f'v{version:03d}').exists(): version += 1
OUT = BASE / f'v{version:03d}'; OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / SOURCE))
scene = bpy.context.scene
rng = random.Random(1003)


def collection(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c


# ---------------------------------------------------------------- terrain and plaza opening
terrain = scene.objects['Terrain_Display_Island']
mw, inv = terrain.matrix_world, terrain.matrix_world.inverted()
moved = 0
for v in terrain.data.vertices:
    w = mw @ v.co
    if w.x < TERRAIN_WEST_FROM + .6:
        w.x += TERRAIN_WEST_TO - TERRAIN_WEST_FROM; v.co = inv @ w; moved += 1
assert moved, 'terrain west edge not found'
for name in CURBS_REMOVED: bpy.data.objects.remove(scene.objects[name])

# ---------------------------------------------------------------- paving
paths = collection('12_West_Street_Paving')
stone = [bpy.data.materials[f'Bluestone_{i}'] for i in range(5)]
dark = bpy.data.materials['Deep_Stone_Joints']


def block(name, x0, x1, y0, y1, z0, z1, material, coll=paths):
    verts = [(x, y, z) for z in (z0, z1) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name + '_Mesh'); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); coll.objects.link(obj); mesh.materials.append(material)
    mod = obj.modifiers.new('Worn_Stone_Edges', 'BEVEL'); mod.width = .012; mod.segments = 2
    return obj


def paving(name, x0, x1, y0, y1):
    """Same construction as the v002 shop lane: mortar bed plus individual 0.8 m flagstones topping out at WALK_Z."""
    block(name + '_Mortar', x0, x1, y0, y1, 0, WALK_Z - .05, dark)
    nx, ny = max(1, round((x1 - x0) / .8)), max(1, round((y1 - y0) / .8)); dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            block(f'{name}_{i}_{j}', x0 + i * dx + .012, x0 + (i + 1) * dx - .012, y0 + j * dy + .012, y0 + (j + 1) * dy - .012, WALK_Z - .09, WALK_Z, stone[rng.randrange(5)])


for name, b in PAVING.items(): paving(name, *b)
x0, x1, y0, y1, z0, z1 = EATERY_PLOT_BASE
block('Eatery_Plot_Base', x0, x1, y0, y1, z0, z1, dark)

# ---------------------------------------------------------------- buildings
placements = {}
for name, (src, loc, rot, note) in PLACEMENTS.items():
    plot = collection(f'13_{name}_West_Street_Plot')
    with bpy.data.libraries.load(str(ROOT / src), link=False) as (s, d):
        d.collections = [n for n in s.collections if not n.startswith('90_')]
    loaded = [c for c in d.collections if c is not None]
    nested = {ch for c in loaded for ch in c.children_recursive}
    for c in loaded:
        if c not in nested: plot.children.link(c)   # nested collections come along with their parent
        c.name = f'{name}_{c.name}'
    pe = bpy.data.objects.new(f'{name}_PLACEMENT', None); plot.objects.link(pe)
    pe.location = loc; pe.rotation_euler.z = math.radians(rot); pe.empty_display_size = 1.5
    pe['source'] = src; pe['note'] = note + '. Move this empty to move the whole building.'
    tops = [o for o in plot.all_objects if o.parent is None and o is not pe]
    for o in tops: o.parent = pe; o.matrix_parent_inverse = Matrix.Identity(4)
    placements[name] = {'source': src, 'location': list(loc), 'rotation_z_degrees': rot, 'objects': len(plot.all_objects) - 1}

# The old west plaza bench sat in the new lane opening; it moves to the stall pad.
fx, fy = BENCH_MOVE['from_centre']; tx, ty = BENCH_MOVE['to_centre']
bench = [o for o in scene.objects if o.name.startswith('Bench_') and abs(o.matrix_world.translation.x - fx) < .5 and o.parent is None]
assert bench, 'west bench not found'
for o in bench: o.location.x += tx - fx; o.location.y += ty - fy

markers = next(c for c in scene.collection.children if c.name.startswith('80_'))
for name, loc in MARKERS.items():
    o = bpy.data.objects.new(name, None); markers.objects.link(o); o.location = loc
    o.empty_display_type = 'ARROWS'; o.empty_display_size = .5; o['purpose'] = 'Layout reference only, not a gameplay component.'
old = scene.objects.get('Future_Inn_West')
if old: bpy.data.objects.remove(old)

studio = next(c for c in scene.collection.children if c.name.startswith('90_'))


def aim(o, target): o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


d = bpy.data.lights.new('West_Street_Fill', 'AREA'); d.energy = 5000; d.size = 14
o = bpy.data.objects.new('West_Street_Fill', d); studio.objects.link(o); o.location = (-16, -8, 16); aim(o, (-14, 2, 1))

# ---------------------------------------------------------------- walk checks
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()


def down(x, y, z=2.2):
    hit, pos, n, i, obj, m = scene.ray_cast(deps, Vector((x, y, z)), Vector((0, 0, -1)), distance=z + 1)
    return hit, pos.z, obj.name if obj else None


walk = []
for x, y in LANE_SAMPLES + STREET_SAMPLES:
    hit, z, name = down(x, y)
    # A sample may land in a 24 mm mortar joint, 50 mm below the flagstones; that still counts as walkable paving.
    joint = name and name.endswith('_Mortar') and abs(z - (WALK_Z - .05)) < .01
    assert hit and (abs(z - WALK_Z) < .02 or joint) and name.startswith(tuple(PAVING) + ('Lower_Plaza_Slab',)), (x, y, z, name)
    walk.append([x, y, round(z, 4)])


def eatery_world(lx, ly):
    px, py, pz = PLACEMENTS['Eatery'][1]; a = math.radians(PLACEMENTS['Eatery'][2])
    return px + lx * math.cos(a) - ly * math.sin(a), py + lx * math.sin(a) + ly * math.cos(a)


ez = PLACEMENTS['Eatery'][1][2]
entry = {}
for label, (lx, ly), want in [('eatery_lower_step', (0, -4.96), .15), ('eatery_upper_step', (0, -4.62), .30),
                              ('eatery_veranda', (-1.25, -3.6), .45), ('eatery_dining_floor', (-1.25, -1.1), .45)]:
    # Local coordinates are relative to the eatery origin (plinth centre), 0.75 m south of the spec's building centre.
    x, y = eatery_world(lx, ly); hit, z, name = down(x, y)
    assert hit and abs(z - (ez + want)) < .02, (label, z, ez + want, name)
    entry[label] = round(z, 3)
assert abs(entry['eatery_lower_step'] - WALK_Z) < .02
shop_steps = []
sx, sy, sz = PLACEMENTS['MaterialShop'][1]
for x in (-12.2, -12.5, -12.85, -13.6):
    hit, z, name = down(x, sy, 3)
    shop_steps.append(round(z, 3))
assert shop_steps[0] > WALK_Z and all(b - a > .1 for a, b in zip(shop_steps, shop_steps[1:3])) and max(b - a for a, b in zip([WALK_Z] + shop_steps, shop_steps)) < .2, shop_steps
entry['materialshop_steps'] = shop_steps

# ---------------------------------------------------------------- export + save
exports = []
for c in scene.collection.children:
    if c.name.startswith(('80_', '90_')): continue
    exports.extend(o for o in c.all_objects if o.type in ('MESH', 'EMPTY'))
exports = list(dict.fromkeys(exports))
for o in scene.objects: o.select_set(False)
for o in exports: o.select_set(True)
bpy.context.view_layer.objects.active = scene.objects['Eatery_PLACEMENT']
bpy.ops.export_scene.fbx(filepath=str(OUT / f'TownLayout_v{version:03d}.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'},
                         apply_unit_scale=True, bake_anim=False, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
for o in scene.objects: o.select_set(False)
camera = scene.camera; camera.data.type = 'ORTHO'
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 32; scene.cycles.use_denoising = True
scene.render.resolution_x = 1600; scene.render.resolution_y = 1100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'TownLayout_v{version:03d}.blend'))

info = json.loads((ROOT / SOURCE).with_name('layout_info.json').read_text())
info = {k: v for k, v in info.items() if not k.endswith('samples')}
info.update({'stage': 'Plaza, house, smithy, and a west street with eatery, materials shop and herbal stall',
             'base_scene': SOURCE, 'layout_plan': 'ArtReferences/TownLayout_v003/TownLayout_v003_plan.png',
             'west_street': {'paving': PAVING, 'walk_z_m': WALK_Z, 'curbs_removed': CURBS_REMOVED,
                             'terrain_extended_x': [TERRAIN_WEST_FROM, TERRAIN_WEST_TO], 'bench_moved': BENCH_MOVE},
             'placements': placements, 'walk_ray_samples': walk, 'entry_heights_m': entry,
             'mesh_objects': sum(o.type == 'MESH' for o in exports), 'blender_version': bpy.app.version_string,
             'unity_verified': False, 'unreal_verified': False,
             'limitations': ['Exterior and interior layout only; no collision meshes, navmesh or gameplay',
                             'North elevated street end and west street ends are placeholder boundaries',
                             'FBX procedural materials need baking/rebuilding; no LOD optimisation',
                             'Saved with Blender 5.2.2 from a v002 file written by Blender 5.3']})
(OUT / 'layout_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
print('SAVED', OUT, flush=True)

for name, loc, target, scale in [('01_town_west_street', (-34, -40, 34), (-4, 0, 1.5), 50),
                                 ('02_town_top_plan', (-3.5, .5, 60), (-3.5, .5, 0), 46),
                                 ('03_west_street_view', (-4, -22, 9), (-12, 5, 2), 26),
                                 ('04_eatery_frontage', (-2, -9, 7), (-15, -3, 3), 17)]:
    camera.location = loc; aim(camera, target); camera.data.ortho_scale = scale
    scene.render.filepath = str(OUT / (name + '.png')); bpy.ops.render.render(write_still=True)
    print('RENDERED', name, flush=True)
print('COMPLETE', flush=True)
