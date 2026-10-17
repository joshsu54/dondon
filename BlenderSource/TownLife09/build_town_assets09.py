"""Step 2 of TownLife09: model each asset in Blender from its concept references.

Requires the ten concept sketches from concept_render09.py to exist first; they
are loaded into each .blend as reference images (collection 80_Concept_References,
never rendered or exported). Every part of the design spec is then modelled with
bevels and materials, exported to FBX, and ten views are rendered from the same
geometry into ArtLibrary/Turnarounds/<Asset>_v001.

Run: python3 build_town_assets09.py [AssetId ...]   (pip bpy) or
     blender --background --python build_town_assets09.py -- [AssetId ...]
"""
import json
import math
import sys
from pathlib import Path

import bpy  # noqa: I001  (bpy must load before bmesh)
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spec import S  # noqa: E402

ROOT = HERE.parents[1]
LIGHT_SCALE, WORLD_STRENGTH, EXPOSURE = .5, .45, 0.0
BACKDROP = (98, 102, 104)   # flat studio grey of the earlier Codex turnarounds


def flatten_backdrop(path):
    from PIL import Image
    fg = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', fg.size, BACKDROP + (255,))
    Image.alpha_composite(bg, fg).convert('RGB').save(path)


def make_materials():
    mats = {}
    for name, (lin, _) in S.PALETTE.items():
        m = bpy.data.materials.new('TL09_' + name.capitalize())
        m.diffuse_color = (*lin, 1)
        m.use_nodes = True
        n, l = m.node_tree.nodes, m.node_tree.links
        bs = n.get('Principled BSDF')
        bs.inputs['Base Color'].default_value = (*lin, 1)
        bs.inputs['Roughness'].default_value = .35 if name in ('glaze', 'water', 'lacquer') else .82
        if name in ('iron', 'brass'):
            bs.inputs['Metallic'].default_value = .7
            bs.inputs['Roughness'].default_value = .5
        if name == 'lantern':
            bs.inputs['Emission Color'].default_value = (1, .35, .12, 1)
            bs.inputs['Emission Strength'].default_value = .6
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 24
        tex.inputs['Detail'].default_value = 3
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .15
        bump.inputs['Distance'].default_value = .02
        l.new(tex.outputs['Fac'], bump.inputs['Height'])
        l.new(bump.outputs[0], bs.inputs['Normal'])
        mats[name] = m
    return mats


def part_object(p, mats, coll, root):
    me = bpy.data.meshes.new(p.name)
    me.from_pydata([tuple(v) for v in p.verts], [], [tuple(f) for f in p.faces])
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mats[p.color])
    o = bpy.data.objects.new(p.name, me)
    coll.objects.link(o)
    o.parent = root
    # origin at each part's bottom centre for easy re-use
    lo = Vector([min(v.co[i] for v in me.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in me.vertices) for i in range(3)])
    pivot = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    me.transform(Matrix.Translation(-pivot))
    o.location = pivot
    if p.smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    small = min(hi - lo)
    if p.bevel and small > .008:
        mod = o.modifiers.new('Edge_Soften', 'BEVEL')
        mod.width = min(.012, small * .18)
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        o.modifiers.new('Weighted_Normals', 'WEIGHTED_NORMAL').keep_sharp = True
    return o


def actual_bounds(objects):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = [e.matrix_world @ v.co for o in objects for e in [o.evaluated_get(dg)] for v in e.data.vertices]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


def add_concept_refs(aid, scene, extent, centre):
    refs = ROOT / 'ArtReferences' / f'{aid}_10Views'
    files = [refs / f'{v}.png' for v, _, _ in S.VIEWS]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise SystemExit(f'{aid}: concept references missing {missing}; run concept_render09.py first')
    coll = bpy.data.collections.new('80_Concept_References')
    scene.collection.children.link(coll)
    size = max(extent.x, extent.z) * 1.1
    for i, f in enumerate(files):
        img = bpy.data.images.load(str(f), check_existing=True)
        e = bpy.data.objects.new('Concept_' + f.stem, None)
        e.empty_display_type = 'IMAGE'
        e.data = img
        e.empty_display_size = size
        e.empty_image_offset = (-.5, 0)
        e.location = (centre.x + (i % 5 - 2) * size * 1.05, centre.y + extent.y / 2 + size * .6 + (i // 5) * .01,
                      (1 - i // 5) * size * 1.05)
        e.rotation_euler = (math.pi / 2, 0, 0)
        e.hide_render = True
        e['concept_reference'] = f'ArtReferences/{aid}_10Views/{f.name}'
        coll.objects.link(e)
    return len(files)


def build(aid):
    spec = S.ASSETS[aid]
    out = ROOT / 'Models' / aid / 'v001'
    turn = ROOT / 'ArtLibrary' / 'Turnarounds' / f'{aid}_v001'
    out.mkdir(parents=True, exist_ok=True)
    turn.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.context.preferences.filepaths.save_version = 0
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    assets = bpy.data.collections.new('01_Editable_Asset')
    scene.collection.children.link(assets)
    root = bpy.data.objects.new(aid + '_ROOT', None)
    assets.objects.link(root)
    root['stage'] = spec['desc']
    mats = make_materials()
    parts = spec['build']().parts
    objects = [part_object(p, mats, assets, root) for p in parts]
    bpy.context.view_layer.update()
    lo, hi = actual_bounds(objects)
    shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in objects:
        o.location -= shift
    bpy.context.view_layer.update()
    lo, hi = actual_bounds(objects)
    centre, extent = (lo + hi) / 2, hi - lo
    n_refs = add_concept_refs(aid, scene, extent, centre)

    studio = bpy.data.collections.new('90_Studio_Not_Exported')
    scene.collection.children.link(studio)

    def studio_obj(name, data):
        o = bpy.data.objects.new(name, data)
        studio.objects.link(o)
        return o

    cam = studio_obj('Reference_Camera', bpy.data.cameras.new('Reference_Camera'))
    scene.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.clip_start, cam.data.clip_end = .01, 1000
    cam.data.ortho_scale = max(extent.length * 1.08, .5)
    ls = max(extent) * .65
    for name, direction, power in [('Key', (-.8, -1.1, 1.5), 1100), ('Fill', (1.2, -.4, .9), 650), ('Rim', (.2, 1.1, 1.3), 950)]:
        d = bpy.data.lights.new(name, 'AREA')
        d.energy = power * ls * ls / 7 * LIGHT_SCALE
        d.shape, d.size = 'DISK', ls
        o = studio_obj(name, d)
        o.location = centre + Vector(direction) * ls
        o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world = bpy.data.worlds.new('Neutral_Studio')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (.19, .21, .22, 1)
    bg.inputs[1].default_value = WORLD_STRENGTH
    scene.render.film_transparent = True
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = EXPOSURE

    def position(direction):
        cam.location = centre + Vector(direction).normalized() * cam.data.ortho_scale * 2.3
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()

    position((1, -1, .65))
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root] + objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(out / f'{aid}_v001.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'},
                             add_leaf_bones=False, axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_anim=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{aid}_v001.blend'), relative_remap=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
    info = {'asset': aid, 'name_zh': spec['name_zh'], 'category': spec['category'], 'stage': 'editable_town_prototype',
            'description': spec['desc'], 'size_note': spec['size'], 'units': 'meters', 'front': '-Y',
            'dimensions_m': list(extent), 'mesh_objects': len(objects), 'bounds_method': 'evaluated mesh vertices',
            'concept_references': f'ArtReferences/{aid}_10Views', 'concept_reference_images': n_refs,
            'modeling_method': 'ten concept sketches drawn first, loaded as reference images, then modelled from the shared design spec; ten views rendered from the same model',
            'uv_baked': False, 'collision': False, 'lod': False, 'unreal_import_verified': False}
    if 'connectors' in spec:
        info['connectors'] = {k: [round(c, 4) for c in (Vector(v) - shift)] for k, v in spec['connectors'].items()}
    (out / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    records = []
    dg = bpy.context.evaluated_depsgraph_get()
    for name, direction, _ in S.VIEWS:
        position(direction)
        projected = [world_to_camera_view(scene, cam, e.matrix_world @ Vector(p)) for o in objects
                     for e in [o.evaluated_get(dg)] for p in e.bound_box]
        assert all(.005 < p.x < .995 and .005 < p.y < .995 and p.z > 0 for p in projected), (aid, name, 'cropped')
        scene.render.filepath = str(turn / f'{name}.png')
        bpy.ops.render.render(write_still=True)
        flatten_backdrop(turn / f'{name}.png')
        records.append({'file': f'{name}.png', 'direction': list(direction), 'camera_location': list(cam.location),
                        'projection': 'orthographic', 'framing_checked': True})
        print('VIEW_COMPLETE', aid, name, flush=True)
    (turn / 'views.json').write_text(json.dumps({'asset': aid, 'source': f'Models/{aid}/v001/{aid}_v001.blend',
                                                 'same_geometry': True, 'concept_references': f'ArtReferences/{aid}_10Views',
                                                 'views': records}, indent=2), encoding='utf-8')
    print('ASSET_COMPLETE', aid, flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    for aid in (args or list(S.ASSETS)):
        build(aid)
