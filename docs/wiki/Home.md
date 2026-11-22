# Diario del Equipo — FutbolHub

Bienvenido al **Diario del Equipo de FutbolHub** (proyecto de *Evolución y Gestión de la Configuración*, curso 2026-2027, ETSII — Universidad de Sevilla).

Según la sección 4 del [Acta Fundacional](Acta-Fundacional), esta wiki constituye el registro oficial y versionado de todas las **actas de reunión**, **decisiones justificadas** e **incumplimientos** del equipo.

---

## 1. Equipo y roles transversales

| # | Miembro | Usuario GitHub | Perfil | Rol transversal | WI principal asignado |
|---|---------|----------------|--------|-----------------|-----------------------|
| 1 | Juan Pozo García | `@jjuanx` | PM | **Project Manager (PM)** | WI-newdataset (`#178`, coord.) y `#214` Contador de descargas (L) |
| 2 | Nicolás Pérez Martín | `@Nicopm0905` | Dev | **Responsable de calidad (QA)** | `#182` Subir desde GitHub / ZIP (H) |
| 3 | Alejandro Pichardo Martínez | `@alepm03` | Dev | **Responsable de gestión de la configuración** | `#196` Versionado mayor (H) |
| 4 | Juan María Sánchez Madroñal | `@Juanitomsp` | Dev | **Responsable de incidencias** | `#195` Versionado menor (M) |
| 5 | Manuel Duarte Álvarez | `@Madunguin` | DevOps | **Responsable de despliegue (DevOps)** | WI-fakenodo (`#177`) y `#211` Datasets en tendencia (L) |
| 6 | Roberto Rolo Guinot | `@RobertoRoloG` | Dev | **Responsable de documentación** | `#194` Búsqueda avanzada (M) |

---

## 2. Índice de reuniones y actas

- **[Plantilla de acta de reunión](Plantilla-Acta-Reunion)** — Formato estándar acordado (asistentes, temas tratados, acuerdos y tareas con responsable).
- **[08/11/2026 — Acta Fundacional (v2)](Acta-Fundacional)** — Constitución del equipo, definición del dominio FutbolHub, reparto de roles y WIs, acuerdos de comunicación, EGCFlow, régimen interno y CI/CD ([PDF firmado](../FutbolHub%20-%20Acta%20fundacional%20v2%20corregida.pdf)).
- **[09/11/2026 — Reunión y Seguimiento Oficial 1](Acta-2026-11-09-Seguimiento-1)** — Entrega del acta fundacional, revisión inicial con el tutor José Manuel Sánchez Ruiz y planificación del primer reparto de tareas para el hito `0.1.0`.

---

## 3. Índice de decisiones registradas

El detalle completo y justificado se encuentra en la página de **[Decisiones del Equipo](Decisiones)**:

| Fecha | Decisión | Resumen y justificación | Referencia |
|-------|----------|-------------------------|------------|
| 08/11/2026 | **D-01: Dominio FutbolHub** | Sustitución de modelos UVL por datasets CSV de resultados de partidos de fútbol (`jornada,fecha,local,visitante,goles_local,goles_visitante`), clasificación automática y filtros de dominio. | [Acta Fundacional, §2](Acta-Fundacional) |
| 08/11/2026 | **D-02: Reparto de roles transversales** | Asignación según perfiles del test SuperPOP (PM: Juan; DevOps: Manuel; Configuración: Alejandro; QA: Nicolás; Incidencias: Juan María; Documentación: Roberto). | [Acta Fundacional, §3](Acta-Fundacional) |
| 08/11/2026 | **D-03: Selección y reparto de WIs** | Elección de 2 WIs comunes (`#178` newdataset, `#177` fakenodo), 2 High (`#182`, `#196`), 2 Medium (`#195`, `#194`) y 2 Low (`#214`, `#211`) formando bloques coherentes y parejas coordinadas. | [Acta Fundacional, §3](Acta-Fundacional) |
| 08/11/2026 | **D-04: Política EGCFlow sin PRs** | Ramas `main` (entregas etiquetadas), `trunk` (integración continua) y ramas de tarea `<nº issue>-<slug>`. Revisión en la propia issue en ≤ 48 h con `git diff trunk...rama`. | [Acta Fundacional, §5 y §7](Acta-Fundacional) |
| 08/11/2026 | **D-05: Render + MariaDB externa (filess.io)** | Plataforma de producción con `Dockerfile.render`, despliegue continuo (`CD_render.yml`) condicionado a CI en verde en `main`. | [Acta Fundacional, §8](Acta-Fundacional) |
| 20/11/2026 | **D-06: Primer reparto de tareas (46 issues)** | Desglose en 46 issues de 1 a 3 días, etiquetas `tipo:` / `prioridad:` / `WI:`, hitos `0.1.0` (23 nov), `0.2.0` (30 nov) y `1.0.0` (defensa) y tablero Kanban. | [Decisiones §20/11/2026](Decisiones#20112026--primer-reparto-de-tareas) · Issue #1 |
| 21/11/2026 | **D-07: Retirada de CD heredado del fork** | Eliminación de `CD_webhook.yml` y `CD_dockerhub.yml` y desactivación de `webhook` en `features_prod` para alinear el despliegue con Render. | [Decisiones §21/11/2026](Decisiones#21112026--retirada-del-despliegue-heredado-del-fork) · Issue #7 |

---

## 4. Régimen interno e incumplimientos

- **[Registro de Incumplimientos](Incumplimientos)** — Seguimiento de las normas de obligado cumplimiento y tabla de escalado (sección 6 del Acta Fundacional).
