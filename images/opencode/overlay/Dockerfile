# Derived image: upstream ships the CLI as a prebuilt musl binary with no git, so the coding
# harness could edit a worktree but never commit. Base is the upstream *image* (pinned by tag,
# kept in step with images.json's `version` / the caller's UPSTREAM_TAG build-arg), not a source
# build — upstream's own Dockerfile only COPYs from a `dist/` that does not exist in a checkout.
ARG UPSTREAM_TAG=1.19.5
FROM ghcr.io/anomalyco/opencode:${UPSTREAM_TAG}

USER root
# libgcc/libstdc++/ripgrep already come from the base; git is the delta.
RUN apk add --no-cache git && git --version
# Upstream image config has no USER (runs as root); keep that for runAsUser overrides (e.g. 10000).
