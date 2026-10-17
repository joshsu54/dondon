"""Reopen TownLayout v003, compare the v002 part with its source, round-trip the FBX.
Writes Models/TownLayout/v003/validation.json."""
import bpy  # noqa: I001
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_town_layout_v003 import OUT, PLACEMENTS, RAILS, ROOT, SRC  # noqa: E402


def mesh_objects(exclude=('80_', '90_')):
    return [o for o in bpy.context.scene.objects if o.type == 'MESH'
            and not any(c.name.startswith(exclude) for c in o.users_collection)]


bpy.ops.wm.open_mainfile(filepath=str(SRC))
source_names = {o.name for o in mesh_objects()}
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'TownLayout_v003.blend'))
names = {o.name for o in mesh_objects()}
missing_v002 = sorted(source_names - names)
assert not missing_v002, missing_v002[:10]
north = bpy.data.collections['12_North_Block_v003']
instances = [c for c in north.children_recursive if any(o.name.endswith('_ROOT') for o in c.objects)]
expected = len(PLACEMENTS) + len(RAILS)
assert len(instances) == expected, (len(instances), expected)
refs = [o for o in bpy.data.collections['80_Concept_References'].objects if o.empty_display_type == 'IMAGE']
assert len(refs) == 10 and all((ROOT / o['concept_reference']).exists() and o.hide_render for o in refs)
count = len(mesh_objects())
# walking surface along the new street, cast from head height (under the archway) and taking the
# highest hit in a 3 x 3 patch so paver joints do not count as holes
from mathutils import Vector  # noqa: E402
dg = bpy.context.evaluated_depsgraph_get()
street = []
for y in (12.4, 14.7, 17.9, 20.9, 23.9, 26.2, 29.2, 32.9):
    zs = []
    for dx in (-.1, 0, .1):
        for dy in (-.1, 0, .1):
            hit, loc, *_ = bpy.context.scene.ray_cast(dg, Vector((.27 + dx, y + dy, 3.0)), Vector((0, 0, -1)))
            if hit:
                zs.append(loc.z)
    street.append({'y': y, 'surface_z': round(max(zs), 3)})
assert all(abs(s['surface_z'] - 1.32) < .04 for s in street), street
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT / 'TownLayout_v003.fbx'))
imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
assert len(imported) == count, (len(imported), count)
assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
result = {'blend_reopened': True, 'v002_mesh_objects_all_present': len(source_names), 'placed_instances': expected,
          'mesh_objects': count, 'fbx_reimported_mesh_objects': len(imported), 'concept_refs_in_blend': 10,
          'north_street_surface_samples': street, 'previews': sorted(p.name for p in OUT.glob('0*.png')),
          'scope': 'geometry/layout check only; no character, collision, navigation or Unreal test'}
(OUT / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('LAYOUT_VERIFIED', json.dumps(result), flush=True)
