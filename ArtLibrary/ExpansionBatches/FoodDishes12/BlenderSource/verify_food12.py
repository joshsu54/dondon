"""Reopen the six FoodDishes12 .blend files, check container + food placement, round-trip FBX, check views; writes ../validation.json.
Run: blender --background --factory-startup --python verify_food12.py
"""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from food_specs import NAMES, CONTAINERS

# Food allowed outside the container's plan outline: chopsticks rest across the noodle bowl rim.
OVERHANG_OK = ('Chopstick',)


def bounds(objects):
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in objects:
        e = o.evaluated_get(dg); m = e.to_mesh(); pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


results = []
for aid in NAMES:
    path = ROOT / 'Models' / aid / 'v001' / f'{aid}_v001.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    meshes = [o for o in bpy.data.collections['01_Editable_Asset'].objects if o.type == 'MESH']
    assert meshes and bpy.data.objects.get(aid + '_ROOT') and all(o.data.vertices and o.data.polygons for o in meshes)
    assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
    lo, hi = bounds(meshes); size = hi - lo
    assert abs(lo.z) < .001 and abs(lo.x + hi.x) < .001 and abs(lo.y + hi.y) < .001, (aid, 'pivot')
    cname, scale, skip = CONTAINERS[aid]
    ce = bpy.data.objects[f'Container_{cname}']
    cont = [o for o in ce.children_recursive if o.type == 'MESH']; food = [o for o in meshes if o not in cont]
    assert cont and food and tuple(round(v, 4) for v in ce.scale) == tuple(scale), (aid, 'container')
    assert not any(o.name.startswith(skip) for o in cont) if skip else True
    clo, chi = bounds(cont)
    # Plan outline: food stays inside the container (5 mm tolerance) except listed overhangs.
    inside = [o for o in food if not o.name.startswith(OVERHANG_OK)]
    flo, fhi = bounds(inside)
    assert flo.x >= clo.x - .005 and fhi.x <= chi.x + .005 and flo.y >= clo.y - .005 and fhi.y <= chi.y + .005, (aid, 'food outside container', flo, fhi, clo, chi)
    # Food rests in the container: its lowest point is above the container bottom and its top is visible above the floor.
    assert flo.z > clo.z + .005 and fhi.z > clo.z + .02, (aid, 'food height', flo.z, fhi.z)
    row = {'asset': aid, 'name_zh': NAMES[aid], 'container': cname, 'container_scale': list(scale), 'container_meshes': len(cont), 'food_meshes': len(food),
           'blend_reopened': True, 'bottom_center_pivot_checked': True, 'food_inside_container_checked': True,
           'dimensions_m': [round(c, 4) for c in size], 'food_top_m': round(fhi.z, 4)}
    count = len(meshes)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path.with_suffix('.fbx')))
    imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    a, b = bounds(imported); delta = max(abs(size[i] - (b - a)[i]) for i in range(3))
    assert len(imported) == count and delta < .001, (aid, 'fbx', len(imported), count, delta)
    assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
    refs = ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001'
    man = json.loads((refs / 'views.json').read_text())
    assert len(man['views']) == 10 and len({tuple(r['direction']) for r in man['views']}) == 10 and all(r['framing_checked'] for r in man['views'])
    digests = set()
    for r in man['views'] + man['extra_views']:
        data = (refs / r['file']).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (1024, 1024); digests.add(hashlib.sha256(data).hexdigest())
    assert len(digests) == 10 + len(man['extra_views']) and (ROOT / 'DesignSheets' / f'{aid}_design.png').exists()
    row.update({'meshes': count, 'extra_views': [r['file'] for r in man['extra_views']], 'fbx_reimported': True, 'fbx_no_studio_objects': True, 'fbx_dimension_error_m': delta, 'ten_view_files_present': True, 'design_sheet_present': True})
    results.append(row); print('VERIFIED', aid, flush=True)
assert (ROOT / 'table_setting_preview.png').exists()
(ROOT / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
assert len(results) == 6
print('ALL_SIX_VERIFIED', flush=True)
