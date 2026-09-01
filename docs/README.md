# Building the MyGene.info docs locally

These are the Sphinx sources for <https://docs.mygene.info>. Read the Docs builds
them automatically from [`.readthedocs.yml`](../.readthedocs.yml); this file covers
building and serving them on your own machine.

All commands are run from the **repository root** unless noted otherwise.

## One-time setup

Create a virtualenv and install the documentation requirements:

```bash
python3 -m venv .venv
.venv/bin/pip install -r docs/requirements_sphinx.txt
```

This installs Sphinx, `sphinx_rtd_theme`, and `sphinxcontrib-jquery`.

> **Note:** `sphinxcontrib-jquery` is not optional. Sphinx 6.0 stopped bundling
> jQuery, and [`_static/mygene_doc.js`](_static/mygene_doc.js) depends on it to
> populate the release-notes list and the indexed-fields table. Without it those
> pages render but stay empty. See issue
> [#173](https://github.com/biothings/mygene.info/issues/173).

## Option A — build once, then serve

```bash
.venv/bin/sphinx-build -b html docs docs/_build/html
cd docs/_build/html && python3 -m http.server 8765
```

Then open <http://localhost:8765/doc/release_changes.html>. Press `Ctrl+C` to stop.

`sphinx-build` only generates files, it does not serve them, so the second command
is required.

> **Do not open the built HTML with `file://`.** The pages fetch data over AJAX,
> which browsers block on `file://` URLs. The symptom is a page stuck on
> "Loading release data . . ." — the same symptom as the missing-jQuery bug, but a
> different cause.

The output directory is created automatically; there is no need to `mkdir` it.

## Option B — autobuild (recommended while editing)

`sphinx-autobuild` rebuilds and reloads the browser whenever you save. It is a
local development tool only, so it is deliberately **not** in
`requirements_sphinx.txt` (that file is installed by Read the Docs in production):

```bash
.venv/bin/pip install sphinx-autobuild
.venv/bin/sphinx-autobuild docs docs/_build/html --port 8765
```

Then open <http://localhost:8765/doc/release_changes.html>. Press `Ctrl+C` to stop.

Omit `--port 8765` to use the default port 8000.

## Option C — the Makefile

[`Makefile`](Makefile) and [`make.bat`](make.bat) are stock `sphinx-quickstart`
wrappers (the `.bat` is the Windows equivalent). They call a bare `sphinx-build`
resolved from `PATH`, so the virtualenv must be **activated** first:

```bash
source .venv/bin/activate
cd docs
make html
```

The output lands in `docs/_build/html`; serve it as in Option A. Run `make help`
for the full target list. Most targets (`epub`, `latexpdf`, `qthelp`, ...) are
unused here. Two that are handy:

```bash
make clean       # remove everything under _build/
make linkcheck   # verify external links resolve
```

## Notes

**Expected warnings.** A successful build currently ends with
`build succeeded, 4 warnings.` Those four are Pygments failing to lex
Python-style dict output that is tagged as `json` (single-quoted keys) in
`doc/annotation_service.rst` and `doc/query_service.rst`. Sphinx falls back to
relaxed mode and the pages render correctly.

**Live data.** The release-notes and indexed-fields pages are populated at runtime
in the browser, not at build time. They call:

- `https://s3-us-west-2.amazonaws.com/biothings-releases/mygene.info/versions.json`
- `https://mygene.info/v3/metadata/fields`

If those pages look empty, check the browser console before suspecting the build.

**Port already in use.** Any port works. To clear a stale server:

```bash
pkill -f "http.server 8765"
pkill -f sphinx-autobuild
```
