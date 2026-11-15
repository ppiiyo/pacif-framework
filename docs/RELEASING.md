# Releasing PACIF

Releases are automated from **git tags**. Pushing `vX.Y.Z` creates a GitHub Release and publishes to PyPI via Trusted Publishing.

## Checklist

1. Version is a single source of truth in `pacif_core/_version.py`.
2. `CHANGELOG.md` has an entry for that version.
3. CI on `main` is green.
4. Tag matches the package version exactly (`v3.1.0` ↔ `__version__ = "3.1.0"`).

## Publish

```bash
git checkout main
git pull
# ensure _version.py == X.Y.Z
git tag -a vX.Y.Z -m "PACIF vX.Y.Z"
git push origin vX.Y.Z
```

Watch **Actions → Publish to PyPI**. On success:

- GitHub Release `vX.Y.Z` (notes auto-generated, artifacts attached)
- Package on https://pypi.org/project/pacif-framework/

## Manual dispatch

**Actions → Publish to PyPI → Run workflow** publishes the current commit to PyPI **without** creating a tag/Release. Prefer tags for production releases.

## Trusted publisher

PyPI publisher must reference:

| Field | Value |
|-------|--------|
| Workflow | `publish.yml` |
| Environment | `pypi` |
| Owner / repo | `ppiiyo` / `pacif-framework` |
