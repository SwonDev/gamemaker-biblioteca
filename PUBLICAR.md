# Distribuir y reconstruir la biblioteca

Repositorio público: [SwonDev/gamemaker-biblioteca](https://github.com/SwonDev/gamemaker-biblioteca).
[Instalar](INSTALACION.md) · [Contribuir](CONTRIBUTING.md) · [Licencias](LICENSE)

## Qué se distribuye

| Parte | Publicación |
|---|---|
| Documentación propia, skill y herramientas | Incluidas, con licencia MIT o CC BY-SA según [LICENSE](LICENSE) |
| Juego de referencia propio | Código y generadores incluidos; imports opcionales mantienen sus licencias |
| Ilustraciones de la portada y el método | Incluidas, originales y generadas con IA; [procedencia](assets/readme/README.md) |
| Catálogo de terceros | Solo `11 - Código descargado/_RUTAS.json` y `_CATALOGO.md`: enlaces y metadatos |
| Manual oficial y código descargado de terceros | Fuera del repositorio; reconstrucción opcional en el equipo del consumidor |
| Proyectos personales, corpus crudo, conversaciones, fuentes y recibos privados | Fuera de la distribución |
| Índices de símbolos y documentos | Se generan localmente desde el runtime y el contenido instalado |

El conjunto publicable se comprueba en Git y sus commits salientes, no solo con
`.gitignore`. Las carpetas documentales numeradas y los recursos propios forman el ámbito
público; otros árboles locales se excluyen por defecto. Los revisores comprueban contenido
y licencias del candidato exacto. No se considera publicable un proyecto anidado por tener
un nombre parecido al de una carpeta de la biblioteca.

## Qué escribe el instalador

El instalador Python comprueba el manifiesto SHA-256 del paquete, sin regenerar derivados
ni requerir dependencias de mantenimiento. En modo normal prepara todos los destinos
compatibles, conserva las copias anteriores y registra la biblioteca junto a cada destino, con fallback en
`~/.config/gamemaker-biblioteca/ruta`. `--harness` registra también esa ruta; `--destino`
solo cambia el fallback global con `--registrar`. `--comprobar` valida sin escrituras.
[CLI compatibles y límites](INSTALACION.md#qué-cli-de-ia-están-soportados).

El bootstrap descarga solo una revisión identificada de esta distribución pública. Conserva
la biblioteca previa al actualizar y registra el commit descargado. El comando publicado
fija el bootstrap mediante SHA-256; la autenticidad se apoya en HTTPS y el repositorio oficial.

No instala el motor, un LLM ni un servicio de embeddings. No modifica modelos, claves o
proveedores. La skill aporta instrucciones; cada agente controla cuándo las carga.

## Índices del runtime

```bash
python _indice/construir-indices.py
```

Genera `simbolos.json` y `documentos.json` desde el runtime instalado y la biblioteca.
Sin GameMaker/runtime disponible, el comando falla con diagnóstico; los documentos
siguen siendo legibles. El instalador solo solicita este paso con `--indices`, antes
de cambiar instalaciones. La comprobación completa es `python _indice/actualizar.py`.

Sin corpus opcional, el índice sigue contrastando símbolos con el runtime y remite al
manual oficial en línea; las búsquedas en código descargado no tienen corpus local.

## Reconstruir el corpus opcional

```bash
./reconstruir.sh manual
./reconstruir.sh codigo
```

Estos comandos descargan contenido, ocupan espacio y piden confirmación antes de empezar.
Son reanudables. Consulta el catálogo y las licencias antes de reutilizar material.

`codigo` resuelve los repositorios libres catalogados y excluye juegos comerciales y
entradas sin una licencia libre reconocida en su categoría. Puedes revisar la exclusión
sin clonar con `python _indice/reconstruccion/clonar_codigo.py --listar-excluidos`.
El catálogo local no convierte material ajeno en contenido redistribuible.

`manual` obtiene el sitemap LTS español/inglés y convierte HTML a Markdown. El conversor
es una reimplementación verificada contra páginas de muestra; no promete reproducir
cada byte del espejo original ni descarga sus imágenes. Tras reconstruir, puedes
aplicar la memoria de traducción de la biblioteca:

```bash
python _indice/traduccion/tm.py aplicar ""
```

El manual sigue siendo obra de YoYo Games. La traducción y los ejemplos no autorizan
redistribuirlo completo. GameMaker y las marcas asociadas pertenecen a sus titulares;
este proyecto es independiente.

## Puertas de publicación

[CONTRIBUTING.md](CONTRIBUTING.md) enumera mantenimiento, compilación, ejecución,
trampas del CLI, privacidad y verificación visual. Cada recibo declara entradas,
fecha, resultado y límites. [Recibo de esta actualización](./_indice/auditorias/r22-publicacion.md).
