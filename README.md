# container-images

One repo to build the container images we need from upstream projects that don't ship one
themselves (or whose image we need to tweak). Each app gets its own workflow file; all of
them call one shared build workflow.

**Registry:** `ghcr.io/pepperlink/<app>` · **Maintained by:** Diane (for Cathelijne) · Created 2026-09-15.

## Apps

<!-- status:start -->
| App | Upstream | Latest upstream release | Our image | Notes |
|---|---|---|---|---|
| `master-fetch` | [dondai1234/master-fetch](https://github.com/dondai1234/master-fetch) | `v12.4.1` (2026-07-24) | [ghcr.io/pepperlink/master-fetch](https://github.com/orgs/pepperlink/packages/container/package/master-fetch) — 12.4.1, 12.4, 12 | Upstream no longer updated; pin tracked by Renovate, last release date in README. |
| `donsetch` | [dondai44423/donsetch](https://github.com/dondai44423/donsetch) | `v4.1.0` (2026-09-14) | [ghcr.io/pepperlink/donsetch](https://github.com/orgs/pepperlink/packages/container/package/donsetch) — 3.6.7, 3.6, 3 | Pin managed by Renovate; merging a pin bump triggers the rebuild. |
| `forage` | [aldemaroc/forage](https://github.com/aldemaroc/forage) | `main` @ 2026-08-19 (no releases) | [ghcr.io/pepperlink/forage](https://github.com/orgs/pepperlink/packages/container/package/forage) — 0.9.0, 0.9, 0 | No upstream releases/tags - weekly sha-check (forage.yml), sha-tagged builds. |
<!-- status:end -->

## How it works

- `.github/workflows/<app>.yml` — one caller per app: a manual "Run workflow" button (forage keeps a light weekly sha-check).
- `.github/workflows/build.yml` — the shared engine: resolve version (pin in `images.json` →
  latest release → latest tag → default branch) → **skip if that version is already built** →
  checkout upstream → optional overlay from `images/<app>/overlay/` → buildx (amd64 by default) →
  push `:<version>`, `:major.minor`, `:major` (when semver), `:sha-<short>`, `:latest` — with OCI labels.
- **Renovate** (`renovate.json`) watches the upstreams and opens a PR bumping the `version` pin in
  `images.json` — automerged for minor/patch/pin; majors gated behind the dependency dashboard.
  The merged bump lands on `main`, and the push trigger below rebuilds exactly that app.
- `.github/workflows/build-all.yml` — runs on pushes that touch `images.json` (and manually): rebuilds whatever pin moved.
- `.github/workflows/status.yml` — weekly refresh of the table above (upstream release dates).
- `images.json` — inventory + version pins; drives builds and the README table.
- `scripts/update_status.py` — regenerates the table.

## Adding a new image

1. Add an entry to `images.json` (include a `version` pin when the upstream has tags, so Renovate can track it).
2. Add `.github/workflows/<app>.yml` (copy an existing caller, adjust `app`/`upstream`).
3. If the build needs tweaks, drop files into `images/<app>/overlay/` — they are copied over
   the upstream checkout before building (e.g. a patched Dockerfile or config files).

### Versioning

Pins follow the upstream tags (Renovate-managed). For upstreams with no tags yet (e.g. forage),
builds get an interim version `0.<commit-date>-<sha7>` (e.g. `0.20260915-93920b3`) until upstream
starts versioning — the pin flow then takes over automatically.

### ARM builds (optional)

We build **amd64 only** by default — arm64 builds run under emulation (slow) and burn a lot of
CI minutes, so they're opt-in. To build multi-arch for an app:

- uncomment the `platforms:` line in that app's caller (`.github/workflows/<app>.yml`), or
- invoke `build.yml` with `platforms: linux/amd64,linux/arm64` (e.g. from `build-all` or another
  workflow).

## Migration log

- 2026-09-15 — Renovate wiring: version pins + auto-PRs (automerge minor/patch/pin; majors gated);
  weekly crons retired except forage's sha-check; builds trigger on pin merges via `build-all`.
- 2026-09-15 — repo created; callers for master-fetch, donsetch, forage.
  Replaces per-fork build workflows and `ghcr.io/cathelijne/*` images. (searcharr dropped — replaced
  by Seerr; backdroppr dropped — upstream archived; forks being deleted.) Fork cleanup handled separately.
