"""Step 5: register TownLife09 in the art library (idempotent).

Updates ArtLibrary/asset_catalog.json and ArtLibrary/index.html, and writes the
batch folder's README.md, inventory.json and index.html.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec import S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / 'ArtLibrary'
BATCH = LIB / 'ExpansionBatches' / S.BATCH_ID
DATE = S.BATCH_DATE
VIEWS = [v for v, _, _ in S.VIEWS]
STATUS = getattr(S, 'STATUS', {})


def info(aid):
    return json.loads((ROOT / 'Models' / aid / 'v001' / 'model_info.json').read_text())


def catalog():
    path = LIB / 'asset_catalog.json'
    data = json.loads(path.read_text())
    known = {e['id'] for e in data['entries']}
    added = 0
    for aid, a in S.ASSETS.items():
        if aid in known:
            continue
        data['entries'].append({
            'id': aid, 'name': a['name_zh'], 'category': a['category'], 'source_version': 'v001',
            'source_path': f'Models/{aid}/v001', 'blend': f'../Models/{aid}/v001/{aid}_v001.blend',
            'fbx': f'../Models/{aid}/v001/{aid}_v001.fbx', 'preview': f'Turnarounds/{aid}_v001/05_front_right.png',
            'views': [f'Turnarounds/{aid}_v001/{v}.png' for v in VIEWS],
            'concept_references': [f'../ArtReferences/{aid}_10Views/{v}.png' for v in VIEWS],
            'status': STATUS.get(aid, '可編輯道具原型；未完成碰撞與引擎驗證'), 'batch': S.BATCH_ID,
            'unreal_import_verified': False, 'uv_baked': False, 'collision_ready': False, 'lod_ready': False})
        added += 1
    if added:
        data['model_asset_sets'] += added
        data['consistent_turnaround_images'] += added * 10
        data['concept_reference_images'] += added * 10
    page = f'ExpansionBatches/{S.BATCH_ID}/index.html'
    if page not in data['supplemental_batches']:
        data['supplemental_batches'].append(page)
    data['updated'] = DATE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return data


def section(aid, prefix=''):
    a = S.ASSETS[aid]
    views = ''.join(f'<a href="{prefix}Turnarounds/{aid}_v001/{v}.png"><img loading="lazy" src="{prefix}Turnarounds/{aid}_v001/{v}.png" alt="{v}"></a>' for v in VIEWS)
    concepts = ''.join(f'<a href="{prefix}../ArtReferences/{aid}_10Views/{v}.png"><img loading="lazy" src="{prefix}../ArtReferences/{aid}_10Views/{v}.png" alt="concept {v}"></a>' for v in VIEWS)
    return (f'<section><h2>{html.escape(a["name_zh"])}</h2><p>{html.escape(STATUS.get(aid, "可編輯道具原型；未完成碰撞與引擎驗證"))}</p>'
            f'<p><a href="{prefix}../Models/{aid}/v001/{aid}_v001.blend">Blender 原檔</a> · <a href="{prefix}../Models/{aid}/v001/{aid}_v001.fbx">FBX</a>'
            f' · <a href="{prefix}../ArtReferences/{aid}_10Views/README.md">建模前概念圖說明</a></p>'
            f'<img class="hero" loading="lazy" src="{prefix}Turnarounds/{aid}_v001/05_front_right.png" alt="{html.escape(a["name_zh"])}">'
            f'<details><summary>展開 10 個角度（同模型渲染）</summary><div class="views">{views}</div></details>'
            f'<details><summary>展開建模前 10 張概念圖</summary><div class="views">{concepts}</div></details></section>')


def library_index(data):
    path = LIB / 'index.html'
    s = path.read_text()
    s = re.sub(r'<p>\d+ 組素材各有 10 張參考圖，共 \d+ 張；',
               f'<p>{data["model_asset_sets"]} 組素材各有 10 張參考圖，共 {data["consistent_turnaround_images"]} 張；', s, count=1)
    link = f' · <a href="ExpansionBatches/{S.BATCH_ID}/index.html">{S.BATCH_TITLE}</a>'
    if link not in s:
        s = s.replace('</nav>', link + '</nav>', 1)
    for aid in S.ASSETS:
        if f'Turnarounds/{aid}_v001/05_front_right.png' not in s:
            s = s.replace('</main></html>', section(aid) + '</main></html>')
    path.write_text(s, encoding='utf-8')


def batch_files():
    rows = []
    for aid, a in S.ASSETS.items():
        i = info(aid)
        rows.append({'asset': aid, 'name_zh': a['name_zh'], 'category': a['category'], 'views': 10,
                     'concept_images_before_modelling': 10, 'concept_folder': f'ArtReferences/{aid}_10Views',
                     'dimensions_m': [round(x, 3) for x in i['dimensions_m']], 'mesh_objects': i['mesh_objects']})
    (BATCH / 'inventory.json').write_text(json.dumps({'batch': S.BATCH_ID, 'created': DATE, 'workflow': [
        '1. 撰寫提示詞與設計規格（town09_shapes.py）', '2. 渲染 10 張建模前概念圖（concept_render09.py，Codex 概念圖風格）',
        '3. 概念圖載入 Blender 作參考後建模、匯出 FBX、渲染同模型十視圖（build_town_assets09.py）',
        '4. 重新開檔與 FBX 回匯驗證（verify_town_assets09.py）'], 'new_assets': rows}, ensure_ascii=False, indent=2),
        encoding='utf-8')
    table = '\n'.join(f'| {a["name_zh"]}／{aid} | {a["size"]} |' for aid, a in S.ASSETS.items())
    (BATCH / 'README.md').write_text(f'''# {S.BATCH_TITLE}

{S.BATCH_INTRO}**每件都先產生 10 張不同角度的概念圖，再進 Blender 建模**。

| 模型 | 規格 |
| --- | --- |
{table}

## 製作流程

1. 每件素材先寫提示詞（含 10 個角度的描述）與設計規格：`BlenderSource/TownLife09/{S.__name__}.py`。
2. **建模前**先依規格在暫存場景排出草模，以接近 Codex image_gen 概念圖的柔光棚拍風格（淺灰背景、暖色主光、接地陰影、透視鏡頭）渲染十個角度，存放在 `ArtReferences/<素材>_10Views/`，提示詞記錄在同資料夾的 `prompts.json`。
   雲端環境沒有 AI 生圖模型，這些不是 AI 繪圖；提示詞可在之後交給生圖工具重新產生。
3. Blender 開新檔，把十張概念圖放進 `80_Concept_References` 集合當參考圖（不渲染、不匯出），再完整建模：倒角、材質與細節零件都在這一步加入。
4. 匯出 FBX，並從同一模型渲染 10 張 1024 × 1024 固定角度圖到 `ArtLibrary/Turnarounds/<素材>_v001/`。
5. 重新開檔、FBX 回匯核對尺寸與物件數；結果記錄在 `validation.json`。

總覽：`concepts/*_concept_10views.jpg` 是建模前概念圖，`*_10views.jpg` 是建模後的同模型十視圖。模型在專案 `Models/<素材>/v001/`，不另複製到本資料夾。重跑：`TL_SPEC={S.__name__} BlenderSource/TownLife09/run_all09.sh`。

{S.BATCH_NOTES}
''', encoding='utf-8')
    cards = ''.join(section(aid, '../../') for aid in S.ASSETS)
    (BATCH / 'index.html').write_text(f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{S.BATCH_TITLE}</title><style>body{{margin:0;background:#edf0e9;color:#243d34;font:16px/1.65 system-ui}}main{{max-width:1100px;margin:auto;padding:32px 16px}}section{{background:white;padding:24px;border-radius:16px;margin:24px 0}}a{{color:#366c59}}.hero{{max-width:440px;width:100%;border-radius:12px}}.views{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}.views img{{width:100%}}summary{{cursor:pointer}}</style><main><h1>{S.BATCH_TITLE}</h1><p>{len(S.ASSETS)} 組素材：每件先畫 10 張建模前概念圖，再用 Blender 建模並渲染 10 張同模型角度圖。</p><p><a href="README.md">批次說明</a> · <a href="../../index.html">回素材庫</a></p>{cards}</main></html>''',
        encoding='utf-8')


if __name__ == '__main__':
    data = catalog()
    library_index(data)
    batch_files()
    print('REGISTERED', data['model_asset_sets'], data['consistent_turnaround_images'])
