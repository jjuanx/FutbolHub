# Guía de contribución — FutbolHub

Esta guía recoge cómo trabaja el equipo: los criterios de revisión de código y
de diseño de pruebas (secciones 1-6) y la política de ramas, commits, revisión
e integración que sigue EGCFlow (secciones 7-12). Todos los miembros la aplican
al escribir, revisar e integrar código. Desarrolla las secciones 5 y 7 del acta
fundacional ([docs/](docs/)).

**Índice**

1. [Checklist de revisión de código](#1-checklist-de-revisión-de-código)
2. [Guía de diseño de pruebas](#2-guía-de-diseño-de-pruebas)
3. [Tipos de pruebas](#3-tipos-de-pruebas-cuándo-usar-cada-una)
4. [Cobertura de código](#4-cobertura-de-código)
5. [Estructura de ficheros de pruebas](#5-estructura-de-ficheros-de-pruebas)
6. [Flujo de trabajo resumido](#6-flujo-de-trabajo-resumido)
7. [Ramas (EGCFlow)](#7-ramas-egcflow)
8. [Commits](#8-commits)
9. [Revisión en la issue y en el tablero](#9-revisión-en-la-issue-y-en-el-tablero)
10. [Integración en trunk sin pull requests](#10-integración-en-trunk-sin-pull-requests)
11. [Rebase y ramas de larga duración](#11-rebase-y-ramas-de-larga-duración)
12. [Entregas a main](#12-entregas-a-main)

---

## 1. Checklist de revisión de código

Antes de dar el visto bueno a una rama, el revisor comprueba **todos** los
puntos de esta lista y deja constancia en la issue (ver sección 7 del acta).

### Legibilidad y estilo

- [ ] El código es claro y se entiende sin comentarios adicionales innecesarios.
- [ ] Los nombres de variables, funciones y clases son descriptivos y siguen las
      convenciones de Python (`snake_case` para funciones/variables,
      `PascalCase` para clases).
- [ ] No hay código comentado, dead code ni `print()` de depuración.
- [ ] El lint pasa igual que en el CI. `rosemary linter` solo ejecuta `flake8`;
      el CI también comprueba formato e imports:
      ```bash
      rosemary linter
      black --check app rosemary
      isort --check-only app rosemary
      ```
      (`rosemary linter:fix` formatea y ordena imports automáticamente.)
- [ ] Quien entrega sabe explicar todo el código, también el generado con IA
      (acta, sección 6, norma 6).

### Pruebas

- [ ] El cambio incluye pruebas que ejercitan el código nuevo o modificado.
- [ ] Las pruebas usan el marker correcto (`@pytest.mark.unit`,
      `@pytest.mark.repository`, etc.; ver sección 3).
- [ ] Los nombres de las pruebas describen el comportamiento esperado
      (`test_rechaza_goles_negativos`, no `test_1`).
- [ ] Los casos cubren particiones de equivalencia y valores límite (ver
      sección 2).

### CI y seguridad

- [ ] El CI está en verde en la rama (commits y lint; pytest también tras integrar #6) y
      `rosemary test` pasa en local.
- [ ] No se suben secretos (tokens, contraseñas, ficheros `.env`).
- [ ] Los ficheros `.env.*.example` se actualizan si se añaden variables nuevas.

### Commits e issues

- [ ] Cada commit sigue Conventional Commits: `feat:`, `fix:`, `test:`,
      `docs:`, `refactor:`, `ci:`, `chore:`.
- [ ] Cada commit referencia la issue: `feat: validar goles negativos (#17)`.
- [ ] Un commit = un cambio lógico y completo.
- [ ] No se sube con `--force` a ramas compartidas.

### Cómo se revisa (sin pull requests)

1. El autor pasa la issue a **En revisión** y asigna un revisor.
2. El revisor examina el diff frente a `trunk` en un plazo de **48 h**:
   `git diff trunk...<rama>` o la comparación de ramas de GitHub.
3. Comentarios y visto bueno quedan **en la issue**.
4. Con el visto bueno y el CI en verde, el autor integra en `trunk`, borra la
   rama y cierra la issue referenciando el commit.

### Plantilla de comentario de revisión

El revisor puede copiar y pegar este bloque como comentario en la issue:

```markdown
## Revisión de `<nombre-de-la-rama>`

- [x] Legibilidad y estilo (flake8, black, isort)
- [x] Pruebas incluidas, con markers correctos y casos límite
- [x] Código nuevo ejercitado (revisado con `rosemary coverage`)
- [x] CI en verde
- [x] Sin secretos
- [x] Commits con Conventional Commits y referencia a issue

**Resultado:** ✅ Aprobado / ❌ Cambios solicitados

**Comentarios:**
(detallar aquí)
```

---

## 2. Guía de diseño de pruebas

### Particiones de equivalencia

Dividir el dominio de entrada en **clases de equivalencia**: conjuntos de
valores que se espera que el sistema trate de la misma forma. Se elige un
representante de cada clase.

**Ejemplo — Validador de CSV de resultados:**

| Entrada          | Clase válida                | Clase inválida                        |
|------------------|-----------------------------|---------------------------------------|
| `goles_local`    | Entero ≥ 0 (p. ej. `0`, `3`) | Negativo (`-1`), no entero (`abc`)  |
| `fecha`          | Formato `AAAA-MM-DD` dentro de la temporada | Formato incorrecto (`15-08-2024`), fuera de temporada |
| `local` vs `visitante` | Equipos distintos (`Sevilla FC` ≠ `Real Betis`) | Mismo equipo (`Sevilla FC` = `Sevilla FC`) |
| `jornada`        | Equipo aparece una vez por jornada | Equipo aparece dos veces en la misma jornada |
| Partidos         | Sin duplicados              | Partidos duplicados                   |

### Valores límite

Probar en los **bordes** de cada partición, donde los defectos aparecen con más
frecuencia.

**Ejemplo — goles:**

| Valor | Esperado       | Por qué es un límite                  |
|-------|----------------|----------------------------------------|
| `-1`  | ❌ Rechazo     | Justo por debajo del mínimo válido     |
| `0`   | ✅ Aceptado    | Mínimo válido (empate a cero)          |
| `1`   | ✅ Aceptado    | Primer valor entero positivo           |

**Ejemplo — fecha de temporada (LaLiga 2024-25, temporada del 15/08/2024 al
30/06/2025):**

| Valor          | Esperado   | Por qué es un límite                      |
|----------------|------------|-------------------------------------------|
| `2024-08-14`   | ❌ Rechazo | Un día antes del inicio de temporada       |
| `2024-08-15`   | ✅ Aceptado | Primer día de la temporada                |
| `2025-06-30`   | ✅ Aceptado | Último día de la temporada                |
| `2025-07-01`   | ❌ Rechazo | Un día después del fin de la temporada    |

### Regla general

> Cada prueba verifica **un solo comportamiento**. Si necesitas probar varios
> valores para la misma regla, usa `@pytest.mark.parametrize`.

> Los ejemplos de código de esta guía son ilustrativos: `validar_fila` y
> `validar_csv` son nombres orientativos del validador del WI-newdataset, que
> aún no existe. Ajusta nombres y firmas al código real.

```python
@pytest.mark.unit
@pytest.mark.parametrize("goles", [-1, -100])
def test_rechaza_goles_negativos(goles):
    errores = validar_fila({"goles_local": goles, ...})
    assert any("negativo" in e.lower() for e in errores)

@pytest.mark.unit
@pytest.mark.parametrize("goles", [0, 1, 5])
def test_acepta_goles_validos(goles):
    errores = validar_fila({"goles_local": goles, ...})
    assert errores == []
```

---

## 3. Tipos de pruebas: cuándo usar cada una

El proyecto usa los markers de pytest definidos en `pyproject.toml`, que siguen
la pirámide de pruebas de splent_framework:

```
         ▲
        / \        e2e (Selenium)         → pocas, lentas, frágiles
       /   \       integration (HTTP)     → flujo completo sin navegador
      /     \      service (DB + lógica)  → orquestación de servicios
     /       \     repository (DB)        → acceso a datos aislado
    /  unit   \    unit (pura lógica)     → muchas, rápidas, estables
   /___________\
```

### `@pytest.mark.unit` — Pruebas unitarias

- **Qué prueban:** Lógica pura, sin Flask ni base de datos.
- **Cuándo usarlas:** Para cualquier función que reciba datos y devuelva un
  resultado sin efectos secundarios: validadores, cálculos, conversiones,
  formateo.
- **Ejemplo:** Validar que un CSV con goles negativos devuelve el error
  correcto.
- **Fixtures:** `tmp_path` (ficheros temporales), `SimpleNamespace` (stubs).
- **Velocidad:** Milisegundos.

```python
pytestmark = pytest.mark.unit

def test_rechaza_csv_con_equipo_contra_si_mismo():
    errores = validar_csv(csv_con_equipo_repetido)
    assert "juega contra sí mismo" in errores[0]
```

### `@pytest.mark.repository` — Pruebas de repositorio

- **Qué prueban:** Consultas y operaciones sobre la base de datos, aisladas
  del resto de la lógica.
- **Cuándo usarlas:** Para comprobar que un modelo se guarda, se consulta y se
  filtra correctamente.
- **Fixtures:** `test_app`, `clean_database`.

### `@pytest.mark.service` — Pruebas de servicio

- **Qué prueban:** La orquestación entre repositorios y lógica de negocio, con
  base de datos real.
- **Cuándo usarlas:** Para flujos que combinan varias operaciones: p. ej.,
  "subir un dataset, validarlo y guardarlo".
- **Fixtures:** `test_app`, `clean_database`.

### `@pytest.mark.integration` — Pruebas de integración

- **Qué prueban:** Endpoints HTTP completos con el test client de Flask.
- **Cuándo usarlas:** Para comprobar que una ruta devuelve el código de estado
  correcto, el contenido esperado o redirige adecuadamente.
- **Fixtures:** `test_client`.

```python
pytestmark = pytest.mark.integration

def test_upload_csv_invalido_devuelve_400(test_client):
    response = test_client.post("/dataset/upload", data={"file": csv_invalido})
    assert response.status_code == 400
```

### `@pytest.mark.e2e` — Pruebas end-to-end (Selenium)

- **Qué prueban:** Flujos completos en el navegador, contra la app y la base
  de datos de desarrollo.
- **Cuándo usarlas:** Para verificar la experiencia del usuario: formularios,
  navegación, mensajes de error en la interfaz.
- **Requisitos:** Docker levantado con
  `docker compose -f docker/docker-compose.dev.yml up`.
- **Ejecución:** `rosemary selenium` o `rosemary test dataset --e2e`.
- **Importante:** Se ejecutan en local antes de integrar, **no** en el CI de
  GitHub Actions.

### Resumen rápido

| Tipo          | Comando                            | ¿Necesita DB? | ¿Necesita Docker? | ¿Corre en CI? |
|---------------|------------------------------------|---------------|--------------------|----------------|
| unit          | `rosemary test --unit`             | No            | No                 | Sí*            |
| repository    | `rosemary test --repository`       | Sí            | Sí                 | Sí*            |
| service       | `rosemary test --service`          | Sí            | Sí                 | Sí*            |
| integration   | `rosemary test --integration`      | Sí            | Sí                 | Sí*            |
| e2e           | `rosemary test --e2e`              | Sí            | Sí (Selenium Grid) | No (local)     |

> \* **Nota sobre CI:** `CI_pytest.yml` corre actualmente en `main`. A partir de la issue #6
> se ejecutará automáticamente en todas las ramas de tarea y `trunk`. Hasta entonces,
> verificar el paso de pruebas en local con `rosemary test`.

> **Por defecto** `rosemary test` ejecuta unit + repository + service +
> integration (todo menos e2e y load).

Para ejecutar solo los tests de una feature:

```bash
rosemary test dataset          # unit + repo + service + integration de dataset
rosemary test dataset --unit   # solo unitarios de dataset
```

---

## 4. Cobertura de código

### Cómo ejecutarla

```bash
# Cobertura de todas las features (unit + repo + service + integration)
rosemary coverage

# Cobertura solo de una feature
rosemary coverage dataset

# Cobertura con informe HTML navegable
rosemary coverage --html
# Abrir htmlcov/index.html en el navegador

# Cobertura solo de tests unitarios
rosemary coverage --unit
```

### Cómo interpretarla en la revisión

La cobertura **no es un objetivo numérico** (no pedimos "90 %"), sino una
herramienta de apoyo para la revisión:

1. **Mira las líneas no cubiertas** (`MISS` en el informe): ¿son caminos de
   error que deberían estar probados?
2. **Comprueba que el código nuevo está ejercitado**: si añades un validador de
   goles negativos, debe haber al menos un test que pase por esa rama.
3. **No cubras código trivial por cubrir**: getters, `__repr__`, imports y
   configuración no necesitan tests propios.

### Ejemplo de lectura del informe

```
Name                                          Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
app/features/dataset/services.py                 42      3    93%   67-69
```

→ Las líneas 67-69 de `services.py` no están cubiertas. Revisa si son un
camino de error importante que debería tener prueba.

---

## 5. Estructura de ficheros de pruebas

Cada feature tiene sus tests en `app/features/<feature>/tests/`:

```
app/features/dataset/tests/
├── __init__.py
├── test_unit.py           # @pytest.mark.unit
├── test_repository.py     # @pytest.mark.repository
├── test_service.py        # @pytest.mark.service
├── test_integration.py    # @pytest.mark.integration
├── test_selenium.py       # @pytest.mark.e2e
└── locustfile.py          # @pytest.mark.load (via rosemary locust)
```

- Cada fichero agrupa un tipo de test.
- El `pytestmark` global al inicio del fichero marca todos los tests del
  fichero.
- Los fixtures compartidos van en `conftest.py` dentro de la carpeta de tests.

---

## 6. Flujo de trabajo resumido

```
1. Crear issue con plantilla; pasarla a "En progreso"
2. Crear rama desde trunk:  git switch --no-track -c 17-validador-csv origin/trunk   (sección 7)
3. Escribir código + tests  (seguir esta guía)
4. rosemary linter          → corregir estilo
5. rosemary test            → pasar pruebas (unit + repo + service + integration)
6. rosemary coverage        → comprobar que el código nuevo está ejercitado
7. git add + git commit     → Conventional Commits referenciando la issue (sección 8)
8. git push origin 17-validador-csv
9. Pasar issue a "En revisión" y añadir al revisor como asignado (sección 9)
10. Revisor: aplicar la checklist (sección 1) y dejar constancia en la issue
11. Con visto bueno: integrar en trunk, borrar la rama y cerrar la issue (sección 10)
```

> ⚠️ **Nunca se integra en trunk con el CI en rojo.** Si trunk se rompe,
> arreglarlo es la prioridad del equipo.

---

## 7. Ramas (EGCFlow)

El equipo sigue EGCFlow: ramas de tarea cortas que se integran a menudo en
`trunk`, y estados estables de `trunk` que se llevan a `main` y se etiquetan.

| Rama | Propósito | Vida | Reglas |
|------|-----------|------|--------|
| `main` | Línea de entregas. Cada estado entregado lleva una etiqueta. | Permanente | Solo recibe estados estables de `trunk` (sección 12). Nadie trabaja ni hace commits directamente en ella. Cada push despliega en Render. |
| `trunk` | Línea de integración del equipo. | Permanente | Siempre construye y pasa las pruebas básicas, para que cualquiera pueda partir de ella. Solo recibe merges de ramas de tarea revisadas. |
| Rama de tarea (`17-validador-csv`) | Una funcionalidad, corrección, refactorización o mejora de documentación concreta. | Hasta que la tarea termina | Se crea desde `trunk`, se integra en `trunk` y se borra. |

### Nombre de la rama

- Una rama por issue, **nunca ramas por persona**.
- Formato: `<nº issue>-<descripción-corta>`, en minúsculas y con guiones:
  `17-validador-csv`, `4-contributing-egcflow`.
- Usa **exactamente** el nombre que indica la tabla *Seguimiento* de la issue.

### Crear la rama

```bash
git fetch origin
git switch --no-track -c 17-validador-csv origin/trunk
git push -u origin 17-validador-csv
```

> `--no-track` evita que la rama quede siguiendo a `origin/trunk`; así un
> `git push` sin argumentos nunca sube por error a `trunk`. El
> `push -u` posterior la deja siguiendo a su propia rama remota.

Al crearla, pasa la issue a **En progreso** en el tablero.

### Mantener la rama cerca de trunk

Mientras la rama está viva, trae los cambios de `trunk` **al menos al empezar
cada sesión de trabajo**. Así los conflictos aparecen pronto y son pequeños:

```bash
git fetch origin
git merge origin/trunk        # o rebase si nadie más usa la rama (sección 11)
```

---

## 8. Commits

### Formato

Se usa [Conventional Commits](https://www.conventionalcommits.org/es/) y cada
commit **termina con la referencia a la issue**:

```
<tipo>(<ámbito opcional>): <qué cambia, en imperativo> (#<nº issue>)

<cuerpo opcional: por qué se hace el cambio>
```

| Tipo | Cuándo |
|------|--------|
| `feat` | Funcionalidad nueva |
| `fix` | Corrección de un error |
| `test` | Añadir o corregir pruebas |
| `docs` | Solo documentación |
| `refactor` | Cambio interno sin cambiar el comportamiento |
| `ci` | Workflows de GitHub Actions y configuración del CI |
| `chore` | Mantenimiento: integraciones, dependencias, scripts |

Ejemplos:

```
feat(dataset): validar goles negativos en el CSV (#17)
test(dataset): valores límite de la fecha de temporada (#17)
docs: documentar EGCFlow en CONTRIBUTING (#4)
chore: integrar 17-validador-csv en trunk (#17)
```

### Reglas

- **Commits atómicos:** un cambio lógico y completo por commit, aunque toque
  varios ficheros. No mezcles en un commit una funcionalidad y un formateo.
- El mensaje explica **qué** cambia y, si no es evidente, **por qué**.
- Para corregir el último commit **antes de subirlo**, usa
  `git commit --amend`; no hagas commits del tipo "se me olvidó la prueba".
  Un commit ya subido a una rama que otros usan no se reescribe.
- **Nunca se suben secretos** (tokens, contraseñas, ficheros `.env`); el
  `.gitignore` está versionado.
- Los commits de merge siguen el mismo formato (ver sección 10).
- El workflow `CI_commits.yml` valida el formato Conventional Commits en cada
  push. La referencia `(#n)` la comprueba el revisor.

---

## 9. Revisión en la issue y en el tablero

No hay pull requests dentro del equipo: la revisión queda registrada **en la
issue**. Los estados del tablero son *Pendiente → En progreso → En revisión →
Hecho* (y *Bloqueada*, con el motivo en la issue).

### Autor: pedir la revisión

1. Sube la rama con todo el trabajo y comprueba que el CI está en verde.
2. Pasa la issue a **En revisión**.
3. **Añade al revisor como asignado** de la issue (el revisor sugerido está en
   la tabla *Seguimiento*):
   ```bash
   gh issue edit 17 --add-assignee <usuario-revisor>
   ```
   Así le aparece en la vista **Mis revisiones** del tablero, que filtra
   `status:"En revisión" assignee:@me`.

### Revisor: revisar en 48 h

1. Abre la vista **Mis revisiones** para ver lo que tienes pendiente.
2. Examina el diff de la rama frente a `trunk`, con la comparación de ramas de
   GitHub (`https://github.com/jjuanx/FutbolHub/compare/trunk...<rama>`) o en
   local:
   ```bash
   git fetch origin
   git diff origin/trunk...origin/17-validador-csv
   ```
   (Los tres puntos muestran solo lo que aporta la rama desde que salió de
   `trunk`.)
3. Aplica la checklist de la sección 1 y deja el resultado como comentario en
   la issue, con la plantilla de revisión.
4. Si pides cambios, el autor los hace en la misma rama, los sube y lo indica
   en la issue; el revisor vuelve a revisar.

### Tras el visto bueno

1. Se **quita al revisor** de los asignados, para que deje de salirle en
   *Mis revisiones*:
   ```bash
   gh issue edit 17 --remove-assignee <usuario-revisor>
   ```
2. El responsable integra la rama en `trunk` (sección 10).

---

## 10. Integración en trunk sin pull requests

La integración la hace el **responsable de la issue**, con Git directamente,
cuando tiene el visto bueno registrado en la issue y el CI de la rama en verde.

### Lista de comprobación de integración

- [ ] La issue tiene el visto bueno del revisor y se le ha quitado de asignado.
- [ ] El CI de la rama está en verde.
- [ ] Rama actualizada con `trunk` y conflictos resueltos **en la rama**:
      ```bash
      git fetch origin
      git switch 17-validador-csv
      git merge origin/trunk
      ```
- [ ] Lint y pruebas pasan en local tras traer `trunk`:
      ```bash
      rosemary linter
      black --check app rosemary
      isort --check-only app rosemary
      rosemary test
      ```
- [ ] Si el merge trajo cambios, se sube la rama y se espera el CI en verde:
      `git push origin 17-validador-csv`.
- [ ] Merge en `trunk`, sin fast-forward para que quede constancia de la
      integración:
      ```bash
      git switch trunk                  # la primera vez: git switch -c trunk origin/trunk
      git pull --ff-only origin trunk
      git merge --no-ff 17-validador-csv -m "chore: integrar 17-validador-csv en trunk (#17)"
      ```
- [ ] Pruebas en `trunk` tras el merge: `rosemary test`.
- [ ] Subida: `git push origin trunk`. Si se rechaza porque otro ha integrado
      antes, `git pull --no-rebase origin trunk`, vuelve a pasar las pruebas y
      repite el push. **Nunca** `--force` en `trunk`.
- [ ] El CI de `trunk` está en verde. Si no, arreglarlo es la prioridad.
- [ ] Rama borrada en remoto y en local:
      ```bash
      git push origin --delete 17-validador-csv
      git branch -d 17-validador-csv
      ```
- [ ] Issue cerrada **referenciando el commit de integración**, y en *Hecho*
      en el tablero:
      ```bash
      gh issue close 17 --comment "Integrada en trunk en <sha del merge>."
      ```

---

## 11. Rebase y ramas de larga duración

### Cuándo se puede usar rebase

- `rebase` **solo** sobre ramas que nadie más ha tomado como base (tu rama de
  tarea, mientras solo trabajas tú en ella).
- Una rama **compartida** (otro trabaja en ella o ha creado una rama a partir de
  ella) se actualiza **siempre con merge**.
- `trunk` y `main` **nunca** se rebasan ni se suben con `--force`.
- Si haces rebase de tu rama ya subida, súbela con
  `git push --force-with-lease origin <rama>`, que falla si alguien ha subido
  algo que no tienes en local.

```bash
git fetch origin
git rebase origin/trunk                       # solo en tu rama no compartida
git push --force-with-lease origin 17-validador-csv
```

### Ramas de más de una semana

- Una rama que lleve **más de una semana sin integrarse** en `trunk` debe
  justificarse con un comentario en su issue: por qué sigue abierta y qué falta.
  Si no puede avanzar, la issue pasa a **Bloqueada** con el motivo.
- Si la tarea es demasiado grande, se divide en issues de uno a tres días y se
  integra lo que ya esté terminado.
- El responsable de gestión de la configuración repasa las ramas vivas en la
  reunión semanal. Para verlas ordenadas por fecha del último commit:
  ```bash
  git fetch --prune origin
  git for-each-ref --sort=committerdate refs/remotes/origin \
    --format='%(committerdate:short) %(refname:short)'
  ```

---

## 12. Entregas a main

- `main` solo recibe estados de `trunk` con el CI en verde, en cada entrega
  (hitos 0.1.0, 0.2.0 y 1.0.0).
- Cada entrega se lleva a `main` con un merge desde `trunk`, se etiqueta con
  versionado semántico (`X.Y.Z`) y se publica una release con la nota de
  cambios.
- Antes de cada entrega se comprueba que `trunk` contiene todo lo que hay en
  `main` (`git log origin/trunk..origin/main` no debe mostrar commits); si no,
  se trae `main` a `trunk` con un merge.
- El procedimiento de cada entrega se sigue en su issue (#11, #12 y #13).
