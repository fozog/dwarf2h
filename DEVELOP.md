# Guide de developpement

Ce document explique comment preparer un environnement de developpement pour `dwarf2h`:

- Sans VS Code (terminal uniquement)
- Avec VS Code

Les instructions fonctionnent sur macOS et Linux avec Python 3.10+.

## Prerequis

- Python 3.10 ou plus recent
- `pip`
- `venv` (inclus avec Python standard)

Verification rapide:

```bash
python3 --version
```

## 1) Setup sans VS Code (terminal)

Depuis la racine du projet:

```bash
cd /chemin/vers/dwarf2header
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Notes:

- Le mode `-e` (editable) permet de modifier le code sans reinstaller le package a chaque changement.
- Sous `zsh`, gardez bien les quotes autour de `'.[dev]'`.

Verifier que tout est correct:

```bash
dwarf2h --help
python -m dwarf2h --help
```

### Commandes de dev utiles

Lancer une extraction simple avec un binaire de reference du repo:

```bash
dwarf2h extract --file references/linux/vmlinux-6.8.0-31-generic page
```

Construire les distributions Python:

```bash
python -m build
```

Desactiver l'environnement virtuel:

```bash
deactivate
```

## 2) Setup avec VS Code

### Ouvrir le projet

Ouvrez le dossier racine `dwarf2header` dans VS Code.

### Creer l'environnement Python

Dans le terminal integre VS Code:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

### Selectionner l'interpreteur

1. Ouvrez la palette de commandes (`Cmd+Shift+P` sur macOS).
2. Lancez `Python: Select Interpreter`.
3. Selectionnez l'interpreteur du projet: `.venv/bin/python`.

### Debugger la CLI

Le repo contient deja une configuration de lancement dans `.vscode/launch.json`.

Vous pouvez:

1. Ouvrir l'onglet Run and Debug.
2. Choisir la configuration `dwarf2h` (ou equivalente definie dans `launch.json`).
3. Lancer le debug.

### Validation rapide dans VS Code

Dans le terminal integre (avec `.venv` actif):

```bash
dwarf2h --help
python -m build
```

## Depannage

- `command not found: dwarf2h`
  - Verifiez que le venv est actif (`which python`) puis reinstallez: `python -m pip install -e '.[dev]'`.
- Mauvais interpreteur dans VS Code
  - Re-selectionnez `.venv/bin/python` avec `Python: Select Interpreter`.
- Erreur d'installation sous `zsh` avec extras
  - Utilisez bien les quotes: `python -m pip install -e '.[dev]'`.

## Fichiers de reference

- Dependances et metadata: `pyproject.toml`
- Usage CLI et exemples: `README.md`
- Debug VS Code: `.vscode/launch.json`