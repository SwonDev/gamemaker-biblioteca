# r25 · Publicación de biblioteca y skill r50

15-10-2026. Referencia de distribución: **r50**. Código comprobado en
`5f7bef857cbe3869edbe1944901a243f11215953`; los recibos posteriores no cambian ese código ni
el paquete de skill. Publicación desde el historial público r48, sin incluir el main local.

## Evidencia de instalación real

[GitHub Actions: seis combinaciones correctas](https://github.com/SwonDev/gamemaker-biblioteca/actions/runs/38773860502).
[Recibo por runner, versiones y descarga](r25-ci.json).

| Sistema | Python | Resultado |
|---|---|---|
| Ubuntu | 3.10.22 / 3.14.8 | Instalación, 32 pruebas, bootstrap 12, rutas 3 y descarga doble correctos |
| macOS | 3.10.11 / 3.14.7 | Mismo recorrido correcto |
| Windows | 3.10.11 / 3.14.8 | Mismo recorrido y PowerShell nativo correctos; 32/32 sin omisiones de enlaces |

Cada runner descarga el commit real y ejecuta la instalación dos veces: quince destinos
únicos, catorce archivos de payload más manifiesto, biblioteca registrada y segunda pasada
sin copias/backups innecesarios. Los índices del runtime y GameMaker no se instalan en CI.

La primera matriz falló en Windows por lecturas de fixtures y captura de subprocess con
codificación implícita CP1252. Se fijó UTF-8 en las pruebas y salida del bootstrap, se
refrescó su SHA-256 en los comandos de instalación y la segunda matriz pasó íntegra.
[Primera pasada conservada](https://github.com/SwonDev/gamemaker-biblioteca/actions/runs/38772290767).
No se ocultaron esos fallos ni se atribuyeron al motor.

Al activar también las seis pruebas de symlinks de Windows se corrigieron dos aserciones:
se comparan los destinos literales antes/después y su resolución, sin asumir que Windows
omita su prefijo de ruta extendida. La omisión depende ahora del permiso real, no del nombre
del sistema. La descarga de un runner recibió HTTP 403 de la API anónima: el bootstrap pasó
a codeload directo, contrasta el commit del comentario ZIP y el SHA solicitado. No necesita
cuenta ni la API de metadatos. [Formato de archivo Git](https://git-scm.com/docs/git-archive).
[Pasada que descubrió ambos casos](https://github.com/SwonDev/gamemaker-biblioteca/actions/runs/38773343106).

## Ámbito público y comprobación local

La distribución pública sin corpus opcional pasó `_indice/actualizar.py` con salida 0:
2.091 rutas correctas, 239 enlaces opcionales sin comprobar, 1.640 anclas; 2.362/3.213
símbolos localizables, 80 tareas estáticas y 3.477 bloques compilados con 306 exclusiones.
Los índices se generaron localmente para esa prueba y permanecen fuera de Git.
El mapa público tiene 268 entradas, frente a 278 del corpus completo local. Ambos declaran
su ámbito; no se copia el resultado completo sobre una instalación sin esas fuentes.

La fuente completa local pasó mantenimiento, trece scripts compilados, banco de ejecución
con 205 correctas/cero fallidas y nueve trampas comprobables vigentes. Las puertas del motor
se ejecutaron secuencialmente en bancos propios, sin reanudar juegos pausados.
Los ensayos r49 conservan sus vistas: verificador público APTO, 70 vistas y tres artefactos
nuevos, cero rutas personales y sin leer sus originales privados.

La instalación local quedó cotejada: dieciséis selectores, quince rutas lógicas únicas y
doce copias físicas; los aliases compartidos se conservan. Los quince archivos del paquete
coinciden y cada ruta adyacente apunta a la biblioteca correcta. Cuatro archivos de
configuración de agentes se cotejaron por hash sin cambios. Las copias anteriores quedan
conservadas, y el corpus completo sigue disponible desde esta biblioteca local.

Se compararon las 592 fuentes iniciales del ámbito: catorce cambiaron dentro del conjunto
previsto y las otras 578 mantienen su hash. Los nuevos archivos pertenecen al encargo.
Las ilustraciones no se cambiaron. No se publica el historial privado, conversaciones,
claves, corpus de terceros ni proyectos personales. Se revisó cada commit saliente; la
identidad pública es SwonDev con correo noreply.

## Qué acredita el resultado

La instalación es reproducible en los runners documentados; no certifica cada app, perfil,
permiso de symlinks o configuración personalizada. Las pruebas de loaders de otros harnesses
siguen teniendo su versión y fecha. La autoactivación y consulta se demostraron con Codex,
no con todos los modelos. [Ensayo nativo](r25-ensayos.md). El advisor experimental de Claude
no se habilita ni es requisito. El usuario conserva sus modelos, proveedores y permisos.
