"""
test_check_firmware_version.py

Tests unitaires pour src/detector/check_firmware_version.py.
Ne teste que la logique de comparaison de version — aucun lien avec un
appareil réel.
"""

import subprocess
import sys
from pathlib import Path

import pytest

import check_firmware_version as cfv

SCRIPT_PATH = Path(__file__).parent.parent / "src" / "detector" / "check_firmware_version.py"


# --- Tests unitaires sur les fonctions internes -----------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("5.19.2", (5, 19, 2)),
        ("5.18.6", (5, 18, 6)),
        ("version: 5.19.2 (stable)", (5, 19, 2)),
        ("v5.19.10-build2231", (5, 19, 10)),
        ("", None),
        ("firmware unknown", None),
    ],
)
def test_parse_version(raw, expected):
    assert cfv.parse_version(raw) == expected


@pytest.mark.parametrize(
    "version,expected_safe",
    [
        ((5, 19, 2), True),   # exactement le seuil
        ((5, 19, 3), True),   # au-dessus
        ((5, 20, 0), True),   # version majeure future
        ((6, 0, 0), True),
        ((5, 19, 1), False),  # juste en dessous
        ((5, 18, 6), False),  # version connue vulnérable
        ((0, 0, 1), False),
    ],
)
def test_is_safe(version, expected_safe):
    assert cfv.is_safe(version) == expected_safe


def test_read_version_from_file_missing(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        cfv.read_version_from_file(missing)


def test_read_version_from_file_ok(tmp_path):
    version_file = tmp_path / "version.txt"
    version_file.write_text("Kindle firmware 5.19.2\n", encoding="utf-8")
    content = cfv.read_version_from_file(version_file)
    assert "5.19.2" in content


# --- Tests bout-en-bout via l'interface CLI ---------------------------------

def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_safe_version_returns_zero():
    result = run_cli("--version", "5.19.2")
    assert result.returncode == 0
    assert "[OK]" in result.stdout


def test_cli_vulnerable_version_returns_one():
    result = run_cli("--version", "5.18.6")
    assert result.returncode == 1
    assert "[VULNÉRABLE]" in result.stdout


def test_cli_unparsable_version_returns_two():
    result = run_cli("--version", "not-a-version")
    assert result.returncode == 2


def test_cli_version_file(tmp_path):
    version_file = tmp_path / "version.txt"
    version_file.write_text("5.19.5", encoding="utf-8")
    result = run_cli("--version-file", str(version_file))
    assert result.returncode == 0


def test_cli_requires_one_argument():
    # Ni --version ni --version-file : argparse doit rejeter (code 2)
    result = run_cli()
    assert result.returncode == 2
