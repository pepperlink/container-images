# overlays

Optional per-app build overlays live here: `images/<app>/overlay/`.

Everything in that directory is copied over the upstream checkout just before the build
(`cp -a images/<app>/overlay/. upstream/`), so you can ship a patched Dockerfile,
extra config files, or small source fixes without forking the upstream.

Apps without an overlay don't need a directory here at all.
