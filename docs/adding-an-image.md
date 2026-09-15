# Adding a new image

This repo builds container images for upstream projects that don't ship their own (or that we
need to tweak). Adding one takes about ten minutes — here's the whole path.

## 0. Preflight

- **Does upstream publish images already?** (Check their README / GHCR / Docker Hub.) If yes, use
  theirs and skip this repo.
- **Is it already here?** Check `images.json`.

## 1. Add the inventory entry — `images.json`

```json
{"app": "myapp", "upstream": "owner/repo", "image": "myapp", "ref": "auto", "version": "v1.2.3", "dockerfile": "Dockerfile", "note": "Why we build this."}
```

| Field | Meaning |
|---|---|
| `app` | Short id — also the name of the optional `images/<app>/overlay/` dir |
| `upstream` | GitHub repo to build from (`owner/repo`) |
| `image` | Image name under `ghcr.io/pepperlink/<image>` (keep stable — consumers reference it) |
| `version` | **Pin** — set to the upstream's latest release tag; Renovate takes over from there |
| `ref` | Usually `auto` (pin → latest release → latest tag → default branch) |
| `dockerfile` | Path inside the upstream checkout (after overlay), default `Dockerfile` |
| `note` | Free text, shown in the README status table |

## 2. Add the caller — `.github/workflows/<app>.yml`

Copy an existing caller and adjust:

```yaml
name: myapp

on:
  workflow_dispatch:

jobs:
  build:
    uses: ./.github/workflows/build.yml
    with:
      app: myapp
      upstream: owner/repo
      # platforms: linux/amd64,linux/arm64   # uncomment for multi-arch (extra CI minutes)
```

## 3. Commit, push — the first build is automatic

Commit both files to `main`. Because `images.json` changed, `build-all` fires and builds exactly
the new app (nothing else — existing images are skipped). You can also build by hand whenever:
**Actions → `<app>` → Run workflow**.

Watch it: **Actions** tab → the run → job summary shows what got resolved, built and pushed.
Verify the result: `https://github.com/orgs/pepperlink/packages` (or pull it: `docker pull ghcr.io/pepperlink/myapp:latest`).

## 4. If the upstream has no releases/tags yet (like `forage`)

- Omit `version` (nothing for Renovate to track).
- Copy `forage.yml`'s shape and keep its weekly `schedule` — a light commit-sha check.
- Interim versions are generated automatically: `0.<commit-date>-<sha7>` (e.g. `0.20260915-93920b3`).
- When upstream starts tagging, add the `version` pin and drop the schedule — Renovate takes over.

## 5. Tweaks & patches — `images/<app>/overlay/`

Anything in `images/<app>/overlay/` is copied **over** the upstream checkout just before building.
Use it for:

- a patched or alternate Dockerfile (then point `dockerfile` at it),
- config files, build settings, small source fixes,
- e.g. a GPU Dockerfile variant or pinned dependency files.

No overlay needed? Don't create the directory — the build uses upstream verbatim.

## 6. What happens afterwards (maintenance)

- **Renovate** opens a PR when upstream releases (automerge for minor/patch/pin; majors wait on the
  dependency dashboard).
- Merging a pin bump triggers a rebuild of just that app.
- The README status table refreshes weekly (upstream release dates), and the `status` workflow
  commits the update.

## Notes

- **ARM:** off by default (runs under emulation → slow + expensive minutes). See the README's
  *ARM builds* section to enable per app.
- **Minutes:** public repo → free; keep an eye on usage if it ever goes private.
- **Naming:** once consumers (charts / ArgoCD) reference `ghcr.io/pepperlink/<image>`, don't rename
  without updating them.
