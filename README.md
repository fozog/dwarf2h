# kdk2h

`kdk2h` is a small Python CLI that parses DWARF information and prints all declared types.

## What it prints

The tool scans all compile units and prints DIE entries for these DWARF tags:

- `DW_TAG_base_type`
- `DW_TAG_atomic_type`
- `DW_TAG_const_type`
- `DW_TAG_volatile_type`
- `DW_TAG_pointer_type`
- `DW_TAG_array_type`
- `DW_TAG_typedef`
- `DW_TAG_structure_type`
- `DW_TAG_union_type`
- `DW_TAG_enumeration_type`
- `DW_TAG_subroutine_type`

## Install (end users)

Recommended (no virtualenv activation needed):

```bash
# one-time
brew install pipx
pipx ensurepath

# from PyPI (after publication)
pipx install kdk2h

# or directly from GitHub
pipx install git+https://github.com/<your-user>/kdk2h.git
```

Then run from anywhere:

```bash
kdk2h --help
```

Alternative with pip user install:

```bash
python3 -m pip install --user kdk2h
```

## Installation (development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
kdk2h extract --kdk-file /path/to/dwarf_file
```

Or resolve from a KDK tag:

```bash
kdk2h extract --kdk t6031@26.4.1
```

To print a specific type and recursively expand dependencies for composite types:

```bash
kdk2h extract --kdk-file /path/to/dwarf_file arm_guest_context_26_t
```

To also print the detailed dependency tree (disabled by default):

```bash
kdk2h extract --kdk-file /path/to/dwarf_file arm_guest_context_26_t --with-dependency-tree
```

Write extracted C declarations to a header file:

```bash
kdk2h extract --kdk t6031@26.5.1 arm_guest_context_t --header /tmp/arm_guest_context.h
```

Example with your KDK path:

```bash
kdk2h extract --kdk-file /Library/Developer/KDKs/KDK_26.4.1_25E253.kdk/System/Library/Kernels/kernel.kasan.t6031.dSYM/Contents/Resources/DWARF/kernel.kasan.t6031
```

List installed KDKs and detected platforms:

```bash
kdk2h kdk-list
```

`*` marks the KDK matching the currently running macOS version/build.

Print platforms and full path as well:

```bash
kdk2h kdk-list --full
```

List known platform codes (hand-maintained mapping):

```bash
kdk2h platforms-list
```

`*` marks the currently running platform.

Export platform codes as CSV:

```bash
kdk2h platforms-list --csv
```

## VS Code launch config

A ready-to-use debug configuration is provided in `.vscode/launch.json`.

## Build and publish (maintainer)

Create distributable artifacts (wheel + sdist):

```bash
python -m pip install -U pip
python -m pip install -e .[dev]
python -m build
python -m twine check dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```

After that, end users can simply run:

```bash
pipx install kdk2h
```

## Create and push private GitHub repository

```bash
git init
git add .
git commit -m "Initial commit: kdk2h"
# Option A: GitHub CLI
gh repo create kdk2h --private --source=. --remote=origin --push
# Option B: create private repo on GitHub UI, then:
# git remote add origin git@github.com:<your-user>/kdk2h.git
# git push -u origin main
```

## Note

The tool supports both ELF and Mach-O inputs containing DWARF sections.
