# r25 · Activación, asesoría e instalación sin fricción

Fecha: 15-10-2026. Entregable previsto: revisión r50 de biblioteca y paquete.
El encargo autoriza publicación de este trabajo; no autoriza reanudar juegos pausados.

## Resultado que se acepta

| ID | Requisito | Evidencia exigida |
|---|---|---|
| R1 | Una petición natural de crear un juego con GameMaker selecciona la skill | Traza de un agente real sin nombrar la skill en el prompt |
| R2 | Capas progresivas y asesor automático cuando aporta valor | Lecturas y delegación reales con brief, resultado y modelo efectivo; control de consulta pequeña y tarea ajena |
| R3 | Una instalación sencilla sin Bash, Git ni paquetes Python adicionales obligatorios | Bootstrap Python con descarga de revisión identificada, instalador stdlib y fixture limpio; GameMaker sigue siendo requisito para ejecutar juegos |
| R4 | Instalar para agentes compatibles sin conocer rutas | Destinos canónicos, opciones explícitas, registro de biblioteca, copias verificadas, alias y perfiles preservados |
| R5 | Actualizar sin perder trabajo ni configuración | Idempotencia, copia previa, fallo y rollback; sin editar modelos, secretos ni configuración del harness |
| R6 | Publicación completa y segura | Commit público revisado, remoto coincidente, instalación desde esa revisión y pruebas de sistemas disponibles |
| R7 | Mantener garantías del conocimiento | Actualización completa, compilación/ejecución/trampas; corpus completo y clon público con denominadores separados |

## Alcance y método

- Una sola entrada descubrible evita competencia entre skills duplicadas. Las referencias se cargan por intención y fase.
- Asesoría inicial mejora decisiones; la crítica fresca final conserva su aislamiento. Un fallback serial se identifica como tal.
- Se heredan o conservan los modelos configurados según la capacidad real del harness; no se habilita el advisor experimental global ni se instala otro método/modelo.
- Descubierta, cargada, asesor invocado y resultado correcto son estados diferentes. Los ensayos textuales r24 no demuestran estos nuevos requisitos.
- Investigación primaria actual y revisión de implementación; pruebas en fixtures antes de instalar. R25 añade lo que falta sobre r49, no duplica los capítulos 13/28–30.
- Matriz de sistemas: pruebas locales macOS; Linux/Windows mediante CI si hay runners disponibles. Una rama Python simulada no se presenta como ejecución nativa.

## Custodia y publicación

La raíz mantiene su WIP anterior. Baseline de 592 archivos y diff previo custodiados fuera del repositorio público. El remoto y el worktree público partían de `519b5be795a86337da309f51a1f5696241edef74` (r48), limpio; el main local tiene otro historial. Se transfieren archivos públicos revisados al worktree, nunca el historial privado. Corpus opcional, conversaciones, juegos y secretos permanecen fuera.

## Cierre de la revisión

Los recibos finales enlazarán cada requisito con pruebas reales y sus límites. Ninguna prueba finita certifica cualquier juego perfecto; sí permite comprobar este recorrido, sus contratos y sus regresiones.
