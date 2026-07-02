# Release guide for kdk2h

## 1. Prepare

```bash
python -m pip install -U pip
python -m pip install -e .[dev]
```

## 2. Build artifacts

```bash
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*
```

Expected files:

- `dist/kdk2h-<version>.tar.gz`
- `dist/kdk2h-<version>-py3-none-any.whl`

## 3. Publish to PyPI

```bash
python -m twine upload dist/*
```

## 4. Validate as a user

```bash
pipx install kdk2h
kdk2h --help
```

## 5. Publish from GitHub repo (optional)

Before publishing, replace placeholders in `pyproject.toml`:

- `https://github.com/<your-user>/kdk2h`
- `https://github.com/<your-user>/kdk2h/issues`
