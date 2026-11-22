# Retirada del despliegue heredado del fork

Fecha: 21 de noviembre de 2026.
Responsable: Manuel Duarte Alvarez.
Tarea: #7. Revisor previsto: Alejandro.

## Contexto y decision

La seccion 8 del acta fundacional establece Render como plataforma de
produccion. Los workflows heredados `CD_webhook.yml` y `CD_dockerhub.yml`
despliegan en un servidor propio y publican imagenes en Docker Hub,
respectivamente. Se eliminan para aplicar el acuerdo del acta y evitar
ejecuciones ajenas al despliegue elegido.

La feature `webhook` deja de cargarse en produccion. Se conserva en
desarrollo y pruebas para mantener su suite existente.

## Alcance y siguientes pasos

Este cambio no configura el despliegue en Render. La creacion del servicio,
la base de datos y `CD_render.yml` pertenecen al hito del 30 de noviembre.
Ese flujo debera desplegar solo cuando commits, lint y pytest hayan pasado
para la revision de `main` que se publique.

Este registro queda versionado para enlazarlo desde el diario de la wiki.
La revision de Alejandro y la integracion en `trunk` quedan pendientes;
su evidencia debe registrarse en la issue #7.
