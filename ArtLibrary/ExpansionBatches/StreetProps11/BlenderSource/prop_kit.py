"""Blender helpers for single-prop batches (from StreetProps11 on): primitives, export and same-geometry ten views.
Usage in a build script:
    import prop_kit as K
    K.build_all(ROOT, BUILDERS, NAMES, DETAILS, SPECS, batch='StreetProps11', materials=make_materials)
Each builder calls K.box / K.cyl / K.beam / K.torus / K.lathe / K.mesh; objects are parented to the asset root.
"""
import bpy, bmesh, math, json
from mathutils import Vector

VIEWS = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_rear', (0, 1, 0)), ('04_left', (-1, 0, 0)),
         ('05_front_right', (1, -1, .45)), ('06_rear_right', (1, 1, .45)), ('07_rear_left', (-1, 1, .45)),
         ('08_front_left', (-1, -1, .45)), ('09_top', (0, 0, 1)), ('10_high_front', (0, -1, 1))]
assets = root = None


def mat(name, c, metal=0, rough=.65, noise=40, bump=.12, emission=0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*c, 1); m.use_nodes = True
    n = m.node_tree.nodes; bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*c, 1); bs.inputs['Metallic'].default_value = metal; bs.inputs['Roughness'].default_value = rough
    if emission: bs.inputs['Emission Color'].default_value = (*c, 1); bs.inputs['Emission Strength'].default_value = emission
    t = n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = noise; t.inputs['Detail'].default_value = 4
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = .01
    m.node_tree.links.new(t.outputs['Fac'], b.inputs['Height']); m.node_tree.links.new(b.outputs['Normal'], bs.inputs['Normal'])
    return m


def place(o, name, m, bevel=0, smooth=False):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    assets.objects.link(o); o.parent = root
    if m: o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Soft_edges', 'BEVEL'); mod.width = bevel; mod.segments = 2; mod.limit_method = 'ANGLE'
        o.modifiers.new('Weighted_normals', 'WEIGHTED_NORMAL')
    if smooth:
        for f in o.data.polygons: f.use_smooth = True
    return o


def box(name, p, s, m, bevel=.006, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p); o = bpy.context.object; o.dimensions = s
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.rotation_euler = rot
    return place(o, name, m, bevel if min(s) > 3 * bevel else 0)


def cyl(name, p, r, d, m, verts=32, rot=(0, 0, 0), bevel=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=p, rotation=rot)
    return place(bpy.context.object, name, m, min(r * .1, .005) if bevel is None else bevel)


def beam(name, a, b, r, m, verts=12):
    a, b = Vector(a), Vector(b); o = cyl(name, (a + b) / 2, r, (b - a).length, m, verts, bevel=0)
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); return o


def slab(name, a, b, width, thick, m, up=(0, 0, 1)):
    """Board from a to b (centre line), given width across and thickness."""
    a, b = Vector(a), Vector(b); o = box(name, (a + b) / 2, (width, thick, (b - a).length), m, .004)
    o.rotation_euler = (b - a).to_track_quat('Z', 'X').to_euler(); return o


def torus(name, p, major, minor, m, rot=(0, 0, 0), seg=48):
    bpy.ops.mesh.primitive_torus_add(major_segments=seg, minor_segments=10, location=p, major_radius=major, minor_radius=minor, rotation=rot)
    return place(bpy.context.object, name, m, smooth=True)


def mesh(name, v, f, m, smooth=False):
    d = bpy.data.meshes.new(name + '_Mesh'); d.from_pydata(v, [], f); d.update(); d.validate()
    bm = bmesh.new(); bm.from_mesh(d); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(d); bm.free()
    o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o); return place(o, name, m, smooth=smooth)


def lathe(name, profile, m, p=(0, 0, 0), segments=64, closed=False):
    pts = list(profile) + ([profile[0]] if closed else [])
    v = [(p[0] + r * math.cos(i * math.tau / segments), p[1] + r * math.sin(i * math.tau / segments), p[2] + z) for r, z in pts for i in range(segments)]
    f = [(j * segments + i, j * segments + (i + 1) % segments, (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
         for j in range(len(pts) - 1) for i in range(segments)]
    d = bpy.data.meshes.new(name + '_Mesh'); d.from_pydata(v, [], f)
    bm = bmesh.new(); bm.from_mesh(d); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(d); bm.free()
    o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o)
    return place(o, name, m, smooth=True)


def gable_roof(prefix, half_x, half_y, eave_z, ridge_z, tile, timber, strips=None):
    """Small two-slope tile roof with ridge along X: underlay boards plus half-round tile strips and a ridge cap."""
    for side in (-1, 1):
        slope = math.atan2(ridge_z - eave_z, half_y)
        n = strips or max(4, round(2 * half_x / .14))
        o = box(f'{prefix}_Underlay', (0, side * half_y / 2, (ridge_z + eave_z) / 2 - .02), (2 * half_x, math.hypot(half_y, ridge_z - eave_z), .03), timber, .004)
        o.rotation_euler.x = -side * slope   # ridge edge up on both slopes
        for i in range(n):
            x = -half_x + (i + .5) * 2 * half_x / n; v = []; f = []
            for t in (0, 1):
                for j in range(7):
                    ang = math.pi * j / 6; xx = x + (half_x / n) * .95 * math.cos(ang)
                    v.append((xx, side * t * half_y, ridge_z + (eave_z - ridge_z) * t + .025 * math.sin(ang)))
            f = [(j, j + 1, j + 8, j + 7) for j in range(6)]
            if side > 0: f = [tuple(reversed(q)) for q in f]
            o = mesh(f'{prefix}_Tile_Strip', v, f, tile); o.modifiers.new('Ceramic_Thickness', 'SOLIDIFY').thickness = .012
    beam(f'{prefix}_Ridge_Cap', (-half_x - .02, 0, ridge_z + .01), (half_x + .02, 0, ridge_z + .01), .035, tile)


def build_all(ROOT, BUILDERS, NAMES, DETAILS, SPECS, batch, materials, ids=None, extra=None):
    """Build, export and render every asset id (skips assets whose views.json exists)."""
    global assets, root
    from bpy_extras.object_utils import world_to_camera_view
    extra = extra or {}
    for aid in (ids or list(BUILDERS)):
        out = ROOT / 'Models' / aid / 'v001'; refs = ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001'
        if (refs / 'views.json').exists(): print('ALREADY_COMPLETE', aid, flush=True); continue
        out.mkdir(parents=True, exist_ok=True); refs.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
        scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1.0
        assets = bpy.data.collections.new('01_Editable_Asset'); scene.collection.children.link(assets)
        root = bpy.data.objects.new(aid + '_ROOT', None); assets.objects.link(root)
        root['stage'] = 'Editable appearance prototype; not game-ready; no baked textures, LOD or collision.'
        materials(); BUILDERS[aid](); bpy.context.view_layer.update()
        objects = [o for o in assets.objects if o.type == 'MESH']

        def bounds():
            dg = bpy.context.evaluated_depsgraph_get(); pts = []
            for o in objects:
                e = o.evaluated_get(dg); me = e.to_mesh(); pts += [e.matrix_world @ v.co for v in me.vertices]; e.to_mesh_clear()
            return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

        lo, hi = bounds(); shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
        for o in objects: o.location -= shift
        bpy.context.view_layer.update(); lo, hi = bounds(); centre = (lo + hi) / 2; extent = hi - lo
        studio = bpy.data.collections.new('90_Studio_Not_Exported'); scene.collection.children.link(studio)
        cam = bpy.data.objects.new('Reference_Camera', bpy.data.cameras.new('Reference_Camera')); studio.objects.link(cam); scene.camera = cam
        cam.data.type = 'ORTHO'; cam.data.clip_start = .001; cam.data.clip_end = 100; L = extent.length; cam.data.ortho_scale = max(L * 1.18, .12)
        k = max(L, .3) / 1.6
        for name, d, power, size in [('Key', (-3, -4, 6), 520, 4), ('Fill', (4, -1, 3), 260, 4), ('Rim', (0, 4, 5), 420, 3)]:
            ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power * k * k; ld.shape = 'DISK'; ld.size = size * k
            o = bpy.data.objects.new(name, ld); studio.objects.link(o); o.location = centre + Vector(d) * k
            o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
        scene.world = bpy.data.worlds.new('Warm_Gray_Studio'); scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.19, .21, .20, 1); bg.inputs[1].default_value = .7
        scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 24; scene.cycles.use_denoising = True
        scene.render.resolution_x = scene.render.resolution_y = 1024; scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'AgX'
        bpy.ops.object.select_all(action='DESELECT')
        for o in [root] + objects: o.select_set(True)
        bpy.context.view_layer.objects.active = root
        bpy.ops.export_scene.fbx(filepath=str(out / f'{aid}_v001.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'}, add_leaf_bones=False,
                                 axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_anim=False)
        bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{aid}_v001.blend'))
        info = {'asset': aid, 'name_zh': NAMES[aid], 'batch': batch, 'stage': 'appearance_prototype', 'description': DETAILS[aid], 'units': 'meters',
                'front': '-Y', 'origin': 'bottom centre', 'dimensions_m': [round(c, 4) for c in extent], 'mesh_objects': len(objects),
                'design_sheet': f'DesignSheets/{aid}_design.png', 'spec': SPECS[aid], 'blender_version': bpy.app.version_string,
                'modeling_method': 'procedural editable mesh built from the batch spec file; views rendered from the same model',
                'uv_baked': False, 'collision': False, 'lod': False, 'unreal_import_verified': False}
        (out / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2))

        def render(name, d):
            cam.location = centre + Vector(d).normalized() * L * 3
            cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            pts = [world_to_camera_view(scene, cam, e.matrix_world @ Vector(p)) for o in objects for e in [o.evaluated_get(dg)] for p in e.bound_box]
            assert all(.005 < p.x < .995 and .005 < p.y < .995 and p.z > 0 for p in pts), (aid, name, 'cropped')
            scene.render.filepath = str(refs / (name + '.png')); bpy.ops.render.render(write_still=True); print('VIEW_COMPLETE', aid, name, flush=True)
            return {'file': name + '.png', 'camera_location': [round(c, 4) for c in cam.location], 'direction': d, 'projection': 'orthographic', 'framing_checked': True}

        records = [render(n, d) for n, d in VIEWS]
        extras = [render(n, d) for n, d in extra.get(aid, [])]
        (refs / 'views.json').write_text(json.dumps({'asset': aid, 'source': f'Models/{aid}/v001/{aid}_v001.blend', 'same_geometry': True,
                                                     'views': records, 'extra_views': extras}, indent=2))
        print('ASSET_COMPLETE', aid, flush=True)
