#!/usr/bin/env python3
"""Refresh the status table in README.md between <!-- status:start --> and <!-- status:end -->.

For each entry in images.json: show upstream latest release (or branch+date fallback)
and our current image tags. Writes README.md only if content actually changed.
"""
import json, os, re, sys
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or ''

def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'pepperlink-container-images'}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    req = urllib.request.Request('https://api.github.com' + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def ghcr_tags(image):
    name = image.replace('ghcr.io/', '')
    try:
        t = json.loads(urllib.request.urlopen(
            f'https://ghcr.io/token?scope=repository:{name}:pull&service=ghcr.io', timeout=20).read())['token']
        req = urllib.request.Request(f'https://ghcr.io/v2/{name}/tags/list',
                                     headers={'Authorization': f'Bearer {t}'})
        return json.loads(urllib.request.urlopen(req, timeout=20).read()).get('tags') or []
    except Exception:
        return []

def sort_key(tag):
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)$', tag)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)

def upstream_info(repo):
    try:
        rel = api(f'/repos/{repo}/releases/latest')
        tag = rel.get('tag_name', '?')
        date = (rel.get('published_at') or '')[:10]
        return f'`{tag}` ({date})'
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return f'error {e.code}'
    except Exception as e:
        return f'error {str(e)[:40]}'
    # fallback: no releases -> default branch + last commit date
    try:
        info = api(f'/repos/{repo}')
        branch = info.get('default_branch', 'main')
        c = api(f'/repos/{repo}/commits/{branch}')
        date = (c['commit']['committer']['date'] if 'commit' in c else '')[:10]
        return f'`{branch}` @ {date} (no releases)'
    except Exception as e:
        return f'error {str(e)[:40]}'

def main():
    entries = json.load(open(os.path.join(ROOT, 'images.json')))
    lines = ['| App | Upstream | Latest upstream release | Our image | Notes |',
             '|---|---|---|---|---|']
    for e in entries:
        img = f"ghcr.io/pepperlink/{e['image']}"
        tags = [t for t in ghcr_tags(img) if t != 'latest']
        tags_sorted = sorted(tags, key=sort_key, reverse=True)
        built = ', '.join(tags_sorted[:4]) if tags_sorted else 'not built yet'
        img_cell = f'[{img}](https://github.com/orgs/pepperlink/packages/container/package/{e["image"]}) — {built}'
        lines.append(f"| `{e['app']}` | [{e['upstream']}](https://github.com/{e['upstream']}) | {upstream_info(e['upstream'])} | {img_cell} | {e.get('note', '')} |")
    table = '\n'.join(lines)

    readme_path = os.path.join(ROOT, 'README.md')
    readme = open(readme_path).read()
    new = re.sub(r'(<!-- status:start -->).*?(<!-- status:end -->)',
                 lambda m: f'{m.group(1)}\n{table}\n{m.group(2)}', readme, flags=re.S)
    if new == readme:
        print('status table unchanged')
        return
    open(readme_path, 'w').write(new)
    print('status table updated')

if __name__ == '__main__':
    main()
