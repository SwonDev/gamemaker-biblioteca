---
name: gamemaker-biblioteca
description: "Úsala para «quiero hacer un juego con GameMaker» o «Game Maker», GML, .yyp/.yy/.gml, gm-cli, «hazme un juego» y «no compila»; errores, diseño, assets, QA, publicación, desarrollo con IA y búsqueda semántica."
---

# GameMaker · biblioteca fidedigna

<!-- SKILL-VERSION: r50 · 2026-10-15 -->
`r50 · 2026-10-15`. Biblioteca local en español; referencia histórica LTS 2026.0
(IDE 2026.0.0.16 · GMS2 2026.0.0.23). **Manda la versión real del proyecto.**

## Antes de actuar

1. Actívala por la intención GameMaker del usuario, sin exigir que nombre la skill.
   Sitúa la tarea: consulta, aprendizaje, nuevo juego, continuación/cambio o verificación.
   En un proyecto, comprueba checkout, reglas, spec, glosario, diseño, WIP y pausa; reutiliza
   lo existente. Una lectura no autoriza reanudar procesos, cambiar modelos ni publicar.
2. Antes de recomendar API, escribir GML u operar el motor, lee una vez por entorno
   [`references/entorno-y-fuentes.md`](references/entorno-y-fuentes.md): sondeo Bash/zsh
   **o PowerShell**, biblioteca/índice/CLI disponibles y fallback. Refresca si cambia el entorno.
   Comprueba engine/runtime/target del proyecto y compáralos con `meta.runtime` del índice.
   `GM_BIBLIOTECA_RUNTIME` selecciona la fuente: un valor explícito inválido es error, sin
   fallback silencioso. La caché de máquina y la etiqueta LTS de esta skill no cambian el proyecto.
3. Lee solo las referencias de la fase actual. Requisitos o método sin API ni operación
   no requieren sondear biblioteca/CLI. Al iniciar un juego, ante una decisión costosa o
   estancamiento, aplica automáticamente [`asesor y activación`](references/asesor-y-activacion.md):
   **Invoca un subagente asesor de solo lectura antes de cerrar la definición inicial o
   decidir el enfoque**; encargo autónomo breve, sin delegación en cascada, modelos/roles
   vigentes y resultado contrastado. Esto autoriza esa delegación dentro del encargo.
   Si falta herramienta, permiso o cuota, declara el fallback de autorrevisión y su causa.
   Leer el protocolo no acredita haber consultado. Una duda puntual no lo exige.

`BIB` es la raíz comprobada de la biblioteca. Las rutas `NN/MM` abrevian
`$BIB/NN - <carpeta>/MM - <archivo>.md`; las referencias del paquete viajan con SKILL.md.
El AGENTS.md de este paquete es una derivación para harnesses sin skills: no necesitas
releer esa copia si ya leíste esta misma revisión. Si solo tienes el paquete, conserva sus contratos y declara
los documentos o herramientas ausentes.

## Qué leer según el trabajo

| Necesitas | Lee antes de actuar |
|---|---|
| Verificar o recomendar API; escribir/revisar GML, firma, obsolescencia, structs o convenciones | [`references/consulta-api.md`](references/consulta-api.md) |
| Init, recursos, eventos, CLI/MCP/IDE, compilar, ejecutar o empaquetar | [`references/operar-gamemaker.md`](references/operar-gamemaker.md): trampas y límites del entorno documentado |
| Crear/continuar un juego, diseñar sistemas, coordinar agentes o rondas de crítica | [`references/desarrollo-y-evidencia.md`](references/desarrollo-y-evidencia.md): spec, arquitectura, propiedad y cinco puertas de IA |
| Iniciar un juego, decidir algo costoso de revertir o salir de un atasco | [`references/asesor-y-activacion.md`](references/asesor-y-activacion.md): asesor disponible, brief, contraste, límites y traza real |
| Cambiar requisitos, revisar reglas del gauntlet, incorporar aprendizajes o evaluar la skill | [`references/contratos-y-aprendizaje.md`](references/contratos-y-aprendizaje.md): trazabilidad, invalidación y promoción |
| Probar, medir, revisar, declarar verde/aceptación/terminado o preparar entrega | [`references/qa-y-entrega.md`](references/qa-y-entrega.md): instrumentos, denominadores, checklist y límites |
| Arte, audio, fuentes, atlas, assets propios/libres, traducción o generación que cuesta dinero | [`references/assets-y-texto.md`](references/assets-y-texto.md) |
| Buscar por significado, clasificar/deduplicar, ahorrar contexto o integrar embeddings/RAG | [`references/contexto-y-recursos.md`](references/contexto-y-recursos.md): consumidor existente, privacidad, reserva y medición |
| Elegir género, disciplina, tutorial o nivel de aprendizaje | [`references/rutas-de-consulta.md`](references/rutas-de-consulta.md) |
| Diseño por disciplina y orden de lectura | [`references/mapa-disciplinas.md`](references/mapa-disciplinas.md) |
| Localizar el título/ruta exactos de un documento | [`references/indice-documentos.md`](references/indice-documentos.md). |

Un desarrollo completo combina desarrollo/asesor → API/operación y assets según los sistemas → QA.
Proyecto largo, varios agentes, gauntlet, crítica o cambio de harness: abre `13/29` completo
si la biblioteca está disponible. Enseñanza continuada: abre `RUTA.md` y sitúa el nivel por
lo que el usuario sabe hacer; ofrece material de ese nivel y el siguiente.

## Contratos que siempre se conservan

- **Verifica cada símbolo y la firma completa antes de recomendarlo**, también en prosa.
  Índice compatible → manual oficial aplicable → notas oficiales por versión; nunca memoria.
  Sin índice o sin CLI, usa el manual oficial web, con rama/versión, URL y fecha. Si la fuente
  no cubre el target, di «no verificado». No inventes funciones ni argumentos.
- Una ausencia solo describe la versión/cobertura consultadas. Revisa `fnames`, structs,
  enumeraciones, plataformas, extensiones y funciones propias. `SOLO EN fnames` es existencia
  sin autocompletado de Feather, no invención. Evita lo obsoleto según la ficha aplicable.
- GML propio: identificadores ASCII, `snake_case`, locales con `_`, prefijos por recurso;
  API en inglés, comentarios y texto visible en español correcto. Desde 2026, los IDs de assets
  son handles; verifica este cambio cuando trabajes con una versión anterior.
- Recursos `.yy`/`.yyp` por ResourceTool/MCP o IDE; `.gml` sí se edita normalmente.
  **Un escritor por proyecto**: ResourceTool guarda incluso con `HELP`; compile/run/package
  comparten `.gmcache`. Verificar leyendo archivos evita otra escritura concurrente.
- Salida «Success» o exit 0 no acredita el efecto. Verifica comando → archivo → juego real.
  `validar-proyecto.py <proyecto> --todo` antes de compilar, si sus fuentes están disponibles;
  el análisis léxico no sustituye runtime. Compilación final también sin `--errors-only`.
- Verde vigente requiere revisión y huellas del WIP/entradas, engine/runtime, target,
  configuración, escenario, aserciones, medidas, omisiones y denominadores. Una batería
  previa es histórica; compilar ahora no la refresca ni certifica p99 o todos los presupuestos.
- Crítica fresca: clave fuera del paquete accesible, sin instrucciones/explicación del
  constructor antes del juicio y con controles negativos e idénticos válidos. Contaminación
  exige nueva ronda. Preferencia visual, mejora integrable y aceptación final son estados distintos.
- Preserva identidad canónica, umbral del usuario, modelos, permisos, recibos y pausa.
  Coordina recursos pesados, orden de bloqueo, FIFO y propiedad verificable; no limpies por nombre.
- No copies código de juegos comerciales. Licencia, estilo y encaje antes de integrar assets;
  usar en el juego y redistribuir la fuente requieren comprobaciones distintas.
  Un rectángulo o PNG de color plano como personaje no acredita arte de producción.
- «Terminado» exige spec y envoltura completas, compilación y comportamiento demostrado,
  checklist `04/00` **y** listas enlazadas `04/41 §4`, `13/05 §4`, `05/02 §4.4`.
  Si no puedes ejecutar, usa maqueta y revisión de lectura con sus límites; declara lo pendiente
  y cada recorte. Publicar, cuentas, gastos y cambios compartidos mantienen sus permisos.

Selecciona el método por fase: contexto → requisitos pendientes → spec → tareas verticales →
implementación/prueba → integración → revisión → evidencia/aceptación. Reutiliza lo existente;
una corrección pequeña no exige rehacer el GDD. El método detallado está en desarrollo.
