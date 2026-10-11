# r21 · Método universal e instalación pública

Fecha: 11-10-2026. Este recibo documenta únicamente el paquete público de la biblioteca
y la skill. Los inventarios, conversaciones, código, assets y recibos del proyecto privado
que inspiró las lecciones se custodian fuera de la publicación.

## Alcance

La metodología generaliza especificación, tareas, implementación, revisión, aceptación,
orquestación, evidencias y recuperación de recursos. La guía de EmbeddingGemma 2 distingue
búsqueda para agentes e integración en un producto, con evaluación y búsqueda literal.
No instala ni arranca un servicio de embeddings.

La portada se separa de las guías de instalación y consulta. Las tres imágenes son
ilustraciones originales generadas con IA, con [procedencia](../../assets/readme/README.md).
La skill conserva el CLI, modelo y permisos elegidos por el consumidor; no promete
calidad AAA automática ni sustituye las puertas del proyecto.

## Comprobaciones observadas

Entorno de comprobación: macOS, Python 3.12.14, gm-cli 2.4.0 y runtime GMS2 2026.0.0.23.
Las carpetas de prueba son desechables y pertenecen a la biblioteca; el proyecto fuente
permanece pausado.

| Puerta | Resultado observado |
|---|---|
| Instalador aislado | Ocho regresiones pasan: opciones desconocidas, copia completa, copia previa, YAML inválido, fallo de índices, comprobar sin instalar, enlace y destino recursivo bloqueado |
| Ámbito | Quince controles y ocho regresiones de consumidores: repo anidado, alias de raíz, enlace externo/interno, búsqueda, nombres, extracción, corpus registrado y error de expresión regular |
| Scripts reutilizables | Los 13 compilan contra el runtime indicado |
| Ejecución | 205 comprobaciones correctas, cero fallidas, dentro del juego de pruebas |
| Trampas del CLI | Las nueve comprobables siguen vigentes |
| Documentación | 3476 bloques compilables pasan; 305 fragmentos se excluyen con motivos |
| Descubrimiento | Las 74 tareas de consulta se resuelven |
| Revisión | Dos ejes independientes: alcance y normas/privacidad; hallazgos corregidos |

El banco detectó nombres de estado interno compartidos con funciones del reloj y la
depuración. Se separaron conservando la API y se añadieron cinco comprobaciones del
reloj antes de iniciar, inicialización automática y reinicio. Se volvió a compilar y ejecutar.

La portada se renderizó con GitHub Flavored Markdown y las hojas de estilo de GitHub,
a 1440 y 390 píxeles, en claro y oscuro. Ambas imágenes cargan, conservan sus alternativas
de texto y se adaptan sin desbordamiento de página; los comandos largos usan desplazamiento
horizontal. Se comprobó el foco visible con teclado. Los colores de texto previstos sobre
papel tienen contraste 11,74:1 y 5,07:1.

Contrato StyleSeed 5.0.0: lectura editorial, educación, portada y autoridad editorial.
Valoración manual de fuente y píxeles: **94/100** (color 16, jerarquía 16, composición 9,
contenedores 10, accesibilidad 16, movimiento 6, coherencia 12, identidad 9). La anchura de
lectura y la interfaz del anfitrión limitan el control editorial; no se modifica la cuenta
ni el tema del consumidor. Esta puntuación no es una certificación automática.

Las imágenes WebP suman menos de 515 KiB; la vista social JPEG mide 1280 × 640 y ocupa
menos de 1 MB. No llevan EXIF, XMP ni comentarios. La vista social, la descripción,
los temas de descubrimiento y el enlace de instalación están configurados en GitHub.

El instalador anterior ignoraba argumentos desconocidos. La primera regresión expuso
que una opción nueva no era aislamiento suficiente: se verificaron las copias previas y
se restauró la ruta registrada. Los fixtures posteriores aíslan también los destinos
por defecto. El instalador nuevo rechaza opciones desconocidas antes de escribir.

La publicación parte de la historia pública anterior. Los inventarios y recibos privados
se excluyen, y las rutas personales de los ejemplos y registros propios se anonimizan.
Se conserva la atribución legal existente. Esto no reescribe publicaciones históricas.

## Límites

Las pruebas finitas acreditan sus casos y entradas. No certifican ausencia universal de
errores ni el comportamiento nativo de todos los agentes o plataformas. La lectura
estática de un proyecto fuente no reejecuta sus pruebas ni reanuda su desarrollo.
