# r24 · Investigación metodológica y skill r49

Fecha: **15-10-2026**. Encargo: profundizar en la biblioteca y su skill GameMaker,
contrastando Matt Pocock, Gentle AI, ECC, otras fuentes primarias y el trabajo actual
de Relicwild. Se mejora el método existente; una revisión finita no certifica que
pueda producir cualquier juego perfecto.

## 1 · Punto de partida y protección

- Biblioteca canónica: este checkout, con WIP extenso anterior a esta ronda. Se conserva
  manifiesto inicial, diff y copia del paquete fuera del repositorio.
- `13/28` ya cubre elicitación; `13/29`, spec-driven, tareas verticales, crítica,
  recursos y evidencia; `13/01` y `13/10`, hipótesis y playtesting.
- Relicwild se consulta en lectura, con su pausa vigente. No se ejecutan ni corrigen
  sus scripts, juego, supervisores o servicios. Cryalis tampoco se reanuda.
- Las fuentes externas se estudian a revisiones fijadas. No se instalan sus hooks,
  agentes, ejecutores ni memorias; no se cambian modelos, configuración global o runtime.
- Esta petición autoriza mejora local; publicación, commits y push quedan fuera.

## 2 · Diferencia que debe entregar la ronda

Un complemento operativo enlaza requisito versionado → cambio → tarea vertical →
casos → evidencia → decisión, sin copiar los capítulos existentes. Desarrolla la
promoción de aprendizajes y la evaluación de la propia skill. Las plantillas viajan
con el paquete; el lector no necesita instalar Matt, Gentle o ECC para aplicarlas.

## 3 · Criterios de aceptación

1. Matriz de fuentes con URL, revisión, licencia aplicable, lectura realizada,
   cobertura existente, adopción/adaptación/rechazo y límites de ejecución.
2. Aprendizajes de Relicwild distinguen contratos previstos y resultados registrados;
   los hallazgos decisivos se contrastan con los archivos fuente actuales.
3. Ejemplo completo adaptado a GameMaker: estados, recurso compartido, dependencias,
   persistencia, casos cruzados, invalidación y aceptación por requisito.
4. Automejora gobernada: observación → reproducción → corrección/prueba → regla
   acotada → evaluación independiente → promoción; conservar resultados negativos.
5. Paquete r49 autónomo, con referencias progresivas, sin nueva dependencia externa;
   rutas descubribles y `AGENTS.md` derivado por el sincronizador.
6. Ensayos de comportamiento con control sin guía y muestras frescas con la skill;
   rúbrica y escenario fijados antes, respuestas conservadas, lectura manual y
   limitaciones. Si el control ya cumple, no atribuir una mejora causal a la skill.
7. Mantenimiento completo de la biblioteca, incluida compilación real del GML
   documental existente; instalación en destino temporal y coherencia del paquete.
   Conservar código de salida y log, sin heredar el verde r48.
8. Revisión independiente de requisitos y normas; corregir hallazgos confirmados.
   Cotejar cambios propios y preservación de fuentes de Relicwild al finalizar.

## 4 · Qué no acredita esta ronda

No integra ECC ni demuestra paridad con sus capacidades. No realiza un playtest de
un juego, no certifica fidelidad de Relicwild ni todos los géneros/targets. Las pruebas
del paquete y del corpus local se informan por separado; el espejo y los repositorios
opcionales presentes aquí no se presuponen en una instalación de solo la skill.

## 5 · Ajuste encontrado durante la verificación

La sincronización real encontró un falso aviso: un enlace a una copia idéntica era tratado
como contenido divergente por no apuntar a la ruta canónica. Se incorpora la corrección
acotada del sincronizador, con reproducción roja y controles de copia alterada, incompleta
y enlace colgante. Conserva enlaces y comprueba bytes; no modifica configuración del harness.
La distribución local actualiza copias físicas existentes y sus enlaces consumidores,
con respaldos de la revisión previa. No crea instalaciones nuevas ni publica.
