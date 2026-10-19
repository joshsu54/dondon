"""Package Eatery10 and merge it into the project library (plain python3, run after build + verify).
Same steps as KitchenWare09/BlenderSource/publish_kitchen09.py, for the single building asset.
Existing files in the project Models / Turnarounds are never overwritten.
"""
import hashlib, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
LIB = BATCH.parents[1]
PROJECT = LIB.parent
sys.path.insert(0, str(HERE))
from eatery_specs import NAME, NAME_ZH

ID, TITLE, DATE = 'Eatery10', '食肆客棧 10', '2026-10-19'
VIEW_NAMES = ['01_front', '02_right', '03_rear', '04_left', '05_front_right', '06_rear_right', '07_rear_left', '08_front_left', '09_top', '10_high_front']
EXTRA_LABEL = {'11_cutaway_ground': '一樓剖視', '12_plan_ground': '一樓俯視', '13_plan_upper': '二樓俯視', '14_cutaway_upper': '二樓剖視'}
SHEETS = ['Eatery_01_elevations.png', 'Eatery_02_plans.png']
STATUS = '可編輯兩層建築原型（含一樓家具配置）；未完成 UV 烘焙、碰撞、導航與引擎驗證'
row = json.loads((BATCH / 'validation.json').read_text())[0]
assert row['asset'] == NAME
subprocess.run([sys.executable, str(HERE / 'contact_sheet.py'), NAME], check=True)
extras = json.loads((BATCH / 'ArtLibrary/Turnarounds' / f'{NAME}_v001/views.json').read_text())['extra_views']
info = json.loads((BATCH / 'Models' / NAME / 'v001/model_info.json').read_text())

inventory = {'batch': ID, 'created': DATE, 'new_asset_sets': 1, 'new_views': 10, 'extra_layout_views': len(extras), 'design_sheets': len(SHEETS),
             'new_assets': [{'asset': NAME, 'name_zh': NAME_ZH, 'views': 10, 'extra_views': row['extra_views'], 'dimensions_m': row['dimensions_m'],
                             'furnishing_in_blend_only': row['furnishing_instances']}]}
(BATCH / 'inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2))


def gallery(prefix, model_prefix, sheet_prefix):
    t = f'{prefix}Turnarounds/{NAME}_v001/'
    imgs = ''.join(f'<a href="{t}{v}.png"><img loading="lazy" src="{t}{v}.png" alt="{v}"></a>' for v in VIEW_NAMES)
    more = ''.join(f'<a href="{t}{e["file"]}"><img loading="lazy" src="{t}{e["file"]}" alt="{EXTRA_LABEL[e["file"][:-4]]}"></a>' for e in extras)
    sheets = ' · '.join(f'<a href="{sheet_prefix}{s}">{"立面設計圖" if "elev" in s else "平面設計圖"}</a>' for s in SHEETS)
    return (f'<p><a href="{model_prefix}Models/{NAME}/v001/{NAME}_v001.blend">Blender 原檔（含家具）</a> · <a href="{model_prefix}Models/{NAME}/v001/{NAME}_v001.fbx">FBX（建築本體）</a> · {sheets}</p>'
            f'<img class="hero" loading="lazy" src="{t}05_front_right.png" alt="{NAME_ZH}">'
            f'<details><summary>展開 10 個角度</summary><div class="views">{imgs}</div><p>配置剖視圖（不計入十視圖）：</p><div class="views">{more}</div></details>')


style = ('body{margin:0;background:#efede4;color:#3a2f24;font:16px/1.7 system-ui}main{max-width:1100px;margin:auto;padding:30px}'
         'section{background:white;border-radius:16px;padding:24px;margin:24px 0}a{color:#8a4b23}.hero{width:100%;max-width:720px;border-radius:12px}'
         '.wide{width:100%;border-radius:12px}.views{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}.views img{width:100%}summary{cursor:pointer}')
dims = ' × '.join(f'{c:.2f}' for c in row['dimensions_m'])
lv_ = info['levels_m']
page = (f'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{TITLE}</title><style>{style}</style><main><h1>{TITLE}</h1><p>1 組兩層建築 · 10 張同源十視圖 · {len(extras)} 張配置剖視圖 · {len(SHEETS)} 張建模設計圖</p>'
        f'<section><h2>{NAME_ZH} {NAME}</h2><p>一樓開放用餐區（4 桌 16 凳）、櫃台與酒架、西牆直跑樓梯、東北角廚房（柴火爐灶、鐵鍋、蒸籠）與穿屋頂煙囪；'
        f'二樓三間客房與走廊；前簷廊、陽台、空白招牌與紅燈籠。外框 {dims} m（含屋簷與台階），{row["meshes"]} 個可編輯網格；'
        f'地坪 {lv_["ground_floor"]} m、二樓 {lv_["upper_floor"]} m、屋脊 {row["ridge_top_m"]} m。</p>'
        f'<p>樓梯 17 級 × 0.20 m，樓梯下方最小淨高 {row["stair_min_headroom_m"]} m；正面開口淨高 {row["front_opening_clear_height_m"]} m。'
        f'家具是 KitchenWare09 的複本，只存在 .blend 中，FBX 只含建築本體。</p>'
        f'{gallery("ArtLibrary/", "", "DesignSheets/")}<p><a href="{NAME}_10views.jpg">十視圖總覽</a></p></section></main></html>')
(BATCH / 'index.html').write_text(page)


def copy_tree(src, dst):
    for f in src.rglob('*'):
        if f.is_file():
            t = dst / f.relative_to(src)
            if t.exists():
                assert t.read_bytes() == f.read_bytes(), f'refusing to overwrite {t}'
                continue
            t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, t)


copy_tree(BATCH / 'Models' / NAME, PROJECT / 'Models' / NAME)
copy_tree(BATCH / 'ArtLibrary/Turnarounds' / f'{NAME}_v001', LIB / 'Turnarounds' / f'{NAME}_v001')
copy_tree(BATCH / 'DesignSheets', PROJECT / 'ArtReferences' / ID)
for f in ('build_eatery10.py', 'eatery_specs.py'): shutil.copy2(HERE / f, PROJECT / 'BlenderSource' / f)

hist = LIB / 'History' / f'Before{ID}'
assert hist.exists(), 'snapshot library metadata (from git HEAD) before editing docs'

cat = json.loads((LIB / 'asset_catalog.json').read_text())
old_sets = cat['model_asset_sets']; added = 0
if NAME not in {e['id'] for e in cat['entries']}:
    cat['entries'].append({'id': NAME, 'name': NAME_ZH, 'category': '小鎮建築', 'source_version': 'v001', 'source_path': f'Models/{NAME}/v001',
                           'blend': f'../Models/{NAME}/v001/{NAME}_v001.blend', 'fbx': f'../Models/{NAME}/v001/{NAME}_v001.fbx',
                           'preview': f'Turnarounds/{NAME}_v001/05_front_right.png', 'views': [f'Turnarounds/{NAME}_v001/{v}.png' for v in VIEW_NAMES],
                           'extra_views': [f'Turnarounds/{NAME}_v001/{e["file"]}' for e in extras],
                           'design_sheets': [f'../ArtReferences/{ID}/{s}' for s in SHEETS], 'status': STATUS, 'batch': ID,
                           'unreal_import_verified': False, 'uv_baked': False, 'collision_ready': False, 'lod_ready': False})
    added = 1
total = old_sets + added
cat['model_asset_sets'] = total; cat['consistent_turnaround_images'] = total * 10
cat['design_sheets'] = cat.get('design_sheets', 0) + added * len(SHEETS)
if f'ExpansionBatches/{ID}/index.html' not in cat['supplemental_batches']: cat['supplemental_batches'].append(f'ExpansionBatches/{ID}/index.html')
cat['updated'] = DATE
(LIB / 'asset_catalog.json').write_text(json.dumps(cat, ensure_ascii=False, indent=2))

idx = (LIB / 'index.html').read_text()
idx = re.sub(r'\d+ 組素材各有 10 張參考圖，共 \d+ 張', f'{total} 組素材各有 10 張參考圖，共 {total * 10} 張', idx)
nav = f'<a href="ExpansionBatches/{ID}/index.html">{TITLE}</a>'
if nav not in idx: idx = idx.replace('</nav>', f' · {nav}</nav>', 1)
if f'<section><h2>{NAME_ZH}</h2>' not in idx:
    idx = idx.replace('</main></html>', f'<section><h2>{NAME_ZH}</h2><p>{STATUS} · 10 張圖片</p>{gallery("", "../", f"../ArtReferences/{ID}/")}</section></main></html>')
(LIB / 'index.html').write_text(idx)


def local_links(page):
    links = re.findall(r'(?:href|src)="([^"#:]+)"', page.read_text())
    return {'page': str(page.relative_to(LIB)), 'local_links': len(links), 'missing': [l for l in links if not (page.parent / l).exists()]}


lv = json.loads((LIB / 'library_validation.json').read_text())
lv.update({'updated': DATE, 'model_asset_sets': total, 'consistent_turnaround_images': total * 10})
checks = {c['page']: c for c in lv['link_checks']}
for p in (LIB / 'index.html', BATCH / 'index.html'):
    c = local_links(p); assert not c['missing'], c; checks[c['page']] = c
lv['link_checks'] = list(checks.values())
(LIB / 'library_validation.json').write_text(json.dumps(lv, ensure_ascii=False, indent=2))


def entry(f):
    b = f.read_bytes(); return {'file': str(f.relative_to(LIB)), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


by = {e['file']: e for e in json.loads((LIB / 'checksums.json').read_text())}
fresh = [LIB / n for n in ['asset_catalog.json', 'index.html', 'library_validation.json', 'README.md', '完整建模清單.md']]
fresh += [f for f in BATCH.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
fresh += list((LIB / 'Turnarounds' / f'{NAME}_v001').iterdir()) + list(hist.iterdir())
for f in fresh: by[str(f.relative_to(LIB))] = entry(f)
(LIB / 'checksums.json').write_text(json.dumps(sorted(by.values(), key=lambda e: e['file']), ensure_ascii=False, indent=2))

zp = PROJECT / 'Deliverables' / f'{ID}.zip'
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(BATCH.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts: z.write(f, Path(ID) / f.relative_to(BATCH))
print('PUBLISHED', ID, 'asset sets', old_sets, '->', total, 'zip', zp.stat().st_size)
