"""Reopen the Eatery .blend, round-trip the FBX and check layout rules; writes ../validation.json.
Run: blender --background --factory-startup --python verify_eatery10.py
"""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from eatery_specs import *


def bounds(objects):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objects:
        e = o.evaluated_get(dg); m = e.to_mesh(); pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


path = ROOT / 'Models' / NAME / 'v001' / f'{NAME}_v001.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
root = bpy.data.objects[NAME + '_ROOT']
meshes = [o for o in bpy.data.collections['01_Editable_Asset'].all_objects if o.type == 'MESH']
assert meshes and all(o.data.vertices and o.data.polygons for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(o.parent == root for o in meshes)
row = {'asset': NAME, 'name_zh': NAME_ZH, 'blend_reopened': True, 'meshes': len(meshes), 'vertices_finite': True}

# Origin: bottom centre of the stone plinth (incl. veranda).
plo, phi = bounds([o for o in meshes if o.name.startswith('Plinth_')])
assert abs(plo.z) < .001 and abs(plo.x + phi.x) < .001 and abs(plo.y + phi.y) < .001, (plo, phi)
assert abs((phi.x - plo.x) - (W + .4)) < .01 and abs((phi.y - plo.y) - (D + VERANDA + .4)) < .01
row['plinth_bottom_centre_pivot_checked'] = True
lo, hi = bounds(meshes); size = hi - lo
row['dimensions_m'] = [round(c, 3) for c in size]
off = root.matrix_world.translation  # building coordinates = world - root offset


def wb(prefix):
    a, b = bounds([o for o in meshes if o.name.startswith(prefix)]); return a - off, b - off


# Stair: 17 treads, 0.20 m risers, top tread level with the upper floor.
treads = sorted([o for o in meshes if o.name.startswith('Stair_Tread')], key=lambda o: bounds([o])[1].z)
tops = [bounds([o])[1].z - off.z for o in treads]
assert len(treads) == STAIR['risers'] and all(abs(tops[i] - (PLINTH + (i + 1) * STAIR['riser'])) < .002 for i in range(len(tops)))
assert abs(tops[-1] - Z_UP) < .002
row['stair_17x200mm_checked'] = True

# Headroom: slab underside above every tread outside the stairwell must be >= 2.0 m above that tread.
slab = [o for o in meshes if o.name.startswith(('Upper_Slab', 'Ceiling_Beam', 'Ceiling_Joist'))]
min_head = 99
for o in treads:
    tlo, thi = bounds([o]); cx, cy = (tlo.x + thi.x) / 2, (tlo.y + thi.y) / 2
    for s in slab:
        slo, shi = bounds([s])
        if slo.x < thi.x and shi.x > tlo.x and slo.y < cy < shi.y: min_head = min(min_head, slo.z - thi.z)
assert min_head >= 2.0 - 1e-4, ('stair headroom', min_head)
row['stair_min_headroom_m'] = round(min_head, 3)

# Front open bays: clear height above the ground floor.
above = [o for o in meshes if o.name.startswith('Ground_Front_Above') and any(a < o.matrix_world.translation.x - off.x < b for a, b in OPEN_BAYS)]
assert len(above) == len(OPEN_BAYS)
clear = min(bounds([o])[0].z - off.z for o in above) - PLINTH
assert clear >= 2.5, clear
row['front_opening_clear_height_m'] = round(clear, 3)

# Chimney pierces the roof; ridge height matches spec.
clo, chi = wb('Chimney_Stack')
ridge = wb('Ridge_Cap')[1].z
assert chi.z > 7.2 and abs(ridge - (Z_RIDGE + .16)) < .2, (chi.z, ridge)
row['chimney_top_m'] = round(chi.z, 3); row['ridge_top_m'] = round(ridge, 3)

# Furnishing: appended KitchenWare09 props, outside the exported asset.
furn = bpy.data.collections['30_Furnishing_KitchenWare09']
roots = [o for o in furn.objects if o.type == 'EMPTY' and o.name != 'Furnishing_ROOT']
counts = {}
for o in roots: counts[o.name.split('_ROOT')[0]] = counts.get(o.name.split('_ROOT')[0], 0) + 1
want = {'CookingHearth': 1, 'IronWok': 1, 'BambooSteamer': 1, 'PrepBoard': 1, 'DiningTable': 4, 'RoundStool': 16, 'CeramicBowl': 5, 'CeramicPlate': 4}
assert counts == want, counts
# Wok ring sits on the hearth seat: its lowest vertex within the seat opening and below the rim.
wok = next(o for o in roots if o.name.startswith('IronWok'))
wlo, whi = bounds([c for c in wok.children_recursive if c.type == 'MESH' and c.name.startswith('Iron_Wok_Body')])
seat = next(o for o in furn.all_objects if o.name.startswith('Cast_Iron_Wok_Seat'))
slo, shi = bounds([seat])
assert wlo.z < shi.z and whi.z > shi.z and abs((wlo.x + whi.x) / 2 - (slo.x + shi.x) / 2) < .01
row['furnishing_instances'] = counts; row['wok_seated_on_hearth_checked'] = True
count = len(meshes)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(path.with_suffix('.fbx')))
imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
a, b = bounds(imported); delta = max(abs(size[i] - (b - a)[i]) for i in range(3))
assert len(imported) == count, ('mesh count', len(imported), count)
assert delta < .001, ('FBX bounds', delta)
assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
row.update({'fbx_reimported': True, 'fbx_building_only': True, 'fbx_dimension_error_m': delta})

refs = ROOT / 'ArtLibrary/Turnarounds' / f'{NAME}_v001'
man = json.loads((refs / 'views.json').read_text())
assert len(man['views']) == 10 and len({tuple(r['direction']) for r in man['views']}) == 10 and all(r['framing_checked'] for r in man['views'])
digests = set()
for r in man['views'] + man['extra_views']:
    data = (refs / r['file']).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (1024, 1024)
    digests.add(hashlib.sha256(data).hexdigest())
assert len(digests) == 10 + len(man['extra_views'])
for n in ('Eatery_01_elevations.png', 'Eatery_02_plans.png'): assert (ROOT / 'DesignSheets' / n).exists()
row.update({'ten_view_files_present': True, 'extra_views': [r['file'] for r in man['extra_views']], 'design_sheets_present': True})
(ROOT / 'validation.json').write_text(json.dumps([row], ensure_ascii=False, indent=2))
print('EATERY_VERIFIED', json.dumps(row, ensure_ascii=False), flush=True)
