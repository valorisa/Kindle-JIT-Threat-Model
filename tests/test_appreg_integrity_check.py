"""
test_appreg_integrity_check.py

Tests unitaires pour src/detector/appreg_integrity_check.py.
Utilise des bases SQLite temporaires factices — aucun lien avec un appareil
réel, aucune manipulation d'un vrai appreg.db.
"""

import json
import sqlite3
from pathlib import Path

import pytest

import appreg_integrity_check as aic


def make_fake_db(path: Path, apps: list[tuple[str, str]]) -> None:
    """Crée une base sqlite factice à plat, avec une table 'apps' générique."""
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE apps (id TEXT PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO apps (id, name) VALUES (?, ?)", apps)
    conn.commit()
    conn.close()


@pytest.fixture
def healthy_db(tmp_path) -> Path:
    db_path = tmp_path / "appreg_healthy.db"
    make_fake_db(db_path, [("com.amazon.kindle.reader", "Kindle Reader"),
                            ("com.amazon.kindle.store", "Kindle Store")])
    return db_path


# --- Tests sur build_snapshot ------------------------------------------------

def test_build_snapshot_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        aic.build_snapshot(tmp_path / "nope.db")


def test_build_snapshot_basic_fields(healthy_db):
    snapshot = aic.build_snapshot(healthy_db)
    assert "file_sha256" in snapshot
    assert snapshot["file_size_bytes"] > 0
    assert snapshot["tables"] == ["apps"]
    assert snapshot["row_counts"] == {"apps": 2}


def test_build_snapshot_hash_changes_with_content(tmp_path):
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    make_fake_db(db_a, [("com.example.one", "One")])
    make_fake_db(db_b, [("com.example.one", "One"), ("com.example.two", "Two")])

    snap_a = aic.build_snapshot(db_a)
    snap_b = aic.build_snapshot(db_b)

    assert snap_a["file_sha256"] != snap_b["file_sha256"]


# --- Tests sur compare_snapshots --------------------------------------------

def test_compare_snapshots_identical_returns_no_findings(healthy_db):
    snap = aic.build_snapshot(healthy_db)
    findings = aic.compare_snapshots(snap, snap)
    assert findings == []


def test_compare_snapshots_detects_hash_drift(tmp_path):
    db_path = tmp_path / "appreg.db"
    make_fake_db(db_path, [("com.example.one", "One")])
    baseline = aic.build_snapshot(db_path)

    # Simule une modification ultérieure du fichier
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO apps (id, name) VALUES ('com.evil.app', 'Rogue Launcher')")
    conn.commit()
    conn.close()

    current = aic.build_snapshot(db_path)
    findings = aic.compare_snapshots(baseline, current)

    assert any("Hash du fichier différent" in f for f in findings)
    assert any("nombre d'entrées modifié" in f for f in findings)


def test_compare_snapshots_detects_new_table(tmp_path):
    db_path = tmp_path / "appreg.db"
    make_fake_db(db_path, [("com.example.one", "One")])
    baseline = aic.build_snapshot(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE rogue_table (x TEXT)")
    conn.commit()
    conn.close()

    current = aic.build_snapshot(db_path)
    findings = aic.compare_snapshots(baseline, current)

    assert any("rogue_table" in f for f in findings)


def test_compare_snapshots_detects_removed_table(tmp_path):
    db_path = tmp_path / "appreg.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE apps (id TEXT)")
    conn.execute("CREATE TABLE extra (id TEXT)")
    conn.commit()
    conn.close()
    baseline = aic.build_snapshot(db_path)

    # Recrée la base sans la table 'extra'
    db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE apps (id TEXT)")
    conn.commit()
    conn.close()

    current = aic.build_snapshot(db_path)
    findings = aic.compare_snapshots(baseline, current)

    assert any("extra" in f for f in findings)


# --- Tests bout-en-bout via l'interface CLI (main) --------------------------

def test_cli_save_and_check_baseline(healthy_db, tmp_path, capsys):
    baseline_file = tmp_path / "baseline.json"

    import sys
    old_argv = sys.argv
    try:
        sys.argv = ["appreg_integrity_check.py", str(healthy_db), "--save-baseline", str(baseline_file)]
        rc = aic.main()
        assert rc == 0
        assert baseline_file.exists()

        saved = json.loads(baseline_file.read_text(encoding="utf-8"))
        assert saved["tables"] == ["apps"]

        sys.argv = ["appreg_integrity_check.py", str(healthy_db), "--baseline-file", str(baseline_file)]
        rc = aic.main()
        captured = capsys.readouterr()
        assert rc == 0
        assert "Aucun écart détecté" in captured.out
    finally:
        sys.argv = old_argv
