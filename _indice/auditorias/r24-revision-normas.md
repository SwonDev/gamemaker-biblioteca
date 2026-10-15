# r24 · Revisión independiente de normas

Fecha: **15-10-2026**. Eje: normas y mantenibilidad documental.

## Alcance

Revisión de los 21 archivos del delta `cambios-r49.patch`, comparados con la instantánea
de inicio de esta ronda, no con HEAD; incluye recomprobaciones del informe, renombrado
y arreglo posterior de `sincronizar-skill.py` y `pruebas/probar-sincronizacion.py` contra
sus originales. Se leyeron AGENTS.md, CLAUDE.md, CONTRIBUTING.md, PUBLICAR.md y
`writing-for-agents`. Se excluyen WIP previo y conclusiones de otro revisor. Sin ejecutar
juegos, proyectos pausados, frameworks externos ni cambios globales.

## Hallazgo y resolución

1. **P3 resuelto — Sustituir la raíz personal del informe enlazado.**
   `_indice/auditorias/r24-aprendizajes-relicwild.md:103` incluía la raíz absoluta personal.
   Regla: `CONTRIBUTING.md:10`, «Retira rutas personales, credenciales y contenido privado
   antes de enviarlo»; `PUBLICAR.md:15` excluye fuentes/recibos privados. Era juicio preventivo
   de preparación pública, sin publicación realizada ni infracción dura del encargo local.
   **Recomprobado:** dice «raíz privada de `Relicwild_World`» y conserva R1–R12 relativos.

Se comprobó además el renombrado a `contratos-y-aprendizaje.md`: ruta antigua ausente
y cuatro referencias actualizadas en SKILL, AGENTS derivado, desarrollo y QA. La ampliación
simultánea del ejemplo conserva C-OP-01–08 y sus políticas alineadas con `13/30`.
Sin problema nuevo de normas observado en estos ajustes.

## Arreglo del sincronizador

La comparación conserva identidad mediante `samefile` y acepta un destino distinto solo
si coincide el contenido completo del paquete. La etiqueta distingue enlace canónico y
enlace a copia; el diagnóstico no sustituye enlaces. Las regresiones rechazan contenido
modificado, archivo ausente y enlace colgante. Sin hallazgos nuevos.

Se leyeron `sincronizacion-rojo.log` y `sincronizacion-verde.log` de custodia. Reejecución
independiente: `/opt/homebrew/bin/python3.12 _indice/pruebas/probar-sincronizacion.py`,
**16/16, exit 0**, Python 3.12.14. El intento previo con Python 3.14.7 sin PyYAML falló
al preparar un fixture; no acredita regresión del arreglo.

## Resultado y límites

No quedan hallazgos abiertos de normas en el delta. El capítulo y la
referencia portátil distinguen contratos, autoridad, versiones, resultados históricos y
pruebas ejecutadas; no importan modelos, número de agentes ni dependencias obligatorias.
La duplicación resumida del procedimiento está justificada por el uso autónomo del paquete
y remite al capítulo completo.

El mantenimiento integral posterior al arreglo queda fuera de esta recomprobación.
La revisión no certifica todos los upstream ni la ejecución futura del consumidor.
