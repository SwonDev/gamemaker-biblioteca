# r23 · Actualidad, contratos HTTP e instalación de la skill r48

Fecha: **11-10-2026**. Continuación sobre r47 pública
`99ad60b410d5709521c91012e2c4172ad88c288e`. Se conserva la metodología universal,
la búsqueda multimodal opcional y las tres ilustraciones de [r22](./r22-publicacion.md).
Esta revisión mejora contratos existentes y añade una referencia transversal;
no crea otra metodología ni cambia modelos, runtimes o herramientas instalados.

## 1 · Investigación e implementación

Los [criterios y decisiones de cobertura](./r23-plan-y-criterios.md) distinguen lo que
ya existía de las diferencias comprobadas. La [investigación primaria](./r23-investigacion-versiones.md)
contrasta GMRT 0.22, Beta R8/R9 y CLI publicado 2.4.1 con fechas, revisiones y huellas.
La instalación usada sigue en CLI 2.4.0 y GMS2 2026.0.0.23; las novedades documentadas
no acreditan su instalación ni ejecución.

HTTP comparte ahora un contrato de progreso, ID, propiedad y aceptación de respuestas.
Liveops filtra el código y JSON; telemetría conserva un volcado nuevo cuando llega la
confirmación de otro anterior. El movimiento conserva la magnitud analógica y limita
la diagonal digital. Las referencias de la skill transmiten estos contratos incluso
cuando no está disponible la biblioteca completa.

## 2 · Verificación observada

| Área | Resultado y alcance |
|---|---|
| HTTP e input | **49 comprobaciones correctas / 0 fallidas**; cuatro mutaciones del fixture detectadas. Ocho peticiones y callbacks reales en servidor loopback propio; progreso y ciertos estados son sintéticos. Cinco compilaciones completas sin `WARNING`. [Recibo y límites](./r23-http-ejecucion.md), [huellas y resultados](./r23-http-recibos.json) |
| Herramientas | `actualizar.py` en Python **3.10.21**, salida **0** en el checkout público y en la biblioteca completa. **23** herramientas con autoprueba ejecutadas |
| Enlaces y secciones | Biblioteca completa: **2.305** rutas y **1.640** anclas correctas; público: **2.066** rutas y **1.639** anclas correctas; **0** rotas en ambos. **2.312** citas por número resueltas y **283** documentos sin números repetidos |
| API y descubrimiento | Biblioteca completa: **3.213 / 3.213** símbolos vigentes localizables; checkout público sin el manual opcional: **2.362 / 3.213**. Ambos resuelven **74** tareas de descubrimiento. El denominador de cobertura no es el total de **3.486** símbolos del índice |
| GML documental | **3.477** bloques compilables sin errores de sintaxis; **306** exclusiones declaradas. El análisis no encuentra prefijos del runtime sin resolver. Compilación no equivale a ejecución de todos los ejemplos |
| Manual opcional completo | **3.119** páginas EN/ES comparadas, **0** ausentes, **0** incompletas, **0** literales traducidos. El espejo completo se reconstruye aparte y no forma parte del repositorio público |
| Skill | Paquete **r48**, entrada de **86** líneas y **12** archivos; `quick_validate.py`: `Skill is valid!`. Los doce archivos coinciden por SHA-256 entre fuente pública, raíz y **11** destinos instalados |
| Revisión independiente | Ejes de requisitos y normas; corregidas cabecera de evidencia, nombre propio que podía confundirse con la API precisión de una descripción de control negativo y atribución de la cobertura completa/pública. **0** hallazgos pendientes en la implementación revisada |

Los recuentos pertenecen a las entradas de esta pasada. Los resultados previos de r47
y sus plataformas se mantienen como evidencia histórica, con su alcance original.
La advertencia de Qwen explica que su configuración actual lee `~/.claude/skills`;
la copia de `~/.qwen/skills` por sí sola no acredita selección nativa. No se modifica
su configuración ni se atribuye autoactivación a un modelo.

## 3 · Lectores nativos con el paquete final

Se volvieron a ejecutar los programas publicados de [Pi/OMP](./r22-harnesses-pi-omp.md),
[MiniMax/Hermes/Gentle](./r22-harnesses-minimax-hermes-gentle.md) y
[DSH](../pruebas/probar-dsh.mjs) en fixtures propios, con el paquete r48 final.
Los [resultados y manifiesto](./r23-loaders-recibos.json) identifican sus entradas.

| Lector instalado | Comprobación ejecutada |
|---|---|
| Pi **1.1.0** | **76** aserciones de descubrimiento y paquete; además catálogo, prompt y expansión del cuerpo exacto |
| OMP **18.8.7** | **74** aserciones de providers nativos y `.agents`, campos y paquete |
| MiniMax Code **0.6.5** | Catálogo y lectura exacta del cuerpo |
| Hermes **0.21.5** | Catálogo y lectura exacta; **6** avisos conocidos de sondas de plugins bloqueadas por el fixture |
| gentle-shell / gentle-pi **4.0.0** | Cinco selecciones de directorio y propagación a Pi; no una conversación completa |
| DSH **0.2.0-rc.2** | Un candidato, cuerpo exacto, base de recursos y **12** archivos idénticos; **0** avisos |

macOS arm64, Node **26.7.0**, Bun **1.3.14** para OMP. Todos los procesos terminan
con **0**; **0** peticiones LLM. Las pruebas consultan fixtures y loaders, sin arrancar
un modelo ni reanudar el proyecto fuente. Acreditan lectura y las rutas ejercitadas,
no que cualquier agente elija automáticamente la skill para cualquier prompt.

## 4 · Conservación y límites

La promoción a la biblioteca completa conserva copias previas y coteja los archivos
modificados. El proyecto fuente sigue pausado; revisión, estado local y archivos de
pausa coinciden con el punto inicial. La historia privada permanece fuera de la
publicación; esta se prepara desde la historia pública de r47.

No se ejecutaron Beta/GMRT, otros targets, TLS/CORS, backend remoto, una cola multisesión
ni mandos físicos. Los detalles están en los recibos enlazados. Esta ronda no demuestra
ausencia absoluta de errores; documenta resultados reproducibles y sus límites.
