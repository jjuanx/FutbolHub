"""Sincroniza las páginas de `docs/wiki/` con el repositorio wiki de GitHub (`FutbolHub.wiki.git`).

Requisito previo en GitHub:
    1. Activar la casilla *Wikis* en `Settings -> Features` del repositorio `jjuanx/FutbolHub`.
    2. Crear la primera página en blanco desde la pestaña *Wiki* de GitHub (necesario para que
       GitHub inicialice el repositorio `jjuanx/FutbolHub.wiki.git`).

Uso:
    python scripts/github/sync_wiki.py
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

WIKI_REMOTE = "https://github.com/jjuanx/FutbolHub.wiki.git"
REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCE_DIR = REPO_ROOT / "docs" / "wiki"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(f"Error ejecutando {' '.join(cmd)}:\n{result.stderr.strip()}")


def sync_wiki() -> None:
    if not WIKI_SOURCE_DIR.is_dir():
        raise SystemExit(f"No se encontró el directorio fuente de la wiki: {WIKI_SOURCE_DIR}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "wiki"
        print(f"Clonando {WIKI_REMOTE}...")
        run(["git", "clone", WIKI_REMOTE, str(tmp_path)])

        copied = []
        for md_file in sorted(WIKI_SOURCE_DIR.glob("*.md")):
            shutil.copy2(md_file, tmp_path / md_file.name)
            copied.append(md_file.name)

        run(["git", "add", "."], cwd=tmp_path)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=tmp_path,
            text=True,
            capture_output=True,
        ).stdout.strip()

        if not status:
            print("La wiki ya está al día.")
            return

        run(["git", "commit", "-m", "docs(wiki): sincronizar diario del equipo desde docs/wiki (#3)"], cwd=tmp_path)
        run(["git", "push", "origin", "HEAD"], cwd=tmp_path)
        print(f"Wiki sincronizada correctamente ({len(copied)} páginas): {', '.join(copied)}")


if __name__ == "__main__":
    sync_wiki()
