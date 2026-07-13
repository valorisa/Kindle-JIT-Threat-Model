# tests/

Tests unitaires et d'intégration légère pour les scripts de
`src/detector/`. Aucun test ici n'interagit avec un appareil réel : toutes
les bases SQLite et fichiers de version utilisés sont générés à la volée
dans des répertoires temporaires (`tmp_path` de pytest).

## Prérequis

```bash
pip install pytest --break-system-packages   # sous Termux
# ou simplement : pip install pytest          # sous Windows / venv classique
```

## Lancer les tests

```bash
cd Kindle-JIT-Threat-Model
python3 -m pytest tests/ -v
```

## Couverture actuelle

- `test_check_firmware_version.py` — parsing de version, comparaison au
  seuil `5.19.2`, comportement CLI (codes retour 0/1/2)
- `test_appreg_integrity_check.py` — construction de snapshot, détection
  d'écarts (hash, tables ajoutées/supprimées, comptage de lignes), cycle
  complet `--save-baseline` / `--baseline-file`

`conftest.py` ajoute `src/detector/` au `sys.path` pour permettre l'import
direct des scripts sans packaging.
