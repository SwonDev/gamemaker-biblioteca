# r22 · Comprobación visual del README y la guía

Fecha: **11-10-2026**. Paquete comprobado:
[`90dc080`](https://github.com/SwonDev/gamemaker-biblioteca/commit/90dc080b733192cd5e39f741993469d084ad6e67).
Ámbito: contenido propio del [README](../../README.md), [guía visual](<../../Método visual.md>),
ilustraciones e iconos. GitHub controla su interfaz, las fuentes del Markdown y los temas.

## 1. Evidencia observada

Se renderizaron ambas páginas en **GitHub real**, en 1440 × 900 y 390 × 844, claro y
oscuro. Se inspeccionaron las ocho capturas y la geometría del DOM. Son capturas a
resolución CSS, DPR 1; no se presentan como capturas a doble densidad. Los archivos y
recibos quedan en custodia privada, fuera del repositorio. La previsualización GFM
anterior sirvió de apoyo; esta revisión usa el CSS nativo del anfitrión.

- Las seis imágenes del README y las tres de la guía cargan. Los SVG decorativos tienen
  alternativa vacía junto a títulos completos; las ilustraciones tienen descripción.
- `scrollWidth` de página coincide con 1440 o 390 en los ocho casos. Los comandos largos
  conservan su desplazamiento dentro del bloque de código.
- Tab activa «Explorar la biblioteca» con contorno azul sólido de 2 píxeles; Enter abre
  `GUIA.md`. En la guía, Tab activa «Elegir cómo consultar» con contorno equivalente.
- Se pulsaron los **28 enlaces del README y los 13 de la guía**, incluidos duplicados,
  anclas, carpetas, imágenes ampliables y la página de incidencias. Todos abren un destino
  existente. No se abrió ni envió una incidencia.
- Los colores computados de cuerpo y enlace tienen contraste **15,80:1 / 5,19:1** sobre
  blanco y **17,39:1 / 6,11:1** sobre el fondo oscuro. Es una medición de esos colores;
  no certifica automáticamente cada píxel del raster ni toda la interfaz de GitHub.
- GitHub registra un 404 en `/_global-navigation/payloads.json`, de su navegación global.
  No afecta a las imágenes ni los destinos del contenido propio. No se afirma una consola
  completamente libre de errores del anfitrión.

Las tres nuevas ilustraciones tienen 1536 × 1024 píxeles y suman 571.110 bytes en WebP.
No llevan EXIF ni XMP. [Procedencia, licencia y prompts](../../assets/readme/README.md).

## 2. StyleSeed

Contrato de StyleSeed 5.0.0: **editorial-reading × product-ui × education × landing ×
editorial-authority × editorial-ink × editorial**. Resolución del contrato local:
`--from-lock .styleseed/README-LOCK.md --agent codex --check`, exit 0.
Dirección y razones: [DESIGN.md](../../DESIGN.md), ENERGY 3, RHYTHM 2, MOTION 1.

Valoración manual de fuente y píxeles: **94/100**. Color 16, jerarquía 16, composición 9,
contenedores 10, accesibilidad 16, movimiento 6, coherencia 12, identidad 9.
La anchura y el espaciado de GitHub reducen el control de composición; los enlaces de
prosa son densos en móvil y los detalles pequeños de las imágenes requieren ampliación.
Las explicaciones en texto conservan el contenido esencial. La identidad es consistente,
con el margen de valoración perceptiva propio de ilustraciones conceptuales.

La inspección de píxeles comprueba foco, ritmo, paleta, contraste, fuente de sistema,
lectura y adaptación. La puntuación es una valoración manual orientada por el contrato;
no es una certificación automática ni un resultado de aceptación de un juego.
No se añaden animaciones, formularios ni superficies de datos: sus estados no aplican.

## 3. Delivery Gate de anti-slop

Cada línea corresponde a un punto del gate. PASS acredita el contenido propio y los
escenarios observados; no transforma la revisión en una auditoría de todo GitHub.

- R-02 PASS: README y guía no contienen rayas largas fuera de las excepciones.
- R-03 PASS: ocho geometrías de página sin desbordamiento; imágenes fluidas.
- R-17 PASS: recuentos remiten a pruebas y fuentes; ninguna métrica comercial ficticia.
- R-18 PASS: no hay testimonios ni perfiles de usuarios inventados.
- R-23 PASS: el autor pidió imágenes e iconos; procedencia y carácter conceptual declarados.
- R-24 PASS: 41 enlaces pulsados llevan a páginas, carpetas, anclas o assets existentes.
- R-25 PASS: colores de prosa y enlaces superan 4,5:1; títulos del raster revisados visualmente.
- R-26 PASS: los controles propios son enlaces y todos tienen destino comprobado.
- R-27 PASS: documentación estática sin superficie de datos; instalación enlaza su diagnóstico.
- R-28 PASS: no hay FAQ de relleno.
- R-32 PASS: foco nativo visible de 2 píxeles y navegación con Tab y Enter.
- R-33 PASS: cambios escritos en Markdown, SVG y fuentes; ninguna inyección CSS publicada.
- R-34 PASS: ambas páginas mantienen lectura y geometría en claro y oscuro del anfitrión.
- R-35 PASS: renderizado real, ocho capturas vistas, 41 enlaces pulsados; consola acotada arriba.
- R-36 PASS: ahorro y calidad se evalúan; no se prometen seguridad, rendimiento ni AAA automáticos.
- R-37 PASS: dirección previa en DESIGN.md y diales explícitos.
- R-38 PASS: imágenes identificadas como ilustraciones; características respaldadas por el paquete.
- R-01 PASS: papel y tinta siguen la paleta razonada; sin gradiente ni glow de plantilla.
- R-04 PASS: iconos propios de páginas, comprobación y búsqueda, relacionados con sus títulos.
- R-06 PASS: serif ilustrada para títulos editoriales; fuente de sistema para texto accesible.
- R-07 PASS: no hay cuadrícula decorativa de fondo.
- R-08 PASS: las flechas explican relaciones del método; no adornan botones.
- R-09 PASS: no hay cápsula decorativa sobre el título.
- R-10 PASS: sin glassmorphism.
- R-12 PASS: profundidad en mundos ilustrados; el documento conserva superficies planas.
- R-13 PASS: sin glow ni estados luminosos decorativos.
- R-14 PASS: no hay tarjetas uniformes de features; los bloques sirven a relaciones concretas.
- R-19 PASS: contenido estático, acorde con MOTION 1, sin animaciones ni bucles.
- R-22 PASS: ilustraciones originales conectan conocimiento, tareas y juego.
- Diales PASS: ENERGY 3, RHYTHM 2 y MOTION 1 declarados en DESIGN.md.
- Coherencia de diales PASS: imagen focal y lectura editorial, composiciones distintas y movimiento estático.
- Foco visual PASS: portada en README e ilustración principal en cada relación de la guía.
- Espacio PASS: títulos, párrafos, comandos e imágenes forman grupos de lectura reconocibles.
- Acento PASS: terracota para conexiones clave de las ilustraciones; enlaces nativos en Markdown.
- Motivo PASS: libros, páginas y fichas reaparecen ligados al contenido.
- Design Read PASS: propósito, público, paleta, composición y razones documentados antes de generar.
- C-1 PASS: decisiones principales justificadas en DESIGN.md.
- C-2 PASS: ningún enlace propio carece de comportamiento.
- C-3 PASS: cada bloque resuelve consulta, instalación o comprensión del procedimiento.
- C-4 PASS: móvil, escritorio, ambos temas y navegación de teclado observados.
- C-5 PASS: recuentos y límites ligados a recibos; ninguna valoración automática inventada.
- R-05 PASS: comando, ciclo, explicación y rutas conservan composiciones según su función.
- R-11 PASS: documentos e imágenes planos; ninguna colección de controles en forma de píldora.
- R-15 PASS: destinos concretos: instalar, consultar la skill, especificar, buscar y verificar.
- R-16 PASS: sin promesas de marketing vacías.
- R-20 PASS: libros transformados en mundos y fichas conectan con el trabajo en GameMaker.
- R-21 PASS: ambos temas pertenecen al anfitrión; ninguna preferencia de cuenta modificada.
- R-29 PASS: tinta, papel y salvia, con terracota de acento en las ilustraciones.
- R-30 PASS: contenido editorial propio; ninguna interfaz de producto ajeno imitada.
- R-31 PASS: cada decisión visual principal conserva una razón escrita.

El suplemento UI comparte estas pruebas de paleta, jerarquía, composición, navegación,
movimiento, dosis visuales, datos reales y adaptación. Estados de formularios y tablas no
aplican porque estas páginas no los incorporan.
