# Guía de Búsqueda Avanzada y Filtros en la URL — FutbolHub

Esta página documenta los filtros disponibles en el módulo **Explore** (`/explore`), tanto los filtros propios del dominio de fútbol (**WI-newdataset**, issue `#21`) como los de búsqueda avanzada (**WI `#194`**, issues `#40`, `#41` y `#42`).

Todos los filtros activos se reflejan automáticamente en la **query string de la URL** (`window.history.replaceState`) y se restauran al abrir el enlace, permitiendo compartir cualquier búsqueda mediante una URL directa.

---

## 1. Catálogo de parámetros de filtrado

| Parámetro URL / JSON | Tipo | Descripción | Ejemplo |
|----------------------|------|-------------|---------|
| `query` | `string` | Texto libre: busca en título, descripción, autores, etiquetas y nombres de ficheros (insensible a mayúsculas y tildes). | `query=laliga` |
| `publication_type` | `string` | Tipo de publicación (`any`, `none`, `article`, `book`, `datamanagementplan`, etc.). | `publication_type=article` |
| `sorting` | `string` | Ordenación por fecha de creación: `newest` (por defecto) u `oldest`. | `sorting=oldest` |
| `tags` | `string` / `list` | Una o varias etiquetas separadas por comas (coincidencia con cualquiera de las etiquetas indicadas). | `tags=primera,espana` |
| `author` | `string` | Filtra por autor buscando en su **nombre**, **afiliación** u **ORCID** (insensible a mayúsculas y tildes). | `author=Universidad+de+Sevilla` |
| `date_from` | `AAAA-MM-DD` | Fecha mínima de publicación del dataset (inclusive, desde las `00:00:00` de ese día). | `date_from=2024-08-15` |
| `date_to` | `AAAA-MM-DD` | Fecha máxima de publicación del dataset (inclusive, hasta las `23:59:59` de ese día). | `date_to=2025-06-30` |
| `competition` | `string` | Competición de fútbol a la que pertenece el dataset. | `competition=LaLiga` |
| `season` | `string` | Temporada declarada del dataset (`AAAA-AA`, `AAAA-AAAA` o `AAAA`). | `season=2024-25` |
| `country` | `string` | País de la competición (insensible a tildes: `España` o `Espana`). | `country=España` |
| `team` | `string` | Equipo participante (el dataset coincide si el equipo disputa al menos un partido en sus CSVs o figura en sus equipos). | `team=Sevilla+FC` |
| `min_matches` | `int` | Número mínimo de partidos del dataset (inclusive). | `min_matches=300` |
| `max_matches` | `int` | Número máximo de partidos del dataset (inclusive). | `max_matches=380` |
| `min_teams` | `int` | Número mínimo de equipos del dataset (inclusive). | `min_teams=18` |
| `max_teams` | `int` | Número máximo de equipos del dataset (inclusive). | `max_teams=20` |

---

## 2. Cómo compartir búsquedas por URL

Al modificar cualquier campo del formulario de `/explore`, la barra de direcciones del navegador se actualiza dinámicamente con los filtros activos (omitiendo los valores por defecto vacíos, `publication_type=any` o `sorting=newest`).

### Ejemplos de enlaces compartibles

1. **Temporadas de LaLiga 2024-25 en España donde juegue el Sevilla FC:**
   ```text
   /explore?competition=LaLiga&season=2024-25&country=Espa%C3%B1a&team=Sevilla+FC
   ```

2. **Búsqueda por autor (afiliación u ORCID) y rango de fechas de publicación:**
   ```text
   /explore?author=Universidad+de+Sevilla&date_from=2024-01-01&date_to=2024-12-31
   ```

3. **Filtro combinado por varias etiquetas y métricas del dataset (entre 18 y 20 equipos, al menos 300 partidos):**
   ```text
   /explore?tags=laliga,premier&min_matches=300&min_teams=18&max_teams=20&sorting=oldest
   ```

4. **Consulta directa en formato JSON mediante query string:**
   Añadiendo `format=json` (o la cabecera HTTP `Accept: application/json`), el endpoint `GET /explore` devuelve directamente la lista JSON de datasets que cumplen los filtros de la URL:
   ```text
   GET /explore?competition=LaLiga&team=Sevilla+FC&format=json
   ```
