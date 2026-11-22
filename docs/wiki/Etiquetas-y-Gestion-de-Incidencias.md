# Etiquetas y Gestión de Incidencias — FutbolHub

Según la **sección 7 del [Acta Fundacional](Acta-Fundacional)** (*Gestión de incidencias y calidad*), todo trabajo en el repositorio comienza con una issue creada a partir de las plantillas de `.github/ISSUE_TEMPLATE/` y clasificada mediante tres familias de etiquetas: **`tipo:`**, **`prioridad:`** y **`WI:`**.

---

## 1. Etiquetas de tipo (`tipo:`)

Indican la naturaleza del cambio. Cada plantilla de `.github/ISSUE_TEMPLATE/` asigna automáticamente su etiqueta de tipo por defecto:

| Etiqueta | Color | Plantilla asociada | Cuándo se utiliza |
|----------|-------|--------------------|-------------------|
| `tipo: feature` | `#1d76db` | `funcionalidad.yml` | Nueva funcionalidad de usuario o de dominio (un WI o parte de él). |
| `tipo: bug` | `#d73a4a` | `incidencia.yml` | Incidencia o defecto: algo no funciona según lo especificado o rompe el CI/despliegue. |
| `tipo: refactor` | `#5319e7` | `tarea.yml` | Reestructuración interna del código o modelos sin cambiar el comportamiento externo. |
| `tipo: docs` | `#0075ca` | `tarea.yml` | Documentación, diario del equipo, actas, `README.md` o `CONTRIBUTING.md`. |
| `tipo: ci` | `#fbca04` | `tarea.yml` | Workflows de GitHub Actions, entornos (Docker, Vagrant, devcontainer), entregas y despliegue en Render. |

---

## 2. Etiquetas de prioridad (`prioridad:`)

Permiten ordenar el trabajo dentro de cada hito:

| Etiqueta | Color | Criterio de asignación |
|----------|-------|------------------------|
| `prioridad: alta` | `#b60205` | Bloquea a otras issues del equipo o entra de forma obligatoria en el próximo seguimiento oficial. |
| `prioridad: media` | `#d93f0b` | Funcionalidad o tarea planificada dentro del hito que no bloquea el arranque de otros compañeros. |
| `prioridad: baja` | `#c5def5` | Mejoras complementarias, endpoints opcionales o ajustes estéticos/rebranding. |

---

## 3. Etiquetas de Work Item de origen (`WI:`)

Vinculan cada issue con el Work Item del proyecto al que pertenece para mantener la trazabilidad completa de cara a las entregas y la defensa:

| Etiqueta | Color | Work Item y responsable principal |
|----------|-------|-----------------------------------|
| `WI: newdataset` | `#0e8a16` | **WI-newdataset (`#178` uvlhub)** — Común a todo el equipo, coordinado por Juan (`@jjuanx`). |
| `WI: fakenodo` | `#0e8a16` | **WI-fakenodo (`#177` uvlhub)** — Común, responsable Manuel (`@Madunguin`). |
| `WI: 182 GitHub/ZIP` | `#006b75` | **`#182` Subir desde GitHub / ZIP (Alta)** — Responsable Nicolás (`@Nicopm0905`). |
| `WI: 196 versionado mayor` | `#006b75` | **`#196` Versionado mayor (Alta)** — Responsable Alejandro (`@alepm03`). |
| `WI: 195 versionado menor` | `#006b75` | **`#195` Versionado menor (Media)** — Responsable Juan María (`@Juanitomsp`). |
| `WI: 194 búsqueda avanzada` | `#006b75` | **`#194` Búsqueda avanzada (Media)** — Responsable Roberto (`@RobertoRoloG`). |
| `WI: 214 contador descargas` | `#006b75` | **`#214` Contador de descargas (Baja)** — Responsable Juan (`@jjuanx`). |
| `WI: 211 tendencias` | `#006b75` | **`#211` Datasets en tendencia (Baja)** — Responsable Manuel (`@Madunguin`). |
| `WI: organización` | `#bfdadc` | Gestión del equipo, documentación transversal, entregas y configuración de CI/CD. |

---

## 4. Hitos y estados del tablero Kanban

Cada issue se asocia a uno de los tres hitos de entrega (`0.1.0 — Seguimiento 23 nov`, `0.2.0 — Seguimiento 30 nov`, `1.0.0 — Defensa 14/16 dic`) y avanza por los cinco estados del tablero **[FutbolHub — Tablero](https://github.com/users/jjuanx/projects/2)**:

1. **Pendiente:** Issue aceptada y estimada (1 a 3 días), sin empezar.
2. **En progreso:** Tiene responsable asignado y rama de tarea `<nº issue>-<slug>` abierta desde `trunk`.
3. **En revisión:** Desarrollo y pruebas terminados en su rama; el revisor sugerido se añade a *Assignees* para que revise el diff frente a `trunk` en un plazo máximo de **48 h**.
4. **Bloqueada:** No puede avanzar por una dependencia o decisión abierta; el motivo consta en un comentario de la issue.
5. **Hecho:** Revisión aprobada con la plantilla de `CONTRIBUTING.md`, integrada en `trunk` con el CI en verde, rama borrada e issue cerrada citando el commit de integración.
