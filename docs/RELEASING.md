# Releasing PACIF

**Supported path:** push a version tag → CI runs tests → GitHub Release → PyPI.

Workflow file name **`publish.yml`** and environment **`pypi`** must not change
(PyPI trusted publisher is bound to them).

## Checklist

1. `pacif_core/_version.py` holds the release version (single source of truth).
2. `CHANGELOG.md` has a dated section for that version.
3. CI on `main` is green.
4. Tag matches package version exactly (`v3.1.0` ↔ `__version__ = "3.1.0"`).

## Publish (tag → tests → release)

```bash
git checkout main
git pull
# ensure pacif_core/_version.py == X.Y.Z and CHANGELOG is updated
git tag -a vX.Y.Z -m "PACIF vX.Y.Z"
git push origin vX.Y.Z
```

Watch **Actions → Publish to PyPI**. The workflow:

1. Reads version via `runpy` on `_version.py` (no package import — avoids needing
   numba/yaml before install).
2. Checks tag == package version.
3. Installs `.[dev]`, runs **ruff**, **mypy**, **pytest**.
4. Builds sdist/wheel.
5. Creates the GitHub Release (artifacts attached).
6. Publishes to PyPI via OIDC trusted publishing.

On success:

- GitHub Release `vX.Y.Z`
- Package on https://pypi.org/project/pacif-framework/

## workflow_dispatch

Emergency-only. Allowed **only on `main`**. Refuses if package version already
matches the latest `v*` tag (bump `_version.py` first). Prefer the tag path for
production releases.

## Trusted publisher

| Field | Value |
|-------|--------|
| Workflow | `publish.yml` |
| Environment | `pypi` |
| Owner / repo | `ppiiyo` / `pacif-framework` |
