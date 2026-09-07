# 24 · Voz, diálogo y localización de audio

> Cómo se **produce** una línea de voz (guion, grabación, edición), cómo se **localiza** a
> varios idiomas sin duplicar sistemas, cómo se subtitulan los efectos de sonido importantes
> con su dirección, y las dos alternativas reales a un lip-sync que GameMaker no tiene.
>
> **Lo que NO cubre**, porque ya está resuelto y enlazado en su sitio: la reproducción y el
> timing de una línea de voz frente al *typewriter* → [`13 · 12` §6.9](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#69-subtítulos-velocidad-de-texto-y-voces)
> y [`04 · 10` §5.6](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md#56-voces-sincronizadas-con-el-typewriter);
> el ducking de música y la mezcla de la voz como referencia de 0 dB →
> [`13 · 09` §4](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#4--la-mezcla); los subtítulos de
> diálogo (caja, nombre del hablante, escala) → [`04 · 27` §2](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md#2--subtítulos-y-texto-legible).

---

## 1 · Los principios

### 1.1 Grabar voz es producción, no un asset más

Un sprite mal recortado se vuelve a exportar en un minuto. **Una línea de voz mal dirigida
cuesta volver a convocar al actor, a la sala y al ingeniero.** Por eso el orden importa: el
guion se cierra y se revisa **antes** de grabar (§2.1), la convención de nombres se decide
**antes** de la primera toma (§2.2), y el idioma de referencia se dobla completo antes de
plantearse los demás (§3.5). Cambiar una línea después de grabada no es editar un `.md`: es
otra sesión de estudio.

### 1.2 Texto siempre, voz cuando compensa

La regla de presupuesto, en una frase: **todo se subtitula, no todo se dobla.** El texto
localizado (`04 · 21`) es barato de generar y de corregir; la voz es cara de grabar, de dirigir,
de editar y de repetir cuando el guion cambia. La voz es una capa **encima** del texto, nunca
un sustituto: un jugador sordo, uno que juega sin volumen y uno cuyo idioma no está doblado
dependen los tres del mismo subtítulo. Qué idioma dobla y cuál solo subtitula es la decisión de
§3.5; qué parte del juego se dobla en absoluto es la de más abajo:

| Contenido | ¿Doblar? |
|---|---|
| Diálogo principal, cinemáticas, tutorial hablado | Sí, si hay presupuesto para el idioma de referencia |
| *Barks* y frases de sistema cortas | Casi nunca: el volumen de líneas (§7) hace el coste inasumible salvo estudios grandes |
| Documentos leídos, *lore* opcional, *flavour text* | Rara vez; son las primeras líneas que un plan ajustado recorta |
| Voces de criatura no verbal (gruñidos, chillidos) | No es «doblaje»: son SFX de personaje → [`13 · 09` §3](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#3--diseñar-un-efecto-de-sonido); o voz procedural → §6 |

---

## 2 · El proceso de grabación

### 2.1 El guion de grabación: una fila, todo el contexto

Un actor que solo ve la frase suelta la actúa mal la mitad de las veces: no sabe si el
personaje está mintiendo, corriendo o a punto de llorar. El guion de grabación es una **tabla**,
no un documento de texto corrido, y cada fila lleva el contexto completo:

| Clave | Personaje | Escena / contexto | Texto | Dirección | Archivo esperado |
|---|---|---|---|---|---|
| `dlg_herrero_intro_1` | Herrero | Primera vez que el jugador entra a la herrería, de espaldas al yunque | «Vaya, un cliente. No es que abunden.» | Seco, sin mirar, sin hostilidad real | `voz_dlg_herrero_intro_1_es.wav` |
| `dlg_herrero_reconoce` | Herrero | Solo si el jugador ya le compró algo antes (`13 · 12` §6.1) | «Tú otra vez. Bien, veamos qué necesitas.» | Más cálido que la línea anterior, ligera sonrisa en la voz | `voz_dlg_herrero_reconoce_es.wav` |
| `bark_aguanta_1` | Ana (compañera) | Vida baja del jugador en cualquier zona (`13 · 12` §3.5/§6.4) | «¡Aguanta, ya casi salimos!» | Gritado, sin aliento, urgencia real | `voz_bark_aguanta_1_es.wav` |

**Columnas que no son opcionales:**

- **Clave** — la MISMA clave que usa la tabla de idiomas (`04 · 21` §1) y el nodo de diálogo
  (`Linea.clave` de [`13 · 12` §6.1](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#61-el-modelo-de-datos-de-la-narrativa)).
  Una clave, un texto, un archivo de voz: nunca tres identificadores para lo mismo.
- **Contexto** — qué está pasando en pantalla, no solo «diálogo con el herrero». El actor actúa
  la escena, no la frase aislada.
- **Dirección** — instrucciones de tono, ritmo y énfasis. «Más contento» no dirige nada: mejor
  «como quien cuenta un chiste que ya ha contado mil veces» o una referencia a otra línea ya
  grabada («como la línea 3, pero más rápido»).
- **Archivo esperado** — se **calcula** de la clave, nunca se inventa a mano (§2.2). Si dos
  filas calculan el mismo nombre, hay una clave duplicada en el guion, no una casualidad.

> 🔺 **Lee el diálogo en voz alta antes de convocar al estudio.** Es la misma prueba de
> [`13 · 12` §4.4](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#44-léelo-en-voz-alta): una frase que
> trastabilla al leerla trastabilla también al grabarla, y ahí ya cuesta dinero.

### 2.2 La convención de nombres: la clave de localización ES el nombre del archivo

El error clásico es inventar un sistema de nombres para el audio distinto del que ya usa el
texto (`dlg_herrero_01.wav` por un lado, `"dialogo_herrero_intro"` por otro) y acabar con dos
tablas que hay que mantener sincronizadas a mano. La regla:

```
nombre del asset de sonido  =  "voz_" + <clave_de_localización> + "_" + <código_de_idioma>

Ejemplos:
  clave "dlg_herrero_intro_1", idioma "es"  →  voz_dlg_herrero_intro_1_es
  clave "dlg_herrero_intro_1", idioma "en"  →  voz_dlg_herrero_intro_1_en
  clave "bark_aguanta_1",      idioma "fr"  →  voz_bark_aguanta_1_fr
```

Esto encaja con dos cosas que ya existen en la biblioteca, sin inventar una tercera:

- El patrón `asset_get_index("voz_" + _archivo)` que ya usa `reproducir_voz()` de
  [`04 · 10` §5.6](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md#56-voces-sincronizadas-con-el-typewriter):
  aquí `_archivo` es `<clave>_<idioma>`, no un nombre de fichero libre.
- Las claves de la tabla de idiomas de [`04 · 21`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md)
  y del grafo de diálogo de `13 · 12` §6.1: **una sola clave gobierna el texto, la voz y el
  nodo**. Cambiar el texto no obliga a renombrar nada del audio.

En disco, antes de importar a GameMaker, la misma convención con carpeta por idioma evita
confundir tomas al mandarlas al estudio:

```
audio/voces/
    es/  voz_dlg_herrero_intro_1_es.wav   voz_bark_aguanta_1_es.wav   …
    en/  voz_dlg_herrero_intro_1_en.wav   voz_bark_aguanta_1_en.wav   …
```

⚠️ **Los nombres de asset de GameMaker son identificadores GML: ASCII puro.** Una clave con
tilde o eñe (`dlg_pequeño_1`) no compila como nombre de recurso. Si el guion en español necesita
esa palabra, la clave se escribe sin acentos (`dlg_pequeno_1`) — el texto sí lleva la ortografía
completa, la clave no ([`05 · 04` — Convenciones](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md)).

### 2.3 La hoja de grabación, generada, no escrita a mano

Copiar a mano las claves del guion de diálogo (`13 · 12` §6.1) y los textos de `es.json`
(`04 · 21` §1) a la tabla del §2.1 es trabajo mecánico y una fuente segura de desincronía en
cuanto el guion cambia una vez más. Con el mismo espíritu reanudable que `traducir_idioma.py`
de [`04 · 21` §5](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#5--traducción-asistida-por-ia--el-flujo-moderno),
un script cruza las dos fuentes de verdad y genera el CSV:

```python
# generar_hoja_grabacion.py — cruza el grafo de diálogo con la tabla de idiomas
# y genera la hoja de grabación (CSV) sin copiar nada a mano.
# Reanudable: si ya existe una hoja de una pasada anterior, conserva "estado" y
# "direccion" de las líneas que ya estaban — el director no pierde su trabajo
# cada vez que el guion crece.
import json, csv, sys, os

idioma = sys.argv[1] if len(sys.argv) > 1 else "es"
ruta_csv = f"hoja_grabacion_{idioma}.csv"

nodos = json.load(open("datafiles/narrativa/nodos.json", encoding="utf-8"))
textos = json.load(open(f"datafiles/idiomas/{idioma}.json", encoding="utf-8"))

# lo que ya había: clave → { estado, direccion } de la pasada anterior
previo = {}
if os.path.exists(ruta_csv):
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            previo[fila["clave"]] = {"estado": fila.get("estado", ""), "direccion": fila.get("direccion", "")}

filas = []
for id_nodo, nodo in nodos.items():
    personaje = nodo.get("quien", "")
    for clave in nodo.get("lineas", []):
        traducida = clave in textos
        anterior = previo.get(clave)
        filas.append({
            "clave": clave,
            "personaje": personaje,
            "escena": id_nodo,
            "texto": textos.get(clave, f"[[{clave}]]"),   # mismo aviso que txt() en tiempo real
            # la dirección la escribe el director (13 · 24 §2.4), nunca el script
            "direccion": anterior["direccion"] if anterior else "",
            "archivo_esperado": f"voz_{clave}_{idioma}.wav",
            # estado: borrador / traducido / revisado / grabado. El script solo AVANZA
            # el estado automático (sin traducir → borrador, traducido → traducido);
            # "revisado" y "grabado" son manuales y, si ya estaban puestos, se conservan
            "estado": (anterior["estado"] if anterior and anterior["estado"] in ("revisado", "grabado")
                       else ("traducido" if traducida else "borrador")),
        })

with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
    escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
    escritor.writeheader()
    escritor.writerows(filas)

print(f"{len(filas)} líneas → {ruta_csv}")
```

> 💡 **Correr esto cada vez que el guion cambie** es la garantía de que la hoja de grabación
> nunca queda desfasada respecto al juego real: el CSV se regenera, pero **el progreso ya
> anotado no se pierde** — solo las líneas nuevas nacen en `borrador`. `[[clave]]` en la
> columna de texto significa lo mismo que en `txt()` de `04 · 21` §2: falta traducir esa línea
> antes de poder marcarla `revisado` ni grabarla en ese idioma.
>
> 🔺 **Si no quieres mantener este script**, [`small_pp_localization_tool`](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte%2C%20audio%20y%20niveles.md#8-localización)
> ya exporta una hoja de traducción a hoja de cálculo, verificada en
> `11 - Código descargado/librerias/localizacion/small_pp_localization_tool`; resuelve el mismo
> problema —una hoja para el traductor o el director, sin copiar texto a mano— sin que tengas
> que escribir ni mantener nada propio.

### 2.4 Dirección de sala

Prácticas de dirección de doblaje que separan una sesión productiva de una que hay que repetir
⚠️ (conocimiento de oficio; no hay una fuente primaria abierta en esta sesión para esta
subsección concreta — ver «Fuentes»):

- **Referencia visual, no solo texto.** Si hay un storyboard, un *animatic* o siquiera un
  boceto de la escena, enséñaselo al actor. Actuar a ciegas produce un tono genérico.
- **Graba siempre 2-3 tomas por línea**, incluso cuando la primera «suena bien». La edición
  (§2.5) decide con calma, la sala no tiene ese lujo.
- **Direcciones de una frase, no de un párrafo.** «Más rápido y más enfadado» se ejecuta; una
  explicación de la motivación del personaje durante tres minutos, no.
- **Deja rodar 1-2 segundos de silencio antes y después de cada toma.** Es lo que necesita la
  edición para recortar limpio sin comerse la primera consonante ni la última.
- **El silencio de la sala también se graba una vez (`ruido de sala`).** Sirve como referencia
  de ruido base para el de-noise en la edición, y para rellenar los huecos si hay que empalmar
  dos tomas de sesiones distintas.

### 2.5 Edición y normalización a la referencia de la mezcla

La edición de voz no vive en GameMaker: pasa por un editor de audio (Audacity — ya catalogado
en [`07 · 09` §5](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md)) **antes**
de importar el fichero. Lo que GameMaker recibe ya tiene que estar:

1. **Recortado**: silencio de sobra al principio y al final fuera, pero sin comerse ninguna
   consonante (§2.4 explica por qué se graba con margen).
2. **Sin ruido de fondo** perceptible — el `ruido de sala` grabado en §2.4 es la referencia para
   un de-noise suave; pasarse de agresivo mete artefactos peores que el ruido original.
3. **Normalizado al mismo pico** que el resto del proyecto: la voz es la referencia de la mezcla
   a **0 dB** ([`13 · 09` §4.1](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#41-la-jerarquía-de-niveles)),
   así que todas las tomas deben quedar al mismo nivel entre sí — una línea gritada y una
   susurrada normalizadas por igual antes de mezclar sería un error: normaliza el **pico**, deja
   que la ganancia relativa de la escena la ponga la mezcla (`voz_decir()` de `13 · 09` §4.2 le
   da a cada línea la misma prioridad; la diferencia de intención va en la interpretación, no en
   el nivel del fichero).
4. **Un fichero por línea**, nunca una sesión entera sin cortar: `asset_get_index` resuelve un
   nombre por línea (§2.2), no un *timestamp* dentro de un fichero grande.

### 2.6 Importar a GameMaker: mono, formato, ¿streamed o no?

Las reglas generales de importación (bitrate, conversión OGG, opciones por plataforma) ya están
en [`13 · 09` §7](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#7--formatos-y-ajustes-de-importación) y
no se repiten. Específico de voz:

- **Mono, siempre.** Una voz grabada en estéreo no aporta espacialidad real y duplica el peso
  sin motivo; y si la línea se reproduce por un emisor posicional (`13 · 09` §5), el motor
  necesita mono para paneársela ([`13 · 09` §5.1](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#51-la-atenuación-el-ajuste-que-todo-el-mundo-olvida)
  y su tabla de errores clásicos).
- **Descomprimir al cargar** para líneas cortas (diálogo normal, *barks*): son las mismas que
  van a un *audio group* por idioma (§3.3) y la descompresión en memoria es barata comparada
  con el coste de decodificar OGG en cada reproducción.
- **⚠️ Los sonidos en *streaming* NO pertenecen a ningún *audio group*** — verificado en
  [`01 · 13` §9](../01%20-%20Fundamentos/13%20-%20Audio.md#9-audio-en-streaming): «los sonidos en
  streaming no pertenecen a ningún audio group». Esto cambia la estrategia para monólogos o
  cinemáticas largas (30 s o más): no se benefician del `audio_group_load()` por idioma de §3.3,
  se gestionan como *stream* individual con la ruta construida a mano:

  ```gml
  /// obj_cinematica_final · Create — un monólogo largo, en streaming, resuelto por idioma
  /// a mano porque el streaming no admite audio groups (01 · 13 §9)
  var _ruta = $"voces/{global.idioma}/cutscene_final.ogg";
  stream_monologo = file_exists(_ruta) ? audio_create_stream(_ruta)
                                       : audio_create_stream($"voces/{IDIOMA_VOZ_POR_DEFECTO}/cutscene_final.ogg");

  /// Clean Up
  audio_destroy_stream(stream_monologo);
  ```

  > 🔺 **`IDIOMA_VOZ_POR_DEFECTO` es una constante del proyecto** (por ejemplo `"en"`), el
  > idioma que sí se dobla siempre y sirve de red de seguridad cuando falta el fichero del
  > idioma activo — la misma idea de doblaje parcial que resuelve §3.5.

---

## 3 · Localización de voz

### 3.1 Un asset por idioma, nunca un array de índices

La tentación es guardar `voz_dlg_herrero_intro_1 = [snd_es, snd_en, snd_fr]` y indexar por
número de idioma. Se rompe en cuanto se añade un idioma nuevo (hay que tocar el array en cada
sitio donde se declaró) y no distingue «este idioma no está doblado» de «me olvidé de rellenar
la posición 3». La convención de nombres del §2.2 (`voz_<clave>_<idioma>`) resuelve las dos
cosas sin estructura extra: **cada combinación clave+idioma es un asset con nombre propio, o no
existe**, y `asset_get_index` es la única «tabla» que hace falta.

### 3.2 Resolución en runtime, con fallback a subtítulos

```gml
// ═══════════ scr_voz_localizada ═══════════
// El patrón asset_get_index("voz_" + …) es el mismo que ya usa reproducir_voz() de
// 04 · 10 §5.6: aquí solo se decide QUÉ nombre construir, según el idioma activo
// (global.idioma, de 04 · 21 §3), y qué pasa si ese nombre no existe.

/// @func voz_localizada_obtener(_clave)
/// @desc Sonido de voz para la clave de localización `_clave` en el idioma actual de
///       global.idioma, o -1 si esa línea no está doblada en ese idioma: el jugador se
///       queda con el subtítulo (13 · 12 §6.9), que es obligatorio y no depende de esto.
function voz_localizada_obtener(_clave)
{
    return asset_get_index("voz_" + _clave + "_" + global.idioma);
}
```

Integrarlo con `reproducir_voz(_archivo)` de `04 · 10` §5.6 es una sola línea: su primera
instrucción, `var _snd = asset_get_index("voz_" + _archivo);`, se sustituye por
`var _snd = voz_localizada_obtener(_archivo);` (donde `_archivo` pasa a ser la clave sin
idioma) y el resto de la función —cortar la voz anterior, sincronizar el *typewriter*— no
cambia ni una línea. Si el proyecto llama directamente a `audio_play_sound`/`audio_play_sound_ext`
en vez de por `reproducir_voz()`, el patrón es:

```gml
/// obj_dialogo · al mostrar la línea `clave_linea_actual`
var _voz = voz_localizada_obtener(clave_linea_actual);
if (_voz != -1)
{
    global.voz_actual = voz_decir(_voz);   // voz_decir(): 13 · 09 §4.2 — corta la anterior con fundido
}
// _voz == -1: no se reproduce nada. El subtítulo de 13 · 12 §6.9 sigue apareciendo igual:
// su duración (subtitulo_duracion()) ya cae al caso «sin audio» de esa misma función.
```

> 💡 **Doblaje parcial sin código adicional.** Si solo grabaste 200 de las 800 líneas de un
> idioma, las 600 restantes simplemente no tienen asset: `voz_localizada_obtener` devuelve -1
> para ellas sin que haga falta una lista de «líneas dobladas» que mantener a mano.

### 3.3 *Audio groups* por idioma

Un *audio group* por idioma agrupa TODAS sus líneas de voz para cargarlas y descargarlas juntas
— la unidad natural, porque el jugador cambia de idioma como bloque, no línea a línea. Convención
de nombre del grupo: `audiogroup_voz_<idioma>` (el grupo se crea en el **Gestor de Grupos de
Audio** del IDE — [`Settings/Audio_Groups`](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Audio_Groups.md)
— y cada `voz_<clave>_<idioma>` se le asigna desde el editor de ese sonido o por lote desde el
Navegador de Activos).

```gml
// ═══════════ scr_voz_idioma — carga/descarga del audio group de voz activo ═══════════
global.voz_grupo_actual = -1;   // -1: ningún grupo de voz cargado todavía

/// @func voz_idioma_cargar(_codigo)
/// @desc Llamar justo después de idioma_cargar(_codigo) de 04 · 21 §1 — al arrancar y cada
///       vez que el jugador cambia de idioma en Opciones. Descarga el grupo anterior antes
///       de pedir el nuevo: solo el doblaje del idioma activo vive en memoria a la vez.
function voz_idioma_cargar(_codigo)
{
    var _grupo_nuevo = asset_get_index("audiogroup_voz_" + _codigo);
    if (_grupo_nuevo == -1)
    {
        show_debug_message($"Sin audiogroup_voz_{_codigo}: idioma sin doblaje, solo subtítulos.");
        global.voz_grupo_actual = -1;
        return;
    }

    if (global.voz_grupo_actual != -1 && global.voz_grupo_actual != _grupo_nuevo
        && audio_group_is_loaded(global.voz_grupo_actual))
    {
        audio_group_unload(global.voz_grupo_actual);
    }

    audio_group_load(_grupo_nuevo);      // ⚠️ ASÍNCRONA: ver el aviso de abajo
    global.voz_grupo_actual = _grupo_nuevo;
}
```

> ⚠️ **`audio_group_load()` es asíncrona — verificado en el manual.** No deja las voces listas
> en la misma línea: dispara la carga en segundo plano y, cuando el grupo entero está en
> memoria, lanza un evento **Async - Save/Load** con `async_load[? "type"] == "audiogroup_load"`
> (manual, `Save_Load.htm`). Reproducir una línea de voz **antes** de ese evento falla en
> silencio (el sonido, sencillamente, no está cargado todavía). El patrón correcto:

```gml
/// obj_control · Async - Save/Load — el grupo de voz ya está listo para reproducirse
if (ds_map_exists(async_load, "type") && async_load[? "type"] == "audiogroup_load"
    && async_load[? "group_id"] == global.voz_grupo_actual)
{
    senal_emitir("voz_idioma_lista", { idioma: global.idioma });   // 04 · 16 — que la UI lo sepa
}
```

> 💡 **En la práctica**, esto solo importa la primera vez que se carga un idioma (o al
> cambiarlo desde Opciones a mitad de partida): el jugador no está esperando una línea de voz
> en ese instante. Si el cambio de idioma ocurre a mitad de una cinemática con voz, muestra un
> indicador de carga breve o retrasa el inicio de la cinemática hasta recibir la señal.

### 3.4 Impacto en el tamaño de build

Dos cosas distintas, y es fácil confundirlas:

| Pregunta | Qué la controla |
|---|---|
| ¿Cuánta RAM ocupa el doblaje **mientras se juega**? | `audio_group_load()` / `audio_group_unload()` de §3.3 — solo el idioma activo vive en memoria |
| ¿Cuánto pesa el **paquete descargable**? | Los objetivos de exportación por plataforma del *audio group*, y las **Configuraciones** del proyecto |

Por defecto, **todos** los *audio groups* personalizados se incluyen en el paquete para
**todas** las plataformas — verificado en el manual (`Settings/Audio_Groups.htm`): «no se pueden
cambiar las opciones de exportación del grupo de audio "por defecto" y [este] siempre se
exportará a todas las plataformas […] cuando construyas un paquete de juego final». Para un
*audio group* **personalizado** (como `audiogroup_voz_fr`) sí puedes elegir a qué plataformas se
exporta, y el manual añade explícitamente que este ajuste **está ligado a las Configuraciones**
del proyecto: puedes crear una Configuración por SKU regional (`Steam_ES`, `Steam_JP`…) y, en
cada una, excluir del paquete los *audio groups* de voz de los idiomas que esa SKU no necesita.
Es más trabajo de configuración (una Configuración por combinación de idiomas que quieras
vender por separado) a cambio de un paquete más ligero por región.

**Para la mayoría de proyectos, la recomendación es la sencilla: una sola Configuración, todos
los idiomas doblados incluidos en el paquete, y `audio_group_load()` controlando solo la RAM.**
Solo vale la pena la ruta de Configuraciones múltiples cuando el doblaje pesa lo bastante (varias
decenas de idiomas, líneas largas) como para que el tamaño de descarga sea, en sí mismo, un
problema de conversión en la tienda.

### 3.5 Cuándo doblar, cuándo doblar parcialmente, cuándo solo subtitular

| Situación | Decisión recomendada |
|---|---|
| Idioma en el que **escribiste** el juego | Doblaje completo si el presupuesto lo permite; si no, subtítulos desde el día uno — nunca al revés |
| Idioma con mercado grande y presupuesto para él (inglés si el original es otro, a veces japonés/alemán/chino) | Doblar si el volumen esperado de ventas lo justifica; si no, subtítulos + el doblaje del idioma de referencia como voz de respaldo (§2.6, `IDIOMA_VOZ_POR_DEFECTO`) |
| El resto de idiomas (localización de «cola larga») | **Solo subtítulos.** Es la norma incluso en juegos AAA: la localización de texto (`04 · 21`) escala a diez idiomas por el precio de una revisión; el doblaje no |
| *Early access* / demo | Un único idioma doblado (el de referencia), subtítulos en todos los demás mientras se valida si el juego sigue cambiando de guion |

> ⚠️ **La síntesis de voz por IA (TTS) es una opción intermedia real en 2026**, pero esta
> biblioteca no tiene abierta ninguna integración verificada de TTS con GameMaker en esta
> sesión: no hay una fuente primaria que citar aquí, así que se queda fuera del alcance de este
> documento. Si se investiga, la pregunta correcta no es «¿suena bien?» sino «¿el estudio y el
> reparto original autorizan sustituir su interpretación por un modelo?» — es una decisión de
> producción y de derechos antes que técnica.

---

## 4 · Subtítulos de efectos de sonido con indicador direccional

### 4.1 Lo que ya existe, y lo que falta

Dos mitades de esta pauta de accesibilidad ya están resueltas por separado:

- [`04 · 27` §5.3](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md#53--el-indicador-visual-la-otra-mitad-de-la-pauta)
  dibuja la **flecha** en el borde de la GUI apuntando a una fuente de sonido
  (`indicador_sonido_mostrar(_wx, _wy)`), reutilizando el ángulo del sistema de mono/estéreo de
  esa misma sección.
- [`13 · 09` §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8--herramientas-licencias-y-accesibilidad)
  pide el **texto** (`[puerta crujiendo]`) y lo remite a `04 · 27` §2, que solo cubre el
  subtítulo de **diálogo**.

Lo que falta, y que ninguno de los dos resuelve, es el **registro** que une un sonido con su
descripción, la **cola visual** que apila varios textos a la vez (una puerta y unos pasos en el
mismo segundo), y el disparo **desde el mismo evento** donde suena el efecto — para que texto y
audio nunca se desincronicen. Esta sección construye esas tres piezas **encima** de las dos que
ya existen, sin reimplementar la flecha.

### 4.2 El registro sonido → texto

```gml
// ═══════════ scr_subtitulos_efecto ═══════════
// Se apoya en indicador_sonido_mostrar()/indicador_sonido_dibujar() de 04 · 27 §5.3 para la
// flecha de dirección: aquí SOLO se añaden el texto, el registro y el apilado.

/// obj_control · Create — una vez, junto a indicador_sonido_iniciar() de 04 · 27 §5.3
function subtitulos_efecto_iniciar()
{
    global.__subtitulos_efecto = [];            // cola visible: { texto, vida, vida_max }
    global.__registro_subtitulo_efecto = {};    // nombre del asset de sonido -> clave de texto
}

/// @func subtitulo_efecto_registrar(_sonido, _clave_texto)
/// @desc Une un sonido con su descripción accesible («[puerta crujiendo]»). Se llama una vez
///       por sonido, al iniciar el juego — es la tabla de la hoja de sonido de 13 · 09 §9,
///       columna «Notas: lleva subtítulo», convertida en datos.
function subtitulo_efecto_registrar(_sonido, _clave_texto)
{
    struct_set(global.__registro_subtitulo_efecto, audio_get_name(_sonido), _clave_texto);
}
```

```gml
/// obj_control · Create — el registro se rellena junto a la hoja de sonido del proyecto
subtitulos_efecto_iniciar();
subtitulo_efecto_registrar(snd_puerta_cruje,   "sfx_puerta_cruje");
subtitulo_efecto_registrar(snd_pasos_espalda,  "sfx_pasos_detras");
subtitulo_efecto_registrar(snd_jefe_ruge,      "sfx_jefe_ruge");
// "sfx_puerta_cruje" etc. son claves normales de la tabla de idiomas (04 · 21 §1):
// {"sfx_puerta_cruje": "[puerta crujiendo]"} en es.json — se traducen igual que cualquier texto.
```

### 4.3 La cola apilada, en el mismo evento que el audio

```gml
/// @func sonido_importante_anunciar(_sonido, _wx, _wy, _duracion_seg = 3)
/// @desc Llamar en el MISMO evento donde se reproduce `_sonido` (junto a sonar_limitado() de
///       13 · 09 §3.3, o justo después). Si el sonido está registrado (§4.2) y los subtítulos
///       están activos, apila el texto Y dispara la flecha de dirección — las dos mitades de
///       la pauta, un único punto de llamada, cero riesgo de que se desincronicen.
function sonido_importante_anunciar(_sonido, _wx, _wy, _duracion_seg = 3)
{
    if (!global.a11y.subtitulos) return;

    var _clave = struct_get(global.__registro_subtitulo_efecto, audio_get_name(_sonido));
    if (is_undefined(_clave)) return;      // sonido no registrado: no se considera "importante"

    var _pasos = round(_duracion_seg * game_get_speed(gamespeed_fps));
    array_push(global.__subtitulos_efecto, { texto: txt(_clave), vida: _pasos, vida_max: _pasos });

    indicador_sonido_mostrar(_wx, _wy, _pasos);   // 04 · 27 §5.3 — la flecha, sin reimplementarla
}

/// obj_juego · Draw GUI — apilados justo encima de la caja de diálogo de 04 · 27 §2
function subtitulos_efecto_dibujar()
{
    var _gw = display_get_gui_width();
    var _y  = display_get_gui_height() - 200;

    for (var _i = array_length(global.__subtitulos_efecto) - 1; _i >= 0; _i--)
    {
        var _s = global.__subtitulos_efecto[_i];
        _s.vida -= 1;
        if (_s.vida <= 0) { array_delete(global.__subtitulos_efecto, _i, 1); continue; }

        draw_set_alpha(min(1, _s.vida / 15));    // se apaga suave, igual que la flecha de 04 · 27
        draw_set_colour(c_ltgray);
        draw_text(_gw - 420, _y, _s.texto);      // "[puerta crujiendo]"
        draw_set_alpha(1);
        _y -= 26;
    }
}
```

### 4.4 Ejemplo completo

```gml
/// obj_puerta · Collision con obj_jugador — el punto donde ya se reproduce el sonido
var _snd = sonar_limitado(snd_puerta_cruje, 2, db_to_lin(-8), 20);   // 13 · 09 §3.3
sonido_importante_anunciar(snd_puerta_cruje, x, y);                  // el texto + la flecha
```

Una sola línea añadida al código que ya reproducía el sonido. Si la fuente está dentro de
pantalla, `indicador_sonido_mostrar` sigue dibujando la flecha igualmente — para efectos
importantes, GAG no distingue «visible» de «fuera de cámara»; quien no oye necesita el aviso en
los dos casos. Si se prefiere ahorrar la flecha cuando la fuente ya se ve, condiciona la llamada
con `en_pantalla(_wx, _wy, 0)` de [`13 · 09` §5.4](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#54-dentro-y-fuera-de-pantalla).

---

## 5 · Lip-sync básico en 2D

### 5.1 Por qué no hay una función que dé la amplitud en tiempo real

⚠️ **Verificado con `python3 "_indice/buscar.py" --listar audio_`: los 130 símbolos `audio_*`
del runtime no incluyen ninguna función de análisis de amplitud o de espectro sobre un sonido
en reproducción.** Hay posición de reproducción (`audio_sound_get_track_position`), pero no un
`audio_sound_get_amplitude()` ni nada parecido. GameMaker no ofrece un lip-sync "gratis" basado
en el volumen instantáneo de la voz: hay que elegir entre las dos alternativas reales de abajo.

### 5.2 La alternativa barata: boca abierta mientras suena

Cero preparación, dos subimágenes (boca cerrada / boca abierta):

```gml
/// obj_boca · Step — mientras la voz de la línea actual esté sonando, boca abierta
image_index = (global.voz_actual != -1 && audio_is_playing(global.voz_actual)) ? 1 : 0;
```

Es «boca que vibra», no lip-sync: no distingue vocales ni consonantes, pero cuesta una línea y
para *barks* o NPC secundarios suele bastar.

### 5.3 La alternativa buena: visemas precalculados fuera de línea

Para personajes principales, la técnica estándar de la animación 2D (Hanna-Barbera, adoptada
por estudios como Disney y Warner Bros., y automatizada hoy por herramientas offline) es
reducir la boca a **6-9 formas** (*visemas*) y decidir, para cada instante de la grabación, cuál
toca mostrar. GameMaker no lo calcula: se calcula **una vez, fuera del motor**, con
**Rhubarb Lip Sync** (`DanielSWolf/rhubarb-lip-sync`, MIT, ★2 597 — verificado en la API de
GitHub el 6 de septiembre de 2026), que analiza un `.wav` y genera un fichero con el visema
activo en cada tramo:

```json
{
  "metadata": { "soundFile": "voz_dlg_herrero_intro_1_es.wav", "duration": 1.87 },
  "mouthCues": [
    { "start": 0.00, "end": 0.05, "value": "X" },
    { "start": 0.05, "end": 0.27, "value": "D" },
    { "start": 0.27, "end": 0.31, "value": "C" },
    { "start": 0.31, "end": 0.43, "value": "B" },
    { "start": 0.43, "end": 1.87, "value": "X" }
  ]
}
```

> — Formato JSON verificado abriendo `README.adoc` del repositorio (2026-09-06). `A`-`F` son los
> seis visemas básicos; `G`, `H`, `X` son opcionales (`X` es la boca en reposo entre frases).

El flujo: para cada `voz_<clave>_<idioma>.wav` grabado, se corre `rhubarb -f json` una vez en
el pipeline de arte/audio y el `.json` resultante se guarda junto al de voz, como
`visemas/<clave>_<idioma>.json`, incluido como *Included File*. En GameMaker se lee igual que
cualquier otro JSON de la biblioteca (mismo patrón que `idioma_cargar()` de `04 · 21` §1 y
`guion_cargar()` de `13 · 12` §6.1) y se consulta comparando su tiempo contra
`audio_sound_get_track_position()` — verificada: «obtendrá la posición (en segundos) dentro del
archivo de sonido».

### 5.4 Código: cargar y reproducir la pista de visemas

```gml
// ═══════════ scr_visemas ═══════════

/// @func visemas_cargar(_ruta)
/// @desc Carga un fichero de visemas (formato Rhubarb JSON, §5.3). Mismo patrón de lectura
///       que idioma_cargar() de 04 · 21 §1: no hay una función de "leer JSON" en el runtime.
function visemas_cargar(_ruta)
{
    if (!file_exists(_ruta)) { return undefined; }   // sin fichero de visemas: cae a §5.2

    var _f = file_text_open_read(_ruta);
    var _crudo = "";
    while (!file_text_eof(_f)) { _crudo += file_text_read_string(_f) + file_text_readln(_f); }
    file_text_close(_f);

    return { cues: json_parse(_crudo).mouthCues, indice: 0 };
}

/// @func visemas_actualizar(_pista, _voz)
/// @desc Llamar cada Step mientras `_voz` esté sonando. Devuelve la letra del visema activo
///       ("A".."H", "X"), o "X" (reposo) si no hay pista o la voz ya no suena.
function visemas_actualizar(_pista, _voz)
{
    if (is_undefined(_pista) || _voz == -1 || !audio_is_playing(_voz)) { return "X"; }

    var _t = audio_sound_get_track_position(_voz);
    var _n = array_length(_pista.cues);

    // El puntero solo avanza (nunca retrocede): coste O(1) amortizado por frame,
    // no una búsqueda completa en cada Step.
    while (_pista.indice < _n - 1 && _t >= _pista.cues[_pista.indice + 1].start)
    {
        _pista.indice += 1;
    }

    return _pista.cues[_pista.indice].value;
}
```

```gml
/// obj_boca · Create
mapa_visemas   = { A: 0, B: 1, C: 2, D: 3, E: 4, F: 5, G: 6, H: 7, X: 8 };  // orden de spr_boca
pista_visemas  = undefined;

/// obj_dialogo · al reproducir la línea (junto a voz_localizada_obtener() de §3.2)
var _voz = voz_localizada_obtener(clave_linea_actual);
if (_voz != -1)
{
    global.voz_actual = voz_decir(_voz);
    obj_boca.pista_visemas = visemas_cargar($"visemas/{clave_linea_actual}_{global.idioma}.json");
}

/// obj_boca · Step
var _letra = visemas_actualizar(pista_visemas, global.voz_actual);
image_index = struct_get(mapa_visemas, _letra);
```

> 💡 **Si el retrato entero cambia de subimagen por emoción** (como en
> [`04 · 10` §4.3](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md#43-retratos)),
> el visema no sustituye esas subimágenes: va en una capa de boca **separada**, superpuesta al
> retrato, para poder combinar «triste» + «vocal abierta» sin multiplicar sprites por cada
> pareja emoción×visema.
>
> ⚠️ **Rhubarb Lip Sync es una herramienta de terceros que corre fuera de GameMaker** (línea de
> comandos, no una extensión GML): entra en el pipeline de producción de audio, no en el
> proyecto. Licencia MIT — verificada en `LICENSE.md` del repositorio (2026-09-06): el resultado
> del análisis es tuyo sin condiciones adicionales.

---

## 6 · Voces procedurales (galimatías tipo Animal Crossing)

⚠️ La técnica de sustituir la voz real por un «blip» sintético por sílaba, popularizada por
juegos como *Animal Crossing* o *Banjo-Kazooie*, es dominio público del oficio: no hay
documentación oficial de esos estudios abierta en esta sesión, así que lo de abajo es una
implementación propia de la biblioteca sobre piezas ya verificadas, no una réplica de un sistema
comercial concreto.

### 6.1 Dos vías

| Vía | Cómo | Cuándo |
|---|---|---|
| **A — banco de grabaciones** | 4-10 «blips» cortos (0,1-0,2 s) por tipo de voz, con el *round robin* + variación de tono de [`13 · 09` §3.2](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#32-variaciones-y-round-robin) | Recomendada: coste de CPU nulo, control total del timbre |
| **B — síntesis en tiempo real** | Un tono corto generado con `tono_generar()` de [`08 · 24` §3](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers,%20colas,%20sincronía%20y%20grabación.md#3--buffer-sounds-síntesis-y-audio-procedural-en-tiempo-real) | Cero assets, útil en un *jam*; cuesta CPU por carácter y exige liberar el *buffer sound* al momento |

### 6.2 El «blip» enganchado al *typewriter*

**Vía A**, apoyada en el mismo punto donde el *typewriter* de
[`04 · 10` §4.2](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md#42-typewriter-effect)
revela un carácter nuevo:

```gml
/// obj_dialogo · Create
personaje_actual = { banco_blips: banco_crear([snd_blip_1, snd_blip_2, snd_blip_3, snd_blip_4]),
                     tono_base: 1.15 };   // > 1 aguda, < 1 grave — un valor por personaje

/// obj_dialogo · Step — el typewriter de 04 · 10 §4.2, con el blip añadido en el ÚNICO
/// punto donde aparece un carácter nuevo (no en cada frame de espera)
contador_frames += 1;
if (contador_frames >= retardo_actual && indice_caracter < string_length(texto_actual))
{
    indice_caracter += 1;
    contador_frames = 0;

    var _c = string_char_at(texto_actual, indice_caracter);
    switch (_c)
    {
        case ".": case "!": case "?": retardo_actual = velocidad_base + 12; break;
        case ",": case ";": case ":": retardo_actual = velocidad_base + 6;  break;
        default:                      retardo_actual = velocidad_base;
    }

    if (_c != " ")   // sin blip en los espacios: silencios entre palabras, como al hablar
    {
        audio_play_sound_ext({
            sound:    banco_siguiente(personaje_actual.banco_blips),   // 13 · 09 §3.2
            priority: 5,
            gain:     db_to_lin(-14) * variacion_ganancia(2),           // 13 · 09 §3.2 — bajo: es ambiente
            pitch:    personaje_actual.tono_base * variacion_tono(2.5)  // 13 · 09 §3.2
        });
    }
}
```

**Vía B**, mismo punto de enganche, sustituyendo el banco por síntesis y liberando el sonido en
cuanto termina:

```gml
/// obj_control · Create
global.__blips_sintetizados = [];   // { sonido, buffer } pendientes de liberar

/// obj_dialogo · en el mismo bloque de arriba, en vez de banco_siguiente()
if (_c != " ")
{
    var _hz = personaje_actual.tono_base * irandom_range(280, 420);
    var _t  = tono_generar(_hz, 0.06);            // 08 · 24 §3 — onda cuadrada de 60 ms
    audio_play_sound(_t.sonido, 5, false);
    array_push(global.__blips_sintetizados, _t);
}

/// obj_control · Step — poda y libera los que ya han terminado (08 · 24 §3: fuga si no se libera)
for (var _i = array_length(global.__blips_sintetizados) - 1; _i >= 0; _i -= 1)
{
    var _b = global.__blips_sintetizados[_i];
    if (!audio_is_playing(_b.sonido))
    {
        audio_free_buffer_sound(_b.sonido);
        buffer_delete(_b.buffer);
        array_delete(global.__blips_sintetizados, _i, 1);
    }
}
```

> 💡 **La voz procedural NO se localiza como el §3**: no hay «blip en francés». Es el mismo
> banco o la misma síntesis para todos los idiomas del texto que acompaña — la localización de
> este sistema es, precisamente, no tener que doblar esas líneas.

---

## 7 · Barks de voz y anti-repetición

El sistema de *barks* por especificidad y su enfriamiento (*cooldown*) **ya están resueltos**
en [`13 · 12` §3.5 y §6.4](./12%20-%20Diseño%20narrativo%20y%20diálogos.md#64-barks-reglas-ordenadas-por-especificidad)
(`BancoBarks`, `elegir()`, un `cooldown_us` por regla) y no se repiten aquí: ese sistema decide
**qué línea** suena. Lo que añade la voz es un segundo nivel de variación dentro de la MISMA
línea, para que «¡Aguanta!» no suene exactamente igual las tres veces que la regla la elige en
una partida: si un *bark* tiene varias tomas de voz grabadas para la misma clave de texto (por
ejemplo `bark_aguanta_1_es_v1.wav` y `..._v2.wav`), se seleccionan con el mismo *round robin*
`banco_crear()`/`banco_siguiente()` de [`13 · 09` §3.2](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#32-variaciones-y-round-robin)
que ya evita repetir la toma anterior:

```gml
/// obj_narrativa · Create — un banco de tomas de voz POR clave de bark, no solo un archivo
global.tomas_bark = {
    bark_aguanta_1_es: banco_crear([voz_bark_aguanta_1_es_v1, voz_bark_aguanta_1_es_v2]),
};

/// al mostrar el bark que devolvió global.barks.elegir() (13 · 12 §6.4)
var _clave_bark = global.barks.elegir(_hechos);
if (!is_undefined(_clave_bark))
{
    bark_mostrar(txt(_clave_bark));   // texto — 13 · 12 §6.4
    var _clave_voz = _clave_bark + "_" + global.idioma;
    if (struct_exists(global.tomas_bark, _clave_voz))
    {
        voz_decir(banco_siguiente(struct_get(global.tomas_bark, _clave_voz)));   // 13 · 09 §4.2
    }
}
```

El enfriamiento de **qué** bark puede repetirse ya vive en la regla (`ultimo_us` de
`13 · 12` §6.4); este banco solo evita que, dentro de ese mismo bark, suene siempre el idéntico
archivo de audio.

---

## 8 · QA de voz

[`13 · 10` — Testing y QA](./10%20-%20Testing%20y%20QA.md) ya avisa de que el audio **no** se
verifica con pruebas automáticas de assert (se comprueba que el juego *decide* reproducir el
sonido correcto, no que suene bien) y [`13 · 09` §10.1](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#101-checklist-antes-de-publicar)
ya pide escuchar en varios altavoces. Específico de voz y localización:

### 8.1 El informe de cobertura por idioma

Lo que SÍ es comprobable por código: que cada clave de diálogo tiene (o no) un asset de voz
para cada idioma activo, sin tener que jugar el juego entero en cada idioma para descubrirlo.

```gml
/// @func voz_qa_reporte(_idiomas)
/// @desc Recorre todas las líneas del guion (13 · 12 §6.1) y para cada idioma en `_idiomas`
///       cuenta cuántas claves tienen doblaje y cuáles no. Pensada para una tecla de depuración
///       o un build de QA, no para el juego final.
function voz_qa_reporte(_idiomas)
{
    var _ids_nodo = struct_get_names(global.guion.nodos);

    for (var _i = 0; _i < array_length(_idiomas); _i += 1)
    {
        var _idioma    = _idiomas[_i];
        var _con_voz   = 0;
        var _sin_voz   = [];

        for (var _n = 0; _n < array_length(_ids_nodo); _n += 1)
        {
            var _nodo = global.guion.obtener(_ids_nodo[_n]);
            for (var _l = 0; _l < array_length(_nodo.lineas); _l += 1)
            {
                var _clave = _nodo.lineas[_l].clave;
                if (asset_get_index("voz_" + _clave + "_" + _idioma) != -1)
                {
                    _con_voz += 1;
                }
                else
                {
                    array_push(_sin_voz, _clave);
                }
            }
        }

        var _total = _con_voz + array_length(_sin_voz);
        show_debug_message($"[{_idioma}] doblaje: {_con_voz}/{_total} líneas");
        if (array_length(_sin_voz) > 0 && array_length(_sin_voz) <= 20)
        {
            show_debug_message($"  sin doblar: {_sin_voz}");
        }
    }
}
```

> 💡 **Esto no distingue «no se dobla a propósito» (§3.5, cola larga) de «se nos olvidó
> grabarla».** Para un idioma que decidiste subtitular solo, un 0/800 es el resultado
> **esperado**, no un fallo. El informe es una foto de cobertura, la decisión de qué cobertura
> es correcta la toma §3.5.

### 8.2 Checklist de escucha

- [ ] Cada idioma con doblaje: `voz_qa_reporte()` corrido y las líneas sin voz **son las
      esperadas** según la decisión de §3.5, no un olvido.
- [ ] El fallback a subtítulos (§3.2) probado de verdad: forzar `global.idioma` a uno sin
      *audio group* de voz y confirmar que el juego no calla asustado ni lanza error, solo
      muestra el subtítulo.
- [ ] Cambiar de idioma a mitad de partida (`voz_idioma_cargar`) no dispara una línea de voz
      antes de que su Async - Save/Load confirme la carga (§3.3).
- [ ] Todas las líneas normalizadas al mismo pico (§2.5) — una pasada de oído detecta la que
      quedó más alta o más baja que las demás.
- [ ] Los ficheros de voz posicional están en **mono** (§2.6); los de streaming (monólogos
      largos) se resuelven por ruta, no por *audio group* (§2.6).
- [ ] Si hay lip-sync (§5.3): el `.json` de visemas existe para cada línea con voz y en cada
      idioma doblado, no solo en el de referencia.
- [ ] Los *barks* con varias tomas de voz (§7) no repiten el mismo archivo dos veces seguidas —
      confirmarlo escuchando 15-20 disparos seguidos de un mismo bark.
- [ ] La hoja de créditos de voz (actores, estudio, fecha, idioma) está tan actualizada como la
      de música y SFX de [`13 · 09` §8](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8--herramientas-licencias-y-accesibilidad).

---

## 9 · Checklist

- [ ] El guion de grabación (§2.1) tiene contexto y dirección por línea, no solo texto suelto.
- [ ] La clave de localización, el nodo de diálogo y el nombre del archivo de voz son **la
      misma identidad** (§2.2) — nunca tres sistemas de nombres paralelos.
- [ ] La hoja de grabación se **genera** del guion real (§2.3), no se copia a mano.
- [ ] Cada línea grabada está recortada, sin ruido perceptible y normalizada al pico común
      (§2.5) antes de importarla.
- [ ] Voz posicional en mono; monólogos largos gestionados como *stream* por ruta, no por
      *audio group* (§2.6).
- [ ] `voz_localizada_obtener()` (o el parche de una línea en `reproducir_voz`) resuelve el
      idioma activo y cae a -1 sin romper nada cuando falta el doblaje (§3.2).
- [ ] Un *audio group* por idioma, cargado y descargado con `voz_idioma_cargar()`, con el
      evento Async - Save/Load respetado antes de reproducir (§3.3).
- [ ] Decidido, por escrito, qué idiomas se doblan completos, cuáles parcial y cuáles solo se
      subtitulan (§3.5) — y por qué.
- [ ] Los efectos importantes registrados con `subtitulo_efecto_registrar()` disparan texto Y
      flecha desde el mismo evento que el audio (§4.3).
- [ ] Lip-sync elegido a conciencia: boca binaria (§5.2) para NPC secundarios, visemas
      precalculados (§5.3) para personajes principales — no una promesa sin implementar.
- [ ] Voces procedurales, si las hay, enganchadas al *typewriter* carácter a carácter, no por
      frame ni por línea completa (§6.2).
- [ ] `voz_qa_reporte()` corrido para cada idioma antes de cerrar el sprint de localización de
      voz (§8.1).

---

## 10 · Errores clásicos y cómo evitarlos

| Error | Qué se ve/oye | Arreglo |
|---|---|---|
| Nombrar el audio distinto del texto (`voz_01.wav` vs. clave `dlg_herrero_1`) | Nadie sabe qué archivo corresponde a qué línea al cabo de un mes | Una sola convención: `voz_<clave>_<idioma>` (§2.2) |
| Reproducir la voz antes de que `audio_group_load()` termine | La línea no suena la primera vez que se entra a ese idioma, y parece un bug aleatorio | Esperar el Async - Save/Load con `"type" == "audiogroup_load"` (§3.3) |
| Tratar un monólogo largo como si fuera del *audio group* de voz | El *stream* nunca se carga por `audio_group_load`, porque el streaming no pertenece a ningún grupo | Gestionar los *streams* largos por ruta (§2.6) |
| Un idioma sin doblaje deja al jugador sin nada | Silencio donde debería haber al menos texto | El subtítulo (`13 · 12` §6.9) es independiente de si hay voz; `voz_localizada_obtener` devolviendo -1 no debe frenar el subtítulo (§3.2) |
| Normalizar cada toma a su propio pico | Una línea susurrada suena tan fuerte como una gritada en la mezcla | Normalizar todas al mismo pico de referencia, la intención va en la interpretación (§2.5) |
| Blip procedural por cada frame en vez de por carácter | Un pitido continuo y molesto, no una voz robótica | Engancharlo al avance del *typewriter*, un blip por carácter no-espacio (§6.2) |
| Subtítulo de efecto sin la flecha (o al revés) | Quien lo necesita sabe que algo importante pasó pero no de dónde viene, o viceversa | `sonido_importante_anunciar()` dispara las dos mitades desde el mismo punto (§4.3) |
| Suponer que existe `audio_sound_get_amplitude()` para lip-sync en vivo | La función no existe: error de compilación o, peor, código que nunca se prueba | Visemas precalculados fuera de línea, o la alternativa binaria (§5) |

---

## Ver también

- [`13 · 09` — Diseño de sonido y mezcla](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md) — la mezcla, el *round robin*, los emisores y el `en_pantalla()` que esta sección reutiliza
- [`13 · 12` — Diseño narrativo y diálogos](./12%20-%20Diseño%20narrativo%20y%20diálogos.md) — el modelo de datos del guion, los *barks* y la sincronía de subtítulos que aquí se presuponen
- [`04 · 10` — Visual Novel y narrativa](../04%20-%20Recetas%20por%20género/10%20-%20Visual%20Novel%20y%20narrativa.md) — `reproducir_voz()` y el *typewriter* que esta sección extiende
- [`04 · 21` — Localización e idiomas](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — la tabla de idiomas y `txt()` de la que sale la clave que gobierna todo este documento
- [`04 · 27` — Accesibilidad](../04%20-%20Recetas%20por%20género/27%20-%20Accesibilidad.md) — subtítulos de diálogo y el indicador de dirección que aquí se completa con texto
- [`08 · 24` — Audio avanzado](../08%20-%20Referencia%20GML%20completa/24%20-%20Audio%20avanzado%20-%20buffers,%20colas,%20sincronía%20y%20grabación.md) — `tono_generar()`/`ruido_generar()` para la síntesis de la vía B del §6
- [`04 · 29` — 3D en GameMaker](../04%20-%20Recetas%20por%20género/29%20-%203D%20en%20GameMaker.md) — si el juego es 3D, el sonido posicional y `audio_listener_orientation` cambian de base
- [`01 · 13` — Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — la API completa de *audio groups* y *streaming*
- [`12 · 05` §8 — Catálogo de librerías de localización](../12%20-%20Utilidades%20e%20integraciones/05%20-%20Pipeline%20de%20arte%2C%20audio%20y%20niveles.md#8-localización) — `small_pp_localization_tool`, alternativa ya hecha a `generar_hoja_grabacion.py` (§2.3)

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Manual oficial de GameMaker (LTS)** — espejo en `09 - Manual oficial/manual-lts-2026-es/`.
Base `https://manual.gamemaker.io/lts/es/`, y a continuación la ruta de cada página citada:

- `Settings/Audio_Groups.htm` — el grupo por defecto se exporta siempre a todas las
  plataformas; un grupo personalizado permite elegir plataforma de exportación, y ese ajuste
  está ligado a las Configuraciones del proyecto (§3.4)
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio_Groups/` → `Audio_Groups.htm`,
  `audio_group_load.htm` (asíncrona, dispara el evento Async - Save/Load), `audio_group_unload.htm`,
  `audio_group_is_loaded.htm`, `audio_group_set_gain.htm`, `audio_group_name.htm`,
  `audio_group_get_assets.htm`
- `The_Asset_Editors/Object_Properties/Async_Events/Save_Load.htm` — claves exactas del mapa
  `async_load` para el evento de carga de un *audio group*: `"type"` == `"audiogroup_load"`,
  `"group_id"`
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_play_sound_ext.htm` — la lista
  completa de claves del struct de parámetros
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_sound_get_track_position.htm` —
  «obtendrá la posición (en segundos) dentro del archivo de sonido»
- `GameMaker_Language/GML_Reference/Asset_Management/Audio/audio_exists.htm` — advierte de que
  llamarla con un índice no inicializado (p. ej. -1) causa un error, no un `false`
  (§3.2: por eso `voz_localizada_obtener` no necesita, ni debe, llamar a `audio_exists`)
- `GameMaker_Language/GML_Reference/Asset_Management/Assets_And_Tags/asset_get_index.htm` —
  «Asset (any asset type)»: confirma que sirve tanto para sonidos como para *audio groups*
- `01 - Fundamentos/13 - Audio.md` §9 — «los sonidos en streaming no pertenecen a ningún audio
  group» (§2.6)

**Rhubarb Lip Sync** (`DanielSWolf/rhubarb-lip-sync`) — verificado en vivo el 6-09-2026:

- API de GitHub: <https://api.github.com/repos/DanielSWolf/rhubarb-lip-sync> — ★2 597, lenguaje
  C++, último *push* 2026-06-16
- `README.adoc` (rama `master`) — seis visemas básicos `A`-`F` (Hanna-Barbera, adoptados por
  Disney y Warner Bros.), tres extendidos opcionales `G`, `H`, `X`; formatos de exportación
  `tsv`/`xml`/`json`/`dat`: <https://raw.githubusercontent.com/DanielSWolf/rhubarb-lip-sync/master/README.adoc>
- `LICENSE.md` — MIT License, Copyright (c) 2015-2016 Daniel Wolf; el resultado del análisis de
  un audio propio es del usuario sin condición adicional:
  <https://raw.githubusercontent.com/DanielSWolf/rhubarb-lip-sync/master/LICENSE.md>
- Repositorio: <https://github.com/DanielSWolf/rhubarb-lip-sync>

**Práctica de oficio (⚠️ conocimiento de dominio, sin fuente primaria abierta en esta sesión)**

- Dirección de sala y grabación de doblaje (§2.4): prácticas estándar de producción de audio
  para videojuegos (guion con contexto, varias tomas, referencia visual), en la línea de
  Stevens & Raybould, *Game Audio Implementation* (Focal Press, 2016) — la ficha del libro dio
  HTTP 403 al intentar abrirla, como ya deja constancia [`13 · 09` — Fuentes](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#fuentes).
- La técnica de voz procedural del §6 (galimatías silábico tipo *Animal Crossing*) es dominio
  público del oficio de audio de videojuegos; no hay documentación oficial de Nintendo o Rare
  abierta en esta sesión que describa su implementación real, así que el código del §6 es una
  construcción propia de la biblioteca sobre piezas ya verificadas (`tono_generar()`, el
  *round robin* de `13 · 09` §3.2), no una réplica de un sistema comercial.

**Verificación**

Todos los símbolos de GML de este documento se comprobaron con
`python3 "_indice/buscar.py" <símbolo>` contra el `GmlSpec.xml` del runtime **2026.0.0.23**:
`asset_get_index`, `audio_exists`, `audio_group_load`, `audio_group_unload`,
`audio_group_is_loaded`, `audio_group_set_gain`, `audio_group_name`, `audio_get_name`,
`audio_play_sound`, `audio_play_sound_ext`, `audio_is_playing`, `audio_sound_get_track_position`,
`audio_free_buffer_sound`, `buffer_delete`, `struct_get`, `struct_set`, `struct_exists`,
`struct_get_names`, `json_parse`, `file_exists`, `file_text_open_read`, `file_text_eof`,
`file_text_read_string`, `file_text_readln`, `file_text_close`, `array_push`, `array_length`,
`array_delete`, `string_char_at`, `string_length`, `irandom_range`, `round`, `game_get_speed`,
`gamespeed_fps`, `show_debug_message`, `display_get_gui_width`, `display_get_gui_height`,
`draw_set_alpha`, `draw_set_colour`, `draw_text`, `async_load`, `ds_map_exists`. Ninguno está
marcado como obsoleto.

Las funciones y constructores de los ejemplos que **no** son del runtime —`voz_idioma_cargar`,
`voz_localizada_obtener`, `subtitulos_efecto_iniciar`, `subtitulo_efecto_registrar`,
`sonido_importante_anunciar`, `subtitulos_efecto_dibujar`, `visemas_cargar`,
`visemas_actualizar`, `voz_qa_reporte`, `generar_hoja_grabacion.py`— son código de esta
biblioteca. Reutilizados de otros documentos, sin redefinirlos: `reproducir_voz` (`04 · 10`
§5.6), `voz_decir`, `sonar_limitado`, `en_pantalla`, `banco_crear`, `banco_siguiente`,
`variacion_tono`, `variacion_ganancia`, `db_to_lin` (`13 · 09` §3-4), `subtitulo_duracion`
(`13 · 12` §6.9), `indicador_sonido_mostrar` (`04 · 27` §5.3), `txt`, `senal_emitir`
(`04 · 21`, `04 · 16`), `tono_generar` (`08 · 24` §3), y los constructores `Linea`, `Nodo`,
`Guion`, `BancoBarks` (`13 · 12` §6.1/§6.4). Ningún símbolo que se quiso usar resultó no existir:
la única comprobación que dio negativo a propósito, para documentar la ausencia, fue
`audio_sound_get_amplitude`-tipo (§5.1) y `audio_group_stub`/`audio_group_load_status`, que no
existen en el runtime y no debían inventarse.
