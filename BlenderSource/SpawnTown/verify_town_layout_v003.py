"""Reopen TownLayout v003, re-run the walk checks on the saved file and round-trip the FBX; writes validation.json.
Run: blender --background --factory-startup --python BlenderSource/SpawnTown/verify_town_layout_v003.py
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from town_v003_specs import *

OUT = ROOT / 'Models/TownLayout/v003'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'TownLayout_v003.blend'))
scene = bpy.context.scene
result = {'blend_reopened': True}

for name, (src, loc, rot, note) in PLACEMENTS.items():
    pe = scene.objects[f'{name}_PLACEMENT']
    assert (pe.location - Vector(loc)).length < 1e-4 and abs(math.degrees(pe.rotation_euler.z) - rot) < 1e-3, name
    assert len(pe.children_recursive) > 50, (name, len(pe.children_recursive))
result['placements_verified'] = sorted(PLACEMENTS)
assert all(n not in scene.objects for n in CURBS_REMOVED); result['curbs_removed_verified'] = CURBS_REMOVED
for keep in ('StarterHouse_ROOT', 'Blacksmith_ROOT', 'Spawn_Player_Feet'): assert keep in scene.objects, keep
result['v002_content_kept'] = True

terrain = scene.objects['Terrain_Display_Island']
tx = min((terrain.matrix_world @ v.co).x for v in terrain.data.vertices)
assert abs(tx - TERRAIN_WEST_TO) < .7, tx
result['terrain_west_edge_m'] = round(tx, 3)

deps = bpy.context.evaluated_depsgraph_get()
bad = []
for x, y in LANE_SAMPLES + STREET_SAMPLES:
    hit, pos, n, i, obj, m = scene.ray_cast(deps, Vector((x, y, 2.2)), Vector((0, 0, -1)), distance=3.2)
    ok = hit and (abs(pos.z - WALK_Z) < .02 or (obj.name.endswith('_Mortar') and abs(pos.z - WALK_Z + .05) < .01))
    if not ok: bad.append((x, y, pos.z, obj.name if obj else None))
assert not bad, bad
result['walk_samples_clear_0_to_2_2m'] = len(LANE_SAMPLES + STREET_SAMPLES)

exports = []
for c in scene.collection.children:
    if c.name.startswith(('80_', '90_')): continue
    exports.extend(o for o in c.all_objects if o.type == 'MESH')
exports = list(dict.fromkeys(exports))


def bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objs:
        e = o.evaluated_get(dg); me = e.to_mesh(); pts += [e.matrix_world @ v.co for v in me.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


lo, hi = bounds(exports); count = len(exports)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT / 'TownLayout_v003.fbx'))
imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
a, b = bounds(imported); err = max(abs((hi - lo)[i] - (b - a)[i]) for i in range(3))
assert len(imported) == count, (len(imported), count)
assert err < .001, err
assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
result.update({'source_mesh_objects': count, 'fbx_mesh_objects': len(imported), 'fbx_bounds_error_m': err, 'studio_excluded': True,
               'scene_size_m': [round(c, 2) for c in hi - lo], 'unity_verified': False, 'unreal_verified': False})
(OUT / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print('TOWN_V003_VERIFIED', json.dumps(result), flush=True)
