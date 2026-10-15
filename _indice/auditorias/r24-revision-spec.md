# r24 · Revisión independiente de especificación

Fecha: **15-10-2026**. Eje Spec de `mp-code-review`. Comparación con la instantánea
inicial r49, no con `HEAD`, que contiene WIP anterior. Solo se modifica este informe;
no se consulta el otro eje.

## Hallazgo inicial, resuelto

**P2 · Ejemplo sin oráculo de estados y casos cruzados.** La versión inicial de
`13/30:98–108` enumeraba casos adicionales sin resultado ni obligatoriedad. Incumplía
parcialmente el criterio 3: «Ejemplo completo adaptado a GameMaker: estados, recurso
compartido, dependencias, persistencia, casos cruzados, invalidación y aceptación por
requisito». La referencia portátil conservaba la ambigüedad.

**Resolución contrastada:** `13/30:110–133` fija política didáctica, estados y ocho casos
con inicio, acción y resultado; la línea 108 exige los ocho en la unión @2, sin omisiones
ni controles inválidos. `references/contratos-y-aprendizaje.md:44–65` conserva el resumen,
control negativo y aceptación. R-UX permanece separado. Los punteros SKILL/AGENTS usan
la referencia renombrada. **P2 cerrado; cero hallazgos Spec pendientes.** Esto acredita
la corrección documental, no ejecución del ejemplo.

## Ajuste del sincronizador

Conforme al criterio 5 y al alcance añadido en §5 del plan. El delta de
`sincronizar-skill.py:383–397` acepta identidad de origen o igualdad del paquete completo;
no escribe ni sustituye el alias. Se revisaron los registros rojo (13 pruebas, un fallo)
y verde (16/16), y se repitieron independientemente **16/16 con Python 3.12, exit 0**:
copia idéntica aceptada, alias intacto y copias alterada/incompleta o enlace colgante
rechazados. El Python 3.14 predeterminado carece de PyYAML y no genera el fixture AGENTS;
esa ejecución termina con error, sin acreditar un defecto del cotejo ni cobertura allí.

## Cobertura y límites

Sin ampliación indebida detectada: se operacionaliza `13/29`, las plantillas viajan con
el paquete y no se instalan frameworks. Se contrastaron fidelidad, reglas v2/v3 y pausa
con fuentes actuales de Relicwild, y la negativa de ejecución con la
[revisión fijada de ECC](https://github.com/affaan-m/ECC/blob/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29/skills/eval-harness/SKILL.md).

Criterio 6: leídas las cinco respuestas finales, conformes a la rúbrica prefijada;
control y variante 5/5, correctamente sin atribución causal ni prueba de juego real.
Criterio 7 cerrado: recibo final y log posterior al ajuste coinciden en salida 0,
23 instrumentos, 80 consultas y 3.477 bloques compilados/306 exclusiones, 27,6 s.
Se verificaron independientemente las huellas de los siete logs, los 13 archivos del
paquete, la instalación temporal y los 12 destinos: idénticos; cuatro enlaces presentes.
La compilación acredita sintaxis, no ejecución de recetas; identidad de destino no prueba
su loader. **Revisión Spec final conforme, sin hallazgos pendientes.**
