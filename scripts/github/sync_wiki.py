"""Sincroniza las páginas de `docs/wiki/` con el repositorio wiki de GitHub (`FutbolHub.wiki.git`).

Requisito previo en GitHub:
    1. Activar la casilla *Wikis* en `Settings -> Features` del repositorio `jjuanx/FutbolHub`.
    2. Crear la primera página desde la pestaña *Wiki* de GitHub (necesario para que
       GitHub inicialice el repositorio Git `jjuanx/FutbolHub.wiki.git`).

Uso:
    python scripts/github/sync_wiki.py
    python scripts/github/sync_wiki.py -m "docs(wiki): actualizar diario del equipo"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

WIKI_REMOTE = "https://github.com/jjuanx/FutbolHub.wiki.git"
REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCE_DIR = REPO_ROOT / "docs" / "wiki"
DEFAULT_COMMIT_MSG = "docs(wiki): sincronizar diario del equipo desde docs/wiki"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(f"Error ejecutando {' '.join(cmd)}:\n{result.stderr.strip()}")


def sync_wiki(commit_message: str = DEFAULT_COMMIT_MSG) -> None:
    if not WIKI_SOURCE_DIR.is_dir():
        raise SystemExit(f"No se encontró el directorio fuente de la wiki: {WIKI_SOURCE_DIR}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "wiki"
        print(f"Clonando {WIKI_REMOTE}...")
        run(["git", "clone", WIKI_REMOTE, str(tmp_path)])

        source_files = {md_file.name: md_file for md_file in sorted(WIKI_SOURCE_DIR.glob("*.md"))}

        # Eliminar de la wiki las páginas .md que ya no existan en docs/wiki/
        removed = []
        for existing_md in sorted(tmp_path.glob("*.md")):
            if existing_md.name not in source_files:
                existing_md.unlink()
                removed.append(existing_md.name)

        copied = []
        for name, md_file in source_files.items():
            shutil.copy2(md_file, tmp_path / name)
            copied.append(name)

        run(["git", "add", "-A"], cwd=tmp_path)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=tmp_path,
            text=True,
            capture_output=True,
        ).stdout.strip()

        if not status:
            print("La wiki ya está al día.")
            return

        run(["git", "commit", "-m", commit_message], cwd=tmp_path)
        run(["git", "push", "origin", "HEAD"], cwd=tmp_path)
        print(f"Wiki sincronizada ({len(copied)} páginas copiadas, {len(removed)} eliminadas).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincroniza docs/wiki/ con FutbolHub.wiki.git")
    parser.add_argument("-m", "--message", default=DEFAULT_COMMIT_MSG, help="Mensaje de commit para la wiki")
    args = parser.parse_args()
    sync_wiki(commit_message=args.message)
