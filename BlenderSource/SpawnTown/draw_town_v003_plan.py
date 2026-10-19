"""Layout plan for TownLayout v003, drawn before building the scene.
Run: python3 BlenderSource/SpawnTown/draw_town_v003_plan.py  -> ArtReferences/TownLayout_v003/TownLayout_v003_plan.png
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from town_v003_specs import *

FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
PAPER, INK, OLD, NEW, PAVE, GRASS, DIM = (244, 240, 228), (40, 52, 46), (190, 196, 192), (196, 120, 70), (214, 210, 200), (206, 214, 186), (150, 60, 40)
# Local footprint bounds of each placed asset (x0, x1, y0, y1), front = -Y, from their model files.
LOCAL = {'Eatery': (-5.93, 5.93, -5.13, 4.96), 'MaterialShop': (-4.39, 4.66, -4.72, 3.47), 'HerbalStall': (-1.71, 1.71, -.87, .87)}
NAMES = {'Eatery': '食肆客棧（新）', 'MaterialShop': '材料鋪（新配置）', 'HerbalStall': '藥草攤（新配置）'}
# v002 elements, world bounds.
EXISTING = {'出生廣場': (-4.6, 4.6, -6.0, .4), '上平台與牌樓': (-3.63, 3.63, .4, 6.7), '北街': (-2.0, 2.0, 6.7, 11.7), '南路': (-1.5, 1.5, -13, -6),
            '新手民宅': (7.28, 15.47, -6.66, 2.39), '鐵匠鋪': (8.98, 14.7, 4.28, 11.72), '東巷': (4.6, 6.65, -3.3, -.7), '商店巷': (6.65, 9.0, 2.05, 11.8),
            '回程石階': (2.0, 4.4, 8.0, 10.4), '迎客松': (-8.0, .2, -1.81, .4)}

W, H = 2200, 1500
img = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(img)
f = lambda s: ImageFont.truetype(FONT, s)
X0, X1, Y0, Y1 = TERRAIN_WEST_TO - 1, 19, -14, 15
s = min((W - 140) / (X1 - X0), (H - 260) / (Y1 - Y0))
ox, oy = 70 - X0 * s, 180 + Y1 * s
P = lambda x, y: (ox + x * s, oy - y * s)


def rect(b, fill, w=2, outline=INK):
    x0, x1, y0, y1 = b; d.rectangle([P(x0, y1), P(x1, y0)], fill=fill, outline=outline, width=w)


def label(x, y, t, size=22, fill=INK):
    tw = d.textlength(t, font=f(size)); px, py = P(x, y); d.text((px - tw / 2, py - size / 2), t, fill=fill, font=f(size))


d.text((50, 30), 'TownLayout v003 · 西街配置平面圖', fill=INK, font=f(46))
d.text((50, 92), '世界座標（m），+Y = 北，正面朝向以箭頭表示；灰色 = v002 既有，橘色 = 本次新增或移入', fill=INK, font=f(24))
rect((TERRAIN_WEST_TO, 18, -13, 14), GRASS)
rect((TERRAIN_WEST_TO, TERRAIN_WEST_FROM, -13, 14), (196, 206, 172), 1)
label((TERRAIN_WEST_TO + TERRAIN_WEST_FROM) / 2, -12.3, '地形向西延伸 14 m', 20)
for n, b in EXISTING.items():
    rect(b, OLD); label((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, n, 18)
for n, b in PAVING.items():
    rect(b, PAVE, 2, NEW); label((b[0] + b[1]) / 2, (b[2] + b[3]) / 2 if n != 'West_Street' else -8.5, {'West_Lane': '西巷', 'West_Street': '西街 3 m', 'Stall_Pad': '攤位石坪', 'Shop_Apron': ''}[n], 18, DIM)
for n, (src, (px, py, pz), rot, note) in PLACEMENTS.items():
    x0, x1, y0, y1 = LOCAL[n]; a = math.radians(rot)
    pts = [(px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a)) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    d.polygon([P(*p) for p in pts], fill=NEW, outline=INK); d.line([P(*p) for p in pts + pts[:1]], fill=INK, width=3)
    label(px, py + .5, NAMES[n], 22)
    fx, fy = math.sin(a), -math.cos(a)        # local -Y (front) after rotation
    d.line([P(px, py - .6), P(px + fx * 2.2, py - .6 + fy * 2.2)], fill=INK, width=4)
    tip = P(px + fx * 2.2, py - .6 + fy * 2.2); d.ellipse([tip[0] - 7, tip[1] - 7, tip[0] + 7, tip[1] + 7], fill=INK)
bx, by = BENCH_MOVE['to_centre']; rect((bx - .3, bx + .3, by - .9, by + .9), NEW); label(bx + 1.0, by, '長凳', 16)
d.line([P(-4.7, -4.39), P(-4.7, -2.02)], fill=DIM, width=6); label(-3.0, -4.9, '拆 3 段路緣', 16, DIM)
for n, (x, y, z) in MARKERS.items():
    q = P(x, y); d.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], outline=DIM, width=2)
for x in range(-24, 19, 4):
    d.line([P(x, -13.6), P(x, -13.3)], fill=INK, width=1); label(x, -13.9, str(x), 14)
y = H - 70
d.text((60, y), '· 全部步行面維持 v002 的 0.24 m；食肆下層台階頂面與西街齊平，台階高 0.15 m；材料鋪台階由街面起算。', fill=INK, font=f(22))
d.text((60, y + 32), '· 西巷避開迎客松根部（y < -2.02），長凳移到攤位石坪；建置後以向下射線檢查巷道、街道與入口高度。', fill=INK, font=f(22))
out = PROJECT / 'ArtReferences' / 'TownLayout_v003'; out.mkdir(parents=True, exist_ok=True)
img.save(out / 'TownLayout_v003_plan.png'); print('PLAN', out / 'TownLayout_v003_plan.png')
