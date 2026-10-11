# r22 · Skill progresiva y consumo portátil

## 1. Fallo observado y corrección

Una prueba fresca recibió solo el paquete de skill r46 en un escenario Windows con
PowerShell, sin CLI ni índices, runtime distinto de la referencia y código privado
que no debía salir de la máquina. La entrada requería un sondeo Bash y el fallback
dependía de `gm-cli`; las referencias a capítulos completos no estaban empaquetadas.
La preparación exigió salir del paquete y leer documentos adicionales.

La entrada r47 tiene **86 líneas**, descripción dentro del límite de 1024 caracteres
y ocho referencias operativas progresivas. El paquete conserva AGENTS y dos índices
de consulta, y contiene **12 archivos**. Ofrece sondeos Bash y PowerShell, consulta
oficial por web, selección explícita de la fuente de API y estados de verificación.
Los capítulos profundos siguen siendo recursos de la biblioteca completa; no se afirma
que formen parte de una copia aislada.

## 2. Prueba fresca posterior

Otro agente sin la solución esperada recibió el mismo escenario y solo el paquete.
Encontró el fallback oficial, comprobó las opciones de filtrado y su firma, señaló que
el manual `monthly` no acredita la revisión exacta del proyecto y preparó una revisión
local de persistencia. Conservó el código privado y no ejecutó juego, modelo o servicio.
La corrección visual y la persistencia quedaron pendientes de prueba en el proyecto.

Lectura declarada por el agente: entrada 85 líneas en el corte observado, referencias
584, total **669**. La última edición añadió una línea sobre el alcance de los handles
de 2026. La base había leído aproximadamente 2300–2600 líneas, con salidas truncadas;
estos datos describen los recorridos, **no una medición de ahorro de tokens**.

## 3. Sondeos ejecutados

El bloque PowerShell de `references/entorno-y-fuentes.md` se extrajo sin reescribirlo
y se ejecutó con PowerShell **7.6.6**, macOS arm64, `-NoProfile -NonInteractive`, en
tres fixtures: sin biblioteca, biblioteca sin índice e índice con runtime de prueba.
Los tres produjeron el diagnóstico esperado y **exit 0**.

Se descargó el tar oficial portable y se contrastó su SHA-256 con
[el manifest de la publicación 7.6.6](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6):
`6df833d094ebac1c1a74340d7b3437f4aaf5e03ce640484a1c4359f3ce8b3db1`.
No se instaló globalmente ni se modificó un perfil. Se usó `GM_BIBLIOTECA` solo en
el proceso de cada fixture, sin redefinir `HOME` ni `CODEX_HOME`.

Esto verifica el bloque y sus tres ramas en PowerShell sobre macOS; **no constituye
una prueba nativa de Windows**. Las búsquedas propuestas por el agente y las pruebas
de guardado no se ejecutaron sobre un proyecto privado durante este ensayo.
