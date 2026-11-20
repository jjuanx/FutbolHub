"""Crea el GitHub Project (tablero Kanban) de FutbolHub con los estados del acta y mete todas las issues.

    python scripts/github/create_board.py            # crea el tablero (necesita `gh auth refresh -s project`)
    python scripts/github/create_board.py --assign   # asigna las issues cuyo responsable aún no estaba asignado

La vista de tablero y los workflows del Project (añadido -> Pendiente, cerrada -> Hecho) no se pueden
configurar por API: se activan a mano en la web del Project.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reparto import I  # noqa: E402

OWNER, REPO = "jjuanx", "jjuanx/FutbolHub"
TITLE = "FutbolHub — Tablero"
STATUS = [  # acta, sección 7
    ("Pendiente", "GRAY", "Issue aceptada, sin empezar"),
    ("En progreso", "BLUE", "Tiene responsable y rama de tarea abierta"),
    ("En revisión", "YELLOW", "Terminada en su rama, esperando la revisión de otro miembro"),
    ("Bloqueada", "RED", "No puede avanzar; el motivo consta en la issue"),
    ("Hecho", "GREEN", "Integrada en trunk con el CI en verde"),
]


def gh(*a, check=True):
    r = subprocess.run(["gh", *a], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"gh {' '.join(a[:4])}: {r.stderr}")
    return r.stdout


def gql(q, **v):
    args = ["api", "graphql", "-f", f"query={q}"]
    for k, val in v.items():
        args += ["-F" if isinstance(val, (int, float)) else "-f", f"{k}={val}"]
    return json.loads(gh(*args))


if "--assign" in sys.argv:
    for n, it in enumerate(I, 1):
        assigned = gh("issue", "view", str(n), "-R", REPO, "--json", "assignees", "--jq", ".assignees[].login")
        if it["who"].lower() not in assigned.lower().split():
            out = subprocess.run(["gh", "issue", "edit", str(n), "-R", REPO, "--add-assignee", it["who"]], capture_output=True, text=True)
            print(f"#{n} -> {it['who']}: {'ok' if out.returncode == 0 else out.stderr.strip()}")
    raise SystemExit

proj = json.loads(gh("project", "create", "--owner", OWNER, "--title", TITLE, "--format", "json"))
pnum, pid = proj["number"], proj["id"]
gh("project", "link", str(pnum), "--owner", OWNER, "--repo", REPO)
print("project", pnum, proj["url"])

fields = json.loads(gh("project", "field-list", str(pnum), "--owner", OWNER, "--format", "json"))["fields"]
status_id = next(f["id"] for f in fields if f["name"] == "Status")
opts = ",".join(f'{{name:"{n}",color:{c},description:"{d}"}}' for n, c, d in STATUS)
res = gql(f"""mutation($f:ID!){{updateProjectV2Field(input:{{fieldId:$f,singleSelectOptions:[{opts}]}}){{
  projectV2Field{{... on ProjectV2SingleSelectField{{options{{id name}}}}}}}}}}""", f=status_id)
opt = {o["name"]: o["id"] for o in res["data"]["updateProjectV2Field"]["projectV2Field"]["options"]}

est = json.loads(gh("project", "field-create", str(pnum), "--owner", OWNER, "--name", "Estimación (días)", "--data-type", "NUMBER", "--format", "json"))["id"]

for n, it in enumerate(I, 1):
    item = json.loads(gh("project", "item-add", str(pnum), "--owner", OWNER, "--url", f"https://github.com/{REPO}/issues/{n}", "--format", "json"))["id"]
    state = "En progreso" if it["key"] == "board" else "Pendiente"
    gh("project", "item-edit", "--id", item, "--project-id", pid, "--field-id", status_id, "--single-select-option-id", opt[state])
    gh("project", "item-edit", "--id", item, "--project-id", pid, "--field-id", est, "--number", str(it["days"]))
    print(f"#{n} -> {state}")
print("DONE", proj["url"])
