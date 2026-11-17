# Releasing PACIF

**Supported path:** push a version tag → CI runs tests → GitHub Release → PyPI.

Workflow file name **`publish.yml`** and environment **`pypi`** must not change
(PyPI trusted publisher is bound to them).

## Checklist

1. `pacif_core/_version.py` holds the release version (single source of truth).
2. `CHANGELOG.md` has a dated section for that version.
3. CI on `main` is green.
4. Tag matches package version exactly (`v3.1.1` ↔ `__version__ = "3.1.1"`).
5. That version is **not** already on PyPI (PyPI forbids re-upload of the same filename).

## Publish (tag → tests → release)

```bash
git checkout main
git pull
# ensure pacif_core/_version.py == X.Y.Z and CHANGELOG is updated
git tag -a vX.Y.Z -m "PACIF vX.Y.Z"
git push origin vX.Y.Z
```

Watch **Actions → Publish to PyPI**. The workflow:

1. Reads version via `runpy` on `_version.py` (no package import).
2. Checks tag == package version.
3. Installs `.[dev]`, runs **ruff**, **mypy**, **pytest**.
4. Builds sdist/wheel.
5. Creates the GitHub Release (artifacts attached).
6. Publishes to PyPI via OIDC (`skip-existing: true` so re-runs do not fail on duplicates).

## workflow_dispatch

Emergency-only. Allowed **only on `main`**. Refuses if package version already
matches the latest `v*` tag. Prefer the tag path for production releases.

## Maintenance mode

Project is in maintenance: security fixes and clear bugs only. Feature work is
paused until a concrete use-case or external demand appears.

## Trusted publisher

| Field | Value |
|-------|--------|
| Workflow | `publish.yml` |
| Environment | `pypi` |
| Owner / repo | `ppiiyo` / `pacif-framework` |
