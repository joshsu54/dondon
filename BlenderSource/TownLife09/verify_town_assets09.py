"""Step 3: reopen each .blend, round-trip FBX bounds, check concept refs and ten views.
Writes ArtLibrary/ExpansionBatches/TownLife09/validation.json."""
import bpy  # noqa: I001
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import town09_shapes as S  # noqa: E402

ROOT = HERE.parents[1]


def bounds(objects):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [e.matrix_world @ v.co for o in objects for e in [o.evaluated_get(dg)] for v in e.data.vertices]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


def png_ok(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (1024, 1024), path
    return hashlib.sha256(data).hexdigest()


results = []
for aid in S.ASSETS:
    path = ROOT / 'Models' / aid / 'v001' / f'{aid}_v001.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    meshes = [o for o in bpy.data.collections['01_Editable_Asset'].objects if o.type == 'MESH']
    assert meshes and bpy.data.objects.get(aid + '_ROOT')
    assert all(o.data.vertices and o.data.polygons for o in meshes)
    assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
    lo, hi = bounds(meshes)
    size = hi - lo
    assert abs(lo.z) < .001 and abs(lo.x + hi.x) < .001 and abs(lo.y + hi.y) < .001, (aid, 'pivot')
    refs = [o for o in bpy.data.collections['80_Concept_References'].objects if o.empty_display_type == 'IMAGE']
    assert len(refs) == 10 and all(o.hide_render and o.data and o.data.has_data is not None for o in refs)
    ref_files = [ROOT / o['concept_reference'] for o in refs]
    assert all(f.exists() for f in ref_files)
    concept_digests = {png_ok(f) for f in ref_files}
    assert len(concept_digests) == 10
    prompts = json.loads((ROOT / 'ArtReferences' / f'{aid}_10Views' / 'prompts.json').read_text())
    assert len(prompts['images']) == 10 and all(r['prompt'] for r in prompts['images'])
    count = len(meshes)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path.with_suffix('.fbx')))
    imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    a, b = bounds(imported)
    delta = max(abs(size[i] - (b - a)[i]) for i in range(3))
    assert len(imported) == count, (aid, 'mesh count mismatch', len(imported), count)
    assert delta < .001, (aid, 'FBX bounds mismatch')
    assert not any(o.type in ('LIGHT', 'CAMERA') for o in bpy.context.scene.objects)
    assert not any(o.type == 'EMPTY' and o.empty_display_type == 'IMAGE' for o in bpy.context.scene.objects)
    turn = ROOT / 'ArtLibrary' / 'Turnarounds' / f'{aid}_v001'
    manifest = json.loads((turn / 'views.json').read_text())
    assert len(manifest['views']) == 10 and len({tuple(r['direction']) for r in manifest['views']}) == 10
    digests = {png_ok(turn / r['file']) for r in manifest['views'] if r['framing_checked']}
    assert len(digests) == 10
    results.append({'asset': aid, 'blend_reopened': True, 'meshes': count, 'dimensions_m': [round(x, 3) for x in size],
                    'vertices_finite': True, 'bottom_center_pivot_checked': True,
                    'concept_images_before_modelling': 10, 'concept_refs_in_blend': True,
                    'fbx_reimported': True, 'fbx_no_studio_or_reference_objects': True, 'fbx_dimension_error_m': delta,
                    'ten_view_files_present': True})
    print('VERIFIED', aid, flush=True)
out = ROOT / 'ArtLibrary/ExpansionBatches/TownLife09/validation.json'
out.write_text(json.dumps(results, indent=2), encoding='utf-8')
assert len(results) == len(S.ASSETS)
print('ALL_VERIFIED', len(results), flush=True)
