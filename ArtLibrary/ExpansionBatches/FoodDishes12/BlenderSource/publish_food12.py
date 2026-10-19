"""Package FoodDishes12 (adapted from StreetProps11/BlenderSource/publish_street11.py) and merge it into the project library (plain python3, run after build + verify).
- batch folder: contact sheets, overview.jpg, inventory.json, index.html
- project: Models/<id>/v001, ArtLibrary/Turnarounds/<id>_v001, ArtReferences/FoodDishes12 design sheets
- ArtLibrary: History snapshot, asset_catalog.json, index.html, library_validation.json, checksums.json
- Deliverables/FoodDishes12.zip
Existing files in the project Models / Turnarounds are never overwritten.
"""
import hashlib, html, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
LIB = BATCH.parents[1]
PROJECT = LIB.parent
sys.path.insert(0, str(HERE))
from food_specs import NAMES, DETAILS

ID, TITLE, DATE = 'FoodDishes12', '料理成品 12', '2026-10-19'
VIEW_NAMES = ['01_front', '02_right', '03_rear', '04_left', '05_front_right', '06_rear_right', '07_rear_left', '08_front_left', '09_top', '10_high_front']
EXTRA_LABEL = {}
STATUS = '可編輯料理外觀原型（含 KitchenWare09 容器）；未完成 UV 烘焙與引擎驗證'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 30)
ids = list(NAMES)
validation = json.loads((BATCH / 'validation.json').read_text())
assert [r['asset'] for r in validation] == ids

# ---- batch previews
subprocess.run([sys.executable, str(HERE / 'contact_sheet.py')] + ids, check=True)
tiles = Image.new("RGB", (3 * 480, 2 * 520), (30, 33, 32)); d = ImageDraw.Draw(tiles)
for i, aid in enumerate(ids):
    im = Image.open(BATCH / 'ArtLibrary/Turnarounds' / f'{aid}_v001/05_front_right.png').convert('RGB').resize((480, 480), Image.LANCZOS)
    x, y = (i % 3) * 480, (i // 3) * 520; tiles.paste(im, (x, y + 40)); d.text((x + 14, y + 4), f'{NAMES[aid]} {aid}', fill=(235, 232, 220), font=FONT)
tiles.save(BATCH / 'overview.jpg', quality=88)

extras = {aid: json.loads((BATCH / 'ArtLibrary/Turnarounds' / f'{aid}_v001/views.json').read_text())['extra_views'] for aid in ids}
inventory = {'batch': ID, 'created': DATE, 'new_asset_sets': len(ids), 'new_views': 10 * len(ids),
             'extra_detail_views': sum(len(v) for v in extras.values()), 'design_sheets': len(ids),
             'new_assets': [{'asset': r['asset'], 'name_zh': r['name_zh'], 'views': 10, 'extra_views': r.get('extra_views', []), 'dimensions_m': r['dimensions_m']} for r in validation]}
(BATCH / 'inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2))


def gallery(prefix, aid, model_prefix, extra_files=()):
    t = f'{prefix}Turnarounds/{aid}_v001/'
    imgs = ''.join(f'<a href="{t}{v}.png"><img loading="lazy" src="{t}{v}.png" alt="{v}"></a>' for v in VIEW_NAMES)
    more = ''.join(f'<a href="{t}{e}"><img loading="lazy" src="{t}{e}" alt="{e[:-4]}"></a>' for e in extra_files)
    extra_html = f'<p>細節圖（不計入十視圖）：</p><div class="views">{more}</div>' if more else ''
    return (f'<p><a href="{model_prefix}Models/{aid}/v001/{aid}_v001.blend">Blender 原檔</a> · <a href="{model_prefix}Models/{aid}/v001/{aid}_v001.fbx">FBX</a>'
            f'{{extra_links}}</p><img class="hero" loading="lazy" src="{t}05_front_right.png" alt="{NAMES[aid]}">'
            f'<details><summary>展開 10 個角度</summary><div class="views">{imgs}</div>{extra_html}</details>')


style = ('body{margin:0;background:#efede4;color:#3a2f24;font:16px/1.7 system-ui}main{max-width:1100px;margin:auto;padding:30px}'
         'section{background:white;border-radius:16px;padding:24px;margin:24px 0}a{color:#8a4b23}.hero{width:100%;max-width:640px;border-radius:12px}'
         '.wide{width:100%;border-radius:12px}.views{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.views img{width:100%}summary{cursor:pointer}')
sections = ''
for r in validation:
    aid = r['asset']; dims = ' × '.join(f'{c * 1000:.0f}' for c in r['dimensions_m'])
    g = gallery('ArtLibrary/', aid, '', [e['file'] for e in extras[aid]]).replace(
        '{extra_links}', f' · <a href="{aid}_10views.jpg">十視圖總覽</a> · <a href="DesignSheets/{aid}_design.png">建模設計圖</a>')
    sections += f'<section><h2>{NAMES[aid]} {aid}</h2><p>{html.escape(DETAILS[aid])}</p><p>外框 {dims} mm（寬 × 深 × 高）· {r["meshes"]} 個可編輯網格</p>{g}</section>'
page = (f'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{TITLE}</title><style>{style}</style><main><h1>{TITLE}</h1><p>6 組模型 · 60 張同源十視圖 · 6 張建模設計圖 · 1 張餐桌預覽</p>'
        f'<section><h2>整批預覽</h2><p>白米飯、湯麵、蒸籠包子、清蒸魚、炒青菜、紅燒肉，盛在 KitchenWare09 的碗盤與蒸籠中。全部為外觀原型。</p><img class="wide" src="table_setting_preview.png" alt="餐桌預覽"><p></p><img class="wide" src="overview.jpg" alt="整批預覽"></section>'
        f'{sections}</main></html>')
(BATCH / 'index.html').write_text(page)

# ---- copy into the project (never overwrite)
def copy_tree(src, dst):
    for f in src.rglob('*'):
        if f.is_file():
            t = dst / f.relative_to(src)
            if t.exists():
                assert t.read_bytes() == f.read_bytes(), f'refusing to overwrite {t}'
                continue
            t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, t)

for aid in ids:
    copy_tree(BATCH / 'Models' / aid, PROJECT / 'Models' / aid)
    copy_tree(BATCH / 'ArtLibrary/Turnarounds' / f'{aid}_v001', LIB / 'Turnarounds' / f'{aid}_v001')
copy_tree(BATCH / 'DesignSheets', PROJECT / 'ArtReferences' / ID)
shutil.copy2(HERE / 'build_food_dishes12.py', PROJECT / 'BlenderSource' / 'build_food_dishes12.py')
for f in ('food_specs.py', 'prop_kit.py', 'sheet_kit.py'): shutil.copy2(HERE / f, PROJECT / 'BlenderSource' / f)

# ---- history snapshot of library metadata before the merge
hist = LIB / 'History' / f'Before{ID}'
if not hist.exists():
    hist.mkdir(parents=True)
    for name in ['README.md', 'asset_catalog.json', 'checksums.json', 'index.html', 'library_validation.json', '完整建模清單.md']:
        shutil.copy2(LIB / name, hist / name)

# ---- catalog
cat = json.loads((LIB / 'asset_catalog.json').read_text())
known = {e['id'] for e in cat['entries']}
old_sets = cat['model_asset_sets']
added = 0
for r in validation:
    aid = r['asset']
    if aid in known: continue
    cat['entries'].append({'id': aid, 'name': NAMES[aid], 'category': '料理成品', 'source_version': 'v001', 'source_path': f'Models/{aid}/v001',
                           'blend': f'../Models/{aid}/v001/{aid}_v001.blend', 'fbx': f'../Models/{aid}/v001/{aid}_v001.fbx',
                           'preview': f'Turnarounds/{aid}_v001/05_front_right.png', 'views': [f'Turnarounds/{aid}_v001/{v}.png' for v in VIEW_NAMES],
                           'extra_views': [f'Turnarounds/{aid}_v001/{e["file"]}' for e in extras[aid]],
                           'design_sheet': f'../ArtReferences/{ID}/{aid}_design.png', 'status': STATUS, 'batch': ID,
                           'unreal_import_verified': False, 'uv_baked': False, 'collision_ready': False, 'lod_ready': False})
    added += 1
# Catalog entries also hold assembled scenes, so counts advance from the stored totals.
total = old_sets + added
cat['model_asset_sets'] = total; cat['consistent_turnaround_images'] = total * 10
cat['design_sheets'] = cat.get('design_sheets', 0) + added
if f'ExpansionBatches/{ID}/index.html' not in cat['supplemental_batches']: cat['supplemental_batches'].append(f'ExpansionBatches/{ID}/index.html')
cat['updated'] = DATE
(LIB / 'asset_catalog.json').write_text(json.dumps(cat, ensure_ascii=False, indent=2))

# ---- main index
idx = (LIB / 'index.html').read_text()
idx = re.sub(r'\d+ 組素材各有 10 張參考圖，共 \d+ 張', f'{total} 組素材各有 10 張參考圖，共 {total * 10} 張', idx)
nav_link = f'<a href="ExpansionBatches/{ID}/index.html">{TITLE}</a>'
if nav_link not in idx:
    idx = idx.replace('</nav>', f' · {nav_link}</nav>', 1)
for r in validation:
    aid = r['asset']
    if f'<section><h2>{NAMES[aid]}</h2>' in idx: continue
    g = gallery('', aid, '../', [e['file'] for e in extras[aid]]).replace('{extra_links}', f' · <a href="../ArtReferences/{ID}/{aid}_design.png">建模設計圖</a>')
    idx = idx.replace('</main></html>', f'<section><h2>{NAMES[aid]}</h2><p>{STATUS} · 10 張圖片</p>{g}</section></main></html>')
(LIB / 'index.html').write_text(idx)

# ---- link check + validation summary
def local_links(page):
    text = page.read_text(); bad = []
    links = [l for l in re.findall(r'(?:href|src)="([^"#:]+)"', text)]
    for l in links:
        if not (page.parent / l).exists(): bad.append(l)
    return {'page': str(page.relative_to(LIB)), 'local_links': len(links), 'missing': bad}

lv = json.loads((LIB / 'library_validation.json').read_text())
lv.update({'updated': DATE, 'model_asset_sets': total, 'consistent_turnaround_images': total * 10})
checks = {c['page']: c for c in lv['link_checks']}
for page in [LIB / 'index.html', BATCH / 'index.html']:
    c = local_links(page); checks[c['page']] = c
    assert not c['missing'], c
lv['link_checks'] = list(checks.values())
(LIB / 'library_validation.json').write_text(json.dumps(lv, ensure_ascii=False, indent=2))

# ---- checksums: refresh changed text files, add every new file under ArtLibrary
def entry(f):
    b = f.read_bytes(); return {'file': str(f.relative_to(LIB)), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

sums = json.loads((LIB / 'checksums.json').read_text())
by = {e['file']: e for e in sums}
fresh = [LIB / n for n in ['asset_catalog.json', 'index.html', 'library_validation.json', 'README.md', '完整建模清單.md']]
fresh += [f for f in BATCH.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
fresh += [f for aid in ids for f in (LIB / 'Turnarounds' / f'{aid}_v001').iterdir()]
fresh += [f for f in hist.iterdir()]
for f in fresh: by[str(f.relative_to(LIB))] = entry(f)
(LIB / 'checksums.json').write_text(json.dumps(sorted(by.values(), key=lambda e: e['file']), ensure_ascii=False, indent=2))

# ---- deliverable zip (batch folder, self-contained)
zp = PROJECT / 'Deliverables' / f'{ID}.zip'
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(BATCH.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts: z.write(f, Path(ID) / f.relative_to(BATCH))
print('PUBLISHED', ID, 'asset sets', old_sets, '->', total, 'zip', zp.stat().st_size)
