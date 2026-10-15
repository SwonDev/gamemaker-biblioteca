# r24 · Recibo de validación de biblioteca y skill r49

Fecha: **15-10-2026**. Revisión metodológica definida en
[el plan y sus criterios](r24-plan-y-criterios.md).

## Resultado

**Revisión local completada y comprobada.** Mantenimiento integral posterior a la última
corrección: salida **0**. Skill r49 de **13 archivos**, instalación aislada idéntica y
**12 destinos locales** cotejados: ocho copias físicas actualizadas y cuatro enlaces
conservados. Cada copia física anterior r48 mantiene un respaldo cotejado. Los
[recibos estructurados](r24-recibos.json) conservan cifras, huellas y alcance.

## Cambios y procedencia

- [Investigación primaria](r24-investigacion-metodos.md): Matt, Gentle AI, ECC, Spec Kit,
  OpenSpec, gm-cli, GM-TestFramework y Olympus con revisión fijada, licencias por archivo
  cuando difieren, y fuentes originales de videojuegos. Se distingue adaptación de ideas
  de integración o paridad de software.
- [Aprendizajes de Relicwild](r24-aprendizajes-relicwild.md): diferencia entre fidelidad y
  gusto, vigencia de reglas/rúbricas, límites de promoción, cancelación y errores del medidor.
- [13 · 30](<../../13 - Diseño y producción de videojuegos/30 - Especificación viva y mejora del método.md>)
  y referencia portátil: requisito versionado → tarea → casos → recibo → decisión,
  invalidación, ocho casos didácticos con oráculo y promoción contrastada del aprendizaje.
- Corrección en `13/01 §7`: un caso observado en una sola persona no se descarta como
  ruido. Muestra y técnica de playtest dependen del propósito; pensar en voz alta tiene límites.
- Sincronizador: reconoce enlaces a copias idénticas mediante comparación de todo el paquete;
  mantiene rechazo de contenido modificado, incompleto y enlace colgante.

## Comprobaciones ejecutadas

Entorno de mantenimiento: **Python 3.12.14**, PyYAML **6.0.3**, Pillow **12.2.0**, macOS arm64.
CLI instalado **2.4.0**, runtime GMS2 **2026.0.0.23**. No se actualizaron herramientas.
El `python3` predeterminado 3.14.7 carecía de PyYAML: el primer intento de sincronización
falló; se usó el intérprete 3.12 existente con las dependencias fijadas de la biblioteca.

| Puerta | Resultado observado |
|---|---|
| `python3.12 -u _indice/actualizar.py`, tras el fix final | Salida 0, «Biblioteca coherente» |
| Autopruebas de instrumentos | 23 herramientas ejecutadas; ninguna autoprueba excluida |
| Enlaces y anclas, dentro del mantenimiento | 2.325 rutas y 1.640 anclas, cero rotas |
| Índice/mapa/ortografía | 278 entradas de mapa existentes, sin faltas señaladas ni nombres incorrectos |
| Descubrimiento estático | 80 tareas resueltas, incluidas seis nuevas; no ejecuta un LLM |
| API en el corpus completo presente | 3.213/3.213 símbolos vigentes localizables; no extrapolable a un clon sin fuentes opcionales |
| GML documental | 3.477 bloques compilados sin error de sintaxis, 306 exclusiones declaradas; 27,6 s en la pasada final |
| Integración estática | Sin duplicaciones graves detectadas por la herramienta |
| Espejo de manual | 3.119 páginas comparadas, cero ausentes/incompletas/literales traducidos en esa comparación |
| Regresión del sincronizador | Rojo 13 pruebas/1 fallo; verde final 16/16 y salida 0; repetido por ambos revisores |
| Instalación real en destino temporal | 13/13 archivos idénticos por SHA-256 |
| Instalaciones existentes | 12 destinos con los mismos 13 archivos; ocho respaldos r48 de las copias físicas |
| Ensayos con agentes | Control 5/5, preliminar 5/5 separado y final 5/5; [prompts, respuestas y rúbrica](r24-ensayos-skill.md) |
| Revisión independiente | [Normas](r24-revision-normas.md) y [Spec](r24-revision-spec.md); hallazgos P3 y P2 corregidos, sin pendientes confirmados |

La primera pasada integral terminó con salida 1 por el nombre de una referencia sin tilde;
se renombró a `contratos-y-aprendizaje.md` y se corrigieron sus punteros. La revisión Spec
concretó estados y ocho casos del ejemplo. Las muestras anteriores quedaron como desarrollo
y se ejecutaron otras cinco sobre el paquete final. Después, la verificación de destinos
reprodujo y corrigió el falso aviso de alias; se repitió el mantenimiento integral.
Todos esos intentos se conservan; no se presenta únicamente la pasada favorable.

Al distribuir se detectaron tres enlaces a la copia compartida de Claude. Se mantuvo esa
topología: el enlace de OpenCode, sustituido inicialmente por una copia al aplicar el
instalador, se restauró desde su respaldo; la copia intermedia quedó conservada. No se
modificaron configuraciones de modelos/proveedores ni se instalaron harnesses nuevos.

Permanece un aviso previo de Qwen: su configuración lee la carpeta de Claude en vez de su
carpeta propia; esa copia y su enlace están al día. No se cambió esa preferencia de carga.
No se ejecutaron conversaciones reales en cada CLI: la comprobación de destinos acredita
identidad de archivos y enlaces, no sus loaders ni comportamiento de todos los harnesses.

## Preservación y límites

El delta se cotejó contra una instantánea al inicio, no contra HEAD: el WIP anterior es
extenso. Las fuentes iniciales ajenas a los cambios enumerados se conservaron. De Relicwild
se compararon **47.956 archivos textuales seleccionados**, sin alterados ni ausentes;
la marca de pausa sigue presente. Esa comparación excluye binarios, imágenes, modelos y
cachés del motor; no se presenta como una auditoría de cada byte del proyecto.

Los logs completos, instantáneas, respaldos y manifiestos de máquina permanecen fuera del
repositorio; sus huellas de atribución están en los recibos estructurados. No hubo commits,
push ni publicación. Las copias locales de la skill sí se actualizaron, con recuperación.

Los datos consultables de los ensayos son vistas anonimizadas: se conservan 69 archivos
originales y el informe en custodia privada. Doce archivos sustituyen únicamente prefijos
de máquina por marcadores; escenario, rúbrica, respuestas, calificaciones y paquetes
mantienen sus bytes. El [manifiesto de vistas](r24-ensayos/vistas-para-publicar.json) separa
huella original y pública; las metadata mantienen la huella del prompt realmente leído y
añaden la de su vista. Se comprobó tanto el conjunto público como su contraste con el bruto.

El control ya aprobaba el escenario: **no se demuestra mejora causal de r49**. Los ensayos
acreditan decisiones textuales, no ejecución de un juego ni los ocho casos didácticos.
Compilar fragmentos acredita sintaxis dentro del banco, no funcionamiento de cada receta.
Una consulta estática tampoco certifica calidad, rendimiento o ausencia universal de errores.

## Alcance

La investigación de upstream es documental; no se ejecutan sus CLIs, hooks o frameworks.
Relicwild se mantiene en lectura y pausa. La compilación del corpus GameMaker y los
ensayos del paquete tienen resultados separados; ninguno acepta el juego de referencia
ni certifica todos los géneros, modelos o plataformas. Las plataformas distintas de este
host mantienen sus recibos históricos y necesitan pruebas propias al aplicar el método.
