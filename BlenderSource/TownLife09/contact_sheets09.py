"""Step 4: 5x2 contact sheets for concept sketches and model turnarounds."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec import S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / 'ArtLibrary/ExpansionBatches' / S.BATCH_ID
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)


def sheet(folder, title, dest, cell=360):
    im = Image.new('RGB', (cell * 5, cell * 2 + 48), (34, 36, 38))
    d = ImageDraw.Draw(im)
    d.text((14, 10), title, fill=(230, 226, 214), font=FONT)
    for i, (view, _, label) in enumerate(S.VIEWS):
        tile = Image.open(folder / f'{view}.png').convert('RGB').resize((cell, cell), Image.LANCZOS)
        im.paste(tile, ((i % 5) * cell, 48 + (i // 5) * cell))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=88)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    for aid, a in S.ASSETS.items():
        if which in ('concept', 'both'):
            sheet(ROOT / 'ArtReferences' / f'{aid}_10Views', f'{a["name_zh"]} {aid}｜建模前十張概念參考',
                  BATCH / 'concepts' / f'{aid}_concept_10views.jpg')
        if which in ('model', 'both'):
            sheet(ROOT / 'ArtLibrary/Turnarounds' / f'{aid}_v001', f'{a["name_zh"]} {aid}｜同模型十視圖',
                  BATCH / f'{aid}_10views.jpg')
