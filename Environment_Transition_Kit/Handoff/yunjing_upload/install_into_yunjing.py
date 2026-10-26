"""Install the ready-made package in this folder (Handoff/yunjing_upload/) into a yun-jing-rpg checkout (Python 3 standard library).

  python3 Environment_Transition_Kit/Handoff/yunjing_upload/install_into_yunjing.py --repo /path/to/yun-jing-rpg
  python3 Environment_Transition_Kit/Handoff/yunjing_upload/install_into_yunjing.py --write-manifest   # after rebuilding the package

--repo checks that every packaged file is really downloaded (no Git LFS pointer) and matches PACKAGE_SHA256.json,
copies EnvironmentTransitionKit/ to <repo>/art/incoming/dondon/EnvironmentTransitionKit/, checks the copies again and
appends README_append.md to art/incoming/dondon/README.md once.  It refuses if the target folder already exists or
the checkout does not look like yun-jing-rpg.  It does not touch git: branch, commit, push and PR are left to the
person or agent running it (see CODEX_UPLOAD.md next to this script).
"""
import hashlib, json, shutil, sys
from pathlib import Path

UPLOAD = Path(__file__).resolve().parent
PKG = UPLOAD / 'EnvironmentTransitionKit'
MANIFEST = UPLOAD / 'PACKAGE_SHA256.json'
MARKER = '## 另一批：環境收邊模組包'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()


def files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)


def write_manifest():
    rec = {str(p.relative_to(PKG)): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files(PKG)}
    MANIFEST.write_text(json.dumps({'package': 'EnvironmentTransitionKit', 'files': len(rec),
                                    'bytes': sum(r['bytes'] for r in rec.values()), 'sha256': rec}, ensure_ascii=False, indent=1))
    print('MANIFEST %d files -> %s' % (len(rec), MANIFEST))


def check(root, want, label):
    bad = []
    for rel, r in want.items():
        p = root / rel
        if not p.is_file(): bad.append('missing ' + rel); continue
        if p.stat().st_size < 200 and p.read_bytes().startswith(b'version https://git-lfs'):
            bad.append('Git LFS pointer, not the file (run: git lfs pull --include="Environment_Transition_Kit/Handoff/**") ' + rel); continue
        if sha(p) != r['sha256']: bad.append('hash differs ' + rel)
    extra = [str(p.relative_to(root)) for p in files(root) if str(p.relative_to(root)) not in want]
    if bad or extra: raise SystemExit('%s check failed:\n  ' % label + '\n  '.join((bad + ['unexpected ' + e for e in extra])[:20]))
    print('%s: %d files match PACKAGE_SHA256.json' % (label, len(want)))


def install(repo):
    repo = Path(repo).resolve(); incoming = repo / 'art' / 'incoming' / 'dondon'; dest = incoming / 'EnvironmentTransitionKit'
    agents = repo / 'AGENTS.md'
    if not (agents.is_file() and '雲境' in agents.read_text(encoding='utf-8') and incoming.is_dir()):
        raise SystemExit('not a yun-jing-rpg checkout (AGENTS.md / art/incoming/dondon missing): %s' % repo)
    if dest.exists(): raise SystemExit('EXISTS (not overwritten): %s' % dest)
    want = json.loads(MANIFEST.read_text())['sha256']
    check(PKG, want, 'source package')
    shutil.copytree(PKG, dest)
    check(dest, want, 'installed copy')
    readme = incoming / 'README.md'; text = readme.read_text(encoding='utf-8')
    if MARKER in text: print('README section already present, left as is')
    else:
        readme.write_text(text.rstrip('\n') + '\n\n' + (UPLOAD / 'README_append.md').read_text(encoding='utf-8').strip('\n') + '\n', encoding='utf-8')
        print('appended README_append.md to', readme.relative_to(repo))
    print('INSTALLED -> %s\nNext (in %s): git add art/incoming/dondon && git lfs status && npm test, then commit, push, PR (CODEX_UPLOAD.md)'
          % (dest.relative_to(repo), repo))


def main():
    a = sys.argv[1:]
    if '--write-manifest' in a: write_manifest()
    elif '--repo' in a: install(a[a.index('--repo') + 1])
    else: raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
