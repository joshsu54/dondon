"""Make <Asset>_10views.jpg contact sheets (5 x 2 grid, labelled) from the rendered turnarounds."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)
for aid in (sys.argv[1:] or [p.name[:-5] for p in sorted((ROOT / 'ArtLibrary/Turnarounds').iterdir())]):
    d = ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001'
    views = json.loads((d / 'views.json').read_text())['views']
    sheet = Image.new('RGB', (5 * 400, 2 * 430), (30, 33, 32)); draw = ImageDraw.Draw(sheet)
    for i, v in enumerate(views):
        im = Image.open(d / v['file']).convert('RGB').resize((400, 400), Image.LANCZOS)
        x, y = (i % 5) * 400, (i // 5) * 430
        sheet.paste(im, (x, y + 30)); draw.text((x + 10, y + 3), v['file'][:-4], fill=(230, 230, 220), font=FONT)
    sheet.save(ROOT / f'{aid}_10views.jpg', quality=88); print('SHEET', aid)
