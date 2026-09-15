# container-images

One repo to build the container images we need from upstream projects that don't ship one
themselves (or whose image we need to tweak). Each app gets its own workflow file; all of
them call one shared build workflow.

**Registry:** `ghcr.io/pepperlink/<app>` · **Maintained by:** Diane (for Cathelijne) · Created 2026-09-15.

## Apps

<!-- status:start -->
| App | Upstream | Latest upstream release | Our image | Notes |
|---|---|---|---|---|
| `master-fetch` | [dondai1234/master-fetch](https://github.com/dondai1234/master-fetch) | `v12.4.1` (2026-07-24) | [ghcr.io/pepperlink/master-fetch](https://github.com/orgs/pepperlink/packages/container/package/master-fetch) — 12.4.1, 12.4, 12 | Upstream no longer updated; last release date tracked in README. |
| `donsetch` | [dondai44423/donsetch](https://github.com/dondai44423/donsetch) | `v4.1.0` (2026-09-14) | [ghcr.io/pepperlink/donsetch](https://github.com/orgs/pepperlink/packages/container/package/donsetch) — 3.6.7, 3.6, 3 | Moved from pepperlink/donsetch fork build. |
| `forage` | [aldemaroc/forage](https://github.com/aldemaroc/forage) | `main` @ 2026-08-19 (no releases) | [ghcr.io/pepperlink/forage](https://github.com/orgs/pepperlink/packages/container/package/forage) — 0.9.0, 0.9, 0 | No upstream releases - builds default branch, sha-tagged. |
<!-- status:end -->

## How it works

- `.github/workflows/<app>.yml` — one caller per app: staggered weekly schedule + manual run.
- `.github/workflows/build.yml` — the shared engine: resolve upstream ref (latest release →
  latest tag → default branch) → **skip if that version is already built** → checkout upstream →
  optional overlay from `images/<app>/overlay/` → buildx (amd64 + arm64) → push `:<version>`,
  `:major.minor`, `:major` (when semver), `:sha-<short>`, `:latest` — with OCI labels.
- `.github/workflows/build-all.yml` — rebuild everything (monthly / on demand).
- `.github/workflows/status.yml` — weekly refresh of the table above (upstream release dates).
- `images.json` — inventory; drives `build-all` + the README table.
- `scripts/update_status.py` — regenerates the table.

## Adding a new image

1. Add an entry to `images.json`.
2. Add `.github/workflows/<app>.yml` (copy an existing caller, adjust `app`/`upstream`).
3. If the build needs tweaks, drop files into `images/<app>/overlay/` — they are copied over
   the upstream checkout before building (e.g. a patched Dockerfile or config files).

## Migration log

- 2026-09-15 — repo created; callers for master-fetch, donsetch, forage.
  Replaces per-fork build workflows and `ghcr.io/cathelijne/*` images. (searcharr dropped — replaced
  by Seerr; backdroppr dropped — upstream archived; forks being deleted.) Fork cleanup handled separately.
