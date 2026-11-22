# Acta Fundacional — FutbolHub (08/11/2026)

- **Documento PDF firmado por todos los integrantes:** [`docs/FutbolHub - Acta fundacional v2 corregida.pdf`](https://github.com/jjuanx/FutbolHub/blob/trunk/docs/FutbolHub%20-%20Acta%20fundacional%20v2%20corregida.pdf)
- **Fecha de firma:** 08/11/2026 (entregada para el primer seguimiento del lunes 09/11/2026)
- **Asignatura:** Evolución y Gestión de la Configuración (EGC), curso 2026-2027
- **Tutor:** José Manuel Sánchez Ruiz
- **Repositorio:** `https://github.com/jjuanx/FutbolHub`

---

## Resumen de secciones del Acta Fundacional

### 1. Identificación del equipo

| # | Nombre completo | UVUS | Correo electrónico | Usuario de GitHub | Perfil |
|---|-----------------|------|--------------------|-------------------|--------|
| 1 | Nicolás Pérez Martín | YGC9995 | `nicpermar@alum.us.es` | `@Nicopm0905` | Dev |
| 2 | Juan Pozo García | DKK2084 | `juapozgar@alum.us.es` | `@jjuanx` | PM |
| 3 | Alejandro Pichardo Martínez | alepicmar | `alepicmar@alum.us.es` | `@alepm03` | Dev |
| 4 | Juan María Sánchez Madroñal | BJN1732 | `juasanmad@alum.us.es` | `@Juanitomsp` | Dev |
| 5 | Manuel Duarte Álvarez | HGB8018 | `manduaalv@alum.us.es` | `@Madunguin` | DevOps |
| 6 | Roberto Rolo Guinot | XXM5911 | `robrolgui@alum.us.es` | `@RobertoRoloG` | Dev |

### 2. Tipo de hub (Dominio)

**FutbolHub** es un repositorio de **datasets de resultados de partidos de fútbol** que sustituye los modelos UVL de UVLHub por ficheros CSV de resultados manteniendo la arquitectura del hub: subir, validar, explorar, publicar con DOI (mediante **fakenodo**) y descargar.

- **Formato de fichero CSV (UTF-8 con cabecera obligatoria):**
  ```csv
  jornada,fecha,local,visitante,goles_local,goles_visitante
  1,2024-08-15,Sevilla FC,Real Betis,2,1
  1,2024-08-16,Real Madrid,Valencia CF,3,0
  ```
- **Reglas de validación al subir (indicando fila y motivo):**
  1. Faltan columnas, hay celdas vacías o tipos incorrectos (jornada y goles enteros, fecha `AAAA-MM-DD`).
  2. Hay goles negativos.
  3. Un equipo juega contra sí mismo, o dos veces en la misma jornada.
  4. Hay partidos duplicados.
  5. Las fechas quedan fuera de la temporada declarada.
- **Metadatos del dataset:** Título, descripción, autores, etiquetas, tipo de publicación + **competición, país, temporada, número de equipos y fuente de los datos**.
- **Prestaciones del hub:**
  - Clasificación automática (3 pts victoria, 1 pt empate; desempate por diferencia de goles y goles a favor).
  - Estadísticas por equipo (jugados, ganados, empatados, perdidos, goles a favor y en contra).
  - Descarga en CSV y exportación a JSON.
  - Filtros en Explore por competición, temporada, país y equipo, más búsqueda avanzada (`#194`).

### 3. Roles y Work Items

- **Project Manager:** Juan (`@jjuanx`)
- **Responsable de calidad (QA):** Nicolás (`@Nicopm0905`)
- **Responsable de despliegue (DevOps):** Manuel (`@Madunguin`)
- **Responsable de gestión de la configuración:** Alejandro (`@alepm03`)
- **Responsable de documentación:** Roberto (`@RobertoRoloG`)
- **Responsable de incidencias:** Juan María (`@Juanitomsp`)

### 4. Acuerdos de comunicación y reuniones

- Canales oficiales: GitHub (issues y Projects), Diario del equipo (wiki), Google Meet, Correo institucional y Grupo de WhatsApp (solo coordinación diaria; toda decisión se traslada a GitHub o al diario).
- Reunión semanal (~30 min) fijada mediante encuesta lunes → martes 14:00, además de breves reuniones presenciales (~10 min) tras cada seguimiento oficial (9, 23 y 30 de noviembre, y defensa el 14 o 16 de diciembre).

### 5. Política de gestión de ramas (EGCFlow)

- `main`: línea de entregas etiquetadas con versionado semántico (`0.1.0`, `0.2.0`, `1.0.0`).
- `trunk`: línea de integración continua del equipo.
- Ramas de tarea: `<nº issue>-<descripción-corta>` creadas desde `trunk`.
- Sin pull requests internos: revisión por otro miembro en la issue en ≤ 48 h (`git diff trunk...rama`) y merge directo a `trunk` cuando el CI está en verde.
- Commits atómicos con Conventional Commits (`feat`, `fix`, `test`, `docs`, `refactor`, `ci`, `chore`) referenciando la issue al final (`(#N)`).

### 6. Régimen interno y sanciones

- Normas de asistencia, plazos (aviso con 48 h), tiempos de respuesta, revisión en 48 h, cumplimiento de EGCFlow y comprensión total del código entregado (incluido el asistido por IA).
- Escalado en 3 niveles registrado en la página de [Incumplimientos](Incumplimientos).

### 7. Gestión de incidencias y calidad

- Trazabilidad completa: `issue → rama → commits → CI → entrega etiquetada → despliegue`.
- Tablero GitHub Projects con estados: `Pendiente`, `En progreso`, `En revisión`, `Bloqueada`, `Hecho`.

### 8. Entornos y despliegue continuo

- Entornos aislados con Python 3.13 y MariaDB 12: Docker (`docker/docker-compose.dev.yml`), Vagrant (`vagrant/Vagrantfile`), CI (GitHub Actions en Ubuntu 24.04) y Producción en **Render** (`Dockerfile.render` + MariaDB en `filess.io`).
