# Decisiones del Equipo — FutbolHub

Esta página recoge de forma cronológica todas las decisiones técnicas, arquitectónicas y organizativas adoptadas por el equipo junto con su justificación (Acta Fundacional, sección 4).

---

### 08/11/2026 — Definición del dominio: datasets CSV de resultados de fútbol (WI-newdataset)
- **Decisión:** Sustituir los modelos de características UVL de UVLHub por **datasets CSV de resultados de partidos de fútbol** (`jornada,fecha,local,visitante,goles_local,goles_visitante` en UTF-8), añadiendo metadatos específicos del dominio (competición, país, temporada, número de equipos y fuente), validación por fila y motivo, cálculo automático de clasificación y estadísticas por equipo, exportación a JSON y filtros en Explore.
- **Motivo:** Permite conservar toda la arquitectura del hub (subida, validación, exploración, publicación con DOI y descarga) aplicándola a un dominio rico en reglas de negocio verificables con particiones de equivalencia y valores límite (goles negativos, fechas límite de temporada, equipos duplicados en una misma jornada).

---

### 08/11/2026 — Reparto de roles transversales del equipo
- **Decisión:** Asignar un rol transversal a cada miembro además de su WI de desarrollo:
  - **Project Manager (PM):** Juan Pozo García (`@jjuanx`)
  - **Responsable de calidad (QA):** Nicolás Pérez Martín (`@Nicopm0905`)
  - **Responsable de despliegue (DevOps):** Manuel Duarte Álvarez (`@Madunguin`)
  - **Responsable de gestión de la configuración:** Alejandro Pichardo Martínez (`@alepm03`)
  - **Responsable de documentación:** Roberto Rolo Guinot (`@RobertoRoloG`)
  - **Responsable de incidencias:** Juan María Sánchez Madroñal (`@Juanitomsp`)
- **Motivo:** El reparto sigue el perfil con el que se formó el equipo (test SuperPOP): Juan (perfil PM) asume la gestión y coordinación con el tutor; Manuel (perfil DevOps) asume CI/CD y entornos; y los cuatro perfiles Dev se reparten configuración, calidad, documentación e incidencias de forma que cada uno vigila un aspecto distinto del trabajo de los demás.

---

### 08/11/2026 — Selección y asignación de Work Items (WIs)
- **Decisión:** Abordar los dos WIs comunes (`WI-newdataset #178` entre todo el equipo coordinado por Juan, y `WI-fakenodo #177` liderado por Manuel) junto con seis WIs específicos:
  - `#182 Subir desde GitHub / ZIP` (Alta — **Nicolás**)
  - `#196 Versionado mayor` (Alta — **Alejandro**)
  - `#195 Versionado menor` (Media — **Juan María**)
  - `#194 Búsqueda avanzada` (Media — **Roberto**)
  - `#214 Contador de descargas` (Baja — **Juan**)
  - `#211 Datasets en tendencia` (Baja — **Manuel**)
- **Motivo:** Forman bloques funcionales coherentes para un hub de temporadas de fútbol y evitan dependencias en cadena con comunidades (`#189`, `#210`) o extensiones adicionales de versionado (`#197`, `#198`). Quienes comparten modelos trabajan en parejas coordinadas (`#196` + `#195`, `#214` + `#211`), mientras que `#194` (Roberto) puede avanzar desde el primer día sobre Explore mientras mantiene el diario y la documentación.

---

### 08/11/2026 — Plataforma de despliegue continuo: Render + MariaDB en filess.io
- **Decisión:** Desplegar la versión de producción en **Render** usando `docker/images/Dockerfile.render` y una base de datos MariaDB 12 externa en **filess.io**, desactivando el *auto-deploy* de Render para desplegar únicamente desde GitHub Actions (`CD_render.yml`) cuando los tres workflows de CI (`CI_commits.yml`, `CI_lint.yml`, `CI_pytest.yml`) terminen en verde sobre `main`.
- **Motivo:** Render no requiere mantener un servidor propio, ofrece un plan gratuito suficiente para el proyecto y el repositorio ya cuenta con `Dockerfile.render` preparado. Condicionar el deploy hook al CI garantiza que nunca se publique en producción código que no haya superado las pruebas.

---

### 20/11/2026 — Primer reparto de tareas
- **Decisión:** el trabajo se divide en 46 issues de 1 a 3 días, cada una con responsable, revisor sugerido, estimación, dependencias y rama de tarea, siguiendo la sección 7 del acta.
- **Etiquetas:** `tipo:` (feature, bug, refactor, docs, ci), `prioridad:` (alta, media, baja) y `WI:` (WI de origen o `organización`).
- **Hitos:** 0.1.0 para el seguimiento del 23 nov (gestión del código e incidencias: 9 issues), 0.2.0 para el del 30 nov (pruebas y CI/CD: 13 issues) y 1.0.0 para la defensa (24 issues).
- **Reparto:** cada miembro lleva las issues de su WI y de su rol transversal; el WI-newdataset se reparte entre todos (modelo: Juan; validador: Nicolás; subida y sincronización: Juan María; clasificación y filtros: Roberto; página del dataset: Alejandro).
- **Temas abiertos para el tutor (#15):** si UVL debe seguir funcionando, la dificultad de #195 (high en uvlhub, M en el acta) y si se usa un CSV por temporada o por jornada.

---

### 21/11/2026 — Retirada del despliegue heredado del fork
- **Decisión:** Eliminar los workflows heredados `CD_webhook.yml` y `CD_dockerhub.yml` y retirar la feature `webhook` de `features_prod` en `pyproject.toml` (manteniéndola en `features_dev` para conservar sus pruebas en desarrollo y CI).
- **Motivo:** La sección 8 del Acta Fundacional establece Render como plataforma de producción; retirar los flujos heredados evita ejecuciones fallidas hacia servidores propios o Docker Hub ajenos al despliegue acordado (ver registro detallado en [`docs/decisiones/2026-11-21-despliegue-render.md`](https://github.com/jjuanx/FutbolHub/blob/trunk/docs/decisiones/2026-11-21-despliegue-render.md), issue #7).
