"""Reopen the eight KitchenWare09 .blend files, round-trip FBX bounds, check specs and views; writes validation.json.
Run: blender --background --factory-startup --python verify_kitchen09.py
"""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from kitchen_specs import NAMES, SPECS

# Expected overall size (x, y, z) from the specs, with a tolerance for rims, ears, handles and logs.
EXPECTED = {
    'CookingHearth': ((1.24, .8, .824), (.0, .45, .05)),   # firewood sticks out of the fire mouth
    'IronWok': ((.55, .55, .16), (.13, .02, .03)),          # loop ears widen X
    'BambooSteamer': ((.40, .40, .275), (.03, .03, .03)),
    'PrepBoard': ((.45, .30, .048), (.005, .005, .01)),
    'CeramicBowl': ((.16, .16, .0725), (.002, .002, .002)),
    'CeramicPlate': ((.24, .24, .0305), (.002, .002, .002)),
    'DiningTable': ((1.0, 1.0, .75), (.005, .005, .005)),
    'RoundStool': ((.32, .32, .45), (.005, .005, .005)),
}


def bounds(objects):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objects:
        e = o.evaluated_get(dg); m = e.to_mesh(); pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


def png_ok(path):
    data = path.read_bytes()
    assert len(data) > 1000 and data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (1024, 1024), path
    return hashlib.sha256(data).hexdigest()


results = []
for aid in NAMES:
    path = ROOT / 'Models' / aid / 'v001' / f'{aid}_v001.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    meshes = [o for o in bpy.data.collections['01_Editable_Asset'].objects if o.type == 'MESH']
    assert meshes and bpy.data.objects.get(aid + '_ROOT')
    assert all(o.data.vertices and o.data.polygons for o in meshes)
    assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
    lo, hi = bounds(meshes); size = hi - lo
    assert abs(lo.z) < .001 and abs(lo.x + hi.x) < .001 and abs(lo.y + hi.y) < .001, (aid, 'pivot', lo, hi)
    want, tol = EXPECTED[aid]
    assert all(-.006 <= size[i] - want[i] <= tol[i] + .002 for i in range(3)), (aid, 'size', list(size), want)
    row = {'asset': aid, 'name_zh': NAMES[aid], 'blend_reopened': True, 'meshes': len(meshes), 'vertices_finite': True,
           'bottom_center_pivot_checked': True, 'dimensions_m': [round(c, 4) for c in size], 'spec_size_checked': True}
    if aid == 'BambooSteamer':
        assert {o.name.split('_')[0] + '_' + o.name.split('_')[1] for o in meshes if o.name.startswith('Tier')} == {'Tier_1', 'Tier_2'}
        assert any(o.name.startswith('Lid') for o in meshes); row['tiers_and_lid_separate'] = True
    if aid == 'CookingHearth':
        seat = bpy.data.objects['Cast_Iron_Wok_Seat']; r = seat.dimensions.x / 2
        assert SPECS['IronWok']['mouth_d'] / 2 > r - .012 > SPECS['CookingHearth']['wok_hole_r'] - .001
        row['wok_rests_on_seat_checked'] = True
    count = len(meshes)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path.with_suffix('.fbx')))
    imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    a, b = bounds(imported); delta = max(abs(size[i] - (b - a)[i]) for i in range(3))
    assert len(imported) == count, (aid, 'mesh count mismatch')
    assert delta < .001, (aid, 'FBX bounds mismatch')
    assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
    refs = ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001'
    manifest = json.loads((refs / 'views.json').read_text())
    assert len(manifest['views']) == 10 and len({tuple(r['direction']) for r in manifest['views']}) == 10
    assert all(r['framing_checked'] for r in manifest['views'])
    digests = {png_ok(refs / r['file']) for r in manifest['views'] + manifest['extra_views']}
    assert len(digests) == 10 + len(manifest['extra_views'])
    assert (ROOT / 'DesignSheets' / f'{aid}_design.png').exists()
    row.update({'fbx_reimported': True, 'fbx_no_studio_objects': True, 'fbx_dimension_error_m': delta, 'ten_view_files_present': True,
                'extra_views': [r['file'] for r in manifest['extra_views']], 'design_sheet_present': True})
    results.append(row); print('VERIFIED', aid, flush=True)
(ROOT / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
assert len(results) == 8
print('ALL_EIGHT_VERIFIED', flush=True)
