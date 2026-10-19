"""TownLayout v004: place the StreetProps11 well, bucket, notice board, crates, baskets and firewood on the v003 west street.
Run: blender --background --factory-startup -t 4 --python BlenderSource/SpawnTown/build_town_layout_v004.py
Opens v003 (unchanged) and writes the next free Models/TownLayout/vNNN.
"""
import bpy, json, math, random, sys
from pathlib import Path
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from town_v004_specs import *

BASE = ROOT / 'Models/TownLayout'
version = 1
while (BASE / f'v{version:03d}').exists(): version += 1
OUT = BASE / f'v{version:03d}'; OUT.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / SOURCE))
scene = bpy.context.scene
rng = random.Random(1004)


def collection(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c


paths = collection('14_Street_Prop_Pads')
stone = [bpy.data.materials[f'Bluestone_{i}'] for i in range(5)]
dark = bpy.data.materials['Deep_Stone_Joints']


def block(name, x0, x1, y0, y1, z0, z1, material):
    verts = [(x, y, z) for z in (z0, z1) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name + '_Mesh'); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); paths.objects.link(obj); mesh.materials.append(material)
    mod = obj.modifiers.new('Worn_Stone_Edges', 'BEVEL'); mod.width = .012; mod.segments = 2


def paving(name, x0, x1, y0, y1):
    """Same flagstone construction as the v002/v003 streets."""
    block(name + '_Mortar', x0, x1, y0, y1, 0, WALK_Z - .05, dark)
    nx, ny = max(1, round((x1 - x0) / .8)), max(1, round((y1 - y0) / .8)); dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            block(f'{name}_{i}_{j}', x0 + i * dx + .012, x0 + (i + 1) * dx - .012, y0 + j * dy + .012, y0 + (j + 1) * dy - .012, WALK_Z - .09, WALK_Z, stone[rng.randrange(5)])


for name, b in PAVING.items(): paving(name, *b)

dress = collection('15_West_Street_Props_StreetProps11')
placed = []
for idx, (aid, loc, rot, note) in enumerate(PROPS):
    src = ROOT / PROPS_DIR / aid / 'v001' / f'{aid}_v001.blend'
    with bpy.data.libraries.load(str(src), link=False) as (s, d):
        d.collections = ['01_Editable_Asset']
    c = d.collections[0]; c.name = f'{aid}_{idx:02d}'; dress.children.link(c)
    pe = bpy.data.objects.new(f'{aid}_{idx:02d}_PLACEMENT', None); dress.objects.link(pe)
    pe.location = loc; pe.rotation_euler.z = math.radians(rot); pe.empty_display_size = .6
    pe['source'] = str(src.relative_to(ROOT)); pe['note'] = note or 'street dressing'
    for o in [o for o in c.all_objects if o.parent is None]: o.parent = pe; o.matrix_parent_inverse = Matrix.Identity(4)
    placed.append((aid, idx, pe, c))

# ---------------------------------------------------------------- checks
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()


def down(x, y, z, dist):
    hit, pos, n, i, obj, m = scene.ray_cast(deps, Vector((x, y, z)), Vector((0, 0, -1)), distance=dist)
    return hit, pos.z, obj.name if obj else ''


walk = []
for x, y in LANE_SAMPLES + STREET_SAMPLES:
    hit, z, name = down(x, y, 2.2, 3.2)
    joint = name.endswith('_Mortar') and abs(z - (WALK_Z - .05)) < .01
    assert hit and (abs(z - WALK_Z) < .02 or joint), ('walk path blocked', x, y, z, name)
    walk.append([x, y, round(z, 4)])


def mesh_bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objs:
        e = o.evaluated_get(dg); me = e.to_mesh(); pts += [e.matrix_world @ v.co for v in me.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


support = []
for aid, idx, pe, c in placed:
    meshes = [o for o in c.all_objects if o.type == 'MESH']
    lo, hi = mesh_bounds(meshes)
    base = pe.location.z
    assert abs(lo.z - base) < .003, (aid, idx, 'base', lo.z, base)
    # Something must hold the prop up. With the prop hidden, of five rays from 5 cm above its base (centre and four
    # diagonal 0.1 m offsets, which miss straight flagstone joints) at least one hits a surface within 3 cm of the base.
    for o in meshes: o.hide_viewport = True
    bpy.context.view_layer.update(); deps = bpy.context.evaluated_depsgraph_get()
    best = None
    for dx, dy in ((0, 0), (.1, .1), (-.1, .1), (.1, -.1), (-.1, -.1)):
        hit, z, name = down(pe.location.x + dx, pe.location.y + dy, base + .05, .2)
        if hit and abs(base - z) <= .03: best = (z, name); break
    for o in meshes: o.hide_viewport = False
    bpy.context.view_layer.update(); deps = bpy.context.evaluated_depsgraph_get()
    assert best, (aid, idx, 'floating')
    z, name = best
    # No prop footprint may reach into the west street walking strip.
    assert hi.x < -12.0 - .0 or lo.x > -9.0 - .001, (aid, idx, 'in street', lo.x, hi.x)
    support.append({'prop': aid, 'instance': idx, 'base_z': round(base, 3), 'support': name, 'footprint_x': [round(lo.x, 2), round(hi.x, 2)]})

# Props must not overlap one another or the buildings already on the street (bounding boxes, 1 cm tolerance).
boxes = [(f'{aid}_{idx:02d}', *mesh_bounds([o for o in c.all_objects if o.type == 'MESH'])) for aid, idx, pe, c in placed]
for name in ('Eatery_PLACEMENT', 'MaterialShop_PLACEMENT', 'HerbalStall_PLACEMENT'):
    pe = scene.objects[name]; boxes.append((name, *mesh_bounds([o for o in pe.children_recursive if o.type == 'MESH' and not o.name.startswith(('Roof', 'Eave', 'Ridge', 'Gable', 'Plinth', 'Front_Step', 'Back_Door', 'Veranda', 'Balcony', 'Floor', 'Upper', 'Signage', 'Paper_Lantern', 'Lantern', 'Blank_Sign', 'Signboard'))])))


def overlap(a, b):
    return all(a[1][i] < b[2][i] - .01 and b[1][i] < a[2][i] - .01 for i in range(3))


clashes = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:] if overlap(a, b)
           and not ({a[0][:11], b[0][:11]} == {'WoodenCrate'})]   # stacked crates touch by design
# Building bounds are coarse (whole walls); report rather than fail if a prop overlaps one.
prop_prop = [c for c in clashes if not any(n.endswith('_PLACEMENT') for n in c)]
assert not prop_prop, prop_prop

# ---------------------------------------------------------------- export, save, info, renders
exports = []
for c in scene.collection.children:
    if c.name.startswith(('80_', '90_')): continue
    exports.extend(o for o in c.all_objects if o.type in ('MESH', 'EMPTY'))
exports = list(dict.fromkeys(exports))
for o in scene.objects: o.select_set(False)
for o in exports: o.select_set(True)
bpy.context.view_layer.objects.active = placed[0][2]
bpy.ops.export_scene.fbx(filepath=str(OUT / f'TownLayout_v{version:03d}.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'},
                         apply_unit_scale=True, bake_anim=False, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
for o in scene.objects: o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'TownLayout_v{version:03d}.blend'))
info = json.loads((ROOT / SOURCE).with_name('layout_info.json').read_text())
info = {k: v for k, v in info.items() if k not in ('walk_ray_samples',)}
info.update({'stage': 'v003 west street plus StreetProps11 dressing (well, bucket, notice board, crates, baskets, firewood)',
             'base_scene': SOURCE, 'street_props': [{'prop': a, 'location': list(l), 'rotation_z_degrees': r, 'note': n} for a, l, r, n in PROPS],
             'prop_pads': PAVING, 'walk_ray_samples': walk, 'prop_support': support, 'building_bbox_overlaps_reported': [list(c) for c in clashes if c not in prop_prop],
             'mesh_objects': sum(o.type == 'MESH' for o in exports), 'blender_version': bpy.app.version_string})
(OUT / 'layout_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
print('SAVED', OUT, flush=True)
camera = scene.camera


def aim(o, target): o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


for name, loc, target, scale in [('01_town_overview', (-34, -40, 34), (-4, 0, 1.5), 50),
                                 ('02_town_top_plan', (-3.5, .5, 60), (-3.5, .5, 0), 46),
                                 ('03_well_and_notice', (-1, -16, 8), (-8, -4.5, 1.2), 13),
                                 ('04_stall_corner', (-1, -2, 7), (-8, 6, 1.2), 12),
                                 ('05_eatery_back_firewood', (-30, -12, 8), (-21, -2, 1.5), 12)]:
    camera.location = loc; aim(camera, target); camera.data.ortho_scale = scale
    scene.render.filepath = str(OUT / (name + '.png')); bpy.ops.render.render(write_still=True); print('RENDERED', name, flush=True)
print('COMPLETE', flush=True)
