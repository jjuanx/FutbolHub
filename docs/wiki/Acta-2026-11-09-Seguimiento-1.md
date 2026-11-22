# Acta de reunión — 2026-11-09: Primer seguimiento oficial y arranque del proyecto

- **Fecha:** 09/11/2026
- **Hora:** 12:30 – 13:00 (reunión presencial tras el primer seguimiento oficial)
- **Modalidad:** Presencial (ETSII — Universidad de Sevilla)
- **Moderador (PM):** Juan Pozo García (`@jjuanx`)
- **Secretario (Documentación):** Roberto Rolo Guinot (`@RobertoRoloG`)

---

## 1. Asistentes

| Miembro | Usuario GitHub | Rol | Asistencia |
|---------|----------------|-----|------------|
| Juan Pozo García | `@jjuanx` | Project Manager (PM) | ✅ Asiste |
| Nicolás Pérez Martín | `@Nicopm0905` | Responsable de calidad (QA) | ✅ Asiste |
| Alejandro Pichardo Martínez | `@alepm03` | Gestión de la configuración | ✅ Asiste |
| Juan María Sánchez Madroñal | `@Juanitomsp` | Responsable de incidencias | ✅ Asiste |
| Manuel Duarte Álvarez | `@Madunguin` | Responsable de despliegue (DevOps) | ✅ Asiste |
| Roberto Rolo Guinot | `@RobertoRoloG` | Responsable de documentación | ✅ Asiste |

---

## 2. Orden del día y temas tratados

1. **Entrega y revisión del Acta Fundacional con el tutor (José Manuel Sánchez Ruiz):**
   - Presentación de la propuesta de dominio **FutbolHub** (datasets CSV de resultados de partidos de fútbol), reparto de roles según perfiles SuperPOP y selección de Work Items.
   - Recogida del feedback del tutor para detallar la trazabilidad de extremo a extremo (`issue → rama → commits → CI → entrega etiquetada → despliegue`) de cara a los seguimientos del **23 de noviembre (`0.1.0`)** y **30 de noviembre (`0.2.0`)**.
2. **Organización del repositorio y flujo EGCFlow:**
   - Creación del fork `jjuanx/FutbolHub` con rama de integración `trunk` y rama de entregas `main`.
   - Acuerdo de prefijar todas las ramas de tarea con el número de issue (`<nº issue>-<slug>`) y referenciar la issue `(#N)` al final de cada commit siguiendo Conventional Commits.
3. **Planificación del Hito `0.1.0` (Seguimiento del 23 de noviembre):**
   - Preparación del tablero Kanban en GitHub Projects, etiquetas (`tipo:`, `prioridad:`, `WI:`), plantillas de issues, guía de contribución y criterios de calidad en `CONTRIBUTING.md`, activación de la wiki como diario del equipo y ejecución del CI en todas las ramas.

---

## 3. Acuerdos adoptados

- **Acuerdo 1 (Versión 2 del Acta Fundacional):** Incorporar las secciones ampliadas de gestión de incidencias, calidad y despliegue continuo en Render en la versión consolidada del Acta Fundacional ([Acta Fundacional v2](Acta-Fundacional)).
- **Acuerdo 2 (Desglose del trabajo en issues pequeñas):** Dividir todos los WIs y tareas transversales en issues de 1 a 3 días de estimación, con responsable, revisor sugerido, dependencias, hito y nombre exacto de rama.
- **Acuerdo 3 (Consultas pendientes con el tutor — Issue #15):** Confirmar con el tutor antes de cerrar el modelo de datos si se utiliza un CSV por temporada o por jornada, si el tipo UVL debe coexistir con el tipo fútbol y la catalogación de dificultad del WI `#195`.

---

## 4. Tareas asignadas con responsable (Hito 0.1.0 — 23/11/2026)

| Issue | Descripción | Responsable | Revisor sugerido | Hito |
|-------|-------------|-------------|------------------|------|
| `#1` | Configurar tablero Kanban, etiquetas, hitos y primer reparto de issues | `@jjuanx` | `@Juanitomsp` | `0.1.0` (23 nov) |
| `#2` | Plantillas de issues: funcionalidad, incidencia y tarea (docs/CI/refactor) | `@Juanitomsp` | `@jjuanx` | `0.1.0` (23 nov) |
| `#3` | Activar la wiki y crear el diario del equipo con la plantilla de acta de reunión | `@RobertoRoloG` | `@jjuanx` | `0.1.0` (23 nov) |
| `#4` | Documentar EGCFlow del equipo en `CONTRIBUTING.md` | `@alepm03` | `@Nicopm0905` | `0.1.0` (23 nov) |
| `#5` | Criterios de revisión de código y de diseño de pruebas | `@Nicopm0905` | `@alepm03` | `0.1.0` (23 nov) |
| `#6` | CI: ejecutar las pruebas en ramas de tarea, `trunk` y `main` | `@Madunguin` | `@alepm03` | `0.1.0` (23 nov) |
| `#7` | Desactivar `CD_webhook.yml` y `CD_dockerhub.yml` y registrar la decisión | `@Madunguin` | `@alepm03` | `0.1.0` (23 nov) |
| `#11` | Entrega `0.1.0`: llevar `trunk` a `main`, etiquetar y publicar la release | `@alepm03` | `@jjuanx` | `0.1.0` (23 nov) |
| `#15` | Cerrar la propuesta de dominio con el tutor y las decisiones abiertas | `@jjuanx` | `@RobertoRoloG` | `0.1.0` (23 nov) |
