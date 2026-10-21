"""Reopen the six FreshIngredients13 .blend files, check sizes / container placement, round-trip FBX, check views; writes ../validation.json.
Run: blender --background --factory-startup --python verify_fresh13.py
"""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from fresh_specs import NAMES, CONTAINERS, SPECS

# Parts allowed to reach past the container outline (leafy tops splay outwards).
OVERHANG_OK = ('Radish_Leaf', 'Carrot_Leaf', 'Napa_Outer_Leaf', 'Scallion')
s = SPECS
# Items without a container: expected outer size and tolerance (x, y, z).
FREE = {
    'RiceSack': ((2 * s['RiceSack']['belly_r'], 2 * s['RiceSack']['belly_r'], s['RiceSack']['rice_top'] + .14), (.06, .06, .04)),   # cloth folds, scoop handle
    'CuredMeatRack': ((s['CuredMeatRack']['width'] + .08, s['CuredMeatRack']['depth'], s['CuredMeatRack']['h']), (.06, .06, .03)),
}


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
    row = {'asset': aid, 'name_zh': NAMES[aid], 'blend_reopened': True, 'bottom_center_pivot_checked': True, 'dimensions_m': [round(c, 4) for c in size]}
    spec = CONTAINERS[aid]
    if spec:
        cname, scale, skip = spec; ce = bpy.data.objects[f'Container_{cname}']
        cont = [o for o in ce.children_recursive if o.type == 'MESH']; food = [o for o in meshes if o not in cont]
        assert cont and food and tuple(round(v, 4) for v in ce.get('baked_scale', ce.scale)) == tuple(scale) and not any(o.name.startswith(tuple(skip)) for o in cont), (aid, 'container')
        clo, chi = bounds(cont); inside = [o for o in food if not o.name.startswith(OVERHANG_OK)]
        flo, fhi = bounds(inside)
        assert flo.x >= clo.x - .005 and fhi.x <= chi.x + .005 and flo.y >= clo.y - .005 and fhi.y <= chi.y + .005, (aid, 'outside container', flo, fhi, clo, chi)
        assert flo.z > clo.z + .005 and fhi.z > clo.z + .03, (aid, 'height', flo.z, fhi.z)
        row.update({'container': cname, 'container_scale': list(scale), 'container_meshes': len(cont), 'item_meshes': len(food), 'items_inside_container_checked': True})
    else:
        want, tol = FREE[aid]
        assert all(-.01 <= size[i] - want[i] <= tol[i] for i in range(3)), (aid, 'size', list(size), want)
        row['spec_size_checked'] = True
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
    row.update({'meshes': count, 'extra_views': [r['file'] for r in man['extra_views']], 'fbx_reimported': True, 'fbx_no_studio_objects': True,
                'fbx_dimension_error_m': delta, 'ten_view_files_present': True, 'design_sheet_present': True})
    results.append(row); print('VERIFIED', aid, flush=True)
(ROOT / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
assert len(results) == 6
print('ALL_SIX_VERIFIED', flush=True)
