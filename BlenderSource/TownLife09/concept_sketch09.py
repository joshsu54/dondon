"""Step 1 of TownLife09: draw ten-angle concept references BEFORE modelling.

No AI image model is available in the cloud session, so each prompt's design
spec (town09_shapes) is drawn as a cel-shaded ink sketch with a small numpy
z-buffer rasteriser. Outputs ArtReferences/<Asset>_10Views/ with ten PNGs,
prompts.json (prompts are reusable with an image model later) and README.md.

Usage: python3 concept_sketch09.py [AssetId ...]
"""
import json
import math
import zlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import town09_shapes as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RES = 1024
SS = 2                     # supersampling
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
LIGHT = np.array([-.45, -.7, .9]) / np.linalg.norm([-.45, -.7, .9])


def triangles(parts):
    tris, cols = [], []
    for p in parts:
        base = np.array(S.PALETTE[p.color][1], float)
        for f in p.faces:
            for k in range(1, len(f) - 1):
                tris.append(p.verts[[f[0], f[k], f[k + 1]]])
                cols.append(base)
    return np.array(tris), np.array(cols)


def camera_basis(direction):
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    fwd = -d
    up = np.array([0, 0, 1.]) if abs(d[2]) < .99 else np.array([0, 1., 0])
    right = np.cross(fwd, up)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd


def render(parts, direction):
    tris, cols = triangles(parts)
    allv = tris.reshape(-1, 3)
    lo, hi = allv.min(0), allv.max(0)
    centre = (lo + hi) / 2
    right, up, fwd = camera_basis(direction)
    rel = tris - centre
    sx, sy, sz = rel @ right, rel @ up, rel @ fwd       # sz: larger = farther
    span = max(sx.max() - sx.min(), sy.max() - sy.min()) * 1.18
    N = RES * SS
    px = (sx - (sx.max() + sx.min()) / 2) / span * N + N / 2
    py = N / 2 - (sy - (sy.max() + sy.min()) / 2) / span * N + N * .02
    zbuf = np.full((N, N), np.inf)
    fid = np.full((N, N), -1, int)
    # flat normals (oriented toward camera) and cel shading
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-12
    n[ok] /= ln[ok, None]
    flip = (n @ fwd) > 0
    n[flip] *= -1
    lam = np.clip(n @ LIGHT, 0, 1)
    tone = np.where(lam > .62, 1.08, np.where(lam > .3, .86, .64))
    rim = np.clip(n[:, 2], 0, 1) * .06
    shade = np.clip(cols * (tone + rim)[:, None], 0, 255)
    for i in np.nonzero(ok)[0]:
        x, y, z = px[i], py[i], sz[i]
        x0, x1 = int(max(math.floor(x.min()), 0)), int(min(math.ceil(x.max()), N - 1))
        y0, y1 = int(max(math.floor(y.min()), 0)), int(min(math.ceil(y.max()), N - 1))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
        den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(den) < 1e-9:
            continue
        a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
        b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
        c = 1 - a - b
        m = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
        if not m.any():
            continue
        depth = a * z[0] + b * z[1] + c * z[2]
        sub_z = zbuf[y0:y1 + 1, x0:x1 + 1]
        sub_f = fid[y0:y1 + 1, x0:x1 + 1]
        w = m & (depth < sub_z - 1e-5)
        sub_z[w] = depth[w]
        sub_f[w] = i
    return zbuf, fid, shade, n


def paper(N, rng):
    y = np.linspace(0, 1, N)[:, None]
    base = np.array([238, 230, 212]) * (1 - .06 * y)[..., None] + np.zeros((N, N, 3))
    grain = rng.normal(0, 4.5, (N // 4, N // 4))
    grain = np.array(Image.fromarray(grain.astype(np.float32)).resize((N, N), Image.BICUBIC))
    return np.clip(base + grain[..., None], 0, 255)


def sketch(aid, view, direction, label):
    parts = [p for p in S.ASSETS[aid]['build']().parts if not p.detail]
    zbuf, fid, shade, normals = render(parts, direction)
    N = RES * SS
    rng = np.random.default_rng(zlib.crc32(f"{aid}{view}".encode()))
    img = paper(N, rng)
    hit = fid >= 0
    # soft ground shadow under the object (except plan view)
    if direction[2] < .99:
        ys, xs = np.nonzero(hit)
        cx, bottom, w = xs.mean(), ys.max(), (xs.max() - xs.min()) * .55
        g = np.zeros((N, N), np.float32)
        yy, xx = np.ogrid[:N, :N]
        g = np.exp(-(((xx - cx) / max(w, 1)) ** 2 + ((yy - bottom) / max(w * .12, 1)) ** 2) * 2.2)
        img *= (1 - .22 * g)[..., None]
    col = shade[np.clip(fid, 0, None)]
    # watercolour-ish wash: blend toward paper slightly, add per-face noise
    col = col * .92 + img * .08
    img[hit] = col[hit]
    # ink lines: face-id and depth discontinuities
    edge = np.zeros((N, N), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a, b = fid[:N - dy, :N - dx], fid[dy:, dx:]
        za, zb = zbuf[:N - dy, :N - dx], zbuf[dy:, dx:]
        na = normals[np.clip(a, 0, None)]
        nb = normals[np.clip(b, 0, None)]
        crease = (np.einsum('ijk,ijk->ij', na, nb) < .8)
        jump = np.abs(np.where(np.isfinite(za) & np.isfinite(zb), za - zb, 1e3)) > .08
        e = (a != b) & (crease | jump | (a < 0) | (b < 0))
        edge[:N - dy, :N - dx] |= e
    ink = Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
    ink = np.asarray(ink.filter(ImageFilter.GaussianBlur(.8)), float) / 255
    img = img * (1 - .82 * ink[..., None]) + np.array([46, 36, 30]) * .82 * ink[..., None]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((RES, RES), Image.LANCZOS)
    d = ImageDraw.Draw(out)
    f1, f2 = ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 20)
    d.text((34, 28), f'{S.ASSETS[aid]["name_zh"]}　{label}', fill=(70, 54, 44), font=f1)
    d.text((34, 68), f'{aid} · {view} · 建模前概念參考（非模型渲染）', fill=(120, 104, 90), font=f2)
    return out


def main(ids):
    for aid in ids:
        out = ROOT / 'ArtReferences' / f'{aid}_10Views'
        out.mkdir(parents=True, exist_ok=True)
        records = []
        for view, direction, label in S.VIEWS:
            sketch(aid, view, direction, label).save(out / f'{view}.png', optimize=True)
            records.append({'name': f'{view}.png', 'title': label, 'direction': list(direction),
                            'prompt': S.prompt_for(aid, view)})
            print('SKETCH', aid, view, flush=True)
        a = S.ASSETS[aid]
        (out / 'prompts.json').write_text(json.dumps({
            'asset': aid, 'name_zh': a['name_zh'], 'stage': 'pre-modelling concept reference',
            'method': 'Claude-written prompt -> design spec (BlenderSource/TownLife09/town09_shapes.py) -> '
                      'cel-shaded ink sketch by BlenderSource/TownLife09/concept_sketch09.py. '
                      'No AI image model was available in the cloud session; the prompts can be re-run with an image model.',
            'master': '05_front_right.png', 'front': 'Blender -Y', 'projection': 'orthographic',
            'images': records}, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = [f'# {a["name_zh"]}（{aid}）：10 張建模前概念參考圖', '',
                 '建模前先產生。依提示詞寫成設計規格，再以程式繪製十個角度的墨線上色草圖；'
                 '雲端環境沒有 AI 生圖模型，所以這些是程式繪製的概念草圖，不是模型渲染，也不是 AI 繪圖。'
                 '提示詞保留在 `prompts.json`，之後可改用生圖工具重新產生。', '',
                 f'- 設計：{a["desc"]}', f'- 尺寸：{a["size"]}',
                 '- 正面＝Blender -Y；主造型依據為 05 右前斜角。草圖省略細節零件（瓦壟、編織帶、格柵條等），細節以 Blender 模型為準。', '',
                 '## 圖片索引', '']
        lines += [f'{i + 1}. [{r["title"]}]({r["name"]})' for i, r in enumerate(records)]
        lines += ['', f'模型：`Models/{aid}/v001/`；同模型十視圖：`ArtLibrary/Turnarounds/{aid}_v001/`。'
                      '這十張圖已作為參考圖片物件放進 .blend 的 `80_Concept_References` 集合（不渲染、不匯出）。', '']
        (out / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:] or list(S.ASSETS))
