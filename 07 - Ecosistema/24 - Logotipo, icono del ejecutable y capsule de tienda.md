# 24 · Logotipo, icono del ejecutable y capsule de tienda

> Los tres activos de marca que ve el **100 %** de la gente que se cruza con tu juego, y que
> hoy en la biblioteca solo tenían tablas de tamaños sin receta de cómo llenarlas sin artista
> (`13 · 11 §5` lo señala del tráiler y la capsule: «la partida que se olvida siempre, y la
> única con fecha límite externa»). Este documento cierra ese hueco para las tres piezas:
> **logotipo del juego** (§1), **icono del ejecutable por plataforma** (§2) y **capsule/portada
> de tienda** (§3). No cubre el icono de una habilidad u objeto de inventario — eso ya está
> resuelto en [`07 · 09` §9](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#9-iconos-de-ui-y-habilidades)
> — ni el sprite de un personaje o enemigo, que tiene su propia escalera de prioridad en
> [`12 · 09` §5.2](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano),
> a la que este documento remite para el propio icono de marca.
>
> Todo lo marcado como «verificado en esta sesión» se ejecutó en vivo el 8 de septiembre de
> 2026, en `~/gm_prueba_assets` (creado y borrado al terminar) y en un proyecto real de prueba
> generado con `gm-cli init`, sobre GameMaker LTS 2026.0 (IDE `2026.0.0.16`, runtime
> `2026.0.0.23`) y `gm-cli` **2.3.0**.

---

## 1 · El logotipo del juego

### 1.1 Qué es, y en qué se diferencia de un logo corporativo

Un logo corporativo tiene que funcionar en una tarjeta de visita, un membrete y un favicon: su
exigencia es la neutralidad. Un **logotipo de videojuego** tiene un trabajo distinto y más
concreto — comunicar el género y el tono en el primer medio segundo, y seguir siendo legible
**a 120 × 45 px**, que es el tamaño real al que Steam reduce tu *small capsule* en la lista de
la tienda (verificado en `13 · 11 §6.2`). Si el título no se lee a ese tamaño, el logo está mal
por bonito que sea a resolución completa — es la misma regla que ya fija esa sección para la
capsule, aplicada al logo que va dentro de ella.

Dos decisiones que se toman una vez y no se cambian: **la tipografía** (o el trazo a mano si el
logo es ilustrado) y **la paleta**, que debería ser un subconjunto de la paleta de arte del
juego (`13 · 03 §2`) para que el logo no parezca pegado con pegamento sobre la interfaz.

### 1.2 Receta: `codex exec` + `gpt-image-2`

Genera 2-3 variantes y elige — nunca la primera que sale. Comando **probado en esta sesión**
(se generó un icono de personaje real con exactamente este patrón; ver la evidencia en
`12 · 09 §5.2`, peldaño 3):

```bash
codex exec -C <dir_proyecto> --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
  -o <scratch>/codex_last.txt \
  "Usa tu herramienta de generación de imágenes (gpt-image-2) para crear un logotipo del
   videojuego '<nombre>': tipografía <estilo>, paleta <colores del juego>, sin fondo o con
   fondo neutro, sin marcas de agua, legible en miniatura. Genera 3 variantes de composición
   distinta. Guarda los PNG en <ruta>, a 2000 px de ancho como mínimo. Al terminar lista las
   rutas exactas."
```

El criterio de cuándo es aceptable IA generativa en una pieza de marca puntual sin animar —y
qué declarar si publicas en Steam o itch.io— ya está resuelto con fuente primaria y fecha en
[`07 · 23` §5](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#5--dónde-encaja-en-un-pipeline-real--recomendación-práctica):
un logotipo entra en la fila «Icono o pieza de UI puntual sin animar» — se puede usar, pero
**declarando siempre**, porque pesa el riesgo de propiedad intelectual de esa misma sección §4.1
(sin edición humana sustancial, la pieza generada puede no ser registrable como tuya). Si el
logo es la imagen de marca central del juego, la vía más segura sigue siendo generar
**referencia** con este mismo comando y pedir a un humano que la redibuje o la retoque a fondo.

### 1.3 Checklist de legibilidad

Mismo criterio que exige `13 · 03 §8.1` para un sprite, aplicado a una pieza de marca:

- [ ] Se lee **en escala de grises** — si el logo solo funciona por el color, falla en
      cualquier reproducción monocromo (prensa, fotocopia del press kit).
- [ ] Se lee **a 120 × 45 px** (la *small capsule* real de Steam) sin ampliar.
- [ ] Se lee **sobre fondo claro y sobre fondo oscuro** — la ficha de itch.io y el Dock de
      macOS no garantizan cuál de los dos vas a tener detrás.
- [ ] No depende de un detalle fino que desaparezca al escalar (una línea de menos de 2 px a
      tamaño real).
- [ ] Es reconocible **sin el nombre del estudio al lado** — el logo del juego, no el tuyo.

---

## 2 · El icono del ejecutable, por plataforma

### 2.1 El icono maestro

Todo empieza en **un único PNG de 1024 × 1024**, con transparencia si el destino la admite. Es
el tamaño que pide el propio GameMaker para su
[generador de imágenes del proyecto](../09%20-%20Manual%20oficial/manual-lts-2026-es/IDE_Tools/Project_Image_Generator.md)
(«al menos 1024×1024px, y con autoría de 24bit `*.png` que puede tener transparencias») y
también el que exigen `icon_png` (macOS) e `icon_itunes_artwork_1024` (iOS) — verificado abajo.
Consíguelo con cualquiera de los tres peldaños de
[`12 · 09` §5.2](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano)
a resolución alta, o con el logotipo de §1 recortado a formato cuadrado.

### 2.2 La vía nativa de GameMaker: `resourcetool options set` (hallazgo verificado)

Esto no estaba documentado en ningún sitio de esta biblioteca: **`gm-cli resourcetool` puede
escribir directamente en las Game Options de cada plataforma**, sin abrir el IDE. El comando es
`options set platform=<plataforma> property=<propiedad> value=<ruta-al-png>` — descubierto
leyendo `options info platform=<plataforma>` (que documenta cada propiedad con su «Target path»
y su tamaño esperado) y **confirmado copiando un icono real** en esta sesión:

```bash
gm-cli resourcetool eval "options set platform=mac property=icon_png value=icono_maestro.png"
# → "Copied icono_maestro.png -> ${options_dir}/mac/icons/1024.png for mac.icon_png"
```

El archivo aparece de verdad en `<proyecto>/options/mac/icons/1024.png`, con el mismo peso que
el original — comprobado con `ls` y comparando tamaños de archivo, no solo confiando en el
mensaje. La tabla de propiedades reales por plataforma, sacada de `options info`:

| Plataforma | Propiedad | Tamaño esperado | Notas |
|---|---|---|---|
| **macOS** | `icon_png` | 1024×1024 | El PNG se copia tal cual — ver §2.3 sobre si hace falta redondearlo tú |
| **Windows** | `icon` | — (target `icons\icon.ico`) | ⚠️ **Bug verificado, ver §2.4**: no convierte, copia el archivo de origen renombrado |
| **Android** | `icon_ldpi` / `icon_mdpi` / `icon_hdpi` / `icon_xhdpi` / `icon_xxhdpi` / `icon_xxxhdpi` | 36 / 48 / 72 / 96 / 144 / 192 px | Icono clásico, un PNG por densidad |
| **Android (adaptativo)** | `icon_adaptive_ldpi` … `icon_adaptive_xxxhdpi` (primer plano) + `icon_adaptivebg_ldpi` … `icon_adaptivebg_xxxhdpi` (fondo) | 81 / 108 / 162 / 216 / 324 / 432 px | Dos capas por densidad — el generador de imágenes del IDE **no** las rellena (§2.6) |
| **iOS (iPhone)** | `icon_iphone_app_120` / `icon_iphone_app_180` / `icon_iphone_notification_40` / `icon_iphone_notification_60` / `icon_iphone_settings_58` / `icon_iphone_settings_87` / `icon_iphone_spotlight_80` / `icon_iphone_spotlight_120` | 120 / 180 / 40 / 60 / 58 / 87 / 80 / 120 px | Un PNG por combinación de contexto y densidad |
| **iOS (iPad)** | `icon_ipad_app_76` / `icon_ipad_app_152` / `icon_ipad_pro_app_167` / `icon_ipad_notification_20` / `icon_ipad_notification_40` / `icon_ipad_settings_29` / `icon_ipad_settings_58` / `icon_ipad_spotlight_40` / `icon_ipad_spotlight_80` | 76 / 152 / 167 / 20 / 40 / 29 / 58 / 40 / 80 px | — |
| **iOS (App Store)** | `icon_itunes_artwork_1024` | 1024×1024 | El icono maestro, tal cual |

Genera cada tamaño desde el maestro con `sips` (ya en macOS) y wíralo con `options set` —
patrón **verificado** para macOS, Windows y Android en esta sesión:

```bash
# Un tamaño de Android, de ejemplo — el mismo patrón vale para cualquier propiedad de la tabla
sips -z 192 192 icono_maestro.png --out icon_xxxhdpi.png
gm-cli resourcetool eval "options set platform=android property=icon_xxxhdpi value=icon_xxxhdpi.png"
```

Comprueba lo que quedó fijado con `options get platform=<plataforma> property=<propiedad>`.

### 2.3 macOS: ¿PNG plano o squircle?

El manual dice, literalmente, que macOS «necesita suministrar un archivo de icono (formato
`.png`, 1024×1024px)» — no exige redondear las esquinas. Pero GameMaker **no aplica ningún
enmascarado automático** sobre ese PNG al empaquetar el `.app` (a diferencia del catálogo de
iconos de Xcode, que sí redondea la variante moderna «Big Sur» por ti): el PNG que le das es
exactamente lo que ve el usuario en el Dock. Si quieres el acabado «squircle» estándar de macOS
—y deberías, es lo que espera cualquiera que use un Mac—, redondéalo tú antes de dárselo a
`icon_png`. Técnica completa, **verificada en esta sesión** con un icono de prueba (máscara
separada + `DstIn`; una máscara *inline* en el mismo comando sale en blanco):

```bash
# 1. Mascara squircle 1024x1024, SEPARADA del icono (la mascara inline falla)
magick -size 1024x1024 xc:none -fill white -draw "roundrectangle 0,0,1023,1023,230,230" mascara.png

# 2. Componer: el icono a traves de la mascara con DstIn
magick icono_maestro.png mascara.png -alpha set -compose DstIn -composite icono_redondeado.png

# 3. Verificacion honesta: comprueba el PNG a ojo antes de empaquetar nada
sips -z 256 256 icono_redondeado.png --out preview_256.png
```

En esta sesión, el resultado se abrió y se comprobó a ojo (256 px): las cuatro esquinas quedan
redondeadas con el radio correcto y el contenido del icono no se recorta ni se desplaza. Si el
PNG compuesto sale completamente en blanco o transparente, la máscara se aplicó *inline* en vez
de como archivo separado — es el error más común de este paso.

**Cuándo hace falta además un `.icns` de verdad** (no solo el PNG que pide `icon_png`): para
íconos que se usan **fuera** del build de GameMaker — la miniatura de la página de itch.io o
Steam en macOS, un README, un instalador aparte. La receta completa, con máscara + `sips` +
`iconutil`, **verificada produciendo un `.icns` real de 94 KB** (si te sale de ~40 KB, la
máscara falló y quedó en blanco — compruébalo abriendo el PNG intermedio):

```bash
mkdir icono.iconset
for s in 16 32 128 256 512; do
  sips -z $s $s icono_redondeado.png --out icono.iconset/icon_${s}x${s}.png
  s2=$((s*2))
  sips -z $s2 $s2 icono_redondeado.png --out icono.iconset/icon_${s}x${s}@2x.png
done
iconutil -c icns icono.iconset -o icono.icns
```

### 2.4 Windows: el `.ico` real, y un bug de `resourcetool` verificado en esta sesión

El manual exige un archivo `.ico` de verdad para Windows (`Settings/Game_Options/Windows.md`,
sección Imágenes). Genera el multi-resolución con ImageMagick — **verificado**, produce un
`.ico` con las 6 resoluciones estándar embebidas:

```bash
magick icono_maestro.png -define icon:auto-resize=256,128,64,48,32,16 icono.ico
magick identify icono.ico   # confirma 6 entradas, de 16x16 a 256x256
```

🔴 **Bug verificado en esta sesión**: `gm-cli resourcetool eval "options set platform=windows
property=icon value=icono.ico"` **rechaza el `.ico` real** («File does not have a valid PNG
signature») y, si le das en cambio un PNG, lo **copia sin convertir**, dejando un archivo
llamado `icon.ico` que `file` identifica como `PNG image data`, no como un icono de Windows —
confirmado con:

```bash
gm-cli resourcetool eval "options set platform=windows property=icon value=icono_maestro.png"
file "<proyecto>/options/windows/icons/icon.ico"
# → PNG image data, 1024 x 1024 ...  (NO es un .ico real, pese al nombre y al mensaje de éxito)
```

**La vía que sí funciona, verificada**: coloca el `.ico` real generado con `magick` directamente
en esa ruta, sin pasar por `options set` para esta propiedad concreta —
`resourcetool` no lo sobrescribe ni lo valida al hacer `options get`, así que el archivo se
queda tal y como lo dejaste:

```bash
cp icono.ico "<proyecto>/options/windows/icons/icon.ico"
gm-cli resourcetool eval "options get platform=windows property=icon"   # confirma la ruta
file "<proyecto>/options/windows/icons/icon.ico"   # ahora sí: MS Windows icon resource, 6 icons
```

### 2.5 Android e iOS: genera cada tamaño desde el maestro

No hay atajo real: son 12 archivos distintos para Android (6 clásicos + 6×2 adaptativos) y 17
para iOS. Un bucle sobre la tabla de §2.2 con `sips -z <ancho> <alto>` y `options set` por cada
propiedad es mecánico pero real — es exactamente lo que le falta hoy a la fila de checklist de
[`04 · 28` §11](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#11--checklist-móvil-antes-de-publicar),
que hasta ahora solo decía «icono adaptativo (Android) e iconos completos (iOS)» sin receta.
El icono adaptativo de Android es **dos capas** (primer plano + fondo) que el sistema combina y
anima él solo — dale al primer plano el margen de seguridad habitual (el contenido dentro del
66 % central) para que no se recorte al aplicar la máscara del fabricante.

### 2.6 La alternativa desde el IDE: Project Image Generator

Si vas a tocar el IDE de todos modos, GameMaker trae una herramienta —**Herramientas → Project
Image Generator**— que toma tu icono maestro de 1024×1024 y tu pantalla de bienvenida, y rellena
**de una vez** las Game Options de imagen de todas las plataformas de destino, con tres modos de
ajuste (mantener relación de aspecto, estirar, recortar). Es más rápido que `options set` propiedad
por propiedad si tienes el IDE a mano, con una excepción documentada por el propio manual: **no
rellena los iconos adaptativos de Android** — esos siguen necesitando §2.2 o el editor manual. Es
la vía recomendada para un humano; la de §2.2 es la que puede ejecutar un agente sin abrir nada.

### 2.7 Checklist

- [ ] Icono maestro a 1024×1024, mismo criterio de silueta y paleta que el resto del arte
      (`13 · 03 §2`).
- [ ] macOS: decidido si lleva squircle propio (§2.3) — por defecto, sí, porque GameMaker no lo
      aplica por ti.
- [ ] Windows: el `.ico` es un `.ico` de verdad — comprobado con `file`, no solo por el nombre
      (§2.4).
- [ ] Android: las 6 densidades clásicas **y** las 12 del icono adaptativo (primer plano + fondo).
- [ ] iOS: las 17 combinaciones de contexto y densidad, incluida `icon_itunes_artwork_1024`.
- [ ] Cada icono se ve correcto **en su tamaño real**, no solo ampliado — la misma prueba que
      exige `13 · 03 §8.1` para un sprite.

---

## 3 · Capsule y portada de tienda

`13 · 11 §6.2` ya tiene los tamaños verificados de Steam (header, small, main, vertical
capsule, page background, capturas) — **no se repiten aquí**. Lo que falta es cómo llenarlos sin
artista, en orden de prioridad:

### 3.1 La escalera

1. **Compón con arte que el propio juego ya genera.** `captura_tomar()` (verificado en
   `13 · 11 §4.7`, sobre `screen_save`/`screen_save_part`) te da capturas reales del juego, ya
   sin HUD ni overlays de depuración. Recorta la escena más vistosa, añade el logotipo de §1
   encima y un fondo de color de marca donde falte composición. Es la opción con más
   credibilidad: lo que se ve en la capsule es literalmente lo que se juega.
2. **`codex exec` + `gpt-image-2` para una pieza compuesta**, cuando el juego aún no tiene una
   escena lo bastante vistosa para una captura directa. Mismo comando de §1.2, adaptado:

   ```bash
   codex exec -C <dir_proyecto> --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
     -o <scratch>/codex_last.txt \
     "Usa tu herramienta de generación de imágenes (gpt-image-2) para crear una imagen de
      portada de tienda para el videojuego '<nombre>': <descripción de escena/personajes/mood>,
      formato horizontal, sin texto. Guarda 2-3 variantes en <ruta> a máxima resolución. Al
      terminar lista las rutas."
   ```

   Declara su uso según
   [`07 · 23` §4.2](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#42-steam-divulgación-obligatoria-con-exención-explícita-para-herramientas-de-desarrollo)
   (Content Survey de Steam, con el procedimiento paso a paso ya en `13 · 11 §9.4`) y
   [§4.3](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#43-itchio-etiquetado-obligatorio-con-delisting-como-sanción-en-páginas-de-assets)
   (AI Disclosure de itch.io) — la portada de tienda es exactamente el tipo de pieza que ambas
   políticas exigen declarar.
3. **Encarga a un humano** si el juego ya genera ingresos. `13 · 11 §5` ya explica cómo negociar
   el encargo (contrato con cesión de uso comercial, pago por hitos, pedir los originales). Es la
   única partida que la propia biblioteca recomienda no ahorrar, precisamente porque es la más
   vista de todas.

En cualquiera de los tres casos, redúcela a **120 × 45 px** para comprobar que el título sigue
siendo legible — la prueba de la *small capsule* que ya exige `13 · 11 §6.2`, y la misma que
pide §1.3 para el logo por separado.

### 3.2 itch.io: la cover image

itch.io no publica tamaños fijos como Steam, sino una relación de aspecto recomendada: el propio
formulario de subida indica **630 × 500 px** (mínimo 315 × 250 px, la mitad exacta) para la
imagen de portada de la página de un proyecto. El fundador de itch.io (leafo) precisó en el foro
oficial que, si la portada es pixel art, conviene dibujarla directamente a un múltiplo entero
(×2, ×3 o ×4) del tamaño final, para que el reescalado del lado del servidor no la emborrone —
el mismo problema de interpolación que ya cubre `13 · 03 §6.1` para el propio juego.

---

## Checklist final

- [ ] Logo, icono e imagen de tienda comparten **la misma paleta** del juego — no se diseñaron
      por separado sin mirarse entre sí.
- [ ] Los tres se probaron a su **tamaño real mínimo** (120×45 px la capsule/logo, el tamaño de
      icono más pequeño de cada plataforma), no solo a resolución completa.
- [ ] Si cualquiera de los tres usó IA generativa, está **declarado** donde corresponda (Steam
      Content Survey, AI Disclosure de itch.io) y anotado en `CREDITS.md`
      (`07 · 09 §1`).
- [ ] El icono de Windows es un `.ico` real, comprobado con `file`, no una copia renombrada
      (§2.4).
- [ ] Los iconos adaptativos de Android llevan las dos capas, con margen de seguridad en el
      primer plano (§2.5).

---

## Ver también

- [`12 · 09` §5.2 — La escalera de prioridad para sprites, sin el rectángulo plano](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano) — el mismo criterio, aplicado al arte jugable
- [`07 · 23` — Arte generado por IA](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md) — dónde encaja la IA generativa, y el estado legal verificado
- [`07 · 09` §9 — Iconos de UI y habilidades](./09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#9-iconos-de-ui-y-habilidades) — sourcing de iconos de inventario/habilidad, no de marca
- [`13 · 03` §8.1 — Cuándo un sprite está terminado](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md#81-un-sprite-está-terminado-cuando) — el mismo criterio de legibilidad, aplicado al arte jugable
- [`13 · 11` §5 — Assets y pipeline](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline) — presupuesto, licencias, y por qué la capsule no se ahorra
- [`13 · 11` §6.2 — Los activos de la página de Steam (tamaños verificados)](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción%2C%20alcance%20y%20lanzamiento.md#62-los-activos-de-la-página-tamaños-verificados) — la tabla de tamaños que este documento no repite
- [`04 · 28` §11 — Checklist móvil antes de publicar](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#11--checklist-móvil-antes-de-publicar) — la fila de iconos que este documento desarrolla

---

## Fuentes

Todas consultadas el **8 de septiembre de 2026**, salvo indicación contraria.

- **Manual oficial de GameMaker (LTS)** — espejo en `09 - Manual oficial/manual-lts-2026-es/`:
  `IDE_Tools/Project_Image_Generator.htm` (icono maestro 1024×1024, el generador no rellena
  iconos adaptativos de Android) · `Settings/Game_Options/Windows.htm` (`.ico` obligatorio) ·
  `Settings/Game_Options/macOS.htm` (PNG 1024×1024, sin mención de enmascarado automático).
- Verificación en vivo en esta sesión, en `~/gm_prueba_assets` (proyecto de prueba creado con
  `gm-cli init` y borrado al terminar): `options info`/`options set`/`options get` de
  `resourcetool` sobre las plataformas `mac`, `windows` y `android`; el bug del `.ico` de
  Windows (`file` confirma `PNG image data` tras `options set`); la técnica squircle de macOS
  (máscara separada + `DstIn`, `.icns` resultante de 94 KB); `magick -define
  icon:auto-resize=...` para el `.ico` real de Windows.
- itch.io, formulario de subida de proyecto (campo «Cover image», tamaño recomendado
  630×500 px, mínimo 315×250 px) y foro de soporte, hilo *«What's up with the recommended
  cover image resolutions?»*, respuesta de leafo (fundador) sobre pixel art a ×2/×3/×4 —
  <https://itch.io/t/474870/whats-up-with-the-recommended-cover-image-resolutions>.
- [`07 · 23` — Arte generado por IA](./23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md) y sus fuentes primarias (U.S. Copyright Office, Steamworks, itch.io quality guidelines), verificadas el 2026-09-07 y reutilizadas aquí sin re-verificar.
- `13 · 11 §6.2` y §4.7 — tamaños de Steam y `captura_tomar()`, verificados en su propia sesión
  de redacción, reutilizados aquí sin re-verificar.
