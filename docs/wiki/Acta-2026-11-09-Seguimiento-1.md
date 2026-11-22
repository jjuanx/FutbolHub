# Acta de reunión — 2026-11-09: Primer seguimiento oficial

- **Fecha:** 09/11/2026
- **Modalidad:** Presencial en clase de laboratorio (ETSII — Universidad de Sevilla), seguida de reunión breve presencial (~10 min) al finalizar el seguimiento (según sección 4 del acta)
- **Moderador (PM):** Juan Pozo García (`@jjuanx`)
- **Secretario (Documentación):** Roberto Rolo Guinot (`@RobertoRoloG`)

---

## 1. Asistentes

| Miembro | Usuario GitHub | Rol | Asistencia |
|---------|----------------|-----|------------|
| Juan Pozo García | `@jjuanx` | Project Manager (PM) | ✅ Asiste (seguimiento oficial obligatorio) |
| Nicolás Pérez Martín | `@Nicopm0905` | Responsable de calidad (QA) | ✅ Asiste (seguimiento oficial obligatorio) |
| Alejandro Pichardo Martínez | `@alepm03` | Gestión de la configuración | ✅ Asiste (seguimiento oficial obligatorio) |
| Juan María Sánchez Madroñal | `@Juanitomsp` | Responsable de incidencias | ✅ Asiste (seguimiento oficial obligatorio) |
| Manuel Duarte Álvarez | `@Madunguin` | Responsable de despliegue (DevOps) | ✅ Asiste (seguimiento oficial obligatorio) |
| Roberto Rolo Guinot | `@RobertoRoloG` | Responsable de documentación | ✅ Asiste (seguimiento oficial obligatorio) |

---

## 2. Orden del día y temas tratados

1. **Presentación del Acta Fundacional firmada (08/11/2026) ante el tutor (José Manuel Sánchez Ruiz):**
   - Exposición de la propuesta de dominio **FutbolHub** (datasets CSV de resultados de partidos de fútbol), el reparto de roles transversales apoyado en el test SuperPOP y la asignación de Work Items entre los 6 integrantes.
   - Revisión con el tutor de la política de ramas **EGCFlow** (`main`, `trunk` y ramas de tarea `<nº issue>-<descripción>`), revisión por pares sin pull requests, gestión de incidencias y propuesta de despliegue continuo en **Render** con MariaDB en **filess.io**.
2. **Puesta en común tras el seguimiento:**
   - Recogida de las observaciones del tutor sobre los temas marcados como *a decidir* en el acta fundacional (granularidad de los ficheros CSV por temporada o jornada, convivencia con el tipo UVL del WI-newdataset y alcance de los WIs de versionado).
   - Organización inicial del trabajo para llegar al segundo seguimiento oficial (23 de noviembre) con la gestión de configuración, incidencias, diario del equipo y CI funcionando sobre el repositorio.

---

## 3. Acuerdos adoptados

- **Acuerdo 1:** Preparar el repositorio `jjuanx/FutbolHub` con la rama de integración `trunk` a partir de `main` y activar las herramientas de seguimiento (issues, etiquetas, tablero y wiki).
- **Acuerdo 2:** Que cada responsable transversal prepare la base de su área antes del seguimiento del 23 de noviembre: tablero y desglose inicial de tareas (PM), plantillas y etiquetas de issues (Incidencias), diario en la wiki (Documentación), guía de EGCFlow en el repositorio (Gestión de la configuración), criterios de revisión y pruebas (QA) y ejecución del CI en todas las ramas (DevOps).
- **Acuerdo 3:** Consultar con el tutor las dudas abiertas del dominio antes de cerrar el modelo de datos del WI-newdataset.

---

## 4. Tareas acordadas con responsable

| Área | Tarea | Responsable |
|------|-------|-------------|
| Gestión / PM | Preparar el desglose de tareas por WI, hitos y tablero Kanban en GitHub Projects, y trasladar al tutor las consultas abiertas del dominio | `@jjuanx` |
| Incidencias | Preparar las plantillas de issues (funcionalidad, incidencia y tarea) y la documentación de etiquetas | `@Juanitomsp` |
| Documentación | Activar la wiki y estructurar el diario del equipo con el acta fundacional, plantilla de acta y registro de decisiones | `@RobertoRoloG` |
| Configuración | Documentar el flujo EGCFlow del equipo (ramas, commits, revisión e integración sin PR) en `CONTRIBUTING.md` | `@alepm03` |
| Calidad (QA) | Redactar la checklist de revisión de código y la guía de diseño de pruebas (particiones de equivalencia y valores límite) | `@Nicopm0905` |
| DevOps / CI | Adaptar el CI para que corra en todas las ramas y retirar los workflows de CD heredados del fork | `@Madunguin` |
