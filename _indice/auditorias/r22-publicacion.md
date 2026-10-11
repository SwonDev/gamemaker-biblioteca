# r22 · Skill portátil, contratos ejecutados y método visual

Fecha: **11-10-2026**. Revisión r47 desde la publicación r46
`11cee593d313a83013faa559a54425a47468861d`. El método conserva las lecciones de
especificación, tareas verticales, skills por fase, búsqueda semántica opcional,
revisión y aceptación. El proyecto fuente continúa pausado y fuera de la publicación.

## 1. Cambios y evidencia

| Área | Resultado observado y recibo |
|---|---|
| Skill portátil | Paquete de 12 archivos, entrada de 86 líneas y consulta progresiva; ensayo fresco sin biblioteca completa ni CLI. [Prueba y límites](./r22-skill-portatil.md) |
| Destinos nativos | Pi, OMP, MiniMax Code, DSH, Hermes y Gentle Shell: loaders reales descubren y leen el paquete en fixtures aislados. [Pi/OMP](./r22-harnesses-pi-omp.md), [MiniMax/Hermes/Gentle](./r22-harnesses-minimax-hermes-gentle.md), [DSH](./r22-harness-dsh.md) |
| Instalación y sincronización | 19 regresiones de instalación y 12 de sincronización; destinos inválidos se rechazan antes de escribir y CODEX_HOME guía la copia activa |
| Fuente de API | 13 regresiones de selección de runtime; GmlSpec y fnames proceden del mismo directorio. Fuentes inválidas no producen un índice vacío presentado como correcto |
| Ámbito | Diez regresiones de consumidores, con manual y código opcional delimitados; no se incorporan repositorios ni alias externos ajenos |
| Correcciones documentales | Cloud, plural entero CLDR, snapshot/ACK/propiedad, replay, movimiento reducido y getter de blending. [Fuentes y alcance](./r22-lagunas.md) |
| Contratos GML | 214 comprobaciones correctas, cero fallidas; nueve bloques extraídos intactos, cinco archivos GML y 397 llamadas validadas. [Ejecución y límites](./r22-contratos-ejecucion.md) |
| Revisión independiente | Dos ejes de alcance y estándares. Destino Codex, revisión primaria de Steam Cloud, timeout de procesos y aislamiento de la prueba del máximo corregidos |

Las firmas y las fuentes citadas se verificaron en sus versiones aplicables. Las
cuentas de Cloud, los sockets y otros targets conservan sus pruebas propias pendientes;
el banco anterior no acredita esas integraciones. Los trece scripts y las 205
comprobaciones de runtime de r46 no cambiaron: [recibo histórico](./r21-publicacion.md).

## 2. Presentación y consulta

Tres iconos vectoriales propios y tres nuevas ilustraciones explican conocimiento,
método, proyecto, especificación y contexto semántico. [Método visual](<../../Método visual.md>)
conserva las explicaciones en texto y alternativas equivalentes. [Procedencia y prompts](../../assets/readme/README.md).
Las nuevas imágenes tienen 1536 × 1024 píxeles y suman 571.110 bytes en WebP, sin EXIF
ni XMP. Son ilustraciones conceptuales, sin métricas ni resultados de juego inventados.

La guía se renderizó con GFM y CSS de referencia de GitHub, en 1440 y 390 píxeles,
claro y oscuro. Las tres imágenes cargan y no hay desbordamiento de página. Esa
previsualización no contiene todo el CSS del anfitrión: el foco se comprueba aparte
en GitHub real antes del cierre de publicación.

La comprobación de enlaces descubrió un grupo atómico de expresión regular disponible
desde Python 3.11, incompatible con el mínimo anunciado de 3.10. Se sustituyó por
lookahead y referencia de captura. La autoprueba pasó de rojo a verde en Python 3.9.6;
4.500 combinaciones de etiquetas y separadores coinciden con el patrón anterior en
Python 3.12. El caso `2.5D` no se reduce falsamente a la sección `2`.
Fuente: [novedades de re en Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html#re).
Esto verifica esa expresión; el requisito general sigue siendo Python 3.10 o posterior.

## 3. Estado de la publicación

El mantenimiento completo termina con **exit 0** tanto en el checkout público como
en la biblioteca con corpus, usando un entorno aislado de Python **3.10.21** con las
dependencias declaradas. Se ejecutan 23 herramientas con autoprueba, 74 tareas de
descubrimiento y la compilación de 3476 bloques; 306 fragmentos tienen exclusiones
explícitas. En la biblioteca completa, los 3213 símbolos vigentes son localizables
y se comparan 3119 páginas del espejo sin ausencias, incompletas ni literales traducidos.
El clon público sin manual declara su cobertura parcial y la ausencia de comparación;
no las presenta como defectos ni como pruebas realizadas.

El fixture del instalador perdió el entorno virtual al invocar Python mediante un
symlink nuevo; se sustituyó por un lanzador que ejecuta su ruta original. Las 19
regresiones pasan dentro del entorno virtual de Python 3.10. La comprobación de
codificación declara ahora su alcance estático; no atribuye una ejecución Windows
a herramientas nuevas que solo se inspeccionaron.

Se promovieron 59 archivos públicos a la biblioteca local tras cotejar cada archivo
existente con r46. Copias previas y huellas quedan en custodia privada. El estado del
proyecto pausado se conserva. Se instalaron y compararon los 12 archivos en once
destinos locales, incluidos los seis harnesses nuevos; Codex conserva su enlace
canónico y la vía compartida de Agent Skills. El instalador conservó las copias previas.
Qwen sigue leyendo su ruta configurada a Claude; no se cambió su configuración.

El cierre remoto añade el clon nuevo y la revisión del README y la guía en GitHub.

## 4. Límites

Las pruebas finitas acreditan sus escenarios y entradas. Cargar una skill no demuestra
que todos los modelos obedezcan sus instrucciones. Los loaders se probaron en macOS;
las ramas Windows/Linux se distinguen de una ejecución nativa. PowerShell 7.6.6 se
ejecutó aislado en macOS, sin instalar perfiles. No se modificaron proveedores, modelos,
credenciales ni configuraciones de inferencia. El contenido privado y el código comercial
extraído quedan fuera de los ejemplos y de la historia publicada.
