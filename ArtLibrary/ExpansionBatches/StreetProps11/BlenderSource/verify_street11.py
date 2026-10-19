"""Reopen the six StreetProps11 .blend files, round-trip FBX bounds, check spec sizes and views; writes ../validation.json.
Run: blender --background --factory-startup --python verify_street11.py
"""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from street_specs import NAMES, SPECS

s = SPECS
# Expected outer size (x, y, z) from the spec, and what may legitimately stick out beyond it.
EXPECTED = {
    'StoneWell': ((s['StoneWell']['roof']['half_x'] + .02 + s['StoneWell']['post_x'] + .26, 2 * s['StoneWell']['apron_r'], s['StoneWell']['roof']['ridge_z'] + .045), (.01, .01, .01)),   # roof+ridge cap on the left, crank on the right
    'WellBucket': ((2 * s['WellBucket']['top_r'], 2 * s['WellBucket']['top_r'], s['WellBucket']['h'] + .16), (.02, .02, .02)),                       # hoops, rope bail
    'NoticeBoard': ((s['NoticeBoard']['roof_w'], s['NoticeBoard']['roof_d'], s['NoticeBoard']['post_h'] + s['NoticeBoard']['roof_rise']), (.06, .03, .05)),
    'WoodenCrate': ((s['WoodenCrate']['size'][0], s['WoodenCrate']['size'][1], s['WoodenCrate']['size'][2] + s['WoodenCrate']['lid_t']), (.03, .01, .03)),
    'BambooBasket': ((2 * s['BambooBasket']['top_r'], 2 * s['BambooBasket']['top_r'], s['BambooBasket']['h']), (.02, .08, .02)),                     # straps on the back
    'FirewoodStack': ((s['FirewoodStack']['length'] + .3 - .01,  # cap planks with 10 mm gaps
                      s['FirewoodStack']['depth'] + .24, s['FirewoodStack']['cap_z'][1]), (.0, .02, .05)),
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
    want, tol = EXPECTED[aid]
    assert all(-.006 <= size[i] - want[i] <= tol[i] + .006 for i in range(3)), (aid, 'size', list(size), want)
    row = {'asset': aid, 'name_zh': NAMES[aid], 'blend_reopened': True, 'meshes': len(meshes), 'vertices_finite': True,
           'bottom_center_pivot_checked': True, 'dimensions_m': [round(c, 4) for c in size], 'spec_size_checked': True}
    if aid == 'StoneWell':
        # Wall top is a usable lean height and the hanging bucket clears the coping.
        cop = bounds([o for o in meshes if o.name.startswith('Well_Coping')])[1].z
        bucket = bounds([o for o in meshes if o.name.startswith('Hanging_Bucket_Stave')])[0].z
        assert .75 <= cop <= .9 and bucket > cop, (cop, bucket)
        row.update({'coping_height_m': round(cop, 3), 'hanging_bucket_clearance_m': round(bucket - cop, 3)})
    if aid == 'WoodenCrate': assert sum(o.name.startswith('Lid_') for o in meshes) == 6; row['lid_separate'] = True
    if aid == 'NoticeBoard': assert sum(o.name.startswith('Blank_Notice') for o in meshes) == 4; row['blank_notices'] = 4
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
    row.update({'fbx_reimported': True, 'fbx_no_studio_objects': True, 'fbx_dimension_error_m': delta, 'ten_view_files_present': True,
                'extra_views': [r['file'] for r in man['extra_views']], 'design_sheet_present': True})
    results.append(row); print('VERIFIED', aid, flush=True)
(ROOT / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
assert len(results) == 6
print('ALL_SIX_VERIFIED', flush=True)
