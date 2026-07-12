#!/usr/bin/env python3
"""
appreg_integrity_check.py

Outil de détection défensive : contrôle d'intégrité générique pour le fichier
de registre applicatif `appreg.db` d'un Kindle, dans le cadre du threat model
documenté dans docs/THREAT_MODEL.md.

Principe : détection par écart à une baseline connue (hash + inventaire des
entrées), PAS par reconstruction du mécanisme d'exploitation. Ce script ne
contient aucune logique d'écriture, d'injection ou de modification de
`appreg.db` — uniquement de la lecture et de la comparaison.

Usage :
    # Générer une baseline sur un appareil considéré sain (après mise à jour 5.19.2)
    python3 appreg_integrity_check.py --baseline appreg.db --save-baseline baseline.json

    # Vérifier un appareil contre la baseline enregistrée
    python3 appreg_integrity_check.py --check appreg.db --baseline-file baseline.json

Limites connues :
- Ce script fournit une détection de premier niveau (hash global + liste des
  entrées visibles via sqlite3). Il ne remplace pas une analyse forensique
  complète.
- Les noms de tables/colonnes réels de `appreg.db` doivent être adaptés selon
  la version de firmware réellement auditée ; les valeurs ci-dessous sont des
  exemples génériques à ajuster.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def list_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return sorted(row[0] for row in cur.fetchall())


def dump_row_counts(conn: sqlite3.Connection, tables: list[str]) -> dict[str, int]:
    counts = {}
    for table in tables:
        try:
            cur = conn.execute(f"SELECT COUNT(*) FROM '{table}'")  # noqa: S608 (lecture seule, nom validé via sqlite_master)
            counts[table] = cur.fetchone()[0]
        except sqlite3.DatabaseError:
            counts[table] = -1
    return counts


def build_snapshot(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {db_path}")

    snapshot: dict[str, Any] = {
        "file_sha256": sha256_of_file(db_path),
        "file_size_bytes": db_path.stat().st_size,
    }

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        tables = list_tables(conn)
        snapshot["tables"] = tables
        snapshot["row_counts"] = dump_row_counts(conn, tables)
        conn.close()
    except sqlite3.DatabaseError as exc:
        snapshot["sqlite_error"] = str(exc)

    return snapshot


def compare_snapshots(baseline: dict[str, Any], current: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if baseline.get("file_sha256") != current.get("file_sha256"):
        findings.append(
            "Hash du fichier différent de la baseline — le fichier a été modifié "
            "depuis la référence connue."
        )

    baseline_tables = set(baseline.get("tables", []))
    current_tables = set(current.get("tables", []))

    added = current_tables - baseline_tables
    removed = baseline_tables - current_tables
    if added:
        findings.append(f"Nouvelle(s) table(s) inattendue(s) : {sorted(added)}")
    if removed:
        findings.append(f"Table(s) manquante(s) par rapport à la baseline : {sorted(removed)}")

    baseline_counts = baseline.get("row_counts", {})
    current_counts = current.get("row_counts", {})
    for table in baseline_tables & current_tables:
        b, c = baseline_counts.get(table), current_counts.get(table)
        if b is not None and c is not None and b != c:
            findings.append(
                f"Table '{table}' : nombre d'entrées modifié ({b} → {c}) — "
                "à investiguer manuellement, notamment tout ajout d'entrée "
                "de lancement d'application non attendue."
            )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Contrôle d'intégrité de appreg.db")
    parser.add_argument("db_path", type=Path, help="Chemin vers le appreg.db à analyser")
    parser.add_argument(
        "--save-baseline",
        type=Path,
        help="Enregistre un snapshot de référence (baseline) au format JSON",
    )
    parser.add_argument(
        "--baseline-file",
        type=Path,
        help="Compare db_path à une baseline JSON précédemment enregistrée",
    )
    args = parser.parse_args()

    snapshot = build_snapshot(args.db_path)

    if args.save_baseline:
        args.save_baseline.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        print(f"[OK] Baseline enregistrée dans {args.save_baseline}")
        return 0

    if args.baseline_file:
        if not args.baseline_file.exists():
            print(f"[ERREUR] Baseline introuvable : {args.baseline_file}", file=sys.stderr)
            return 2
        baseline = json.loads(args.baseline_file.read_text(encoding="utf-8"))
        findings = compare_snapshots(baseline, snapshot)
        if not findings:
            print("[OK] Aucun écart détecté par rapport à la baseline.")
            return 0
        print("[ALERTE] Écarts détectés :")
        for f in findings:
            print(f"  - {f}")
        return 1

    print(json.dumps(snapshot, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
