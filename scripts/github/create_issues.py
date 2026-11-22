"""Crea en GitHub las etiquetas, los hitos y las issues del reparto definido en reparto.py.

    python scripts/github/create_issues.py --dry --show nd-upload   # previsualiza el cuerpo de una issue
    python scripts/github/create_issues.py --labels                 # etiquetas e hitos
    python scripts/github/create_issues.py --issues                 # issues (solo en un repo sin issues ni PR)

Los números de issue se predicen a partir del orden de reparto.py, porque issues y PR comparten numeración.
Por eso --issues se niega a ejecutarse si el repositorio ya tiene issues o PR.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reparto import I, LABELS, MILESTONES  # noqa: E402

REPO = "jjuanx/FutbolHub"
DRY = "--dry" in sys.argv


def gh(*args, input=None):
    if DRY:
        return ""
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input)
    if r.returncode:
        raise SystemExit(f"gh {' '.join(args[:3])} failed: {r.stderr}")
    return r.stdout


def collaborators():
    out = subprocess.run(
        ["gh", "api", f"repos/{REPO}/collaborators", "--jq", ".[].login"], capture_output=True, text=True
    ).stdout
    return {login.lower() for login in out.split()}


num = {it["key"]: i + 1 for i, it in enumerate(I)}
by_key = {it["key"]: it for it in I}
for it in I:
    for d in it["deps"]:
        assert d in num, (it["key"], d)


def body(it):
    n = num[it["key"]]
    deps = ", ".join(f"#{num[d]}" for d in it["deps"]) or "—"
    blocks = ", ".join(f"#{num[o['key']]}" for o in I if it["key"] in o["deps"]) or "—"
    tasks = "\n".join(f"- [ ] {t}" for t in it["tasks"])
    crit = "\n".join(f"- [ ] {c}" for c in it["crit"])
    return f"""## Descripción
{it['desc']}

## Tareas
{tasks}

## Criterios de aceptación
{crit}
- [ ] Revisión de otro miembro registrada en esta issue y CI en verde antes de integrar en `trunk`

## Seguimiento
| | |
|---|---|
| **Responsable** | @{it['who']} |
| **Revisor sugerido** | @{it['rev']} |
| **Estimación** | {it['days']} día(s) |
| **Depende de** | {deps} |
| **Bloquea a** | {blocks} |
| **Rama** | `{n}-{it['slug']}` (desde `trunk`) |
"""


if "--labels" in sys.argv:
    for name, desc, color in LABELS:
        gh("label", "create", name, "-R", REPO, "-d", desc, "-c", color, "--force")
        print("label", name)
    for title, due, desc in MILESTONES:
        gh(
            "api",
            f"repos/{REPO}/milestones",
            "-f",
            f"title={title}",
            "-f",
            f"due_on={due}T23:59:59Z",
            "-f",
            f"description={desc}",
        )
        print("milestone", title)

if "--issues" in sys.argv:
    if not DRY:
        existing = gh("api", f"repos/{REPO}/issues?state=all&per_page=1", "--jq", "length").strip()
        if existing != "0":
            raise SystemExit("El repositorio ya tiene issues o PR: la numeración no sería la prevista.")
    collab = set() if DRY else collaborators()
    for it in I:
        n = num[it["key"]]
        labels = [f"tipo: {it['typ']}", f"prioridad: {it['prio']}", f"WI: {it['wi']}"]
        args = ["issue", "create", "-R", REPO, "-t", it["title"], "-F", "-", "-m", it["ms"]]
        for lb in labels:
            args += ["-l", lb]
        if it["who"].lower() in collab:
            args += ["-a", it["who"]]
        url = gh(*args, input=body(it)).strip()
        got = int(url.rsplit("/", 1)[-1]) if url else n
        if got != n:
            raise SystemExit(f"numbering drift: expected #{n}, got {url}")
        print(f"#{n:>2} {it['who']:<13} {it['title']}")

if "--show" in sys.argv:
    print(body(by_key[sys.argv[-1]]))

if "--json" in sys.argv:
    print(json.dumps({num[k]: v["who"] for k, v in by_key.items()}, indent=1))
