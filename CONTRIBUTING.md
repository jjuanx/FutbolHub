# Guía de contribución — FutbolHub

Esta guía recoge los criterios de revisión de código y de diseño de pruebas del
equipo. Todos los miembros la aplican al escribir y revisar código.

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
1. Crear issue con plantilla
2. Crear rama desde trunk:  git checkout -b 17-validador-csv trunk
3. Escribir código + tests  (seguir esta guía)
4. rosemary linter          → corregir estilo
5. rosemary test            → pasar pruebas (unit + repo + service + integration)
6. rosemary coverage        → comprobar que el código nuevo está ejercitado
7. git add + git commit     → Conventional Commits referenciando la issue
8. git push origin 17-validador-csv
9. Pasar issue a "En revisión" y asignar revisor
10. Revisor: aplicar la checklist (sección 1) y dejar constancia en la issue
11. Con visto bueno: integrar en trunk y borrar la rama
```

> ⚠️ **Nunca se integra en trunk con el CI en rojo.** Si trunk se rompe,
> arreglarlo es la prioridad del equipo.
