# Primer reparto de tareas de FutbolHub (acta fundacional v2 + WIs de EGCETSII/uvlhub)

JUAN, NICO, ALE, JUANMA, MANU, ROBER = "jjuanx", "Nicopm0905", "alepm03", "Juanitomsp", "Madunguin", "RobertoRoloG"

LABELS = [
    # tipo (acta, sección 7)
    ("tipo: feature", "Nueva funcionalidad", "1d76db"),
    ("tipo: bug", "Incidencia: algo no funciona", "d73a4a"),
    ("tipo: refactor", "Reestructuración sin cambio de comportamiento", "5319e7"),
    ("tipo: docs", "Documentación, diario, actas, README", "0075ca"),
    ("tipo: ci", "Workflows, entornos, despliegue y configuración del repo", "fbca04"),
    # prioridad
    ("prioridad: alta", "Bloquea a otros o entra en el próximo seguimiento", "b60205"),
    ("prioridad: media", "", "d93f0b"),
    ("prioridad: baja", "", "c5def5"),
    # WI de origen
    ("WI: newdataset", "WI-newdataset (#178 uvlhub) — común, coordina Juan", "0e8a16"),
    ("WI: fakenodo", "WI-fakenodo (#177 uvlhub) — común, Manuel", "0e8a16"),
    ("WI: 182 GitHub/ZIP", "#182 uvlhub — Subir desde GitHub / ZIP (H) — Nicolás", "006b75"),
    ("WI: 196 versionado mayor", "#196 uvlhub — Versionado mayor (H) — Alejandro", "006b75"),
    ("WI: 195 versionado menor", "#195 uvlhub — Versionado menor (M) — Juan María", "006b75"),
    ("WI: 194 búsqueda avanzada", "#194 uvlhub — Búsqueda avanzada (M) — Roberto", "006b75"),
    ("WI: 214 contador descargas", "#214 uvlhub — Contador de descargas (L) — Juan", "006b75"),
    ("WI: 211 tendencias", "#211 uvlhub — Datasets en tendencia (L) — Manuel", "006b75"),
    ("WI: organización", "Gestión del equipo, entregas, CI/CD: no pertenece a un WI", "bfdadc"),
]

MILESTONES = [
    ("0.1.0 — Seguimiento 23 nov", "2026-11-23", "Gestión del código e incidencias: tablero, plantillas, EGCFlow, diario y CI en todas las ramas. Primera entrega etiquetada en main."),
    ("0.2.0 — Seguimiento 30 nov", "2026-11-30", "Pruebas y CI/CD: CD a Render, fakenodo, núcleo del dominio (modelo, validador CSV, subida, clasificación) con sus pruebas."),
    ("1.0.0 — Defensa 14/16 dic", "2026-12-14", "Todos los WIs terminados, desplegados y trazados. Entrega 1.0.0."),
]
M1, M2, M3 = (m[0] for m in MILESTONES)

# Cada issue: key, title, assignee, type, prio, wi, milestone, days, reviewer, deps(keys), slug, desc, tasks, criteria
I = []


def add(key, title, who, typ, prio, wi, ms, days, rev, deps, slug, desc, tasks, crit):
    I.append(dict(key=key, title=title, who=who, typ=typ, prio=prio, wi=wi, ms=ms, days=days,
                  rev=rev, deps=deps, slug=slug, desc=desc, tasks=tasks, crit=crit))


# ───────────────────────── Organización (0.1.0) ─────────────────────────
add("board", "Configurar tablero Kanban, etiquetas, hitos y primer reparto de issues", JUAN, "docs", "alta", "organización", M1, 1, JUANMA, [], "tablero-kanban",
    "Montar el seguimiento del proyecto en GitHub según la sección 7 del acta: issues desglosadas por WI, etiquetas de tipo/prioridad/WI y tablero con los estados acordados.",
    ["Activar issues en el repositorio", "Crear etiquetas `tipo:`, `prioridad:` y `WI:`", "Crear hitos 0.1.0 (23 nov), 0.2.0 (30 nov) y 1.0.0 (defensa)",
     "Crear las issues del primer reparto con responsable, estimación y dependencias",
     "Crear el GitHub Project con estados Pendiente / En progreso / En revisión / Bloqueada / Hecho y vista de tablero",
     "Activar los workflows del Project: item añadido → Pendiente, issue cerrada → Hecho",
     "Registrar el reparto en el diario"],
    ["Todas las issues del reparto están en el tablero con responsable e hito", "El tablero se repasa en la siguiente reunión semanal"])

add("templates", "Plantillas de issues: funcionalidad, incidencia y tarea (docs/CI/refactor)", JUANMA, "docs", "alta", "organización", M1, 1, JUAN, [], "plantillas-issues",
    "Crear las plantillas de `.github/ISSUE_TEMPLATE/` que pide el acta (sección 7), de forma que todo el trabajo empiece por una issue con la información necesaria.",
    ["Plantilla de **incidencia**: resumen, contexto, pasos para reproducir, resultado esperado, resultado observado, entorno e información adicional (trazas, capturas, CSV de ejemplo)",
     "Plantilla de **funcionalidad**: historia de usuario, tareas, criterios de aceptación, WI de origen",
     "Plantilla de **tarea** (docs / ci / refactor)", "Que cada plantilla aplique por defecto su etiqueta `tipo:`",
     "`config.yml` desactivando issues en blanco", "Documentar las etiquetas y su uso en la wiki"],
    ["Al pulsar *New issue* aparecen las tres plantillas", "Cada plantilla deja la etiqueta de tipo correcta"])

add("wiki", "Activar la wiki y crear el diario del equipo con la plantilla de acta de reunión", ROBER, "docs", "alta", "organización", M1, 1, JUAN, [], "diario-equipo",
    "El acta establece la wiki del repositorio como diario del equipo (actas de reunión y decisiones justificadas). Ahora mismo la wiki está desactivada.",
    ["Activar la wiki en *Settings → Features*", "Página de inicio del diario con índice de reuniones y de decisiones",
     "Plantilla de acta: asistentes, temas, acuerdos, tareas con responsable", "Subir el acta fundacional (enlace o PDF) y el acta de la reunión del 9 nov",
     "Registrar las decisiones ya tomadas: reparto de WIs, roles, Render como plataforma de despliegue",
     "Página de *Incumplimientos* (sección 6 del acta), vacía"],
    ["La wiki está activa y enlazada desde el README", "Hay al menos un acta de reunión con el formato acordado"])

add("egcflow", "Documentar EGCFlow del equipo en CONTRIBUTING.md (ramas, commits, revisión sin PR, integración)", ALE, "docs", "alta", "organización", M1, 1, NICO, [], "contributing-egcflow",
    "Recoger en el repositorio la política de ramas y commits de la sección 5 del acta para que cualquiera la consulte al trabajar.",
    ["Ramas: `main` (entregas), `trunk` (integración), ramas de tarea `<nº issue>-<descripción>` creadas desde trunk",
     "Commits: Conventional Commits (`feat`, `fix`, `test`, `docs`, `refactor`, `ci`, `chore`) y referencia a la issue: `feat: validar goles negativos (#12)`",
     "Procedimiento de integración sin PR: traer trunk, merge, pruebas, push, borrar la rama",
     "Revisión: pasar la issue a *En revisión*, revisor en 48 h con `git diff trunk...rama`, visto bueno en la issue",
     "Reglas de rebase (solo en ramas no compartidas) y de ramas de más de una semana",
     "Comprobar que `trunk` está al día con `main`"],
    ["CONTRIBUTING.md está en trunk y enlazado desde el README", "Incluye una lista de comprobación de integración paso a paso"])

add("qa-criteria", "Criterios de revisión de código y de diseño de pruebas", NICO, "docs", "alta", "organización", M1, 1, ALE, [], "criterios-calidad",
    "Como responsable de calidad, definir qué se mira en cada revisión y cómo se diseñan las pruebas (acta, sección 7).",
    ["Checklist de revisión: legibilidad, pruebas incluidas, CI en verde, sin secretos, commit referenciando la issue",
     "Guía de diseño de pruebas: particiones de equivalencia y valores límite con ejemplos del dominio (goles 0 y −1, jornadas repetidas)",
     "Cuándo usar pruebas unitarias, de integración y de interfaz (Selenium)", "Cómo ver la cobertura (`rosemary coverage`) y cómo usarla en la revisión",
     "Publicarlo en la wiki o en CONTRIBUTING.md"],
    ["La checklist se puede pegar como comentario de revisión en una issue"])

# ───────────────────────── CI / CD ─────────────────────────
add("ci-branches", "CI: ejecutar las pruebas en ramas de tarea, trunk y main (sin depender de PR)", MANU, "ci", "alta", "organización", M1, 1, ALE, [], "ci-todas-las-ramas",
    "`CI_pytest.yml` solo se ejecuta en push a `main` y en PR. Como el equipo no usa PR e integra en trunk, hay que ejecutarlo en todas las ramas (acta, sección 8).",
    ["Cambiar el disparador de `CI_pytest.yml` a push en cualquier rama", "Comprobar que usa Ubuntu 24.04, Python 3.13 y MariaDB 12",
     "Verificar que `CI_commits.yml` y `CI_lint.yml` pasan en verde en trunk", "Añadir las insignias de los workflows al README"],
    ["Un push a una rama de tarea lanza commits, lint y pytest", "Los tres workflows están en verde en trunk"])

add("ci-disable-cd", "Desactivar CD_webhook.yml y CD_dockerhub.yml y registrar la decisión", MANU, "ci", "media", "organización", M1, 1, ALE, [], "desactivar-cd-fork",
    "Los workflows de despliegue del fork están pensados para un servidor propio y Docker Hub. El equipo despliega en Render (acta, sección 8).",
    ["Desactivar o eliminar `CD_webhook.yml` y `CD_dockerhub.yml`", "Revisar si la feature `webhook` en `features_prod` debe seguir activa",
     "Registrar la decisión y su motivo en el diario"],
    ["No se ejecuta ningún workflow de despliegue del fork", "La decisión consta en el diario"])

add("render-setup", "Crear el servicio en Render con Dockerfile.render y la base de datos MariaDB en filess.io", MANU, "ci", "alta", "organización", M2, 2, ALE, ["ci-branches"], "render-setup",
    "Preparar el entorno de producción: servicio web en Render construido con `docker/images/Dockerfile.render` y base de datos MariaDB externa.",
    ["Crear la base de datos en filess.io", "Crear el servicio en Render apuntando a `main` y a `Dockerfile.render`",
     "Configurar variables y secretos en el panel de Render (nunca en el repo)", "Comprobar que las migraciones se aplican al arrancar",
     "Desactivar el *auto-deploy* de Render", "Documentar la URL pública en el README"],
    ["La versión de main está accesible en la URL pública", "Ningún secreto está en el repositorio"])

add("cd-render", "Crear CD_render.yml: desplegar en Render solo cuando el CI de main está en verde", MANU, "ci", "alta", "organización", M2, 2, ALE, ["render-setup"], "cd-render",
    "Despliegue continuo según el acta (sección 8): el push a main lanza el CI completo y, solo si termina en verde, se llama al deploy hook de Render.",
    ["Workflow `CD_render.yml` disparado con `workflow_run` tras los tres workflows de CI en main",
     "Secreto `RENDER_DEPLOY_HOOK_URL` en el repositorio", "Tras desplegar, comprobar que la aplicación responde (health check con reintentos)",
     "Si el despliegue falla, abrir automáticamente una issue `tipo: bug` + `prioridad: alta`"],
    ["Un push a main con CI en rojo no despliega", "Un push a main con CI en verde despliega y el health check pasa"])

add("env-check", "Verificar Docker, devcontainer y Vagrant antes de cada entrega", MANU, "ci", "media", "organización", M3, 1, NICO, ["nd-model"], "verificar-entornos",
    "El acta exige que los entornos aislados funcionen igual para todos y que Manuel compruebe Vagrant antes de cada entrega.",
    ["Arrancar `docker-compose.dev.yml` desde cero (app, MariaDB, nginx, Selenium Grid)", "Comprobar el devcontainer en VS Code",
     "Aprovisionar Vagrant desde cero", "Actualizar los `.env.*.example` con las variables nuevas (fakenodo, etc.)",
     "Renombrar el proyecto Compose y las BD de `uvlhub` a `futbolhub` si procede", "Anotar el resultado en el diario en cada entrega"],
    ["Los tres entornos arrancan desde cero y pasan las pruebas"])

# ───────────────────────── Entregas ─────────────────────────
add("rel-010", "Entrega 0.1.0: llevar trunk a main, etiquetar y publicar la release", ALE, "ci", "alta", "organización", M1, 1, JUAN, ["ci-branches", "egcflow"], "entrega-0-1-0",
    "Primera entrega etiquetada con versionado semántico para el seguimiento del 23 de noviembre (acta, sección 5).",
    ["Comprobar que trunk está en verde", "Integrar trunk en main", "Etiqueta `0.1.0` y release en GitHub con la nota de cambios (issues incluidas)",
     "Registrar la entrega en el diario"],
    ["La release 0.1.0 enumera las issues que incluye"])

add("rel-020", "Entrega 0.2.0: llevar trunk a main, etiquetar y publicar la release", ALE, "ci", "alta", "organización", M2, 1, JUAN, ["cd-render", "rel-010"], "entrega-0-2-0",
    "Segunda entrega para el seguimiento del 30 de noviembre (pruebas y CI/CD). Debe desplegarse en Render mediante el CD.",
    ["Comprobar que trunk está en verde", "Integrar trunk en main y verificar el despliegue en Render",
     "Etiqueta `0.2.0` y release en GitHub con la nota de cambios", "Automatizar la creación de la release al empujar una etiqueta (opcional)"],
    ["0.2.0 está desplegada en Render y su release enumera las issues"])

add("rel-100", "Entrega 1.0.0 para la defensa", ALE, "ci", "alta", "organización", M3, 1, JUAN, ["rel-020"], "entrega-1-0-0",
    "Entrega final con todos los WIs integrados y desplegados.",
    ["Congelar trunk", "Integrar en main, etiqueta `1.0.0` y release", "Verificar el despliegue en Render"],
    ["1.0.0 está desplegada y su release enumera todos los WIs"])

add("defensa", "Preparar la defensa: guion, demo y reparto de quién explica qué", JUAN, "docs", "alta", "organización", M3, 2, ROBER, [], "preparar-defensa",
    "La nota es individual y la defensa puede incluir preguntas individuales: cada miembro debe explicar su WI y el proceso del equipo.",
    ["Guion de la demo sobre la versión de Render", "Diapositivas sobre trazabilidad: issue → rama → commit → CI → entrega → despliegue",
     "Reparto del tiempo por miembro", "Ensayo con todo el equipo la semana anterior"],
    ["Ensayo completo hecho y registrado en el diario"])

# ───────────────────────── WI-newdataset ─────────────────────────
add("nd-proposal", "Cerrar la propuesta de dominio con el tutor y las decisiones abiertas", JUAN, "docs", "alta", "newdataset", M1, 1, ROBER, [], "propuesta-dominio",
    "El acta deja temas *a decidir* y el WI #178 tiene requisitos que hay que confirmar con el tutor antes de tocar el modelo.",
    ["Decidir: un CSV por temporada o un CSV por jornada", "Confirmar con el tutor si UVL debe seguir funcionando como tipo (el WI #178 lo pide; el acta dice que se sustituye)",
     "Confirmar la dificultad de #195 (en uvlhub figura como *high*; en el acta como M)", "Registrar las decisiones y su motivo en el diario"],
    ["Las decisiones constan en el diario y en esta issue"])

add("nd-model", "Modelo de datos: BaseDataset común y dataset de fútbol con sus metadatos + migración", JUAN, "refactor", "alta", "newdataset", M2, 3, ALE, ["nd-proposal"], "modelo-dataset-futbol",
    "Separar lo común de lo específico de UVL (WI #178): `FeatureModel`, `FMMetaData.uvl_*`, `DSMetrics.number_of_features`, etc. Añadir los metadatos de fútbol del acta.",
    ["Crear la feature con `rosemary feature:create` y registrarla en `[tool.splent]` de `pyproject.toml`",
     "Base común (`BaseDataset`) y modelo de fútbol con competición, país, temporada, número de equipos y fuente de los datos",
     "Modelo de fichero de resultados (sustituye a `FeatureModel` / `FMMetaData` en el tipo fútbol)",
     "Métricas del tipo fútbol (nº de partidos, nº de equipos) en lugar de `number_of_features`",
     "Nueva migración sobre `001`", "Mantener UVL o retirarlo según lo decidido en la propuesta"],
    ["La migración se aplica desde cero y las pruebas existentes pasan", "Pruebas unitarias del modelo nuevo"])

add("nd-validator", "Validador de CSV de resultados con fila y motivo del error", NICO, "feature", "alta", "newdataset", M2, 3, JUAN, ["nd-proposal"], "validador-csv",
    "Sustituye la validación de flamapy para el tipo fútbol. Es la base de la subida y de #182 (ZIP/GitHub). Formato del acta: `jornada,fecha,local,visitante,goles_local,goles_visitante`, UTF-8 con cabecera.",
    ["Rechazar si faltan columnas, hay celdas vacías o tipos incorrectos (jornada y goles enteros, fecha AAAA-MM-DD)",
     "Rechazar goles negativos", "Rechazar si un equipo juega contra sí mismo o dos veces en la misma jornada",
     "Rechazar partidos duplicados", "Rechazar fechas fuera de la temporada declarada",
     "Devolver todos los errores con número de fila y motivo", "Ficheros CSV de ejemplo válidos e inválidos en los tests"],
    ["Pruebas con particiones equivalentes y valores límite para cada regla (goles 0 y −1, jornada repetida, fecha límite de temporada)"])

add("nd-upload", "Subida de datasets CSV: Dropzone, validación y formulario con metadatos de fútbol", JUANMA, "feature", "alta", "newdataset", M2, 3, NICO, ["nd-model", "nd-validator"], "subida-csv",
    "Adaptar el flujo de subida (`upload_dataset.html`, `/dataset/file/upload`, `save_temp_uvl`) a ficheros CSV de resultados.",
    ["Dropzone con `acceptedFiles: '.csv'`", "Sustituir `save_temp_uvl` por un guardado que valide con el validador y muestre fila y motivo de los errores",
     "Formulario con los metadatos de fútbol (competición, país, temporada, nº de equipos, fuente)", "Calcular las métricas del dataset al crearlo"],
    ["Un CSV válido crea el dataset; uno inválido se rechaza mostrando los errores", "Pruebas de integración y una prueba Selenium del flujo"])

add("nd-standings", "Clasificación automática y estadísticas por equipo", ROBER, "feature", "alta", "newdataset", M2, 2, JUANMA, ["nd-model"], "clasificacion",
    "Calcular a partir de los partidos la clasificación y las estadísticas por equipo que describe el acta.",
    ["Servicio de clasificación: 3 puntos por victoria, 1 por empate, desempate por diferencia de goles y después por goles a favor",
     "Estadísticas por equipo: jugados, ganados, empatados, perdidos, goles a favor y en contra",
     "Funciona con uno o varios ficheros por dataset"],
    ["Pruebas unitarias con empates a puntos que se deshacen por DG y por GF, y con temporada sin partidos"])

add("nd-view", "Página del dataset: bloques comunes y bloque de fútbol (clasificación, estadísticas, partidos)", ALE, "feature", "media", "newdataset", M3, 2, ROBER, ["nd-standings"], "vista-dataset",
    "Construir `view_dataset.html` de forma extensible (WI #178): bloques comunes (título, autores, DOI, etiquetas, descargas) y bloque propio del tipo fútbol.",
    ["Bloque de metadatos de fútbol", "Tabla de clasificación y estadísticas por equipo", "Vista previa de los partidos por jornada",
     "Retirar el árbol UVL del tipo fútbol"],
    ["Prueba Selenium que abre un dataset de ejemplo y ve la clasificación"])

add("nd-explore", "Explore: filtros por competición, temporada, país y equipo", ROBER, "feature", "alta", "newdataset", M3, 2, NICO, ["nd-model"], "explore-filtros-dominio",
    "Filtros propios del dominio en Explore (acta, sección 2). Son la base sobre la que #194 añade los filtros genéricos.",
    ["Adaptar la consulta de `explore/repositories.py::filter` a los modelos nuevos",
     "Filtros por competición, temporada, país y equipo (un equipo aparece si juega algún partido del dataset)", "Formulario en la interfaz de Explore"],
    ["Pruebas de cada filtro y de combinaciones"])

add("nd-export", "Descarga en CSV y exportación a JSON", JUAN, "feature", "media", "newdataset", M3, 2, ROBER, ["nd-standings"], "exportar-json",
    "Ofrecer los datos del dataset en CSV (ficheros originales) y en JSON (partidos y clasificación).",
    ["Adaptar la descarga ZIP actual a los ficheros CSV", "Exportación a JSON con partidos, clasificación y metadatos",
     "Botones en la página del dataset"],
    ["Pruebas de que el JSON contiene todos los partidos y la clasificación correcta", "La descarga sigue registrando `DSDownloadRecord`"])

add("nd-seeders", "Seeders y ficheros de ejemplo de fútbol (sustituyen a uvl_examples)", NICO, "feature", "media", "newdataset", M2, 1, JUANMA, ["nd-model"], "seeders-futbol",
    "Datos de ejemplo para desarrollo, pruebas y demo: varias temporadas de distintas competiciones y países.",
    ["CSV de ejemplo (p. ej. LaLiga 2024-25, Premier League 2024-25) en lugar de `uvl_examples/`",
     "Seeders del tipo fútbol", "Incluir descargas y visitas con fechas variadas para #214 y #211"],
    ["`rosemary db:seed` carga los datos sin errores en Docker"])

add("nd-zenodo", "Sincronizar los datasets CSV con fakenodo (depósito, ficheros, DOI)", JUANMA, "feature", "media", "newdataset", M3, 2, MANU, ["nd-upload", "fn-config"], "sync-fakenodo",
    "El WI #178 exige que el tipo nuevo se publique en Zenodo/fakenodo como hoy los UVL.",
    ["Adaptar `zenodo/services.py` para enviar los metadatos de fútbol y los ficheros CSV", "Guardar el DOI devuelto en el dataset"],
    ["Prueba de integración: subir un dataset CSV contra fakenodo devuelve un DOI"])

add("nd-rebrand", "Rebranding: UVLHub → FutbolHub en plantillas, títulos y menús", JUANMA, "refactor", "baja", "newdataset", M3, 1, JUAN, [], "rebranding",
    "Que la aplicación se presente como FutbolHub.",
    ["Nombre, logotipo y textos de la portada", "Títulos de página y menús", "Eliminar referencias visibles a UVL y feature models"],
    ["Ninguna página visible menciona UVLHub"])

# ───────────────────────── WI-fakenodo ─────────────────────────
add("fn-skeleton", "fakenodo: elegir cómo se implementa y crear el esqueleto", MANU, "feature", "alta", "fakenodo", M2, 1, ALE, [], "fakenodo-esqueleto",
    "El WI #177 admite dos opciones: una feature (`rosemary feature:create fakenodo` en `features_dev`) o un contenedor aparte en `docker-compose.dev.yml`. Hay que justificar la elección.",
    ["Elegir la opción y registrar el motivo en el diario", "Crear el esqueleto y hacerlo arrancar en el entorno Docker"],
    ["fakenodo responde en el entorno de desarrollo"])

add("fn-endpoints", "fakenodo: endpoints de depósito (crear, subir fichero, publicar, obtener, listar, borrar)", MANU, "feature", "alta", "fakenodo", M2, 2, ALE, ["fn-skeleton"], "fakenodo-endpoints",
    "Simular solo las llamadas que hace hoy `app/features/zenodo/services.py`.",
    ["`POST /` crear depósito", "`POST /<id>/files` subir fichero", "`POST /<id>/actions/publish` publicar y devolver DOI",
     "`GET /<id>` y `GET /`", "`DELETE /<id>`"],
    ["Pruebas de cada endpoint"])

add("fn-versions", "fakenodo: metadatos → mismo DOI; ficheros nuevos → nueva versión con nuevo DOI y concept DOI", MANU, "feature", "alta", "fakenodo", M2, 2, ALE, ["fn-endpoints"], "fakenodo-versiones",
    "Lógica de Zenodo que necesitan #195 y #196. Coordinar con Alejandro y Juan María.",
    ["Editar solo metadatos no cambia el DOI", "`POST /<id>/actions/newversion` y publicar con ficheros cambiados da un DOI nuevo",
     "Todas las versiones comparten `conceptrecid` / concept DOI"],
    ["Pruebas de la regla «metadatos → mismo DOI / ficheros → nuevo DOI»"])

add("fn-config", "Conectar FutbolHub a fakenodo mediante ZENODO_API_URL y enlaces desde configuración", MANU, "feature", "media", "fakenodo", M2, 1, JUANMA, ["fn-endpoints"], "fakenodo-config",
    "Cambiar a fakenodo debe bastar con `ZENODO_API_URL`, sin variables paralelas (WI #177).",
    ["`ZENODO_API_URL` apuntando a fakenodo en desarrollo y pruebas (`.env.*.example`)",
     "Los enlaces a Zenodo de `view_dataset.html` (fijos a zenodo.org/sandbox) se construyen desde configuración"],
    ["Subir un dataset en desarrollo funciona sin token de Zenodo"])

# ───────────────────────── #182 Subir desde GitHub / ZIP ─────────────────────────
add("182-zip", "Subir un dataset desde un ZIP con protección frente a zip slip y zip bomb", NICO, "feature", "alta", "182 GitHub/ZIP", M3, 3, ALE, ["nd-upload"], "subida-zip",
    "Una temporada puede tener un CSV por jornada: subir un ZIP evita cargarlos uno a uno.",
    ["Aceptar `.zip` en la subida, descomprimir en el servidor y quedarse con los CSV",
     "Protección *zip slip* (rutas con `../` o absolutas)", "Protección *zip bomb* (límite de tamaño descomprimido y de número de ficheros)",
     "Validar cada CSV con el validador"],
    ["Pruebas con ZIP válidos, con CSV inválidos, con ficheros que no son CSV y con ZIP maliciosos"])

add("182-github", "Importar un dataset desde un repositorio público de GitHub", NICO, "feature", "alta", "182 GitHub/ZIP", M3, 2, ALE, ["182-zip"], "importar-github",
    "Muchos datos de fútbol se publican en repositorios de GitHub.",
    ["Aceptar URL de repositorio público, con rama y carpeta opcionales", "Descargar el repositorio y reutilizar el tratamiento del ZIP",
     "Errores claros si el repositorio no existe o es privado"],
    ["Pruebas con GitHub *mockeado* (sin red)"])

add("182-report", "Informe de ficheros importados y rechazados con su motivo", NICO, "feature", "media", "182 GitHub/ZIP", M3, 1, JUANMA, ["182-zip"], "informe-importacion",
    "Mostrar al usuario qué ficheros se han importado y cuáles se han rechazado y por qué.",
    ["Listado en la interfaz tras subir ZIP o importar de GitHub", "Motivo de rechazo: no es CSV, error de validación con fila y motivo, ruta peligrosa"],
    ["Prueba Selenium del informe"])

# ───────────────────────── #196 Versionado mayor ─────────────────────────
add("196-model", "Modelo de versiones de dataset con concept DOI + migración", ALE, "feature", "alta", "196 versionado mayor", M3, 2, JUANMA, ["nd-model"], "modelo-versiones",
    "Base del versionado (compartida con #195). Zenodo devuelve `conceptrecid` pero hoy no se guarda.",
    ["Diseñar el modelo (tabla `DatasetVersion` o enlace por concept DOI) junto con Juan María",
     "Número de versión mayor.menor en el dataset", "Guardar el concept DOI", "Migración"],
    ["Pruebas unitarias del modelo"])

add("196-files", "Almacenar los ficheros por versión", ALE, "feature", "alta", "196 versionado mayor", M3, 1, NICO, ["196-model"], "ficheros-por-version",
    "Hoy los ficheros viven en `uploads/user_<id>/dataset_<id>/` sin carpeta de versión.",
    ["Estructura `uploads/user_<id>/dataset_<id>/v<N>/`", "Migrar o adaptar los datasets existentes y los seeders"],
    ["Las versiones anteriores conservan sus ficheros"])

add("196-flow", "Publicar una nueva versión: añadir, reemplazar o quitar ficheros con nuevo DOI", ALE, "feature", "alta", "196 versionado mayor", M3, 3, MANU, ["196-files", "fn-versions"], "nueva-version",
    "Una temporada en curso crece cada jornada: se publica una versión nueva con DOI nuevo.",
    ["Formulario para añadir, reemplazar o quitar CSV (solo el propietario)", "Validar los ficheros nuevos",
     "`newversion` → subir → publicar en fakenodo", "La versión mayor sube (v1.x → v2.0)"],
    ["Pruebas: la versión nueva tiene DOI nuevo, comparte concept DOI y la anterior conserva sus ficheros"])

add("196-ui", "Historial de versiones en la página del dataset y DOIs antiguos que siguen funcionando", ALE, "feature", "media", "196 versionado mayor", M3, 1, JUANMA, ["196-flow"], "historial-versiones",
    "Que se puedan consultar y descargar las versiones anteriores.",
    ["Listado de versiones con DOI, fecha y enlace", "Los DOIs antiguos redirigen a su versión (`DOIMapping`)"],
    ["Prueba de que un DOI antiguo abre su versión"])

# ───────────────────────── #195 Versionado menor ─────────────────────────
add("195-edit", "Editar los metadatos de un dataset (solo el propietario)", JUANMA, "feature", "alta", "195 versionado menor", M3, 2, ALE, ["nd-model"], "editar-metadatos",
    "Hoy no existe la edición de datasets. Corregir metadatos (fuente, nº de equipos...) no debe cambiar el DOI.",
    ["Ruta y formulario de edición: título, descripción, autores, etiquetas, publicación relacionada y metadatos de fútbol",
     "Solo el propietario puede editar (403 en otro caso)", "No permite cambiar ficheros (eso es #196)"],
    ["Pruebas de permisos y de edición"])

add("195-sync", "Versión menor: actualizar metadatos en fakenodo manteniendo el DOI", JUANMA, "feature", "alta", "195 versionado menor", M3, 2, ALE, ["195-edit", "196-model", "fn-versions"], "version-menor",
    "Editar metadatos actualiza el depósito sin nuevo DOI y sube la versión menor (v1.0 → v1.1).",
    ["Actualizar los metadatos del depósito en fakenodo", "Incrementar la versión menor y mostrarla en la página"],
    ["Pruebas: editar mantiene el DOI e incrementa la versión menor"])

add("195-log", "Registro de cambios de metadatos (quién, cuándo, campos, valor anterior y nuevo)", JUANMA, "feature", "media", "195 versionado menor", M3, 1, ALE, ["195-edit"], "registro-cambios",
    "Guardar cada edición para poder mostrarla (base de #199 si se hiciera).",
    ["Modelo y migración del registro", "Mostrar el historial de cambios en la página del dataset"],
    ["Prueba de que cada edición queda registrada con sus valores"])

# ───────────────────────── #194 Búsqueda avanzada ─────────────────────────
add("194-author-date", "Búsqueda avanzada: filtros por autor y por rango de fechas", ROBER, "feature", "media", "194 búsqueda avanzada", M2, 2, NICO, [], "filtro-autor-fecha",
    "No depende de otros WIs: puede empezarse ya sobre el Explore actual.",
    ["Filtro por autor: nombre, afiliación u ORCID", "Filtro por rango de fechas de publicación", "Campos en el formulario de Explore"],
    ["Pruebas de cada filtro, incluidos rangos vacíos y límites"])

add("194-tags-metrics", "Búsqueda avanzada: varias etiquetas desde el formulario y filtros por métricas", ROBER, "feature", "media", "194 búsqueda avanzada", M3, 2, NICO, ["194-author-date", "nd-model"], "filtro-etiquetas-metricas",
    "Hoy el filtro de etiquetas solo se alcanza pulsando una etiqueta.",
    ["Selector de varias etiquetas en el formulario", "Filtros por métricas del dataset (nº de partidos, nº de equipos)"],
    ["Pruebas de cada filtro y de combinaciones con los de dominio"])

add("194-url", "Filtros de búsqueda en la URL para compartir búsquedas + documentación de uso", ROBER, "feature", "media", "194 búsqueda avanzada", M3, 1, JUAN, ["194-tags-metrics"], "busqueda-url",
    "Una búsqueda debe poder compartirse con un enlace.",
    ["Reflejar todos los filtros en la query string", "Restaurar los filtros al abrir el enlace", "Documentar los filtros en la wiki"],
    ["Prueba de que abrir una URL con filtros devuelve los mismos resultados"])

# ───────────────────────── #214 Contador de descargas ─────────────────────────
add("214-counter", "Contador de descargas y visitas por dataset (página, explore y API)", JUAN, "feature", "media", "214 contador descargas", M3, 2, MANU, ["nd-model"], "contador-descargas",
    "`DSDownloadRecord` ya registra las descargas, pero solo se muestran totales globales.",
    ["Decidir y documentar si se cuentan descargas únicas o todas", "Mostrar descargas y visitas en la página del dataset y en Explore",
     "Añadirlas a `/api/v1/datasets`"],
    ["Pruebas de que el contador sube tras una descarga y aparece en la API"])

add("214-stats", "Endpoint /api/v1/datasets/<id>/stats con descargas y visitas por mes", JUAN, "feature", "baja", "214 contador descargas", M3, 1, MANU, ["214-counter"], "api-stats",
    "Parte opcional de #214.",
    ["Totales y desglose mensual de descargas y visitas"],
    ["Pruebas con registros de varios meses"])

# ───────────────────────── #211 Datasets en tendencia ─────────────────────────
add("211-service", "Ranking de datasets en tendencia por descargas o visitas en la última semana o mes", MANU, "feature", "media", "211 tendencias", M3, 1, JUAN, ["nd-model"], "ranking-tendencias",
    "Usa los mismos datos que #214 (`DSDownloadRecord`, `DSViewRecord`). Coordinar con Juan.",
    ["Servicio de ranking parametrizado por métrica (descargas/visitas) y periodo (semana/mes)"],
    ["Pruebas con registros dentro y fuera del periodo"])

add("211-ui", "Sección «Datasets en tendencia» en la portada", MANU, "feature", "media", "211 tendencias", M3, 1, JUAN, ["211-service"], "portada-tendencias",
    "Mostrar las temporadas más populares en la portada.",
    ["Título, autor principal y nº de descargas/visitas en el periodo", "Selector semana/mes"],
    ["Prueba Selenium de la sección"])
