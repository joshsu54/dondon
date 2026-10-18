"""KitchenWare09: eight editable eatery props, each with ten views rendered from the same mesh.
Run: blender --background --factory-startup -t 4 --python build_kitchen_assets09.py [-- AssetID ...]
Dimensions come from kitchen_specs.py (shared with draw_design_sheets.py). Completed assets are skipped.
Wok, steamer, bowl and plate also get interior / underside views (and an open-lid view for the steamer)
as extra images; these do not replace the ten basic views.
"""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from kitchen_specs import NAMES, DETAILS, SPECS, BOWL_PROFILE, PLATE_PROFILE

VIEWS = [('01_front', (0, -1, 0)), ('02_right', (1, 0, 0)), ('03_rear', (0, 1, 0)), ('04_left', (-1, 0, 0)),
         ('05_front_right', (1, -1, .45)), ('06_rear_right', (1, 1, .45)), ('07_rear_left', (-1, 1, .45)),
         ('08_front_left', (-1, -1, .45)), ('09_top', (0, 0, 1)), ('10_high_front', (0, -1, 1))]
EXTRA = {'IronWok': ['11_interior', '12_underside'], 'CeramicBowl': ['11_interior', '12_underside'],
         'CeramicPlate': ['11_interior', '12_underside'], 'BambooSteamer': ['11_lid_open', '12_underside']}
EXTRA_DIR = {'11_interior': (0, -.35, 1), '12_underside': (.25, -.6, -1), '11_lid_open': (1, -1, .8)}


def mat(name, c, metal=0, rough=.65, noise=40, bump=.12):
    m = bpy.data.materials.new(name); m.diffuse_color = (*c, 1); m.use_nodes = True
    n = m.node_tree.nodes; bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*c, 1); bs.inputs['Metallic'].default_value = metal; bs.inputs['Roughness'].default_value = rough
    tex = n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = noise; tex.inputs['Detail'].default_value = 4
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = .01
    m.node_tree.links.new(tex.outputs['Fac'], b.inputs['Height']); m.node_tree.links.new(b.outputs['Normal'], bs.inputs['Normal'])
    return m


def make_materials():
    global wood, board, plaster, stone, slab, iron, char, bamboo, straw, glaze, clay, ember
    wood = mat('Dark_Chestnut', (.20, .09, .045)); board = mat('Warm_Timber', (.36, .20, .09))
    plaster = mat('Lime_Plaster', (.58, .54, .46), rough=.9, noise=18, bump=.25); stone = mat('Blue_Gray_Stone', (.27, .32, .32), rough=.85)
    slab = mat('Dark_Stone_Slab', (.12, .13, .13), rough=.7); iron = mat('Seasoned_Iron', (.07, .07, .07), .85, .45, 60, .05)
    char = mat('Soot_Char', (.025, .02, .018), rough=1); bamboo = mat('Aged_Bamboo', (.55, .42, .20), rough=.55, noise=90, bump=.08)
    straw = mat('Woven_Bamboo_Lid', (.47, .35, .16), rough=.7, noise=160, bump=.2)
    glaze = mat('Celadon_Glaze', (.30, .40, .34), .05, .25, 30, .03); clay = mat('Raw_Stoneware', (.36, .24, .15), rough=.9)
    ember = mat('Glowing_Ember', (.9, .25, .04)); ember.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3
    ember.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1, .3, .05, 1)


def place(o, name, m, bevel=0, smooth=False):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    assets.objects.link(o); o.parent = root
    if m: o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Soft_edges', 'BEVEL'); mod.width = bevel; mod.segments = 3; mod.limit_method = 'ANGLE'
        o.modifiers.new('Weighted_normals', 'WEIGHTED_NORMAL')
    if smooth:
        for f in o.data.polygons: f.use_smooth = True
    return o


def box(name, p, s, m, bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p); o = bpy.context.object; o.dimensions = s
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return place(o, name, m, bevel)


def cyl(name, p, r, d, m, bevel=None, verts=48, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=p, rotation=rot)
    return place(bpy.context.object, name, m, min(r * .1, .006) if bevel is None else bevel)


def beam(name, a, b, r, m, verts=16):
    a, b = Vector(a), Vector(b); o = cyl(name, (a + b) / 2, r, (b - a).length, m, r * .2, verts)
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); return o


def torus(name, p, major, minor, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=12, location=p, major_radius=major, minor_radius=minor, rotation=rot)
    return place(bpy.context.object, name, m, smooth=True)


def lathe(name, profile, m, p=(0, 0, 0), segments=72, closed=False):
    pts = list(profile) + ([profile[0]] if closed else [])
    v = [(p[0] + r * math.cos(i * math.tau / segments), p[1] + r * math.sin(i * math.tau / segments), p[2] + z) for r, z in pts for i in range(segments)]
    f = [(j * segments + i, j * segments + (i + 1) % segments, (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
         for j in range(len(pts) - 1) for i in range(segments)]
    d = bpy.data.meshes.new(name + '_Mesh'); d.from_pydata(v, [], f)
    bm = bmesh.new(); bm.from_mesh(d); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(d); bm.free()
    o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o)
    return place(o, name, m, smooth=True)


def cut(target, cutter, inner=None):
    """Apply a difference boolean; faces made by the cutter take `inner` material when given."""
    mod = target.modifiers.new('Cut', 'BOOLEAN'); mod.object = cutter; mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'
    if inner:
        cutter.data.materials.clear(); cutter.data.materials.append(inner); mod.material_mode = 'TRANSFER'
    bpy.context.view_layer.objects.active = target
    # Boolean must sit before the bevel so bevelled edges follow the cut.
    while target.modifiers.find('Cut') > 0: bpy.ops.object.modifier_move_up(modifier='Cut')
    bpy.ops.object.modifier_apply(modifier='Cut'); bpy.data.objects.remove(cutter)


def arch_prism(name, cx, z0, w, h, y0, y1):
    """Arched opening solid (flat bottom, semicircular top) extruded along Y."""
    r = w / 2; prof = [(cx - r, z0)] + [(cx - r * math.cos(t * math.pi / 16), z0 + h - r + r * math.sin(t * math.pi / 16)) for t in range(17)] + [(cx + r, z0)]
    v = [(x, y0, z) for x, z in prof] + [(x, y1, z) for x, z in prof]; n = len(prof)
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    d = bpy.data.meshes.new(name); d.from_pydata(v, [], f); d.update(); d.validate()
    o = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(o)
    bm = bmesh.new(); bm.from_mesh(d); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(d); bm.free()
    return o


# ---------------------------------------------------------------- builders

def hearth():
    s = SPECS['CookingHearth']; X, Y, Z = s['size']; ph, th = s['plinth_h'], s['top_h']; hx, hr = s['wok_hole_x'], s['wok_hole_r']
    fm, vent = s['fire_mouth'], s['vent']
    box('Stone_Plinth', (0, 0, ph / 2), (X + .04, Y + .04, ph), stone, .012)
    body = box('Plastered_Body', (0, 0, (ph + Z - th) / 2), (X, Y, Z - th - ph), plaster, .01)
    cut(body, arch_prism('mouth', hx, fm['z'], fm['w'], fm['h'], -Y / 2 - .05, .05), char)
    # Chamber is wider than the wok opening so only soot is visible through it.
    cy0, cy1 = -Y / 2 + .07, Y / 2 - .08; cw = 2 * hr + .05
    cut(body, box('fire_chamber', (hx, (cy0 + cy1) / 2, (fm['z'] + Z - th + .01) / 2), (cw, cy1 - cy0, Z - th - fm['z'] + .01), char, 0), char)
    v = box('vent_cut', (0, Y / 2, vent['z'] + vent['h'] / 2), (vent['w'], .16, vent['h']), plaster, 0); cut(body, v, char)
    top = box('Stone_Cooktop', (0, 0, Z - th / 2), (X + .03, Y + .03, th), slab, .006)
    cut(top, cyl('hole', (hx, .02, Z - th / 2), hr, th + .1, slab, 0, 64))
    torus('Cast_Iron_Wok_Seat', (hx, .02, Z + .004), hr + .012, .012, iron)
    box('Firebox_Floor_Ash', (hx, (cy0 + cy1) / 2, fm['z'] + .006), (cw - .01, cy1 - cy0 - .01, .012), char, 0)
    box('Vent_Soot', (0, Y / 2 - .06, vent['z'] + vent['h'] / 2), (vent['w'], .02, vent['h']), char, 0)
    box('Fire_Mouth_Lintel_Stone', (hx, -Y / 2 - .012, fm['z'] + fm['h'] + .035), (fm['w'] + .12, .03, .07), stone, .006)
    box('Fire_Mouth_Sill', (hx, -Y / 2 - .03, fm['z'] - .012), (fm['w'] + .1, .1, .03), stone, .006)
    for i, (dx, dz, ang) in enumerate([(-.07, .035, .08), (.07, .035, -.06), (0, .09, .02)]):
        o = beam('Firewood_Log_%d' % i, (hx + dx, -Y / 2 - .16, fm['z'] + dz), (hx + dx + ang, -.05, fm['z'] + dz + .02), .032, board, 12)
    box('Embers', (hx, -.08, fm['z'] + .02), (.18, .16, .02), ember, .004)
    for sx in (-1, 1):
        for sy in (-1, 1): box('Corner_Quoin_Stone', (sx * (X / 2 - .03), sy * (Y / 2 - .03), (ph + Z - th) / 2), (.07, .07, Z - th - ph), stone, .006)
    box('Prep_Surface_Board', (.32, 0, Z + .012), (.42, .5, .024), board, .004)


def wok():
    s = SPECS['IronWok']; r, dz, t = s['mouth_d'] / 2, s['depth'], s['wall']
    R = (r * r + dz * dz) / (2 * dz); amax = math.asin(r / R); n = 24
    outer = [(R * math.sin(a), R - R * math.cos(a)) for a in [i / n * amax for i in range(n + 1)]]
    inner = [((R - t) * math.sin(a), R - (R - t) * math.cos(a)) for a in [i / n * amax for i in range(n + 1)]]
    inner = [(x, z) for x, z in inner if z <= dz][::-1]
    lathe('Iron_Wok_Body', outer + inner, iron)
    torus('Rolled_Rim', (0, 0, dz), r - t / 2, .005, iron)
    for sgn in (-1, 1):
        torus('Loop_Ear', (sgn * (r + .025), 0, dz - .012), s['ear_r'] * .62, .007, iron, (0, 0, 0))
        box('Ear_Rivet_Plate', (sgn * (r - .002), 0, dz - .02), (.012, .05, .03), iron, .003)


def steamer():
    s = SPECS['BambooSteamer']; r = s['d'] / 2; th = s['tier_h']

    def tier(i):
        z = i * th; name = 'Tier_%d' % (i + 1)
        parts = [lathe(name + '_Bamboo_Ring', [(r - .012, z), (r, z), (r, z + th), (r - .012, z + th)], bamboo, closed=True)]
        for zz in (.015, .075): parts.append(torus(name + '_Binding', (0, 0, z + zz), r + .002, .004, straw))
        for x in (-.08, .08): parts.append(box(name + '_Floor_Beam', (x, 0, z + .012), (.018, 2 * r - .03, .014), bamboo, .003))
        k = 0
        while -r + .03 + k * .028 < r - .03:
            x = -r + .03 + k * .028; L = 2 * math.sqrt((r - .012) ** 2 - x * x) - .004
            parts.append(box(name + '_Floor_Slat', (0, x, z + .022), (L, .016, .006), bamboo, .001)); k += 1
        return parts

    for i in range(s['tiers']): tier(i)
    lz = s['tiers'] * th
    lathe('Lid_Ring', [(r - .008, lz), (r + .006, lz), (r + .006, lz + s['lid_ring_h']), (r - .008, lz + s['lid_ring_h'])], bamboo, closed=True)
    dome = [(0, lz + s['lid_ring_h'] + s['lid_dome_h'])] + [((r + .004) * math.sin(a * math.pi / 20), lz + s['lid_ring_h'] + s['lid_dome_h'] * math.cos(a * math.pi / 20)) for a in range(1, 11)]
    o = lathe('Lid_Woven_Dome', dome, straw); o.modifiers.new('Weave_thickness', 'SOLIDIFY').thickness = .004
    for k in range(1, 6): torus('Lid_Weave_Ring', (0, 0, lz + s['lid_ring_h'] + s['lid_dome_h'] * math.cos(math.asin(k / 6))), (r + .004) * k / 6, .0025, bamboo)
    torus('Lid_Binding', (0, 0, lz + .015), r + .008, .004, straw)
    top = lz + s['lid_ring_h'] + s['lid_dome_h']
    box('Lid_Handle_Bar', (0, 0, top + .012), (.12, .022, .016), wood, .005)
    for x in (-.05, .05): box('Lid_Handle_Post', (x, 0, top + .002), (.014, .014, .02), wood, .002)


def board_():
    s = SPECS['PrepBoard']; X, Y, Z = s['size']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, Z / 2)); o = bpy.context.object; o.dimensions = (X, Y, Z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Vertical corner edges get the 30 mm round; top/bottom edges a small chamfer.
    bm = bmesh.new(); bm.from_mesh(o.data)
    vert_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > Z * .9]
    bmesh.ops.bevel(bm, geom=vert_edges, offset=s['corner_r'], segments=8, profile=.5, affect='EDGES'); bm.to_mesh(o.data); bm.free()
    place(o, 'End_Grain_Board', board, .004)
    cut(o, cyl('hole', (s['hole_x'], 0, Z / 2), s['hole_r'], Z + .02, board, 0, 32))
    for k in range(5):
        box('Knife_Mark', (-.08 + k * .045, -.02 + (k % 2) * .03, Z + .0005), (.09, .002, .001), wood, 0).rotation_euler[2] = .3 + k * .2
    for x in (-X / 2 + .06, X / 2 - .06): box('Board_Foot', (x, 0, -.004), (.04, Y - .06, .008), wood, .002)


def bowl():
    lathe('Stoneware_Bowl', BOWL_PROFILE, clay)
    lathe('Inner_Glaze', [(r, z + .0008) for r, z in BOWL_PROFILE[10:]], glaze)


def plate():
    lathe('Stoneware_Plate', PLATE_PROFILE, clay)
    lathe('Inner_Glaze', [(r, z + .0008) for r, z in PLATE_PROFILE[8:]], glaze)


def table():
    s = SPECS['DiningTable']; X, Y, Z = s['size']; t, L, ins, ah, sz = s['top_t'], s['leg'], s['leg_inset'], s['apron_h'], s['stretcher_z']
    for i in range(4): box('Top_Plank_%d' % i, (-X / 2 + (i + .5) * X / 4, 0, Z - t / 2), (X / 4 - .004, Y, t), board, .006)
    for x in (-1, 1): box('Breadboard_Cleat', (x * (X / 2 - .2), 0, Z - t - .012), (.06, Y - .14, .024), wood, .003)
    c = X / 2 - ins - L / 2; span = 2 * c - L
    for sx in (-1, 1):
        for sy in (-1, 1): box('Leg', (sx * c, sy * c, (Z - t) / 2), (L, L, Z - t), wood, .008)
    for sgn in (-1, 1):
        box('Apron_X', (0, sgn * c, Z - t - ah / 2), (span, .025, ah), wood, .004)
        box('Apron_Y', (sgn * c, 0, Z - t - ah / 2), (.025, span, ah), wood, .004)
        box('Stretcher_X', (0, sgn * c, sz), (span, .035, .035), wood, .004)
        box('Stretcher_Y', (sgn * c, 0, sz + .05), (.035, span, .035), wood, .004)


def stool():
    s = SPECS['RoundStool']; H, r, t = s['h'], s['seat_d'] / 2, s['seat_t']
    cyl('Seat', (0, 0, H - t / 2), r, t, board, .008, 64)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; ca, sa = math.cos(a), math.sin(a)
        beam('Splayed_Leg', (s['leg_top'] * ca, s['leg_top'] * sa, H - t + .005), (s['leg_foot'] * ca, s['leg_foot'] * sa, s['leg_r']), s['leg_r'], wood)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=s['leg_r'], location=(s['leg_foot'] * ca, s['leg_foot'] * sa, s['leg_r']))
        place(bpy.context.object, 'Leg_Foot', wood, smooth=True)
    frac = (H - t - s['ring_z']) / (H - t)
    torus('Ring_Stretcher', (0, 0, s['ring_z']), s['leg_top'] + (s['leg_foot'] - s['leg_top']) * frac, .011, wood)
    torus('Seat_Apron_Ring', (0, 0, H - t - .02), s['leg_top'] + .004, .012, wood)


BUILDERS = {'CookingHearth': hearth, 'IronWok': wok, 'BambooSteamer': steamer, 'PrepBoard': board_, 'CeramicBowl': bowl,
            'CeramicPlate': plate, 'DiningTable': table, 'RoundStool': stool}

# ---------------------------------------------------------------- export + render

ids = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else list(BUILDERS)
for aid in ids:
    out = ROOT / 'Models' / aid / 'v001'; refs = ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001'
    if (refs / 'views.json').exists(): print('ALREADY_COMPLETE', aid, flush=True); continue
    out.mkdir(parents=True, exist_ok=True); refs.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1.0
    assets = bpy.data.collections.new('01_Editable_Asset'); scene.collection.children.link(assets)
    root = bpy.data.objects.new(aid + '_ROOT', None); assets.objects.link(root)
    root['stage'] = 'Editable appearance prototype; not game-ready; no baked textures, LOD or collision.'
    make_materials(); BUILDERS[aid](); bpy.context.view_layer.update()
    objects = [o for o in assets.objects if o.type == 'MESH']

    def bounds(objs=None):
        dg = bpy.context.evaluated_depsgraph_get()
        pts = [e.matrix_world @ v.co for o in (objs or objects) for e in [o.evaluated_get(dg)] for v in e.to_mesh().vertices]
        for o in (objs or objects): o.evaluated_get(dg).to_mesh_clear()
        return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

    lo, hi = bounds(); shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in objects: o.location -= shift
    bpy.context.view_layer.update(); lo, hi = bounds(); centre = (lo + hi) / 2; extent = hi - lo

    studio = bpy.data.collections.new('90_Studio_Not_Exported'); scene.collection.children.link(studio)

    def studio_obj(name, data):
        o = bpy.data.objects.new(name, data); studio.objects.link(o); return o
    cam = studio_obj('Reference_Camera', bpy.data.cameras.new('Reference_Camera')); scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.clip_start = .001; cam.data.clip_end = 100; cam.data.ortho_scale = max(extent.length * 1.18, .12)
    L = extent.length
    # Same light layout as earlier batches, scaled with the asset so small props are not over-lit.
    k = max(L, .3) / 1.6
    for name, direction, power, size in [('Key', (-3, -4, 6), 520, 4), ('Fill', (4, -1, 3), 260, 4), ('Rim', (0, 4, 5), 420, 3)]:
        d = bpy.data.lights.new(name, 'AREA'); d.energy = power * k * k; d.shape = 'DISK'; d.size = size * k
        o = studio_obj(name, d); o.location = centre + Vector(direction) * k
        o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world = bpy.data.worlds.new('Warm_Gray_Studio'); scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.19, .21, .20, 1); bg.inputs[1].default_value = .7
    scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 24; scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 1024; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'AgX'

    def position(direction):
        cam.location = centre + Vector(direction).normalized() * L * 3
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()

    position((1, -1, .65))
    bpy.ops.object.select_all(action='DESELECT')
    for o in [root] + objects: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=str(out / f'{aid}_v001.fbx'), use_selection=True, object_types={'MESH', 'EMPTY'}, add_leaf_bones=False,
                             axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_anim=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / f'{aid}_v001.blend'))
    info = {'asset': aid, 'name_zh': NAMES[aid], 'batch': 'KitchenWare09', 'stage': 'appearance_prototype', 'description': DETAILS[aid],
            'units': 'meters', 'front': '-Y', 'origin': 'bottom centre', 'dimensions_m': [round(c, 4) for c in extent], 'mesh_objects': len(objects),
            'design_sheet': f'DesignSheets/{aid}_design.png', 'spec': SPECS[aid],
            'modeling_method': 'procedural editable mesh built from kitchen_specs.py; views rendered from the same model',
            'uv_baked': False, 'collision': False, 'lod': False, 'unreal_import_verified': False}
    (out / 'model_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2))

    from bpy_extras.object_utils import world_to_camera_view

    def render(name, direction, check=True):
        position(direction)
        if check:
            dg = bpy.context.evaluated_depsgraph_get()
            pts = [world_to_camera_view(scene, cam, e.matrix_world @ Vector(p)) for o in objects for e in [o.evaluated_get(dg)] for p in e.bound_box]
            assert all(.005 < p.x < .995 and .005 < p.y < .995 and p.z > 0 for p in pts), (aid, name, 'cropped')
        scene.render.filepath = str(refs / (name + '.png')); bpy.ops.render.render(write_still=True)
        print('VIEW_COMPLETE', aid, name, flush=True)
        return {'file': name + '.png', 'camera_location': [round(c, 4) for c in cam.location], 'direction': direction, 'projection': 'orthographic', 'framing_checked': check}

    records = [render(n, d) for n, d in VIEWS]
    extras = []
    for name in EXTRA.get(aid, []):
        if name == '11_lid_open':
            lid = [o for o in objects if o.name.startswith('Lid')]
            for o in lid: o.location += Vector((extent.x * .62, extent.y * .25, -(hi.z - lo.z) + .07))
            bpy.context.view_layer.update()
            saved = cam.data.ortho_scale; cam.data.ortho_scale *= 1.45
            extras.append(render(name, EXTRA_DIR[name], check=False))
            cam.data.ortho_scale = saved
            for o in lid: o.location -= Vector((extent.x * .62, extent.y * .25, -(hi.z - lo.z) + .07))
            bpy.context.view_layer.update()
        else:
            extras.append(render(name, EXTRA_DIR[name]))
    (refs / 'views.json').write_text(json.dumps({'asset': aid, 'source': f'Models/{aid}/v001/{aid}_v001.blend', 'same_geometry': True,
                                                 'views': records, 'extra_views': extras}, indent=2))
    print('ASSET_COMPLETE', aid, flush=True)
