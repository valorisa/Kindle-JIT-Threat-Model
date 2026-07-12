#!/usr/bin/env python3
"""
check_firmware_version.py

Outil de détection défensive : vérifie si la version de firmware d'un Kindle
est antérieure au seuil de sécurité 5.19.2 (correctif de la faille V8/Turbofan
documentée par Synacktiv, juin-juillet 2026).

Ce script ne réalise AUCUNE action offensive : il compare uniquement des
numéros de version fournis en entrée (fichier de version local, ou saisie
manuelle) et retourne un statut de conformité.

Usage :
    python3 check_firmware_version.py --version 5.18.6
    python3 check_firmware_version.py --version-file /path/to/version.txt

Sortie : code retour 0 si sûr, 1 si vulnérable/à mettre à jour, 2 si version
illisible.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Seuil de sécurité publié : premier firmware corrigé pour la faille
# documentée par Synacktiv (patch de janvier 2026).
SAFE_VERSION: tuple[int, int, int] = (5, 19, 2)

VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def parse_version(raw: str) -> tuple[int, int, int] | None:
    """Extrait un triplet (major, minor, patch) d'une chaîne de version."""
    match = VERSION_RE.search(raw.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def is_safe(version: tuple[int, int, int]) -> bool:
    """Retourne True si `version` >= SAFE_VERSION."""
    return version >= SAFE_VERSION


def read_version_from_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vérifie la conformité du firmware Kindle au seuil de sécurité 5.19.2."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--version", help="Numéro de version à vérifier, ex: 5.18.6")
    group.add_argument(
        "--version-file",
        type=Path,
        help="Fichier texte contenant la version (ex: export d'un diagnostic appareil)",
    )
    args = parser.parse_args()

    raw = args.version if args.version else read_version_from_file(args.version_file)
    version = parse_version(raw)

    if version is None:
        print(f"[ERREUR] Impossible d'interpréter la version depuis : {raw!r}", file=sys.stderr)
        return 2

    version_str = ".".join(str(part) for part in version)
    safe_str = ".".join(str(part) for part in SAFE_VERSION)

    if is_safe(version):
        print(f"[OK] Firmware {version_str} >= {safe_str} — appareil à jour.")
        return 0

    print(
        f"[VULNÉRABLE] Firmware {version_str} < {safe_str} — mise à jour requise.\n"
        "Action recommandée : connecter l'appareil au Wi-Fi pour déclencher la "
        "mise à jour automatique OTA, ou appliquer le correctif hors-ligne "
        "(voir SECURITY_POLICY.md)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
