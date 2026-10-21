"""Generate concept images with fal.ai from an ArtReferences prompts.json.
The API key is read from the FAL_KEY environment variable (or a key file given with --key-file); it is never written to the repo.

Usage:
  FAL_KEY=... python3 Tools/fal_generate.py ArtReferences/Eatery_10Views/prompts.json            # master first, then the other views
  FAL_KEY=... python3 Tools/fal_generate.py ArtReferences/Eatery_10Views/prompts.json --only 01_front_right.png
  python3 Tools/fal_generate.py <prompts.json> --dry-run                                           # print what would be sent

prompts.json format (as in ArtReferences/*_10Views): {"master": "01_x.png", "images": [{"name", "prompt"}], "props_concept"?: {...}}
The master image is made with a text-to-image model; every other view is made with an image-editing model that receives
the master as reference, so the views follow one design. Results, the model used and the fal request id are recorded back
into prompts.json ("generated" list). Existing PNGs are skipped unless --force.
"""
import argparse, base64, json, os, sys, time, urllib.request
from pathlib import Path

TEXT_MODEL = 'fal-ai/flux/dev'                 # master / standalone concepts
EDIT_MODEL = 'fal-ai/flux-pro/kontext'         # views that follow the master image


def call(model, payload, key):
    req = urllib.request.Request(f'https://fal.run/{model}', data=json.dumps(payload).encode(), method='POST',
                                 headers={'Authorization': f'Key {key}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=300) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f'fal.ai {model} failed: HTTP {e.code} {e.read().decode()[:300]}')


def save(url, path):
    with urllib.request.urlopen(url, timeout=120) as r: path.write_bytes(r.read())


def data_uri(path): return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('prompts'); ap.add_argument('--only', nargs='*'); ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--key-file'); ap.add_argument('--size', default='landscape_4_3')
    a = ap.parse_args()
    pj = Path(a.prompts); folder = pj.parent; spec = json.loads(pj.read_text())
    key = os.environ.get('FAL_KEY') or (Path(a.key_file).read_text().strip() if a.key_file else None)
    if not key and not a.dry_run: sys.exit('Set FAL_KEY (or --key-file) first.')
    jobs = list(spec['images']) + ([spec['props_concept']] if 'props_concept' in spec else [])
    master = spec.get('master'); jobs.sort(key=lambda j: j['name'] != master)          # master first
    done = spec.setdefault('generated', [])
    for j in jobs:
        if a.only and j['name'] not in a.only: continue
        out = folder / j['name']
        if out.exists() and not a.force: print('SKIP', out); continue
        follows = master and j['name'] != master and j['name'] != spec.get('props_concept', {}).get('name')
        model = EDIT_MODEL if follows else TEXT_MODEL
        payload = {'prompt': j['prompt'], 'num_images': 1, 'output_format': 'png'}
        if follows:
            ref = folder / master
            if not ref.exists() and not a.dry_run: sys.exit(f'Generate the master {master} first.')
            payload['image_url'] = data_uri(ref) if ref.exists() else '<master image>'
        else:
            payload['image_size'] = a.size
        if a.dry_run: print('DRY', model, out.name, payload['prompt'][:90]); continue
        t = time.time(); res = call(model, payload, key)
        save(res['images'][0]['url'], out)
        done.append({'name': j['name'], 'model': model, 'seed': res.get('seed'), 'request_id': res.get('request_id'),
                     'reference': master if follows else None, 'date': time.strftime('%Y-%m-%d')})
        pj.write_text(json.dumps(spec, ensure_ascii=False, indent=2)); print('SAVED', out, f'{time.time() - t:.0f}s')


if __name__ == '__main__':
    main()
