# r23 · Investigación de versiones, CLI y GMRT

Fecha de consulta: **11-10-2026**. Investigación de fuentes primarias y contraste de
contenido; no actualización de herramientas, runtimes ni proyectos. Los juegos pausados
no se han ejecutado. Este informe identifica cambios para integrar en los capítulos
existentes; no certifica ejecución de las Betas, GMRT ni todos los targets.

## 1. Fuentes y versiones observadas

| Componente | Publicado al consultar | Evidencia | Relación con esta biblioteca |
|---|---|---|---|
| LTS 2026.0 | IDE `2026.0.0.16`, GMS2 runtime `2026.0.0.23`; Minor Update 1 del 27-05-2026 | [Notas LTS](https://releases.gamemaker.io/release-notes/2026/0.html) | Sigue siendo la referencia comprobada; no se ha descubierto una nueva LTS publicada |
| Beta 2026.100.0 | Release 9, IDE 1171 / runtime 1116, 07-10-2026 | [Notas Beta](https://releases.gamemaker.io/release-notes/2026/100.html) | AGENTS.md y la auditoría r22 ya citan esta versión; faltan varios cambios en los capítulos temáticos |
| GMRT | `0.22.0`, septiembre de 2026 | [Índice oficial de releases](https://releases.gamemaker.io/), [notas 0.22](https://releases.gamemaker.io/release-notes/2026/GMRT_MS_22) | `02 · 03` mantiene el estado de agosto y la versión 0.21; es una ausencia real de novedades posteriores |
| CLI publicado | `@gamemaker/gm-cli@2.4.1`, 28-09-2026 | [Metadatos del registro oficial del paquete](https://registry.npmjs.org/@gamemaker%2fgm-cli), [CHANGELOG fijado](https://github.com/YoYoGames/gm-cli/blob/cf3ca060a50d9cfcc01b254e52c25b7aa6670d39/CHANGELOG.md) | El binario local devuelve `2.4.0`; publicar una nueva versión no refresca las pruebas de la instalada |

La instalación IDE, el runtime seleccionado, el CLI, ProjectTool, PackageTool, ResourceTool
y los paquetes de Prefabs tienen revisiones distintas. La corrección de una pieza no
demuestra la de todas las combinaciones. Esta distinción ya está presente en la metodología
y la skill r47: procede ampliar sus ejemplos de diagnóstico, no crear otro protocolo.

Context7 fue consultado antes de investigar APIs y devolvió cuota mensual agotada.
Se acudió a documentación y código oficiales directos, sin configurar credenciales.

## 2. Hallazgos que cambian decisiones del agente

| Hallazgo | Contenido existente y problema | Integración concreta |
|---|---|---|
| CLI 2.4.1 instala un módulo faltante en el runtime cacheado exacto | `07 · 13` describe 2.4.0 como última publicada en su instantánea y no explica este fallo | Añadir actualización fechada y el diagnóstico de módulo/versión; conservar las mediciones locales 2.4.0 |
| Existe CHANGELOG oficial aunque GitHub tenga cero Releases | `07 · 13` §10 infiere ausencia de notas a partir de cero Releases y README idéntico | Sustituir esa inferencia por una referencia al CHANGELOG, distinguiendo historial publicado y rama de desarrollo |
| CLI 2.4.0 copia los Prefabs que ya tiene el IDE | `07 · 13` §10 solo recoge el cambio de Igor; `12 · 09` empieza con una trampa de Prefabs descrita como fallo de hoy | Explicar alcance del arreglo y las dependencias; no afirmar que el seed resuelve una máquina sin esos paquetes |
| Split workspaces está habilitado en Beta Release 8 | `02 · 09` §1.5 y `02 · 10` §8 aún lo dejan pendiente de activar | Actualizar ambos, acotado a esa Beta y a sus restricciones |
| GMRT 0.22 añade físicas 3D y sombras direccionales | `02 · 03` termina en 0.21; `04 · 29` presenta GM3D como futuro | Añadir la rama experimental 0.22; conservar la tubería clásica GMS2 y su tabla de capacidades |
| Android Beta Release 9 cambia la creación de páginas de fuente y optimiza el arranque | No hay explicación de estas correcciones recientes en `02 · 06`, `02 · 01` ni `12 · 09` | Añadir consecuencias de QA y versión mínima documentada, sin atribuir el arreglo a LTS |
| Las novedades de septiembre/octubre no autorizan fijar el SDK más nuevo | `02 · 01` conserva el snapshot de agosto; la metodología general ya exige verificar versión/target | Extender la tabla de novedades y enlazar la guía SDK de la familia del runtime |

Los capítulos mencionados se consultaron por su contenido, además de buscar los términos
y versiones nuevas en `02`, `04`, `07`, `12` y `13`. Una coincidencia en un catálogo de
repositorios no equivale a un procedimiento operativo, pero tampoco se ha tratado como
ausencia el mero hecho de que un concepto use otra denominación.

## 3. CLI: diferencias verificadas en las fuentes publicadas

### 3.1 De 2.4.0 a 2.4.1

El [CHANGELOG de 2.4.1](https://github.com/YoYoGames/gm-cli/blob/cf3ca060a50d9cfcc01b254e52c25b7aa6670d39/CHANGELOG.md)
contiene una corrección: si un runtime cacheado carece de un módulo, instalar ese módulo
para **esa versión exacta**, en lugar de resolver nuevamente la última versión del feed.
El [commit de la corrección](https://github.com/YoYoGames/gm-cli/commit/38a28126d8895238fcf6b7e5eb6cf46c82949105)
deriva `installVersion` del directorio cacheado antes de resolver la descarga.

Esto importa cuando una compilación YYC encuentra un runtime ya presente con módulos
incompletos. La observación útil es la terna **runtime elegido → módulos presentes →
versión a la que se instala el módulo**. No debe diagnosticarse automáticamente como
GML defectuoso ni resolverse cambiando el runtime del proyecto.

### 3.2 Lo que ya cambió en 2.4.0

La preferencia por el Igor que trae el runtime ya está descrita en `07 · 13` §10.
El [commit 69e2cdd](https://github.com/YoYoGames/gm-cli/commit/69e2cdded44b8566af3f4f36bc7135b75f524db8)
añade otra parte relevante: antes de restaurar, copia los paquetes de Prefabs referenciados
que encuentre en los almacenes del IDE. El código consulta `ForcedPrefabProjectReferences`,
respeta los paquetes presentes junto al proyecto o en la caché y copia los restantes si
los localiza. Si no encuentra el almacén o el paquete, deja la resolución a ProjectTool.

Por tanto, **no prueba** restauración offline universal, descarga desde un registro roto
ni funcionamiento sin IDE o sin paquetes preparados. Las [notas Beta Release 8](https://releases.gamemaker.io/release-notes/2026/100.html)
declaran además arreglado el fallo de proyectos con Prefabs. El
[issue 15984](https://github.com/YoYoGames/GameMaker-Bugs/issues/15984) identifica un desajuste
por reflexión entre PackageTool y GMPM. La vieja matriz de plantillas 2.3.0 sigue siendo
evidencia histórica; no se debe presentar como matriz ejecutada de 2.4.1.

Para diagnosticar, comprobar versiones de los componentes, presencia y procedencia del
paquete, efecto real de la restauración y compilación. El método de control de revisiones
ya existe en `13 · 29`; lo nuevo es este caso concreto y el orden de comprobación.

### 3.3 Publicado no es igual a main

La rama main contiene el [commit e67838d](https://github.com/YoYoGames/gm-cli/commit/e67838d4c087ad88d6de18b04e09abb40e44303e)
del 02-10-2026, que corrige la interpolación del mensaje de parseo de `gm-options.json`.
El paquete publicado **2.4.1 aún conserva** el marcador literal `{parseResults.error}`.
Se comprobó en su bundle `dist/chunk-SZ5CRKP6.js` y en
[la fuente de 2.4.1](https://github.com/YoYoGames/gm-cli/blob/cf3ca060a50d9cfcc01b254e52c25b7aa6670d39/src/gm-options.ts).
No atribuir esa mejora de main a una versión distribuida todavía no acreditada.

### 3.4 Recibo de inspección de paquetes

Las dos tarballs se descargaron en un directorio temporal propio, sin instalar ni ejecutar
sus scripts. Su SHA-512 coincidió con `dist.integrity` del registro. SHA-256 observado:

| Paquete | SHA-256 |
|---|---|
| 2.4.0 | `0eba2f37af00b806dc84f48be73916b7f5e2b934bf7779f2fbe8ff4283e11018` |
| 2.4.1 | `ded26682d95a693c798edf89dfc6eefe3a2781f8126f7fc467c74168701daa7e` |

`gm-cli --version` devolvió `2.4.0` y avisó de 2.4.1 disponible. No se ejecutó una
compilación con 2.4.1. La inspección de fuente demuestra el arreglo implementado; su
comportamiento en un proyecto real exige la prueba correspondiente.

## 4. GMRT 0.22: disponibilidad y contrato de consulta

Las [notas oficiales 0.22](https://releases.gamemaker.io/release-notes/2026/GMRT_MS_22)
añaden físicas 3D mediante Jolt —colisiones, triggers, cuerpos rígidos y vehículos— y
sombras direccionales para mallas estáticas, con skinning e instanciadas. No hay ayuda
de sintaxis en el IDE para estas incorporaciones. La lista de incompatibilidades mantiene
Prefabs, SVG, vídeo fuera de Windows, dos métodos de medida Flexpanel, comprobaciones
de existencia de vertex buffers/formats y consulta del dibujado de application surface.

La API del ejemplo oficial debe leerse en su **archivo real del recurso Note**:
[GM3D_API.md.txt, revisión bfe720b](https://github.com/YoYoGames/GM3D-Samples/blob/bfe720b1c6025b406fcefd4a4562b954053af44b/notes/GM3D_API.md/GM3D_API.md.txt).
`notes/GM3D_API.md` es un directorio, no un Markdown plano. La nota leída tiene
1.629 líneas, SHA-256
`170e3d526ee76298cf484e6d841fcad2fc04196de7698de3285fdaea9d97b280`.
Declara expresamente su carácter experimental y documenta, entre otros,
`GM3D_PhysicsWorld`, componentes de cuerpo/forma/vehículo y métodos de sombra en
`GM3D_LightComponent`. Es consulta de firmas, **no ejecución de estas capacidades**.

El índice de GMS2 LTS no es autoridad de ausencia para GM3D: no contiene este runtime.
`04 · 29` ya distingue la tubería clásica, por lo que procede actualizar su párrafo de GMRT
y enlazar la fuente aplicable; no introducir esos símbolos en los ejemplos GMS2 ni borrar
el aviso de incompatibilidad. Una integración posterior requiere checkout oficial fijado,
matriz de capacidades, ejecución de sus ejemplos en el target declarado y comparación
antes/después. Esta investigación no atribuye paridad a un juego ni a una plataforma.

## 5. Beta: cambios recientes y consecuencias acotadas

Release 8, del 28-09-2026, añade división horizontal o vertical de workspaces, con una sola
dirección a la vez y varias divisiones de esa dirección; no permite comparar dos eventos
del mismo objeto abriéndolo dos veces. La nota también añade control de audio en modo
silencio de iOS/iPadOS, sin alterar el comportamiento predeterminado, y dependencias
de Prefabs con rangos/minimum IDE version. Release 9, del 07-10-2026, informa de SDKs de
consola actualizados y aviso de valores incompatibles en preferencias, sin cambiarlos
automáticamente. [Notas Beta](https://releases.gamemaker.io/release-notes/2026/100.html).

El [issue 15930](https://github.com/YoYoGames/GameMaker-Bugs/issues/15930) documenta el
empaquetado de texturas externas `.yytex` de GX.games en una ruta distinta de la solicitada
por el runner. El efecto puede aparecer solo al cargar el grupo. Añadir al diagnóstico
**estructura del ZIP → solicitud del navegador → respuesta HTTP → imagen visible**;
la carga inicial o un exit 0 no lo comprueban. La solución de Igor 2.4.0 ya está descrita,
por lo que no se necesita repetirla en otro capítulo.

La corrección Android de las notas R9 cambia la creación de páginas de fuente a demanda:
`font_get_texture()` puede no aportar toda la información en ese momento, y la nota
remite a `font_get_info()`. El [issue 15987](https://github.com/YoYoGames/GameMaker-Bugs/issues/15987)
es el problema de memoria asociado. Debe documentarse como cambio de esa Beta, sin
extrapolarlo al getter de LTS o dar una firma que no se haya contrastado.

El [issue 16078](https://github.com/YoYoGames/GameMaker-Bugs/issues/16078) relaciona ANRs
con pausar o rotar durante la preparación de scripts de un proyecto grande. El equipo
describe una optimización, pero no sustituye el arranque completo por trabajo repartido
en fotogramas. Por eso el QA debe incluir interrupción durante el arranque y dispositivos
lentos; un tiempo menor en un único teléfono no certifica ausencia de ANRs.

La [guía de SDKs 2026.1](https://github.com/YoYoGames/GameMaker-Bugs/wiki/2026.1)
explica que esta familia está disponible como Beta y soporta Xcode 27; las notas R8 lo
sitúan en macOS/iOS/tvOS. Esa compatibilidad no se atribuye a 2026.0. La guía advierte que
usar versiones distintas de las requeridas, también más recientes, puede romper el build.
El permiso para investigar no autoriza modificar SDKs ni publicar en tiendas.

## 6. Integración recomendada sin duplicar

1. **Actualizar fuentes/versiones en `07 · 13`**, ampliando §10 con 2.4.1, el cambio de
   Prefabs de 2.4.0 y el límite main/publicación. Mantener intacta la fecha de cada prueba.
2. **Añadir una actualización fechada en `02 · 01`** y extender su apartado Beta; conservar
   el snapshot anterior como histórico, con la separación clara de LTS/Beta/GMRT.
3. **Extender `02 · 03` con 0.22** y sus fuentes exactas; actualizar los párrafos que hablan
   de compatibilidad/estado actual y no únicamente la cabecera. Corregir la misma distinción
   en `04 · 29` y en el resumen de `02 · 10`.
4. **Actualizar `02 · 09` §1.5** y `02 · 08` §2.12 con los cambios R8, reutilizando las
   secciones existentes. Añadir a `02 · 06` la consecuencia de fuentes Android.
5. **Acotar la Trampa 1 de `12 · 09`** al entorno histórico, enlazar la corrección anunciada
   y exigir reproducción actual antes de descartarla. El archivo ya explica que las
   advertencias envejecen: falta aplicar ese criterio a esta nueva fuente.
6. **La skill ya cumple el contrato de versiones**: si se cambia, añadir solo la remisión
   a la actualización pertinente y el límite del índice para APIs experimentales. No
   convertirla en un changelog ni repetir la guía SDK, la metodología o todas las trampas.

No se ha encontrado necesidad de crear otro manual de CLI, otro protocolo spec-driven
ni otra receta genérica de 3D. El valor nuevo está en actualizar datos y decisiones
operativas de los documentos que ya resuelven esos temas.

## 7. Límites de esta auditoría

- Se contrastaron las secciones citadas, fuentes oficiales y paquetes publicados. No se
  afirma una revisión semántica de todos los documentos de la biblioteca.
- No se instalaron 2.4.1, GMRT 0.22, SDKs ni componentes de IDE. No se ejecutaron demos
  GMRT, dispositivos Android/iOS o consolas. Las correcciones anunciadas no son pruebas
  locales ni verifican todos los proyectos.
- La página pública de roadmap bloqueó el acceso del buscador. Las fechas Q2/Q3/Q4 ya
  escritas para JavaScript/TypeScript/C# continúan siendo planes mientras no haya una
  publicación primaria comprobada. No se infiere disponibilidad porque haya pasado la fecha.
- La función nueva de control de silencio iOS se ha identificado por sus notas, pero no
  se ha localizado su firma en la página del manual consultada. Se puede incluir la noticia
  con su límite; no inventar el nombre ni añadir una llamada GML basada en conjeturas.
