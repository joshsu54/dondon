"""Step 1 of TownLife09: ten-angle concept references BEFORE modelling.

Codex-like look: soft studio 3D concept render (perspective camera, light grey
seamless backdrop, warm key light, contact shadows), no ink lines or labels.
The design spec written from each prompt (town09_shapes) is blocked out in a
throwaway scene and rendered from the ten standard angles. Nothing here is
saved as a model; build_town_assets09.py models the asset afterwards with the
ten images loaded as references.

Outputs ArtReferences/<Asset>_10Views/{01..10}.png, prompts.json, README.md.
Usage: python3 concept_render09.py [AssetId ...]
"""
import bpy  # noqa: I001
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spec import S  # noqa: E402
from build_town_assets09 import actual_bounds, make_materials, part_object  # noqa: E402

ROOT = HERE.parents[1]


def studio_backdrop(path):
    """Composite the transparent render over a soft grey studio gradient."""
    import numpy as np
    from PIL import Image
    fg = Image.open(path).convert('RGBA')
    n = fg.size[1]
    y = np.linspace(0, 1, n)[:, None, None]
    top, bottom = np.array([168, 168, 170]), np.array([214, 213, 211])
    grad = top + (bottom - top) * y ** .8
    x = np.linspace(-1, 1, n)[None, :, None]
    grad = grad * (1 - .06 * x ** 2) + np.zeros((n, n, 3))
    bg = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert('RGBA')
    Image.alpha_composite(bg, fg).convert('RGB').save(path)


def concept_scene(aid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    coll = bpy.data.collections.new('Concept_Blockout')
    scene.collection.children.link(coll)
    root = bpy.data.objects.new('Concept_ROOT', None)
    coll.objects.link(root)
    mats = make_materials()
    objs = [part_object(p, mats, coll, root) for p in S.ASSETS[aid]['build']().parts]
    bpy.context.view_layer.update()
    lo, hi = actual_bounds(objs)
    shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in objs:
        o.location -= shift
    bpy.context.view_layer.update()
    lo, hi = actual_bounds(objs)
    centre, extent = (lo + hi) / 2, hi - lo
    R = extent.length / 2
    # seamless light-grey studio floor that fades into a matching world colour
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=R * 30, fill_type='NGON', location=(0, 0, 0))
    floor = bpy.context.object
    fm = bpy.data.materials.new('Studio_Floor')
    fm.use_nodes = True
    fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.52, .52, .52, 1)
    fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .9
    floor.data.materials.append(fm)
    floor.is_shadow_catcher = True
    scene.render.film_transparent = True
    scene.world = bpy.data.worlds.new('Concept_Studio')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (.46, .46, .47, 1)
    bg.inputs[1].default_value = .55
    for name, direction, power, colour in [('Key', (-.9, -1.2, 1.6), 650, (1, .95, .88)),
                                           ('Fill', (1.3, -.6, .8), 220, (.88, .93, 1)),
                                           ('Top', (0, .4, 2.2), 260, (1, 1, 1))]:
        d = bpy.data.lights.new(name, 'AREA')
        d.energy = power * R * R / 4
        d.size = R * 1.6
        d.color = colour
        o = bpy.data.objects.new(name, d)
        scene.collection.objects.link(o)
        o.location = centre + Vector(direction).normalized() * R * 3
        o.rotation_euler = (centre - o.location).to_track_quat('-Z', 'Y').to_euler()
    cam = bpy.data.objects.new('Concept_Camera', bpy.data.cameras.new('Concept_Camera'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = 50
    cam.data.clip_start, cam.data.clip_end = .01, R * 200
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -.75
    return scene, cam, centre, R, objs


def main(ids):
    for aid in ids:
        out = ROOT / 'ArtReferences' / f'{aid}_10Views'
        out.mkdir(parents=True, exist_ok=True)
        scene, cam, centre, R, objs = concept_scene(aid)
        fov = cam.data.angle
        records = []
        for view, direction, label in S.VIEWS:
            d = Vector(direction).normalized()
            cam.location = centre + d * (R / math.sin(fov / 2) * 1.08)
            cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
            if abs(d.z) > .99:
                cam.rotation_euler = (0, 0, 0)
            scene.render.filepath = str(out / f'{view}.png')
            bpy.ops.render.render(write_still=True)
            studio_backdrop(out / f'{view}.png')
            records.append({'name': f'{view}.png', 'title': label, 'direction': list(direction),
                            'prompt': S.prompt_for(aid, view)})
            print('CONCEPT', aid, view, flush=True)
        a = S.ASSETS[aid]
        (out / 'prompts.json').write_text(json.dumps({
            'asset': aid, 'name_zh': a['name_zh'], 'stage': 'pre-modelling concept reference',
            'method': f'Claude-written prompt -> design spec (BlenderSource/TownLife09/{S.__name__}.py) -> '
                      'Codex-style soft studio concept render of a throwaway blockout by BlenderSource/TownLife09/concept_render09.py. '
                      'No AI image model was available in the cloud session; the prompts can be re-run with an image model.',
            'style_reference': 'ArtReferences/HerbalStall/concept.png and ArtReferences/Blacksmith_10Views (Codex image_gen)',
            'master': '05_front_right.png', 'front': 'Blender -Y', 'projection': 'perspective 50 mm',
            'images': records}, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = [f'# {a["name_zh"]}（{aid}）：10 張建模前概念參考圖', '',
                 '建模前先產生。依提示詞寫成設計規格，在暫存場景排出草模，以接近 Codex image_gen 概念圖的柔光棚拍風格'
                 '（淺灰無縫背景、暖色主光、接地陰影、透視鏡頭）渲染十個角度。'
                 '雲端環境沒有 AI 生圖模型，所以這些不是 AI 繪圖；提示詞保留在 `prompts.json`，之後可改用生圖工具重新產生。', '',
                 f'- 設計：{a["desc"]}', f'- 尺寸：{a["size"]}',
                 '- 正面＝Blender -Y；主造型依據為 05 右前斜角。風格參考：`ArtReferences/HerbalStall/concept.png`、`ArtReferences/Blacksmith_10Views/`。', '',
                 '## 圖片索引', '']
        lines += [f'{i + 1}. [{r["title"]}]({r["name"]})' for i, r in enumerate(records)]
        lines += ['', f'模型：`Models/{aid}/v001/`；同模型十視圖：`ArtLibrary/Turnarounds/{aid}_v001/`。'
                      '這十張圖已作為參考圖片物件放進 .blend 的 `80_Concept_References` 集合（不渲染、不匯出）。', '']
        (out / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    main(args or list(S.ASSETS))
