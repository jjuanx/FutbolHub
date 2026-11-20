# Seguimiento del proyecto en GitHub

Scripts con los que se montó el seguimiento del proyecto descrito en la sección 7 del acta fundacional (issue #1).
Quedan versionados como registro del primer reparto y para poder repetir o completar la configuración.

| Fichero | Qué hace |
|---|---|
| `reparto.py` | Datos del primer reparto: etiquetas, hitos e issues con responsable, revisor, estimación, dependencias y rama. |
| `create_issues.py` | Crea en GitHub las etiquetas, los hitos y las issues a partir de `reparto.py`. |
| `create_board.py` | Crea el GitHub Project con los estados del acta y mete todas las issues. Con `--assign`, asigna las issues cuyo responsable aún no estaba asignado. |

## Convenciones

- **Etiquetas**: `tipo:` (feature, bug, refactor, docs, ci), `prioridad:` (alta, media, baja) y `WI:` (WI de origen, o `WI: organización`).
- **Hitos**: `0.1.0` (seguimiento del 23 nov), `0.2.0` (seguimiento del 30 nov) y `1.0.0` (defensa).
- **Estados del tablero**: Pendiente → En progreso → En revisión → Hecho, más Bloqueada.
- Cada issue indica su rama de tarea: `<nº issue>-<descripción>`, creada desde `trunk`.

## Uso

Requiere `gh` autenticado con los scopes `repo` y `project` (`gh auth refresh -s project`).

```bash
python scripts/github/create_issues.py --dry --show nd-validator    # previsualizar sin tocar GitHub
python scripts/github/create_issues.py --labels                     # etiquetas e hitos
python scripts/github/create_issues.py --issues                     # solo en un repositorio sin issues ni PR
python scripts/github/create_board.py                               # tablero
python scripts/github/create_board.py --assign                      # cuando un miembro acepta la invitación
```

La vista de tablero y los workflows del Project (añadido → Pendiente, cerrada → Hecho) no se pueden configurar por API
y se activan a mano en la web del Project.

Las issues nuevas se crean con las plantillas de `.github/ISSUE_TEMPLATE/` (#2), no con estos scripts.
