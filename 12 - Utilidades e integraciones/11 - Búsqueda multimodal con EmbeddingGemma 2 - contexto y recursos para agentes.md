# Búsqueda multimodal con EmbeddingGemma 2 — contexto y recursos para agentes

> Para localizar código, decisiones, documentación y recursos en cualquier proyecto GameMaker.
> Complementa la búsqueda literal y el índice de GML. No es una dependencia obligatoria del
> ejecutable del juego. Contratos del MCP y documentación oficial consultados el 11-10-2026.

## 1 · Dos usos que tienen despliegues diferentes

| Uso | Consumidor | Qué necesita |
|---|---|---|
| Ayuda al desarrollo | IA, diseñador o herramienta de producción | Buscar fuentes con ubicación y procedencia; abrirlas y comprobarlas |
| Función del producto | Juego o herramienta que ofrece RAG, clasificación o recomendaciones | Especificación, runtime compatible, presupuesto, almacenamiento y pruebas del consumidor real |

El primer uso puede ahorrar lectura y contexto del LLM sin añadir embeddings al juego.
El segundo requiere diseño e integración propios; un MCP funcionando en el equipo del autor
no instala el modelo en el ordenador del jugador.

**EmbeddingGemma 2** es el modelo elegido para este método. El identificador upstream es
`google/embeddinggemma-2`; el servicio descrito aquí anuncia `embeddinggemma-2`. Texto/código,
imagen, audio y vídeo comparten un espacio de embeddings. La [ficha oficial de Google](https://huggingface.co/google/embeddinggemma-2)
y su [guía multimodal](https://ai.google.dev/gemma/docs/embeddinggemma/multimodal-embeddinggemma-with-sentence-transformers)
explican modalidades y tareas. No genera la respuesta del agente ni demuestra que un resultado
sea verdadero. Conserva modelo, revisión, precisión y dimensiones; no lo sustituyas en silencio.

## 2 · Elegir búsqueda antes de cargar contexto

| Necesidad | Primera vía | Comprobación después |
|---|---|---|
| Saber si existe una función GML y su firma | `buscar.py <símbolo>` y manual oficial | Índice vigente y firma, sin inferirla desde similitud |
| Nombre, texto, regex o ruta exactos | `rg`; `tg` si está instalado e indexado | Todas las coincidencias pertinentes y sus ámbitos |
| «Dónde se restaura el guardado», sin conocer nombre | `semantic_search`, `kinds: ["code"]` | Abrir implementación, llamadores y pruebas de la frontera |
| Decisión o concepto sin palabra exacta | `semantic_search`, `kinds: ["doc", "pdf"]` | Fuente, fecha, autoridad y decisión posterior |
| Sprite, textura, icono o sonido por descripción | `semantic_search` por modalidad | Inspección/escucha, licencia, identidad, alfa y vigencia |
| Momento de un vídeo o grabación | `semantic_search`, `kinds: ["video", "audio"]` | Revisar el intervalo real, sus límites y su población |
| Recursos similares o casi duplicados | `find_similar` | Bytes, uso y diferencias; similitud no autoriza borrado |
| Clasificar contenido contra etiquetas | `compare`, tarea `classification` | Etiquetas representativas, umbral calibrado y categoría desconocida |
| Agrupar un banco grande | `embed`, tarea `clustering`, y agrupador validado | Cohesión, casos frontera, etiquetas y revisión humana |

La búsqueda literal y la semántica responden a preguntas distintas. Combínalas cuando haga
falta: una descripción encuentra el candidato y un símbolo exacto localiza todos sus usos.
Una puntuación alta no certifica duplicidad, licencia, calidad ni equivalencia de comportamiento.

## 3 · Llamadas reales del MCP

Comprueba primero las herramientas expuestas en el harness. Los siguientes bloques son
argumentos JSON, no código GML ni comandos que se pegan en la terminal. Sustituye las rutas
por las del proyecto o banco autorizado; los marcadores no son rutas existentes.

`semantic_search` para una frontera de código:

```json
{"query":"restaurar todos los archivos del guardado después de una prueba interrumpida","path":"<RUTA_PROYECTO>","kinds":["code"],"k":5,"refresh":true}
```

Para encontrar un recurso por contenido:

```json
{"query":"icono de inventario legible en tamaño pequeño y con fondo transparente","path":"<RUTA_ASSETS>","kinds":["image"],"k":5,"refresh":true}
```

`find_similar` para comparar un archivo con su banco:

```json
{"file":"<RUTA_ASSET_REFERENCIA>","path":"<RUTA_ASSETS>","kinds":["image"],"k":5}
```

`compare` para clasificación contra dos etiquetas ilustrativas:

```json
{"a":[{"image":"<RUTA_ASSET>"}],"b":["icono de interfaz","textura de escenario"],"task":"classification"}
```

`k=5` es un punto de partida del ejemplo, no un límite universal. Añade etiquetas y ejemplos
negativos del proyecto; si ninguna etiqueta alcanza el criterio calibrado, devuelve desconocido.
No confundas el coseno con una probabilidad calibrada de clase.

La interfaz consultada incluye `index_path(path, collection?, wait_seconds?)`,
`index_status(job_id?, wait_seconds?)`, `list_collections` y `integration_guide(topic)`.
Si el indexado devuelve un trabajo pendiente, revisa su cobertura antes de presentar resultados
como completos. `refresh: false` consulta lo existente; no demuestra que el índice esté vigente.

## 4 · Índices acotados, vigentes y recuperables

Acota por proyecto, subcarpeta y modalidad. Evita indexar por defecto el home, el disco,
worktrees duplicados, cachés de compilación, modelos, backups y resultados intermedios.
Separa biblioteca, proyecto, recursos aprobados y archivo histórico en colecciones o raíces
identificables. Incluye solo lo necesario y conserva las exclusiones; no vuelvas invisible un
contrato obligatorio por una exclusión destinada a ahorrar coste.

El MCP consultado respeta `.gitignore` y excluye credenciales. Verifica también las exclusiones
y raíces reales de tu instalación. No incluyas `.env`, trazas con entorno heredado ni secretos
en el corpus para facilitar una búsqueda. Indexar puede escribir cachés o cargar el modelo:
respeta pausa, reservas y permisos. No actualices un índice de un proyecto pausado por iniciativa
propia; usa su estado existente si está autorizado y marca su antigüedad.

El manifiesto conserva ruta, ubicación, huella de fuente, fragmentación, modelo/revisión,
precisión, dimensión y fecha. Índices de configuraciones distintas no se mezclan. Actualiza
incrementalmente lo cambiado y prueba renombrados, borrados e interrupción; una raíz ausente
no autoriza purgarla como si estuviera vacía. Cambiar dimensión o cuantización requiere decisión
y evaluación; el ahorro no autoriza cambiar el modelo elegido.

No borres una colección, fuente o supuesto duplicado sin autorización específica. Una colección
reconstruible no sustituye la custodia de sus originales, licencias y decisiones.

## 5 · Recuperación para ahorrar tokens sin perder la frontera

1. Formula una pregunta acotada con vocabulario del glosario, comportamiento y modalidad.
2. Recupera pocos candidatos con ruta/ubicación/huella; conserva consulta y filtros.
3. Abre las fuentes relevantes y comprueba contrato, llamadores, estado y pruebas. Amplía a
   cuerpos completos cuando la decisión dependa de orden, ámbito, excepciones o restauración.
4. Entrega al implementador un paquete corto: requisito, fragmentos con procedencia,
   fronteras compartidas y controles. Separa autoridad vigente de alternativas históricas.
5. Si cambian entradas, invalida el paquete afectado y vuelve a recuperar; no reenvíes un
   resumen desfasado como fuente actual.

No pegues todo el repositorio o catálogo en cada prompt ni ocultes contradicciones por ahorrar
contexto. Cargar una skill significa leer su procedimiento pertinente; listar veinte nombres
sin usarlos no aporta método. Consulta el mapa y carga por fase, evitando repetir lecturas
vigentes. El agente debe poder volver al original, no depender únicamente de resúmenes de otro.

Mide el ahorro sobre tareas equivalentes: tokens de entrada realmente registrados por el
harness, fuentes abiertas, latencia total, arranque frío, coste de indexación y respuesta correcta.
Contar caracteres no acredita tokens facturados. Comparar una respuesta corta incorrecta con
una lectura completa correcta tampoco acredita una optimización. Conserva casos sin resultado,
latencia de cola y descartes, además de los aciertos.

## 6 · Clasificación, catálogo y deduplicación útiles

Etiquetas como UI, personaje, escenario, ambiente o documento de diseño pueden ayudar a
ordenar candidatos. Añade después metadatos verificables: licencia, autor, versión, resolución,
alfa, duración, idioma, uso y estado de aprobación. Clasificación por contenido no infiere esos
permisos ni convierte un borrador en asset aprobado.

Calibra umbrales con positivos, casi duplicados y negativos del propio banco, agrupando por
fuente autoritativa: todas sus variantes permanecen en un mismo conjunto. Evalúa con fuentes
independientes del entrenamiento/ajuste y sus derivados. No adoptes `0,95` como
prueba universal de duplicidad. Un recorte, un recolor y un original pueden ser necesarios;
registra relaciones sin eliminar por similitud.

## 7 · Si no tienes este MCP o servicio

La biblioteca y la metodología siguen siendo utilizables. Indica que la vía semántica no está
disponible y usa índice, mapa, catálogo y búsqueda literal; no inventes resultados ni descargues
un modelo alternativo. Si el usuario autoriza instalar EmbeddingGemma 2, consulta primero
`integration_guide` cuando esté disponible, o la documentación oficial enlazada si el
MCP aún no está instalado. Comprueba la versión vigente para su plataforma.

El perfil local estudiado sirve una API compatible con OpenAI en
`http://127.0.0.1:8737/v1`, con `POST /embeddings` relativo a esa base. Esa dirección pertenece
al equipo que lo instala; no es un servicio público ni una promesa de la biblioteca. Configura
la base y el identificador real en el consumidor, verifica `GET /v1/models` y no introduzcas
credenciales en ejemplos. La política de autenticación depende del servicio y su exposición.

Para integrarlo en una función de producto, define primero dónde corre, modalidades necesarias,
licencias, presupuesto y actualización del índice. Reutiliza el servicio autorizado en
herramientas locales. En un juego distribuido, evalúa el runtime del destino; no apuntes al
localhost del desarrollador. No se publica ni instala infraestructura remota por este capítulo.

## 8 · Puerta de calidad de recuperación

Prepara consultas representativas y un baseline literal antes de ajustar. Reserva preguntas
fuera del corpus y sus derivados. Mide relevancia de código/documentos/medios, cobertura,
procedencia, errores y coste por modalidad. Fidelidad de vectores, calidad de búsqueda y uso
real por el harness son tres pruebas diferentes; una suite antigua de otra arquitectura no
certifica el cliente actual. Las reglas de [Desarrollo con IA](<../13 - Diseño y producción de videojuegos/29 - Desarrollo con IA - orquestación, crítica y evidencia.md>)
§11.1 conservan ese contrato.

Este capítulo documenta las interfaces consultadas; no afirma haber reindexado el proyecto fuente,
ejecutado su servicio ni medido un ahorro de tokens durante esta revisión.
El [recibo público](../_indice/auditorias/r21-publicacion.md) delimita las pruebas de la biblioteca.
