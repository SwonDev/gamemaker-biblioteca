# 11 · Producción, alcance y lanzamiento

> Cómo se lleva un juego de GameMaker **de la idea al día siguiente al lanzamiento** siendo una
> persona sola o un equipo de dos o tres: cuánto abarcar, en qué fases partirlo, cómo saber que
> una fase terminó, cómo numerar y etiquetar las builds, y qué hay que tener listo antes de
> pulsar «publicar».
>
> **No explica cómo se exporta a cada plataforma**: eso está en
> [05 · 02 — Publicar y exportar](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md)
> (las 13 plataformas, licencias, Game Options, CI) y en
> [01 · 16](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) (lo básico). Logros,
> anuncios y compras están en
> [04 · 20](../04%20-%20Recetas%20por%20g%C3%A9nero/20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md);
> las jams e itch.io, en
> [07 · 08](../07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md) y
> [12 · 06](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets%2C%20herramientas%20y%20jams.md).

---

## 1 · Alcance: el único problema que de verdad mata juegos

### 1.1 El principio

Un juego no se abandona porque el código sea malo, sino porque **el trabajo que queda deja de
caber en la vida de quien lo hace**. Tres afirmaciones que conviene aceptar antes de discutirlas:

1. **Tu primer juego terminado tiene que ser pequeño.** Terminar enseña lo que empezar no enseña
   —menús, guardado, opciones, pulido, subir a una tienda, el bug del día 1—, y eso solo se
   aprende llegando al final. Un juego de 30 minutos terminado vale más que un RPG al 20 %.
2. **El coste de una funcionalidad no es programarla.** Es programarla, integrarla, darle arte y
   sonido, meterla en las opciones, traducirla, hacerla funcionar con mando, arreglarla cuando
   choque con otra y mantenerla viva hasta el final.
3. **El alcance no se decide una vez**, sino en cada hito, y casi siempre hacia abajo.

### 1.2 Estimar: multiplica por tres

Regla práctica del oficio: **estima con honestidad y multiplica por tres**. No por dos, que es lo
que apetece. El factor tres absorbe lo que la estimación nunca ve.

| Lo que ves al estimar | Lo que no ves | Cuánto pesa |
|---|---|---|
| Escribir el sistema | Integrarlo con lo que ya hay | ×1,5 |
| Que funcione | Que funcione con mando, en pantalla ancha y en el idioma B | +30 % |
| Que funcione | Los bugs que salen al combinarlo con otros sistemas | +30 % |
| El código | El arte, el sonido y la interfaz de ese sistema | ×1 a ×2 |
| Todo lo anterior | Tu vida: enfermedad, trabajo, cansancio, semanas perdidas | +20 % |

- **Estima en tareas de un día, no en semanas.** Lo que no sabes descomponer en días es lo que
  todavía no entiendes; descomponerlo ya revela el triple del tamaño real.
- **Guarda tus estimaciones y compáralas con lo que tardaste.** Tras diez tareas tendrás tu
  factor personal —suele estar entre 2 y 4— y podrás dejar de usar el 3 genérico.
- **Estima en calendario, no en horas.** Ocho horas de tarea con dos horas libres al día son
  cuatro días, no uno.

### 1.3 El core loop primero, el contenido después

```
1. Core loop jugable          →  ¿el minuto a minuto es divertido SIN contenido?
2. Un nivel/zona completa     →  ¿aguanta veinte minutos seguidos?
3. El arco: menú, guardado,   →  ¿es un juego, o es una demo técnica?
   pausa, opciones, créditos
4. Contenido                  →  repetir el paso 2 tantas veces como haga falta
5. Pulido y bugs              →  reservado desde el principio, no lo que sobre
```

El error más caro es invertir el 3 y el 4: llenar el juego de contenido antes de saber si el
bucle se sostiene. Cada hora de contenido construida sobre un bucle que luego cambia se tira. El
diseño de ese bucle está en
[13 · 01](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md);
el arco de escenas, en
[04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20g%C3%A9nero/00%20-%20Anatom%C3%ADa%20de%20un%20juego%20completo.md).

### 1.4 Prototipo, MVP y vertical slice: tres cosas distintas

La definición canónica de *vertical slice* es la de Greg Donovan (Volition) en *The Vertical
Slice Challenge*, GDC 2015: «A section (level, gameplay duration, X number of missions, whatever)
of the full game that successfully communicates the team's intended **PLAYER EXPERIENCE**». Es
decir, **una porción del juego final con la calidad del juego final**: como una porción de tarta,
tiene todas las capas pero no es la tarta entera.

| | **Prototipo** | **MVP** | **Vertical slice** |
|---|---|---|---|
| Responde a | ¿Esta idea es divertida? | ¿Esto es un juego? | ¿Podemos hacer ESTE juego? |
| Arte / audio | Cuadrados, sin audio | Placeholder decente | **Calidad final** |
| Duración jugable | Un minuto | El bucle completo | 10–20 min representativos |
| Menús y guardado | No | Mínimos | Los del juego final |
| ¿Se enseña fuera? | No | A amigos | **A prensa, publishers, tráiler** |
| ¿Se tira después? | Sí, casi siempre | A veces | **No: es la primera pieza del juego** |
| Cuándo | Preproducción | Preproducción tardía | **Puerta a producción** |

**Checklist: esto contiene un vertical slice.** Si falta una casilla, tienes un prototipo bonito
—el autoengaño más común del oficio—, no un vertical slice.

- [ ] **Una porción concreta y acotada** del juego real (un nivel, una zona, tres misiones), no
      mecánicas sueltas en una sala de pruebas.
- [ ] **10–20 minutos seguidos** que un desconocido pueda jugar sin que le expliques nada.
- [ ] **Arte final**: sprites, tilesets, efectos e interfaz al nivel visual del juego terminado.
- [ ] **Audio final**: música de la zona, SFX de las acciones principales, sonido de interfaz.
- [ ] **Todos los sistemas del bucle integrados entre sí**: movimiento, mecánica central, cámara,
      colisiones, daño o fallo, progreso, HUD.
- [ ] **El envoltorio**: pantalla de título mínima, pausa, guardado y carga, Game Over y reintento.
- [ ] **Game feel y juice** aplicados —ver [04 · 15](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md)—:
      lo que separa «funciona» de «apetece».
- [ ] **Corre a la velocidad objetivo en la máquina objetivo**, exportado, no en el IDE.
- [ ] **Deuda técnica conocida y escrita.** Donovan es explícito: uno de los criterios para pasar
      a producción es «Do you have an acceptable level of Technical Debt?». Si el slice se hizo
      con humo y espejos —valores a mano, scripts que solo valen para ese nivel—, **mintió**, y la
      producción se construirá sobre arena.
- [ ] **Nada falseado que no puedas repetir veinte veces.** Si el nivel está colocado a mano y no
      tienes herramienta para hacer los otros diecinueve, no has terminado.

Las tres preguntas de Donovan son la puerta real: ¿el juego transmite la experiencia pretendida?
¿la deuda técnica es aceptable? ¿el equipo **sabe qué hace y cómo hacerlo**? Si alguna es «no», la
respuesta correcta no es seguir: es recortar, rehacer o cambiar de juego. *«Be objective. Analyze
the results and have uncomfortable conversations.»*

### 1.5 La matriz de recorte

Cuando hay que quitar —y siempre hay que quitar—, esta matriz decide en cinco minutos lo que si no
se discute durante semanas:

| | **Coste bajo** | **Coste alto** |
|---|---|---|
| **Toca el core loop** | ✅ **Hazlo ya.** Es el trabajo de más valor del proyecto | ⚠️ **Hazlo, pero solo uno.** Si hay dos así, el juego es demasiado grande: elige |
| **No toca el core loop** | 🕓 **Al final, si sobra tiempo.** Lista «bonito de tener» | ❌ **Córtalo hoy.** De aquí salen los años perdidos |

- «Toca el core loop» significa: **si lo quitas, el minuto a minuto cambia**. Un segundo idioma no
  lo toca; un modo de dificultad tampoco; el sistema de daño sí.
- Lo que se corta **no se borra: se escribe en la lista «después del lanzamiento»**. Duele mucho
  menos cuando la idea queda anotada.
- Si al aplicar la matriz no cortas nada, la has aplicado mal.

### 1.6 Feature creep y cómo se frena

Nadie decide hacer un juego el doble de grande: simplemente cada semana entra una idea buena y no
sale ninguna. Se frena con mecanismos, no con fuerza de voluntad:

1. **Una lista congelada.** Al terminar el vertical slice se escribe la lista de funcionalidades
   del juego final; a partir de ahí es cerrada. **Una dentro, una fuera.** Es la única regla que
   aguanta.
2. **El cuaderno de ideas.** Toda idea nueva va a `IDEAS.md`, no al tablero. Apuntarla la calma;
   meterla en el tablero la convierte en trabajo.
3. **La pregunta de la puerta:** «¿esto acerca la fecha de lanzamiento o la aleja?». Si la aleja,
   necesita justificación escrita en el registro de decisiones (§3.5).
4. **Fecha antes que contenido.** Fija cuánto tiempo tienes y deduce cuánto contenido cabe. Al
   revés no funciona nunca.
5. **Nada nuevo después de *feature complete*** (§2). Ese hito existe para eso: después de él, una
   idea nueva es un bug de proceso.

---

## 2 · Fases y hitos: las puertas del proyecto

> ⚠️ **Esta escalera está calibrada a un calendario humano de semanas o meses.** Si la
> especificación salió del protocolo de elicitación de
> [13 · 28](./28%20-%20De%20hazme%20un%20juego%20a%20una%20especificación%20-%20el%20protocolo%20de%20elicitación%20del%20agente.md)
> y la pregunta 2 de esa lista respondió «esta sesión» (el caso más común de un agente
> construyendo con esta biblioteca), estas fases y sus criterios de salida **no aplican**: el
> criterio de cierre correcto es el checklist de cierre de
> [13 · 28 §3.1](./28%20-%20De%20hazme%20un%20juego%20a%20una%20especificación%20-%20el%20protocolo%20de%20elicitación%20del%20agente.md#31--la-plantilla-de-especificación-mínima)
> (o la sección 15 del GDD completo, `13 · 14 §3.4`), no «feature complete» ni un vertical slice
> de 10-20 minutos con arte final. Sigue leyendo esta sección cuando el proyecto sí vaya a durar
> más de una sesión: el contenido de aquí en adelante es correcto y no cambia por eso.

```
Prototipo → Vertical slice → Alfa → Beta → Gold / Release → Post-lanzamiento
   ¿es        ¿podemos      todas    todo el   se manda        se sostiene
divertido?    hacerlo?     las cosas contenido  a tienda
                           que hace  + pulido
```

Dos conceptos que marcan dos hitos distintos y se confunden todo el rato:

- **Feature complete** (fin de la alfa): **todo lo que el juego SABE HACER está hecho.** No se
  añade ni una funcionalidad más. Puede faltar contenido: niveles, enemigos, textos, música.
- **Content complete** (fin de la beta): **todo lo que el juego CONTIENE está dentro.** El último
  nivel existe, el último enemigo existe, los créditos tienen todos los nombres. A partir de aquí
  solo se arregla.

Entre ambos hay una zona peligrosa: tienta añadir «una funcionalidad pequeña» mientras se mete
contenido. No se hace. Esa es la definición operativa de disciplina de alcance.

**Los criterios de salida.** Cada fila es una **puerta binaria**: se responde sí/no sin
interpretar nada. Mientras haya un «no», la fase no ha terminado.

| Fase | Termina cuando… (todos obligatorios) | Entregable |
|---|---|---|
| **Prototipo** | 1) El bucle central es jugable con teclado. 2) Alguien que no eres tú lo ha jugado. 3) Sabes decir en una frase por qué es divertido —o has decidido tirarlo | Un `.exe` feo que se juega un minuto |
| **Vertical slice** | Las 10 casillas del checklist de §1.4 y las 3 preguntas de Donovan respondidas con «sí» | 10–20 min con calidad final + deuda técnica escrita |
| **Alfa** (feature complete) | 1) Cero funcionalidades pendientes en la lista congelada. 2) El juego se puede terminar de principio a fin, con contenido incompleto. 3) Guardado, opciones, pausa y créditos existen. 4) Compila para **todas** las plataformas de destino, no solo la tuya. 5) La lista de bugs conocidos está escrita | Build jugable de punta a punta |
| **Beta** (content complete) | 1) Cero contenido pendiente: último nivel, últimos textos, última pista. 2) Cero bugs bloqueantes. 3) Traducciones integradas. 4) Tres personas ajenas han terminado el juego sin ayuda tuya. 5) Rendimiento medido en la máquina más lenta que soportas | Build candidata, con todo dentro |
| **Gold / Release** | 1) Cero bloqueantes y cero de prioridad alta. 2) Build generada con configuración `Release` y runtime nativo. 3) Etiqueta de Git sobre el commit exacto de esa build. 4) Página de tienda aprobada y activa. 5) Checklists de tienda superadas (§10). 6) Copia de seguridad de build y claves fuera de tu máquina | El ZIP o instalador que se sube |
| **Post-lanzamiento** | No termina: se decide cuándo cerrarlo. Criterio: 30 días sin bugs nuevos de prioridad alta y decisión escrita sobre si habrá contenido nuevo | Parches, postmortem, decisión de roadmap |

**Cuánto dura cada fase.** ⚠️ Regla de dedo del oficio, no un dato medido: prototipo 10 % ·
vertical slice 20 % · alfa 25 % · beta 20 % · **pulido, bugs y lanzamiento 25 %**.

Ese último cuarto es el que todo el mundo se come, y el que decide si el juego parece profesional.
**Resérvalo en el calendario desde el primer día**, con nombre y fecha. Si al llegar a beta no
queda, recorta contenido, nunca pulido.

---

## 3 · Planificar siendo una persona (o tres)

Los métodos de estudio grande no valen: no hay a quién asignar tareas. Lo que sí hace falta es **no
perder el hilo entre sesiones** y **no engañarse sobre el avance**.

### 3.1 Un tablero de cuatro columnas

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   BACKLOG    │  ESTA SEMANA │   HACIENDO   │    HECHO     │
│  (todo lo    │  (5–8 tareas │  (máximo 1,  │  (se vacía   │
│   pendiente) │   como mucho)│   nunca 3)   │  cada hito)  │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

- **«Haciendo» tiene un límite duro de una o dos tarjetas.** Es la regla más importante del
  tablero: trabajar en cinco cosas a la vez es no terminar ninguna.
- **«Esta semana» se llena el lunes y no se toca hasta el lunes siguiente.** Si aparece algo
  urgente, entra sacando otra cosa.
- **«Hecho» se vacía al cerrar cada hito**, y antes se lee entera: es la prueba material de que el
  proyecto avanza, y la materia prima del diario y del postmortem.

### 3.2 Tareas de un día como máximo

Una tarjeta debe caber en **una jornada real de trabajo** (para muchos, dos horas). Si no cabe, no
es una tarea: es un objetivo, y se parte.

| ❌ Mal escrita | ✅ Partida en tareas de un día |
|---|---|
| «Hacer el sistema de combate» | Golpe básico con hitbox · Daño y vida del enemigo · Parpadeo y retroceso al recibir · Muerte con partículas · Sonido de golpe e impacto · Enfriamiento del ataque |
| «Menú de opciones» | Estructura de navegación · Volumen de música y SFX · Pantalla completa y resolución · Remapeo de teclas · Guardar y cargar los ajustes |
| «Pulir el nivel 1» | Ajustar los 4 saltos difíciles · Colocar 6 monedas · Poner la música · Revisar colisiones del borde · Añadir el cartel del tutorial |

Una tarea bien escrita empieza por un verbo y tiene una condición de terminada evidente.

### 3.3 Un solo objetivo por semana

Además del tablero, escribe **una sola frase** para la semana: *«Que el jefe del nivel 2 se pueda
derrotar»*. Si el viernes es cierta, la semana fue bien aunque quedaran tarjetas. Si es falsa, la
semana falló aunque cerraras diez —y eso significa que estabas trabajando en lo que no tocaba.
Doce semanas son doce frases: ese es tu plan de hitos real, y cabe en una pantalla.

### 3.4 Ciclos de dos semanas con build jugable al final

**Cada dos semanas se genera una build ejecutable y se juega.** No una compilación de prueba desde
el IDE: un `.exe` empaquetado, en una carpeta con fecha, que se abre y se juega diez minutos.
Sirve para tres cosas que ninguna otra práctica da:

1. **Detecta el fallo de exportación pronto**, cuando aún es barato. El primer export siempre rompe
   algo; si el primero es la semana del lanzamiento, es un desastre.
2. **Mide el avance de verdad.** Comparar la build de hoy con la de hace dos semanas es el único
   indicador honesto: o hay algo nuevo que jugar, o no lo hay.
3. **Da algo que enseñar.** Los GIFs, capturas y devlogs salen de estas builds sin trabajo extra.

```bash
# Build quincenal: rápida, para jugar (VM basta)
gm-cli package --target windows --output ./builds/2026-09-06-w12.zip
```

El detalle del comando y de los workflows de GitHub Actions que genera `gm-cli init` está en
[07 · 13 — GM CLI](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md).

### 3.5 Registro de decisiones (ADR ligero)

Dentro de seis meses no recordarás por qué el guardado usa `.json` y no un buffer binario, y
volverás a discutirlo contigo mismo. Un ADR (*Architecture Decision Record*) ligero lo evita: **un
archivo por decisión, cinco líneas, en `decisiones/`**.

```markdown
# ADR 007 · El guardado usa JSON, no un buffer binario
Fecha: 2026-09-06 · Estado: aceptada

**Contexto.** Hay que persistir 30 variables de progreso y el inventario.
**Decisión.** Serializar con JSON a un archivo de texto en la carpeta de guardado.
**Alternativas.** Buffer binario (más rápido y opaco); .ini (no admite estructuras).
**Por qué.** El volumen es pequeño y poder abrir el archivo con un editor durante las
pruebas ahorra horas de depuración.
**Consecuencias.** Los guardados son legibles y editables por el jugador; si eso molesta,
habrá que ofuscarlos antes del lanzamiento (ADR pendiente).
```

Se escribe cuando la decisión **es cara de revertir**: formato de guardado, biblioteca externa,
estructura de las salas, sistema de estados, resolución base. No para el color de un botón. Qué
decisiones estructurales merecen una, en
[13 · 06 — Arquitectura de un proyecto GameMaker](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md).

### 3.6 El diario de desarrollo

Tres líneas al final de cada sesión, en un `DIARIO.md`, de lo más reciente a lo más antiguo:

```markdown
## 2026-09-06
Hecho: retroceso del enemigo + sonido de golpe.
Atascado: la cámara tiembla al empujar (¿el shake se suma dos veces?).
Mañana: mirar el shake, luego la muerte del enemigo.
```

Cuesta un minuto y resuelve el problema más caro del desarrollo en solitario: **los diez minutos
de cada sesión que se van en recordar dónde estabas**. Y al final tendrás el proyecto entero
contado por ti mismo, con fechas: es la materia prima de los devlogs y del postmortem.

### 3.7 Herramientas gratuitas

Cualquiera vale. Lo que importa es **usar una sola** y que esté donde estás tú.

| Herramienta | Plan gratuito | Va bien para | Fricción |
|---|---|---|---|
| **Archivos `.md` en el repo** | — | Quien ya vive en el editor; se versiona con el código | Cero |
| **GitHub Projects** | Sí, con repos privados | Enlazar tareas con *issues* y commits | El proyecto debe estar en GitHub |
| **Trello** | Sí, tableros ilimitados | Kanban visual, arrastrar tarjetas | Otra pestaña más |
| **Notion** | Sí, uso personal | Mezclar tablero, notas de diseño y wiki | Tienta a diseñar la herramienta en vez del juego |
| **HacknPlan** | Sí, un proyecto | Pensado para videojuegos: categorías de diseño, estimado vs. real | Curva de aprendizaje mayor |

⚠️ Los planes gratuitos cambian: confirma las condiciones antes de apoyarte en ellas. Y sin
ironía: **la herramienta no es el trabajo**. Media tarde configurando un tablero perfecto es media
tarde sin tocar el juego.

---

## 4 · Control de versiones y builds

### 4.1 Git con GameMaker

Git no es opcional en producción: es lo que te deja recortar sin miedo, porque lo cortado sigue
existiendo. Los fundamentos —qué es Git, commits, revertir, recuperar un recurso borrado— están en
[03 · 24 — Control de versiones con Git](../03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md).
Lo específico de producción es esto.

**`gm-cli init` ya genera el `.gitignore` y el `.gitattributes` correctos** (verificado creando un
proyecto real el 06-09-2026 con `gm-cli init -t "Space Rocks"`):

```gitattributes
*.yy linguist-generated=true        # no cuenta para las estadísticas de lenguaje
*.gml  text eol=lf                  # forzar LF en los metadatos simplifica los merges
*.yy   text eol=lf
*.yyp  text eol=lf
*.json text eol=lf
```

Forzar `LF` **es lo que hace mezclable un `.yyp`** entre Windows y macOS: sin eso, cada cambio de
plataforma reescribe el archivo entero y los conflictos son irresolubles. El `.gitignore` generado
ignora `*.resource_order`, `*.old` y el directorio `Build` de GMRT.

> ⚠️ **Hueco verificado en el `.gitignore` generado**: `.gmcache/` **no está ignorado**, y en el
> proyecto de prueba recién creado ya ocupaba **131 MB** (`git check-ignore -v .gmcache` no
> devuelve nada). Es la caché de runtimes del CLI y no debe entrar nunca en el repositorio.
> Añade a mano `.gmcache/` y `builds/`.

- **Nunca un proyecto de GameMaker dentro de Dropbox, OneDrive o iCloud.** La sincronización
  automática y el IDE se pelean por los mismos archivos y corrompen el `.yyp`. Git es el respaldo;
  la nube de archivos no lo es.
- **Un commit por tarea terminada**, con mensaje que describe el cambio, no el archivo: `Añade
  retroceso al recibir daño`, no `cambios en obj_player`.
- **`.yy` y `.yyp` no se editan a mano jamás**, ni para resolver un conflicto de merge: se descarta
  una de las dos versiones y se rehace el cambio con `gm-cli resourcetool` o con el IDE.
- **`main` siempre compila.** Una rama por funcionalidad grande y arriesgada; para el resto,
  commits directos a `main` son razonables en solitario.

**Git LFS: el proyecto es, en peso, casi todo binario.** El `.yyp`/`.yy` es JSON —texto, se
diferencia línea a línea y Git lo comprime bien—, pero el resto de un proyecto de GameMaker son
sprites en `.png`, audio en `.ogg`/`.wav` y a veces vídeo. Git no sabe diferenciar binarios: cada
vez que retocas un solo píxel de `spr_jugador.png` y confirmas, Git no guarda «el cambio», guarda
**el archivo entero otra vez**, y la versión vieja se queda para siempre en el historial. Un
sprite de 2 MB retocado 200 veces durante el desarrollo —nada raro en una hoja de animación que
se ajusta cada semana— son varios cientos de megas de historial muerto que además **se descarga
entero cualquiera que clone el repositorio**, aunque solo quiera la versión actual.

**Git LFS (*Large File Storage*)** sustituye el archivo por un puntero de unos bytes en el
commit y guarda el contenido real aparte, en un almacén que sí sabe qué versiones nadie pide ya.
`gm-cli init` no lo activa (el `.gitattributes` verificado arriba no menciona `filter=lfs`): se
configura a mano, y **cuanto antes, mejor**, porque no limpia lo ya commiteado.

```bash
git lfs install                        # una vez por máquina
git lfs track "*.png" "*.gif"          # sprites y sus frames sueltos
git lfs track "*.ogg" "*.wav" "*.mp3"  # audio
git lfs track "*.ttf" "*.otf"          # fuentes grandes
git lfs track "*.mp4" "*.webm"         # vídeo, si hay cinemáticas
git add .gitattributes
git commit -m "Configura Git LFS para binarios"
```

- **`.yy` y `.yyp` no van a LFS, nunca.** Son texto: meterlos en LFS cambia un diff legible por
  un puntero opaco, justo lo contrario de lo que hace falta para revisar qué cambió un recurso —
  y no ahorra casi nada, porque pesan poco.
- **Configúralo antes del primer commit de arte real**, no cuando el repositorio ya pesa gigas:
  añadir el `track` tarde solo evita que siga creciendo, no limpia lo de atrás. Reescribir el
  historial existente es `git lfs migrate import --include="*.png,*.ogg,*.wav" --everything`, que
  según el propio manual de `git-lfs migrate` **reescribe todos los commits** (cambian los hashes
  de arriba abajo) y exige que fuerces el push a todos los remotos y que cualquier colaborador
  vuelva a clonar desde cero. Es una operación de una sola vez, avisada y con copia de seguridad
  antes — no mantenimiento rutinario.

> ⚠️ **LFS cuesta dinero pasado un umbral, y el umbral es bajo para un proyecto con mucho arte.**
> Verificado en la documentación de GitHub (06-09-2026): las cuentas **GitHub Free** y **GitHub
> Pro** incluyen **10 GiB** de almacenamiento y **10 GiB** de ancho de banda de descarga al mes
> para Git LFS, gratis; **GitHub Team** y **Enterprise Cloud** suben a 250 GiB cada uno. Al
> superar la cuota, sin un método de pago configurado el *push* queda bloqueado hasta el mes
> siguiente; con uno, se cobra por lo que exceda —facturación por uso, que sustituyó a los
> antiguos «paquetes de datos» de pago único—. 10 GiB de sprites y audio se alcanzan rápido con
> arte final para varias zonas: vigílalo en *Settings → Billing* del repositorio.
>
> **Cuando el alojamiento no da LFS, o el límite se queda corto**: GitLab tiene su propio LFS
> dentro de la cuota de almacenamiento del repositorio; también puedes montar un servidor LFS
> propio (el protocolo es abierto). Y si el problema de fondo es más grande que un repositorio
> —binarios enormes, bloqueo de archivos para que dos personas no pisen el mismo sprite, un
> equipo que crece—, la alternativa real del oficio es cambiar de sistema de control de
> versiones: **Perforce Helix Core es gratis hasta 5 usuarios y 20 *workspaces*** (verificado en
> perforce.com, 06-09-2026), y es lo que usa buena parte de la industria precisamente porque Git
> no está pensado para binarios. Para un proyecto de una persona, Git + LFS desde el día uno basta.

### 4.2 Etiquetas por hito

Una etiqueta de Git en el commit exacto de cada build que sale de tu máquina. Cuando alguien
reporte un bug con «v0.7.2», podrás volver a ese estado exacto:

```bash
git tag -a v0.4.0-slice -m "Vertical slice: 15 min, arte y audio finales"
git tag -a v0.7.0-alpha -m "Feature complete: sin funcionalidades pendientes"
git tag -a v0.9.0-beta  -m "Content complete: todo el contenido dentro"
git tag -a v1.0.0       -m "Gold: build enviada a Steam"
git push --tags
```

**Toda build que salga de tu máquina —a un tester, a la prensa, a una tienda— lleva etiqueta.** Una
build sin etiqueta es un bug que no podrás reproducir.

### 4.3 Numerar las versiones

Semver adaptado, porque un juego no tiene API pero sí tiene partidas guardadas:

```
MAYOR . MENOR . PARCHE   (+ número de build)
  │       │        └── correcciones; no cambia nada de lo que el jugador ve
  │       └─────────── contenido o funcionalidad nueva; compatible con guardados
  └─────────────────── rompe los guardados anteriores, o es una reedición
```

Antes del lanzamiento: `0.1.x` prototipo · `0.4.x` vertical slice · `0.7.x` alfa · `0.9.x` beta ·
`1.0.0` lanzamiento. El punto clave para un juego: **sube MAYOR cuando los guardados dejan de ser
compatibles**; es la información que necesita quien ya tiene una partida empezada.

**Dónde se escribe.** En *Game Options* de cada plataforma hay un campo **Version** de cuatro
números (`X.Y.Z.B`: los tres de semver más el número de build). Ese valor es el que devuelve la
constante `GM_version` en tiempo de ejecución, y es también el formato que espera
`gm-cli gxgames upload --version X.Y.Z.B` (ver
[05 · 02 §3.1](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md)).

```bash
gm-cli resourcetool eval "options info platform=windows"   # ver las propiedades disponibles
gm-cli resourcetool eval "options get  platform=windows"   # ver sus valores → version = 1.0.0.0
```

> 🛑 **La versión NO se puede escribir por CLI. Ábrela en el IDE.** Es la corrección de un
> ejemplo que este documento daba por bueno y **falla**. Verificado el 08-09-2026 con
> `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`, tres variantes:
>
> ```
> $ options set platform=windows property=version value=1.0.0.42
> Property 'version' cannot be set on 'windows' because it is read-only.
>
> $ options set platform=main property=version value=1.0.0.42
> Property 'version' is not available for platform 'main'. Valid properties: …
>
> $ options set platform=windows property=option_windows_version value=1.0.0.42
> Property 'option_windows_version' is not available for platform 'windows'. Valid properties: …
> ```
>
> `version` **se lee** con `options get` y punto. Tampoco la alcanza `resource set`: las
> opciones no están entre los 17 tipos que devuelve `RESOURCE TYPES` y su nombre no es raíz de
> expresión válida (Trampa 10 de
> [`12 · 09`](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md)).
> De las 30 propiedades de Windows **solo cinco son escribibles** —`interpolate_pixels`,
> `start_fullscreen`, `display_name`, `icon` y `splash_screen`—; la versión, el nombre de
> producto, el copyright y el nombre del ejecutable **no** están entre ellas.
>
> **Qué hacer entonces**, por orden:
>
> 1. **Subir de versión es una acción del humano**, en *Game Options → Windows → Version*. Un
>    agente que prepara un lanzamiento debe **pedirlo**, no intentarlo y fallar.
> 2. **Para GX.games no hace falta**: `gm-cli gxgames upload` acepta `--version X.Y.Z.B` como
>    flag y no lee la opción del proyecto (*«Prompts for the version number if --version is not
>    provided»*, verificado en su `--help`).
> 3. **Para Steam y las demás tiendas, la versión que ve el jugador es la del canal de la
>    tienda**, no la del ejecutable: el `build` de Steamworks, el `versionCode` de Play. La
>    opción del `.yy` solo alimenta `GM_version` dentro del juego y las propiedades del `.exe`
>    en Windows.

> ⚠️ **Dos nombres para lo mismo, y no son intercambiables.** Verificado el 08-09-2026 con
> `options info platform=windows`: el comando `resourcetool options set/get` usa los nombres
> **cortos** — `icon`, `display_name`, `version` —, mientras que `option_windows_icon`,
> `option_windows_display_name` y `option_windows_version` son los nombres del campo **dentro del
> `.yy`** de opciones. Si le pasas el nombre largo al comando, no lo reconoce.

> ⚠️ **El nombre de la propiedad ya está cerrado — no es `Version`.** No hay ninguna propiedad
> llamada `Version` a secas: leyendo los ficheros de esquema del propio toolchain instalado
> (`ResourceTool@2026.0.17`, `Formats/225/BaseProject/options/`, la misma clase de fuente
> primaria que ya usa `_indice/simbolos.json` con `GmlSpec.xml`) hay **dos** campos de versión
> distintos: `option_version` (Main Options, un **entero plano**, p. ej. `100` — no sirve para
> `X.Y.Z.B`) y `option_windows_version` (por plataforma, un **struct** `{ major, minor,
> revision, build }` — este sí es el que corresponde a `X.Y.Z.B`). El icono y el nombre visible
> tienen su propio nombre real también: `option_windows_icon` (ruta a `.ico`),
> `option_windows_display_name` y `option_windows_product_info`. Detalle completo, con la
> tabla de propiedades por plataforma leída del propio esquema, en
> [07 · 24 §2.2](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#22-la-vía-nativa-de-gamemaker-resourcetool-options-set-hallazgo-verificado).
>
> ✅ **`resourcetool options set/get/info` funciona.** Salida real del 08-09-2026 en la máquina
> de referencia, con un proyecto creado a partir de *Blank Pixel Game*:
>
> ```
> Copied /tmp/ico_test.png -> ${options_dir}/mac/icons/1024.png for mac.icon_png
> Saved successfully
> ```
>
> El comando valida además las dimensiones: con un PNG de 512×512 responde
> `Image ... dimensions (512 x 512) do not match the expected dimensions (1024 x 1024)`.
>
> ⚠️ **Si te devuelve `No licensed options for platform 'X'`, no es tu licencia: es la red.**
> Bajo el *sandbox* del Bash de un agente, Igor no puede validar la licencia y falla con
> `Failed to fetch license` (`FetchLicense exited with code 255`); el mensaje que acaba viendo el
> agente es el engañoso `No licensed options`. Es el mismo problema de red que hace que
> `resourcetool` se cuelgue, descrito en
> [12 · 09](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md),
> Trampa 2. Ejecuta esas llamadas **con el sandbox desactivado** y comprueba que el proyecto
> tiene su carpeta `options/` (varias plantillas de la Marketplace no la traen). Si aun así falla,
> queda el IDE — *Game Options* por plataforma, o
> *Herramientas → Project Image Generator* para el icono (`07 · 24 §2.6`) — editando los mismos
> campos que aquí se documentan, nunca el `.yy` a mano (`AGENTS.md §4`).

### 4.4 El sello de versión dentro del juego

Un bug reportado sin número de build es un bug que no se puede arreglar. La solución es dibujar la
identidad de la build en el propio juego: siempre en las builds de prueba, y en la esquina de la
pantalla de título en la de release. GameMaker da cuatro constantes para esto:

| Constante | Tipo | Qué contiene |
|---|---|---|
| `GM_version` | String | La versión de *Game Options → Version* de la plataforma destino |
| `GM_build_date` | Datetime | Instante (UTC) en que se compiló el ejecutable |
| `GM_build_type` | String | `"exe"` si es un ejecutable creado, `"run"` si es una prueba del IDE |
| `GM_runtime_version` | String | El runtime con el que se construyó |

```gml
/// @func sello_version_texto()
/// @desc Línea que identifica sin ambigüedad la build que tiene delante el jugador.
/// @return {String}
function sello_version_texto() {
    // GM_version sale de Game Options → Version. GM_build_date es el instante de compilar.
    var _fecha = date_datetime_string(GM_build_date);
    var _tipo  = (GM_build_type == "run") ? "PRUEBA-IDE" : "EXE";
    return "v" + GM_version + " · " + _tipo + " · " + _fecha + " · rt " + GM_runtime_version;
}

/// @func sello_version_dibujar()
/// @desc Dibuja el sello abajo a la derecha. Se llama desde el evento Draw GUI.
function sello_version_dibujar() {
    var _ancho = display_get_gui_width();
    var _alto  = display_get_gui_height();
    draw_set_halign(fa_right);
    draw_set_valign(fa_bottom);
    draw_set_colour(c_white);
    draw_set_alpha(0.45);
    draw_text(_ancho - 8, _alto - 8, sello_version_texto());
    draw_set_alpha(1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
}
```

### 4.5 Recoger las caídas desde el día 1

El día del lanzamiento no vas a poder depurar en la máquina de nadie, pero sí puedes hacer que el
juego deje escrito qué le pasó. `exception_unhandled_handler` sustituye el diálogo de error de
GameMaker por código tuyo; el juego se cierra igual, pero deja un informe.

```gml
/// @func caidas_instalar_manejador()
/// @desc Sustituye el diálogo de error por un informe en disco. Se llama una vez, al arrancar.
function caidas_instalar_manejador() {
    exception_unhandled_handler(function(_ex) {
        var _informe = "== CAIDA ==\n"
                     + sello_version_texto() + "\n"
                     + "sala: " + room_get_name(room) + "\n"
                     + "mensaje: " + _ex.longMessage + "\n"
                     + "origen: " + string(_ex.script) + " linea " + string(_ex.line) + "\n";
        var _n = array_length(_ex.stacktrace);
        for (var _i = 0; _i < _n; _i++) {
            _informe += "  " + _ex.stacktrace[_i] + "\n";
        }
        if (file_exists("caida.txt")) file_delete("caida.txt");
        var _f = file_text_open_write("caida.txt");
        file_text_write_string(_f, _informe);
        file_text_close(_f);
        show_debug_message(_informe);
        return 1;   // código de salida distinto de 0: lo detecta el CI
    });
}
```

Tres advertencias del manual oficial que hay que respetar: **no se puede dibujar nada** desde el
manejador (no se ejecuta dentro de un evento); **el juego se cierra igualmente** (no sirve para
recuperarse); y lo más seguro es exactamente lo de arriba, **escribir un archivo** y procesarlo en
el siguiente arranque —por ejemplo ofreciendo copiar el informe con `clipboard_set_text` para que
el jugador lo pegue en tu Discord.

> Los bloques de §4.4 y §4.5 se escribieron en un proyecto real y **compilan con
> `gm-cli compile --errors-only --toolchain GMS2@2026.0.0.23` con código de salida 0, sin
> errores de sintaxis** (06-09-2026). `--errors-only` no puede certificar «sin advertencias» —
> silencia justo los `WARNING`, ver la Trampa 8 de
> [`12 · 09` §0](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta) —
> así que esta verificación cubre la sintaxis de los bloques, no la ausencia de avisos.

#### El manejador amable: mensaje al jugador, autoguardado de emergencia y dónde está el log

El manejador de arriba le dice a un archivo qué pasó, pero al jugador no le dice nada: el juego
simplemente desaparece. Tres añadidos lo arreglan sin saltarse ninguna de las tres restricciones
del manual (nada de render, no hay forma de seguir jugando, y solo la E/S de archivo —y los
diálogos del propio sistema operativo— son seguros aquí dentro). **Este bloque REEMPLAZA al de
§4.5** — mismo nombre, no lo declares dos veces (GameMaker no lo permite):

```gml
/// @func caidas_instalar_manejador()
/// @desc Versión ampliada de la de §4.5: además del informe, avisa al jugador
///       en su idioma, intenta un autoguardado de emergencia y le dice dónde
///       quedó el log.
function caidas_instalar_manejador() {
    exception_unhandled_handler(function(_ex) {
        var _ruta_log = "caida.txt";
        var _informe  = "== CAIDA ==\n" + sello_version_texto() + "\n"
                      + "sala: " + room_get_name(room) + "\n"
                      + "mensaje: " + _ex.longMessage + "\n";
        var _n = array_length(_ex.stacktrace);
        for (var _i = 0; _i < _n; _i++) { _informe += "  " + _ex.stacktrace[_i] + "\n"; }

        if (file_exists(_ruta_log)) { file_delete(_ruta_log); }
        var _f = file_text_open_write(_ruta_log);
        file_text_write_string(_f, _informe);
        file_text_close(_f);

        // Autoguardado de emergencia (13 · 06 §3.10): el estado puede estar
        // corrupto por la misma causa de la caída, así que va en su propio
        // try/catch y nunca debe impedir que el resto del manejador termine.
        try {
            if (variable_global_exists("datos_partida_recolectar")
            && is_method(global.datos_partida_recolectar)) {
                save_game("emergencia", global.datos_partida_recolectar());
            }
        } catch (_e2) {
            // Si esto también falla, al jugador le queda su último guardado
            // manual. No hay nada mejor que intentarlo.
        }

        // Mensaje al jugador, en su idioma. NO es render (Draw): es un diálogo
        // modal del propio sistema operativo, y el ejemplo del manual oficial
        // llama a show_message() desde este mismo manejador (lo etiqueta
        // «solo para depuración», pero no documenta ninguna restricción más).
        var _mensaje = variable_global_exists("textos")
            ? txt("caida_mensaje_jugador", { ruta: _ruta_log })
            : "El juego se cerró por un error inesperado.\nSe guardó un informe en: " + _ruta_log;
        show_message(_mensaje);

        return 1;   // código de salida distinto de 0: lo detecta el CI
    });
}
```

La clave se define como cualquier otra del catálogo de idiomas
([04 · 21 §2](../04%20-%20Recetas%20por%20g%C3%A9nero/21%20-%20Localizaci%C3%B3n%20e%20idiomas%20%28con%20traducci%C3%B3n%20por%20IA%29.md#2--la-funci%C3%B3n-txt--con-variables-y-plurales)):

```
"caida_mensaje_jugador": "El juego se ha cerrado por un error inesperado. Se ha guardado un informe en:\n{ruta}\nSúbelo al canal de soporte para que podamos solucionarlo. Se intentó guardar tu partida automáticamente."
```

Sin esto, un jugador que no lea el idioma en el que compilaste el mensaje de depuración por
defecto ni siquiera entiende que algo falló, y es justo el que menos posibilidades tiene de
escribirte un reporte útil. ⚠️ En consolas certificadas no está verificado si un `show_message`
se comporta igual (la documentación técnica está bajo NDA, ver
[05 · 02 §3.8 bis](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md#38-bis--qué-exige-una-consola-aunque-no-puedas-contarlo)):
pruébalo en el kit de desarrollo real antes de depender de él fuera de PC.

### 4.6 Builds reproducibles

```bash
gm-cli compile --config Release --target windows --runtime native --errors-only
gm-cli package --config Release --target windows --output ./builds/v1.0.0-win.zip
```

- **VM durante el desarrollo, native (YYC) para el release.** VM compila rápido; YYC ejecuta rápido.
- **La build de release se genera desde un árbol limpio** (`git status` sin cambios) y sobre el
  commit etiquetado: una build hecha sobre trabajo sin commitear no se puede reproducir.
- **Se prueba esa build entera antes de subirla**, no la de VM de ayer: YYC cambia el
  comportamiento en los bordes.
- **Repite este `compile` una vez sin `--errors-only` antes de empaquetar el release y lee la
  salida completa.** El flag es para iterar; silencia los `WARNING` de compilación, incluido el
  de un *included file* creado por `resourcetool` que no llegó al paquete — detalle en
  [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).
- Automatizarlo con GitHub Actions está resuelto en
  [07 · 13 §11](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) y
  [05 · 02 §5](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md).

### 4.7 Captura, modo foto y compartir

Un botón que guarda la pantalla actual es barato de construir y rentable dos veces: un jugador
comparte tu juego sin que tengas que perseguirlo, y tú tienes la vía más rápida de reunir capturas
limpias para la página de Steam (§6.2) y el press kit (§6.6) sin montar una escena a mano.

```gml
/// @func captura_tomar()
/// @desc Guarda un PNG de la pantalla completa en la carpeta de guardado del
///       usuario, con nombre único por fecha para no pisar la anterior.
/// @returns {String}  La ruta del PNG guardado.
function captura_tomar() {
    var _nombre = game_save_id + "captura_" + string(current_year) + string(current_month)
                + string(current_day) + "_" + string(current_hour) + string(current_minute)
                + string(current_second) + ".png";
    screen_save(_nombre);
    return _nombre;
}

/// @func captura_tomar_recorte(_x, _y, _w, _h)
/// @desc Igual que la anterior, pero solo de una región: la base de un modo
///       foto que oculta la interfaz y deja ver solo el área jugable.
/// @returns {String}
function captura_tomar_recorte(_x, _y, _w, _h) {
    var _nombre = game_save_id + "captura_" + string(current_time) + ".png";
    screen_save_part(_nombre, _x, _y, _w, _h);
    return _nombre;
}
```

**Qué ocultar antes de disparar la captura**: la propia HUD (vida, munición, minimapa), cualquier
overlay de depuración (FPS, colisiones) y las marcas de agua de «Debug/Beta». Un modo foto serio
baja una bandera propia (`global.hud_visible = false`) un frame antes de llamar a
`captura_tomar()` y la restaura justo después; si la HUD se dibuja entera en la capa GUI, basta con
envolver ese Draw GUI en `if (global.hud_visible) { ... }`. Sin esto, cada captura que comparte un
jugador lleva tu barra de vida y tu contador de FPS de depuración — justo lo que un tráiler o un
post en redes no necesita.

**Por qué ayuda al marketing**: una captura que hace el propio jugador, sin HUD, en el momento que
a él le importa, vende mejor que una tuya: no parece publicidad. Steam recomienda screenshots
limpios como parte de los activos de la página (§6.2); un modo foto accesible desde el menú de
pausa multiplica cuántos jugadores generan ese material gratis para ti.

---

## 5 · Assets y pipeline

**La lista de assets por sistema.** El error más común con el arte no es que sea caro: es
**descubrir tarde que falta**. Se evita escribiendo, al terminar el vertical slice, qué necesita
cada sistema.

| Sistema | Arte | Audio | Otros |
|---|---|---|---|
| Jugador | Idle, andar, saltar, caer, daño, muerte, ataque(s) | Pasos, salto, daño, muerte, ataque | — |
| Cada enemigo | Idle, movimiento, ataque, daño, muerte | Alerta, ataque, daño, muerte | — |
| Cada zona | Tileset, 1–3 fondos, props, partículas de ambiente | 1 tema, 1 ambiente, SFX propios | Paleta |
| HUD | Vida, iconos, marcos, fuente | Sonidos de aviso | Textos + traducciones |
| Menús | Fondo, botones (3 estados), logo | Mover, aceptar, cancelar, atrás | Textos |
| **Tienda y marketing** | Capsule, iconos, capturas, GIFs | — | Tráiler, press kit |

Esa última fila es la que se olvida siempre, y la única con fecha límite externa (§6).

**Placeholders desde el día uno.** Ningún sistema espera a tener su arte definitivo: un rectángulo
de color del tamaño correcto es un placeholder válido, y tiene la virtud de que se ve a un
kilómetro que es provisional, así que nunca se cuela en la build final.

- **El placeholder tiene el tamaño y el origen definitivos.** Cambiar dimensiones u origen después
  rompe colisiones y animaciones; cambiar píxeles no rompe nada.
- **Nombre definitivo desde el principio**: `spr_player_idle` con un cuadrado dentro. Sustituir el
  contenido de un sprite existente no toca el código.
- **Los placeholders se listan en `PLACEHOLDERS.md`**, que se vacía durante la beta. Lo que no está
  en la lista es lo que aparece en la captura de prensa. **La lista cubre arte y audio por igual**:
  un `snd_jugador_muerte` sintetizado con las funciones de
  [13 · 09 §8 bis](./09%20-%20Diseño%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad)
  es un placeholder tanto como un sprite provisional, y entra en la misma tabla.
- Para prototipar rápido, los *Asset Bundles* oficiales y Kenney.nl son la vía más corta: catálogo
  en [07 · 09](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md). Si
  ningún pack encaja y hace falta dibujar algo con criterio, la escalera completa —sin caer en el
  rectángulo de color como sprite final— está en
  [12 · 09 §5.2](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano).

**Comprar o encargar.** Antes del dinero, la licencia: la tabla completa y la práctica del
`CREDITS.md` están en
[07 · 09 §1](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md). Tres
trampas que en producción se pagan caras: **CC-BY-NC no vale para un juego que se vende** (ni en
Steam, ni en itch.io con precio, ni con anuncios); **una fuente tipográfica es software con
licencia propia**, distinta de la del pack donde venía; y **la música «para vídeos de YouTube» no
es una licencia de videojuego**.

Si encargas trabajo: **contrato o correo escrito** con qué se entrega, formato, fecha, precio y
—imprescindible— **cesión que permita uso comercial en el juego y en su publicidad** (sin esa
cláusula no puedes usar ese arte en la capsule); **paga por hitos**; **pide los originales**
(`.aseprite`, `.psd`, stems), no solo el PNG exportado; y **empieza por una prueba pequeña de
pago**, que descubrir que el estilo no encaja cuesta mucho menos así.

**Presupuesto.** ⚠️ Sin verificar contra fuente primaria: son órdenes de magnitud de la práctica
habitual, no precios de mercado comprobados; dependen del país, del artista y del año.

| Partida | Coste (⚠️ orden de magnitud) | Alternativa a coste cero |
|---|---|---|
| Licencia comercial de GameMaker | 99,99 USD, pago único (verificado, §9.1) | Free, pero **no puedes vender el juego** |
| Arte de personajes y enemigos | La partida más grande, con diferencia | Assets CC0, o hacerlo tú |
| Música y SFX | Por pista / por lote | Bancos CC0, Freesound (revisar licencia una a una) |
| **Capsule y tráiler** | Puntual, pero **no lo ahorres** | Hacerlo tú, con mucho cuidado |
| Cuota de alta en tienda | Steam cobra por producto; itch.io no | — |
| Traducciones | Por palabra | Comunidad, o traducción asistida revisada |

Si solo puedes pagar una cosa, **paga la capsule y el tráiler**: son lo único que ve el 99 % de la
gente que se cruza con tu juego.

---

## 6 · Lanzamiento

### 6.1 La página de Steam es el primer hito de marketing, no el último

Es el cambio de mentalidad más rentable de esta sección: la página **no se hace cuando el juego
está listo**, sino cuando el juego se puede enseñar, y a partir de ahí trabaja sola acumulando
listas de deseados (*wishlists*) mientras tú programas.

Plazos duros de Valve, verificados en la documentación de Steamworks (06-09-2026):

| Plazo | Cita |
|---|---|
| La página **Coming Soon** publicada **≥ 2 semanas** antes de lanzar | «you must have a Coming Soon page up for at least two weeks before releasing» |
| La revisión tarda normalmente **3–5 días hábiles** | Documentación de *Releasing your game* |
| Envía la página a revisión **≥ 7 días hábiles** antes de quererla publicada | «submit your request for review at least 7 business days before you want your page live» |
| El juego **no se publica solo**: hay que pulsar «Release App» | «Approved titles will not release themselves» |

Y la recomendación del oficio, de Chris Zukowski (*How To Market A Game*): publicar la página
**6 meses antes del lanzamiento, y mejor un año**. Sus tres requisitos previos —no hace falta el
juego terminado, hace falta esto—: 1) sabes exactamente **de qué género es** y te vas a mantener en
él; 2) **el estilo artístico está decidido** (no arte final: decisión final); 3) tienes arte para
enseñar **tres entornos distintos**, porque el comprador quiere ver profundidad. Su conclusión vale
más que cualquier plan: *no retrases la página esperando el momento perfecto*.

### 6.2 Los activos de la página (tamaños verificados)

| Activo | Tamaño | ¿Obligatorio? |
|---|---|---|
| Header capsule | 920 × 430 px | Sí |
| Small capsule | 462 × 174 px (Steam genera 184×69 y 120×45) | Sí |
| Main capsule | 1232 × 706 px | Sí |
| Vertical capsule | 748 × 896 px | Sí |
| Page background | 1438 × 810 px | No |
| Capturas | Mínimo 1920 × 1080, 16:9, **al menos 5** | Sí |

- **La small capsule se ve a 120 × 45 px.** Si el título no se lee a ese tamaño, la capsule está
  mal por bonita que sea a tamaño completo. Redúcela antes de darla por buena.
- **El tráiler ya no es obligatorio para aprobar la página** (Valve retiró el requisito), pero es
  lo que más convierte. Que empiece con gameplay en los tres primeros segundos.
- **Los GIFs son el formato de las redes** y salen gratis de tus builds quincenales. Grábalos desde
  la build, no desde el IDE.
- **Cómo llenar estos tamaños sin artista**, la cover de itch.io y el icono del ejecutable por
  plataforma (Windows/macOS/Android/iOS), con la escalera de prioridad completa y comandos
  probados: [07 · 24 §2-3](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md).

### 6.3 Las wishlists como métrica

Cifras de referencia de *How To Market A Game*, artículo actualizado en junio de 2026 (⚠️ datos de
terceros sobre el mercado, no una garantía, y envejecen rápido):

| Deseados al lanzar | Qué suele significar |
|---|---|
| < 6 000 | Rara vez entras en *Popular Upcoming*; visibilidad orgánica casi nula |
| 7 000 – 10 000 | Colocación breve en *Popular Upcoming* |
| 10 000 – 20 000 | Colocación sólida |

La conversión de deseados a ventas, según el mismo análisis: mediana del **15 %** por debajo de
5 000 deseados, **20 %** entre 5 000 y 40 000, y hasta el **25 %** por encima de 100 000. Los
deseados no se convierten linealmente y los juegos pequeños convierten peor. El consejo del propio
autor: si estás muy por debajo de 7 000 y no vas a poder acercarte, **lanza el juego** en vez de
gastar en publicidad.

Para un primer juego la métrica útil no es «cuántos deseados tengo» sino **la velocidad**: cuántos
entran por semana y qué acción los provocó. Eso es lo que dice si algo funciona.

### 6.4 Steam Next Fest

Festival de demos que Valve organiza tres veces al año. Verificado en Steamworks (06-09-2026):

- **Solo entran juegos con demo**: «Steam Next Fest only includes games with demos».
- Al inscribirte **eliges hasta 2 categorías**; revisa también las etiquetas de la tienda, porque
  de ahí sale buena parte de la visibilidad.
- **Valve comparte la lista de participantes con la prensa 10 días antes**: para entonces tu página
  y tu press kit tienen que estar presentables.
- La demo debe estar **activa antes de que empiece**, y las builds pasan revisión: deja margen.
- Valve recomienda un **enlace a un formulario de opinión** en la pantalla principal de la demo, e
  indicar si la demo se retirará al acabar. Si haces directos, pruébalos antes y deja el chat activo.

Regla de producción: **el Next Fest es una fecha externa e inamovible**. Se elige uno y se
planifica hacia atrás desde él, como si fuera el lanzamiento. Participar con una demo mala es peor
que no participar.

### 6.5 itch.io como primer escaparate

Para un primer juego o para un juego pequeño, **itch.io es el sitio correcto para empezar**:
publicar es inmediato, no hay revisión, no hay cuota de alta y la comunidad es receptiva a juegos
raros y cortos. El flujo completo —export, `butler`, canales, checklist previa— está en
[07 · 08 §2](../07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md) y en
[12 · 06](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets%2C%20herramientas%20y%20jams.md);
el paso a paso en vídeo, en
[03 · 12](../03%20-%20Cursos%20%28YouTube%29/12%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2012%20-%20Exportar%20y%20Publicar.md).

Estrategia habitual y sensata: **jam → itch.io → si funciona, página de Steam**. La versión de
itch.io sigue siendo útil después: es donde vive la demo web y donde llegan quienes no compran en
Steam.

### 6.6 Demo, claves y press kit

**La demo** es un producto aparte con su propio coste: decidir hacerla es decidir gastar dos o
cuatro semanas. Corta (20–40 min); **del principio del juego**, no de la mejor parte, para que
quien la juegue quiera continuar donde lo dejó; **con final propio** —una pantalla que diga «hasta
aquí la demo» con enlace a la tienda y a la lista de deseados, que es la que convierte—; **hecha en
una rama de Git** con contenido desactivado por bandera, no borrando cosas del proyecto; y
**congelada**, porque una demo que se actualiza cada semana es un segundo proyecto en producción.

**Las claves**: genera **lotes identificados** (uno por medio o por evento) para saber de dónde
salió una clave revendida, y no las mandes a granel —un correo personal a diez personas que cubren
tu género rinde más que quinientas claves a una lista comprada—. **Un mes antes** para prensa que
escribe; **una semana antes, con embargo** hasta la hora del lanzamiento, para creadores de vídeo.
Manda la clave **con el press kit**, y **autoriza explícitamente la monetización** de los vídeos:
quita una duda que hace pasar de largo a un creador.

**El press kit** es una página donde alguien que quiere hablar de tu juego encuentra todo lo que
necesita sin escribirte. La referencia del oficio es **presskit()**, la herramienta gratuita de
Rami Ismail (dopresskit.com), pensada para montar esa página en 30-60 minutos con una estructura
que la prensa reconoce al instante. La herramienta da igual; lo que importa son los contenidos:
plantilla en §8.4.

### 6.7 Fecha, precio y regiones

- **La fecha se anuncia cuando el juego está en beta**, nunca antes: anunciar fecha en alfa es
  firmar un retraso público. Deja **dos semanas de colchón** entre tu fecha interna y la pública;
  se usan enteras, siempre.
- ⚠️ **Martes a jueves** es la ventana habitual —el fin de semana no hay prensa y el lunes compite
  con los anuncios— y conviene mirar qué sale ese día. No hay fuente oficial que lo fije: es
  práctica del sector.
- Con los plazos de §6.1, la fecha real de «no vuelta atrás» es **tres semanas antes** del
  lanzamiento.

⚠️ **No hay un precio correcto y esta biblioteca no lo va a inventar.** Lo que sí se puede decir:
el precio se fija **mirando a los vecinos** (mismo género, duración y producción parecidas, últimos
doce meses); **duración no es precio** —un juego corto y excelente sostiene mejor su precio que uno
largo y mediocre—; y **bajar el precio no arregla un juego que no se ve**, porque la visibilidad es
un problema distinto.

Reglas de Steam verificadas (06-09-2026) que **condicionan la planificación**:

- Los precios se pueden fijar en cualquier moneda; la herramienta *Suggest Prices* propone el resto
  a partir de un precio en USD, y tú aceptas o ajustas.
- **No puedes cambiar el precio durante los 30 días siguientes al lanzamiento.**
- **Tras subir un precio hay 30 días de espera** antes de poder aplicar un descuento.
- El **descuento máximo depende del precio base**: hasta 50 % en un producto de 0,99 USD, 75 % en
  uno de 1,99 USD y 90 % a partir de 4,99 USD. El descuento de lanzamiento sí está permitido el
  mismo día.
- **Regiones**: acepta las sugerencias de Steam salvo que tengas un motivo. Ajustarlas a la baja en
  países de menor poder adquisitivo es práctica normal y amplía el alcance; al alza suele salir mal.

### 6.8 El día 1

| Momento | Qué haces |
|---|---|
| **Día −1** | Build final subida y probada **desde la tienda**, no desde tu carpeta. Página revisada. Press kit publicado. Claves enviadas. Duerme |
| **Hora 0** | Pulsa «Release App» tú mismo. Comprueba que la compra funciona de verdad |
| **Hora 0 → +4** | **Estás disponible**: foros, Discord, redes, reseñas. Es el momento de mayor impacto por minuto de todo el proyecto |
| **Todo el día** | **Vigila las caídas** (§4.5) y las reseñas negativas: casi todas señalan un bug real y concreto |
| **Día +1 a +3** | **Parche del día 1**: solo lo que rompe el juego —cuelgues, progreso bloqueado, guardado corrupto—. Nada de mejoras |
| **Semana +1** | Agradece públicamente y recoge lo aprendido para el postmortem mientras está fresco |

**No planifiques trabajo de desarrollo para el día del lanzamiento.** Ese día se atiende, se mira y
se parchea.

> «Build final subida» no es un solo clic: el alta de la app en Steamworks, `steamcmd` y las ramas
> beta, la firma y notarización de macOS, la firma de Windows, y el trámite de Google Play y App
> Store están en
> [05 · 05](<../05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md>).

---

## 7 · Post-lanzamiento

**Parches.** El del día 1 solo arregla lo que rompe el juego. Cada parche sube el número de PARCHE,
lleva su etiqueta de Git y lleva notas, aunque sean tres líneas: las notas son la prueba visible de
que el juego está vivo, y eso pesa en las reseñas. Un parche que toca el formato de guardado sube
el MAYOR y avisa antes de aplicarse.

**Roadmap público, ¿sí o no?**

| Publícalo si… | No lo publiques si… |
|---|---|
| El juego es de acceso anticipado o servicio | Es un juego cerrado que ya contó su historia |
| Tienes contenido ya comprometido y financiado | Las fechas dependen de cosas que no controlas |
| La comunidad participa en decidir prioridades | No estás seguro de querer seguir trabajando en él |
| Puedes actualizarlo aunque no haya novedades | Vas a usarlo para vender expectativas |

Si lo publicas: **temas, no fechas**. «Lo próximo: modo desafío» envejece bien; «modo desafío en
marzo» te persigue hasta marzo. Y borrar cosas de un roadmap público cuesta credibilidad: pon menos
de lo que crees que vas a hacer.

**Telemetría con consentimiento.** Medir cómo juega la gente sirve para ajustar dificultad y
detectar dónde abandonan; el diseño de esas métricas está en
[13 · 01](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md).
Lo que corresponde a producción es el marco:

1. **Pregunta antes de enviar nada**: una pantalla clara la primera vez, con «no» tan fácil como
   «sí», y la posibilidad de cambiar de idea en las opciones.
2. **Recoge lo mínimo.** Muerte en el nivel 3 en el minuto 12: sí. Identificadores de la máquina,
   ubicación, nombre de usuario: no. Lo que no recoges no lo puedes perder ni filtrar.
3. **Sin consentimiento, sin envío**: el juego debe funcionar igual con la telemetría desactivada.
4. **Si recoges algo, necesitas política de privacidad** (§9.3), y la tienda te la va a pedir.
5. **Lo local también sirve**: un contador de muertes por sala guardado en el equipo del jugador,
   que solo se envía si él lo autoriza, resuelve el 80 % de las preguntas de diseño sin problema.

**El postmortem** es un documento de **una página** escrito **entre dos y cuatro semanas después
del lanzamiento**: lo bastante pronto para acordarse, lo bastante tarde para no escribir en
caliente. Es lo único que convierte un proyecto en experiencia transferible, y se escribe **aunque
el juego haya ido mal** —sobre todo entonces—. Plantilla en §8.5.

---

## 8 · Plantillas para rellenar

### 8.1 Alcance de una página

```markdown
# <Nombre del juego> · Alcance
**Frase.** <Un renglón. Si no cabe, el juego no está definido.>
**Género y referentes.** <Género> · como <juego A> pero con <la diferencia>.
**Plataformas.** <Windows / itch.io web / …>   **Idiomas.** <es, en>
**Duración objetivo para el jugador.** <X> minutos u horas.
**Fecha objetivo.** <AAAA-MM> (interna: <AAAA-MM-DD>)

## El core loop
<Tres o cuatro frases: qué hace el jugador una y otra vez, y por qué apetece.>

## Dentro (lista congelada)
- [ ] <Sistema 1>   - [ ] <Sistema 2>   - [ ] <Contenido: N niveles, M enemigos…>

## Fuera (decidido, no olvidado)
- <Cosa> — porque <razón>

## Riesgos
| Riesgo | Probabilidad | Qué hacemos si pasa |
|---|---|---|
| <…> | alta/media/baja | <plan B concreto> |

## Presupuesto de tiempo
| Fase | Semanas | Fecha de salida |
|---|---|---|
| Prototipo · Vertical slice · Alfa · Beta · Pulido | | |
```

### 8.2 Definición de vertical slice

```markdown
# Vertical slice de <Nombre del juego>
**La porción.** <Qué trozo exacto del juego: nivel, zona, misiones.>
**Duración.** <10–20> minutos jugados por alguien que no lo conoce.
**La experiencia que debe transmitir.** <Una frase. Es el criterio de éxito.>

## Contiene
- [ ] Arte final de: <lista>          - [ ] Audio final de: <lista>
- [ ] Sistemas integrados: <lista>    - [ ] Envoltorio: título, pausa, guardado, Game Over
- [ ] Game feel aplicado              - [ ] <N> FPS en <máquina objetivo>, exportado

## No contiene (y está bien)
- <lo que deliberadamente falta>

## Deuda técnica aceptada
| Qué | Por qué se acepta | Cuándo se paga |
|---|---|---|
| <…> | <…> | <fase> |

## Puerta a producción — responder sí/no
- [ ] ¿Transmite la experiencia pretendida?
- [ ] ¿La deuda técnica es aceptable?
- [ ] ¿Sabemos qué estamos haciendo y cómo hacerlo?
```

### 8.3 Plan de hitos

```markdown
# Plan de hitos · <Nombre del juego>
| # | Hito | Criterio de salida (binario) | Fecha | Etiqueta Git | Estado |
|---|---|---|---|---|---|
| 1 | Prototipo | Bucle jugable + probado por alguien ajeno | | `v0.1.0-proto` | |
| 2 | Vertical slice | Checklist §1.4 completa | | `v0.4.0-slice` | |
| 3 | Alfa | Feature complete + compila en todos los targets | | `v0.7.0-alpha` | |
| 4 | Página de tienda | Publicada y aprobada | | — | |
| 5 | Demo | Congelada y subida | | `v0.8.0-demo` | |
| 6 | Beta | Content complete + 3 personas la terminan | | `v0.9.0-beta` | |
| 7 | Gold | Cero bloqueantes + build de release probada | | `v1.0.0` | |
| 8 | Lanzamiento | Botón pulsado | | — | |

## Un objetivo por semana
| Semana | La frase |
|---|---|
```

### 8.4 Press kit

```markdown
# Press kit · <Nombre del juego>

## Ficha
- Título · Desarrollador · Web · Plataformas · Fecha · Precio
- Idiomas · Motor: GameMaker · Clasificación por edades

## Descripciones
- Una línea (máx. 150 caracteres) · Párrafo corto (~50 palabras) · Larga (~200 palabras)

## Características
- <5–7 viñetas, empezando por lo que hace distinto al juego>

## Historia
<Cómo nació el proyecto, quién lo hace y por qué. 150–300 palabras.>

## Material descargable
- Tráiler (YouTube + archivo) · Capturas (ZIP, ≥5, sin HUD de depuración, resolución nativa)
- GIFs (3–5, cortos, de gameplay) · Logo e iconos (PNG con transparencia) · Capsule

## Permisos
- Monetización de vídeos: permitida sin restricciones.
- Uso del material: libre para cobertura periodística y vídeos.

## Contacto
- Prensa · Redes · Discord · Cómo solicitar claves
```

### 8.5 Postmortem

```markdown
# Postmortem · <Nombre del juego>
Lanzamiento: <…> · Este documento: <…>

## Los números
- Tiempo de desarrollo · Horas estimadas vs. reales · Deseados al lanzar
- Ventas primera semana y primer mes · Precio · Reseñas (n y % positivas)

## Qué salió bien (3–5)
1. <Qué pasó> → <por qué funcionó> → <lo repito porque…>

## Qué salió mal (3–5)
1. <Qué pasó> → <causa raíz, no síntoma> → <coste real>

## Qué haría distinto
1. <Cambio concreto y accionable en el próximo proyecto>

## Para el siguiente proyecto
- Mi factor de estimación real resultó ser ×<N>.
- Decisiones técnicas que repetiría / que no: <…>
```

### 8.6 EULA mínimo

> ⚠️ **Esto no es asesoramiento legal**, igual que el resto de §9. Un EULA (*End User License
> Agreement*, licencia de usuario final) es lo que le dices al jugador sobre **qué puede hacer
> con tu juego**, distinto de la política de privacidad (§9.3, sobre sus datos) y del análisis de
> marcas y fan games de
> [13 · 25](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md)
> (sobre la propiedad intelectual de *otros*, no la tuya). Un juego pequeño **puede publicarse sin
> EULA** —la mayoría de tiendas no lo exigen como requisito de publicación, a diferencia de la
> política de privacidad—, pero sin él no tienes por escrito ni el límite de responsabilidad ni la
> prohibición de ingeniería inversa, y ambos cuestan caro el día que hagan falta.

**Qué cubre, como mínimo, un EULA razonable para un estudio pequeño:**

- **Licencia de uso, no de propiedad**: el jugador compra el derecho a jugar, no una copia del
  código ni del arte — la distinción que ya usa
  [13 · 11 §12.5](#125-cesi%C3%B3n-de-derechos-por-qu%C3%A9-lo-pagu%C3%A9-no-es-es-m%C3%ADo) para
  encargos de arte, aplicada ahora al revés: tú retienes la propiedad, el jugador solo licencia
  el uso.
- **Prohibición de ingeniería inversa, reventa y redistribución** del ejecutable fuera de la
  tienda donde se compró.
- **Limitación de responsabilidad**: el juego se entrega «tal cual» (*as is*), sin garantía de
  que funcione en cualquier configuración, y tu responsabilidad como estudio no supera lo que el
  jugador pagó por él.
- **Terminación por incumplimiento**: si el jugador rompe los términos (piratea, hace trampas en
  modo competitivo, redistribuye el ejecutable), la licencia se revoca.
- **Ley aplicable y jurisdicción**: qué país/tribunales rigen el contrato si hay disputa — esto sí
  depende por completo de dónde tributes y de dónde vendas, como el resto de §9.

```markdown
# EULA (Licencia de Usuario Final) · <Nombre del juego>
Versión: 0.1 · Última actualización: AAAA-MM-DD

Este es un acuerdo de licencia entre tú (el jugador) y <Estudio/Nombre> para el uso del software
«<Nombre del juego>» ("el Juego"). Al instalar o ejecutar el Juego, aceptas estos términos.

## 1. Concesión de licencia
Se te concede una licencia limitada, no exclusiva e intransferible para instalar y usar el Juego
con fines personales y no comerciales, en los dispositivos que permita la plataforma donde lo
adquiriste. Esta licencia no te transfiere ningún derecho de propiedad sobre el Juego, su código,
su arte o su música.

## 2. Restricciones
No puedes: (a) realizar ingeniería inversa, descompilar o desensamblar el Juego, salvo en la
medida en que la ley aplicable lo permita expresamente pese a esta restricción; (b) revender,
alquilar, prestar o redistribuir el Juego fuera de la plataforma de compra autorizada; (c) usar el
Juego para fines ilegales o para desarrollar un producto competidor.

## 3. Propiedad intelectual
El Juego, incluidos su código, arte, música y diseño, es propiedad de <Estudio/Nombre> y está
protegido por las leyes de propiedad intelectual aplicables. Esta licencia no te concede ningún
derecho sobre esas marcas o creaciones más allá del uso descrito en la sección 1.

## 4. El Juego se entrega "tal cual"
El Juego se proporciona "tal cual", sin garantías de ningún tipo, expresas o implícitas, incluidas
—entre otras— garantías de comerciabilidad o idoneidad para un fin concreto. No garantizamos que
el Juego funcione sin errores en todas las configuraciones de hardware o software.

## 5. Limitación de responsabilidad
En la medida máxima permitida por la ley aplicable, <Estudio/Nombre> no será responsable de daños
indirectos, incidentales o consecuentes derivados del uso del Juego, y su responsabilidad total no
superará el importe que pagaste por él.

## 6. Terminación
Esta licencia termina automáticamente si incumples cualquiera de estas condiciones. Al terminar,
debes dejar de usar el Juego y eliminar todas las copias en tu posesión.

## 7. Ley aplicable
Este acuerdo se rige por las leyes de <tu país/jurisdicción>, sin perjuicio de los derechos que la
legislación de protección al consumidor de tu país de residencia te reconozca de forma imperativa.

## 8. Contacto
Preguntas sobre esta licencia: <email de contacto>.
```

⚠️ Es una plantilla de partida, no un contrato listo para publicar: revísala con un profesional
si tu juego maneja datos sensibles, pagos recurrentes o distribución en un país con requisitos de
consumo específicos (la UE, por ejemplo, reconoce derechos de consumidor que ningún EULA puede
anular por contrato — ver la nota de la sección 7 de la propia plantilla).

---

## 9 · Legal y administrativo mínimo

> ⚠️ **Nada de esta sección es asesoramiento legal ni fiscal**, y buena parte depende del país en
> el que vivas y tributes. Sirve para saber qué existe y qué preguntar.
>
> Esta sección cubre tu propia licencia y tus propios datos. El riesgo simétrico —usar sin
> permiso el nombre, los personajes o la marca de **otra persona** (fan games, parodia, el nombre
> de una consola en tu ficha)— tiene su propio documento, con casos reales verificados y fecha:
> [13 · 25 — Legal de terceros: marcas, fan games y parodia](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md).

### 9.1 La licencia de GameMaker

Verificado en <https://gamemaker.io/en/get> el 06-09-2026:

| | **Free** | **Professional** | **Enterprise** |
|---|---|---|---|
| Coste | Gratis | **99,99 USD, pago único** | Suscripción mensual o anual |
| Uso | **No comercial** | **Comercial** | **Comercial** |
| GX.games, escritorio, web, móvil | ✅ | ✅ | ✅ |
| **Consolas** | ❌ | ❌ | ✅ |
| Código fuente del runtime | ❌ | ❌ | ✅ |
| Marca de agua | Ninguna en ningún nivel | | |

La FAQ oficial es explícita: *«If you want to make money from your game, you need to buy a
Commercial License for $99.99. If you want to export to Console you need the Enterprise
subscription. Other than that, everything else is free and unlimited!»*

- **Esta biblioteca trabaja con Professional**, que cubre PC, web y móvil comerciales. Para
  cualquier consola hacen falta **Enterprise** *y* el acceso de desarrollador de la plataforma, que
  se solicita aparte: ver
  [05 · 02 §1.4 y §3.8](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md). El registro
  real de los tres fabricantes (Nintendo, PlayStation, Xbox), el NDA que firmas antes de ver nada
  y qué exige el *lotcheck*/TRC/XR de cada uno están en
  [05 · 06 — Publicar en consolas](../05%20-%20Referencia/06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md).
- **GMRT** será gratis para uso no comercial; para publicar comercialmente con GMRT, YoYo pide
  licencia Professional.
- Con una licencia permanente antigua de GMS2 **puedes seguir publicando comercialmente con el
  runtime GMS2**. Las suscripciones Creator/Indie no se renuevan, y al pasar a Professional se
  aplica un descuento por lo ya pagado.

### 9.2 Licencias de los assets

Ver [07 · 09 §1](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md) y
§5 de este documento. La práctica que hay que mantener desde el primer día es un `CREDITS.md` en el
repositorio con **nombre, autor, URL y licencia** de cada asset externo. Vale su peso en oro al
rellenar la ficha de la tienda —y al recibir un aviso—: reconstruirlo a posteriori es casi
imposible.

### 9.3 Política de privacidad

**La necesitas si el juego envía cualquier dato fuera del equipo del jugador**: telemetría, tablas
de puntuación en línea, informes de caídas automáticos, anuncios, multijugador o el SDK de una
tienda que recoja datos. Las tiendas la piden por URL en la ficha del producto. Debe decir, como
mínimo: **qué se recoge, para qué, dónde se guarda, cuánto tiempo, con quién se comparte y cómo se
pide su borrado**.

⚠️ Los requisitos concretos dependen de la jurisdicción de tus jugadores —el RGPD europeo es el más
exigente y aplica por la residencia del jugador, no por la tuya— y el trato de datos de menores
tiene reglas propias. Si **no** envías nada fuera, dilo explícitamente: es más corto, más honesto y
mejor argumento comercial que una política genérica copiada.

**RGPD/GDPR, en lo que afecta a un juego de un estudio pequeño** (no es asesoría legal: es el
armazón mínimo para no diseñar a ciegas; la última palabra la tiene un abogado si el volumen de
datos o de jugadores lo justifica):

- **Base legal para telemetría de juego.** Con el marco de consentimiento de **§7 arriba**
  ("Telemetría con consentimiento": preguntar antes, «no» tan fácil como «sí»), la base es el **consentimiento**
  explícito del artículo 6.1.a — la más simple de justificar para un estudio sin departamento
  legal. La alternativa, **interés legítimo** (6.1.f), evita pedir permiso pero exige poder
  justificar por qué el dato es necesario y proporcionado si alguien lo pregunta; para telemetría
  de diseño (muertes por sala, embudos) que no hace falta para que el juego funcione, pedir
  consentimiento es el camino que menos dudas deja.
- **Derecho de acceso y de borrado.** Un jugador puede pedir qué datos tienes sobre él y que los
  borres. Con la telemetría local-primero de §7 arriba (el JSON vive en el disco del jugador
  hasta que él consiente enviarlo), la respuesta práctica más simple es **no acumular un
  identificador estable de jugador en el backend**: si cada sesión es un pseudónimo nuevo sin
  ligar a una cuenta (el patrón de `sesion: $"{fecha}#{irandom(9999)}"` de
  [`13 · 01 §9.5`](./01%20-%20Diseño%20de%20juego%20-%20core%20loop,%20mecánicas,%20balance%20y%20dificultad.md#95--telemetría-contar-muertes-por-sala-y-volcarlas-a-json)),
  no hay a quién asociarle un borrado porque no hay identidad que borrar. Si en cambio ligas
  telemetría a una cuenta (login, IAP, multijugador con perfil), sí necesitas un mecanismo real
  de "borra todo lo mío" antes de lanzar.
- **Plazo de retención.** El RGPD exige guardar datos personales **solo mientras hagan falta**,
  no indefinidamente. Para telemetría de diseño, una retención de unos pocos meses (lo que dura
  ajustar el balance de una versión) es defendible; conservar años de eventos de jugadores que
  ya no juegan no lo es. Documenta el plazo en la política de privacidad, aunque sea aproximado.
- **Notificación de brecha.** Si tu backend propio (no el de un tercero como Firebase, que ya
  tiene su propio cumplimiento) sufre una fuga de datos personales, el RGPD exige notificarlo a
  la autoridad de protección de datos en un plazo corto (72 horas desde que tienes constancia,
  según el texto del reglamento). ⚠️ No verificado con una fuente primaria en esta sesión el
  detalle exacto de excepciones y umbrales: si tu juego llega a manejar datos personales de
  verdad (no solo telemetría anónima), confírmalo con una fuente legal antes de necesitarlo.

**Datos de menores — COPPA (EE. UU.) y el umbral de edad del RGPD.** Son dos regímenes distintos,
y confundirlos es el error más común:

- **COPPA** (*Children's Online Privacy Protection Act*, EE. UU., en vigor desde 2000 y con una
  norma final revisada por la FTC que entró en vigor el 23 de junio de 2025) exige
  **consentimiento verificable de un padre o tutor** antes de recoger cualquier dato personal de
  un menor de **13 años**, y se aplica si tu juego está **dirigido a niños** o si **sabes a
  sabiendas** que recoges datos de menores de 13, con independencia de dónde esté tu estudio.
  Verificado en la Federal Trade Commission, *Complying with COPPA: Frequently Asked Questions* —
  <https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions>
  (consultado 07-09-2026): *«operators must obtain verifiable parental consent before collecting
  any personal information from a child»*, salvo excepciones concretas; la propia FTC explica que
  el Congreso limitó la protección a menores de 13 años *«recognizing that younger children are
  particularly vulnerable to overreaching by marketers»*. Un juego para todos los públicos
  (clasificación PEGI 3 / ESRB Everyone, §9.4) que no verifica la edad de nadie está, en la
  práctica, obligado a tratar a **todo** su público como potencialmente sujeto a COPPA si no
  recoge ningún dato personal — la salida más simple para un estudio pequeño casi siempre es **no
  recoger datos personales de nadie**, en vez de construir un flujo de verificación parental.
  **En la práctica, cuando el juego lleva anuncios**, el efecto directo de quedar sujeto a COPPA
  (o a su equivalente de plataforma) es que esos anuncios tienen que ser **no personalizados** —
  la misma exigencia que ya documenta
  [05 · 05 §5.6](<../05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md#56-cuestionario-de-contenido-y-público-objetivo>)
  para el formulario de *«Target audience and content»* de Google Play, que es **dónde** se
  declara esto en la práctica en esa tienda concreta — no se repite aquí ese trámite.
- **RGPD**: el umbral de "puede dar consentimiento él mismo" varía **por país de la UE entre 13 y
  16 años** (cada Estado miembro fija el suyo dentro de ese rango, artículo 8 del RGPD); por
  debajo del umbral local hace falta el consentimiento de quien tenga la patria potestad. ⚠️ No
  verificado en esta sesión el umbral exacto país por país: si publicas en la UE y tratas datos
  personales de menores, compruébalo en la fuente vigente de cada mercado, no asumas 13 ni 16
  como regla única. **España** fija el umbral en **14 años**: el tratamiento de datos de un menor
  basado en su propio consentimiento solo es lícito a partir de esa edad; por debajo, hace falta
  el consentimiento de quien tenga la patria potestad o la tutela. Verificado en el texto
  consolidado, artículo 7 de la Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos
  Personales y garantía de los derechos digitales — <https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673>
  (consultado 07-09-2026).
- **La salida que ya recomienda esta biblioteca sigue siendo la más barata**: el marco de
  consentimiento de arriba ("recoge lo mínimo… identificadores de máquina, ubicación, nombre de
  usuario: no") aplicado con criterio evita la mayoría de estas obligaciones por la vía de no
  generar el dato que las dispara, en vez de cumplirlas una por una.

### 9.4 Clasificación por edades: PEGI, ESRB e IARC

**IARC** (*International Age Rating Coalition*) evita tener que pedir clasificación a cada organismo
del mundo. Verificado en <https://www.globalratings.com/> (06-09-2026):

- **Rellenas un cuestionario una sola vez** en la tienda participante. IARC asigna automáticamente
  **edad, descriptores de contenido y «elementos interactivos»** (compras dentro del juego,
  incluidas las aleatorias; interacción entre usuarios; compartir ubicación; acceso a internet)
  **de cada región**.
- Recibes un **certificado con un ID reutilizable** en otras tiendas IARC: «Developers only have to
  complete the IARC questionnaire once.» **Es gratuito** para el desarrollador.
- Participan nueve organismos: **PEGI** (Reino Unido y Europa), **ESRB** (EE. UU. y Canadá),
  **USK** (Alemania), **ClassInd** (Brasil), **ACB** (Australia), **GRAC** (Corea del Sur),
  **IGRS** (Indonesia), la **General Authority for Media Regulation** (Arabia Saudí) y el
  **Digital Game Self-regulation Committee** (Taiwán).
- Los organismos **vigilan las clasificaciones** y las corrigen si el cuestionario se rellenó mal:
  responderlo con ligereza tiene consecuencias.

⚠️ **Steam no usa IARC.** Tiene su propio **Content Survey**, obligatorio antes de enviar el juego a
revisión, con tres bloques: contenido general (de donde salen las clasificaciones regionales de la
ficha), contenido adulto (violencia y sexo) y **uso de IA generativa** —distinguiendo entre
contenido pregenerado y generado en vivo—. Hay páginas específicas para los requisitos obligatorios
de **Alemania** e **Indonesia**. ⚠️ La lista de tiendas que sí usan IARC no se pudo leer (la página
*Storefronts* de globalratings.com carga su contenido por JavaScript y no devolvió datos):
compruébalo en la tienda donde vayas a publicar.

> El detalle de qué cuenta como IA generativa a efectos de esa declaración (con exención para
> herramientas de desarrollo), la política equivalente de itch.io y el riesgo de propiedad
> intelectual sobre arte generado sin edición humana están en
> [07 · 23 — Arte generado por IA §4](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#4--el-estado-legal-verificado-el-2026-09-07-con-fuente-primaria-y-fecha).

### 9.5 Impuestos de las tiendas

Verificado en la documentación fiscal de Steamworks (06-09-2026), aplicable en lo esencial a
cualquier tienda estadounidense:

- Si **no eres residente fiscal en EE. UU.**, completa el **W-8BEN** (persona física) o
  **W-8BEN-E** (empresa) para acogerte al convenio de doble imposición entre tu país y EE. UU.
- **Sin convenio o sin formulario, la retención es del 30 %** sobre tus ingresos de fuente
  estadounidense. Con convenio suele ser bastante menor, y en algunos casos cero.
- Hace falta un **TIN**: tu número fiscal extranjero, o un **ITIN** (personas físicas) o **EIN**
  (autónomos y empresas) estadounidense. Solicitar un ITIN para acogerse al convenio **no obliga a
  presentar declaración en EE. UU.**
- Se rellena en la **entrevista fiscal** de la propia plataforma, no por correo.

⚠️ Todo lo relativo a **tu** país —cómo se declara ese ingreso, si hace falta darse de alta como
autónomo o constituir sociedad, cómo se factura el IVA de una venta digital— depende de tu
jurisdicción. Pregúntalo antes de la primera venta, no después.

---

## 10 · Checklist de lanzamiento

Lo **técnico por tienda** (opciones del IDE, VM vs YYC, iconos, configuraciones, targets del CLI)
está en [05 · 02 §4.4](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md). Esta es la de
producción, y las tres partes tienen que estar marcadas.

**Tres semanas antes**

- [ ] Página de la tienda **enviada a revisión** (≥ 7 días hábiles) y publicada como *Coming Soon*
      (≥ 2 semanas antes de lanzar)
- [ ] Precio decidido y monedas regionales revisadas
- [ ] Clasificación por edades resuelta (cuestionario IARC o Content Survey de Steam)
- [ ] Política de privacidad publicada y enlazada, si envías datos
- [ ] Formulario fiscal completado en la plataforma
- [ ] Press kit publicado, con tráiler, capturas, GIFs y logo
- [ ] Claves generadas por lotes; envíos a prensa preparados

**Una semana antes**

- [ ] Build de release desde árbol limpio, con `--config Release --runtime native`
- [ ] Etiqueta de Git sobre ese commit exacto
- [ ] Build **descargada de la tienda** y jugada de principio a fin en la máquina objetivo
- [ ] Guardado probado: crear, cargar, salir y volver; y en una instalación limpia
- [ ] Cero bugs bloqueantes; lista de bugs conocidos escrita
- [ ] Sello de versión visible (§4.4) y manejador de caídas instalado (§4.5)
- [ ] Créditos completos y `CREDITS.md` al día con todas las licencias
- [ ] Textos revisados en todos los idiomas soportados
- [ ] Copia de seguridad de build, repositorio y claves fuera de tu máquina
- [ ] Claves con embargo enviadas a creadores de vídeo

**El día**

- [ ] Publicar a mano, a la hora decidida · [ ] Comprobar que la compra funciona de verdad
- [ ] Estar disponible cuatro horas · [ ] Vigilar caídas y reseñas
- [ ] Parche del día 1 preparado para salir en 24–72 h

---

## 11 · Errores clásicos y cómo evitarlos

| Error | Por qué pasa | Qué hacer en su lugar |
|---|---|---|
| **Empezar por el menú y las opciones** | Es lo primero que ve el jugador, y además se sabe hacer | Empieza por el bucle central; el menú se hace en la alfa, cuando ya sabes qué opciones ofrecer |
| **Meses sin una build jugable** | Todo funciona en el IDE, así que parece que funciona | Build empaquetada cada dos semanas (§3.4): el primer export siempre rompe algo |
| **Marketing la semana del lanzamiento** | Se cree que el marketing es «anunciar el juego terminado» | La página de la tienda es un hito de **producción**, seis meses o un año antes (§6.1) |
| **No reservar tiempo para pulido y bugs** | El plan cubre construir, no terminar | El 25 % final tiene nombre y fecha desde el día uno (§2). Se recorta contenido, nunca pulido |
| **Un «vertical slice» que es un prototipo** | La trampa que describe Donovan: algo bonito hecho con humo y espejos | Checklist de §1.4 casilla por casilla. Sin arte final ni deuda técnica escrita, no es un slice |
| **Estimar en semanas** | Las semanas esconden el trabajo real | Tareas de un día (§3.2) y tu factor medido (§1.2) |
| **Añadir funcionalidades durante la beta** | «Es que es pequeñito» | Después de *feature complete* no entra nada: va a `IDEAS.md` (§1.6) |
| **Anunciar la fecha en alfa** | Optimismo | Fecha pública solo en beta, con dos semanas de colchón (§6.7) |
| **Perder la trazabilidad de una build** | Se manda un `.zip` a un tester sin etiquetar | Etiqueta de Git + sello de versión en pantalla (§4.2 y §4.4) |
| **Meter `.gmcache` en el repositorio** | El `.gitignore` generado no lo incluye | Añádelo a mano: son cientos de megas de caché (§4.1) |
| **Descubrir la licencia de un asset al publicar** | Se descargó «para probar» y se quedó | `CREDITS.md` desde el primer asset externo (§9.2) |
| **Guardar el proyecto en Dropbox u OneDrive** | Parece una copia de seguridad | Git: la sincronización de archivos corrompe el `.yyp` (§4.1) |
| **Programar el día del lanzamiento** | Nervios | Ese día se atiende y se parchea; el desarrollo vuelve el día +3 (§6.8) |
| **No escribir el postmortem si fue mal** | Duele | Es justo cuando más enseña (§7) |

---

## 12 · Trabajar con otras personas

Todo lo anterior asume que el proyecto lo lleva una persona, o un equipo que ya se conoce bien.
En cuanto entra alguien de fuera —a quien pagas por un encargo, o a quien invitas a colaborar sin
pagarle— aparecen tres preguntas que ningún tutorial de GameMaker responde: **qué le pides**,
**qué le debes** y **qué es tuyo al final**.

> 🎮 **¿La otra persona es un *porting house* o un publisher de consola?** Esta sección cubre el
> caso general — colaboradores, contratados, cesión de derechos. La variante específica de
> consola (porting houses verificadas hoy, *fee* fijo frente a *revenue share*, quién figura
> como «publisher de récord» ante Nintendo/PlayStation/Xbox) está en
> [05 · 06 §7.4](../05%20-%20Referencia/06%20-%20Publicar%20en%20consolas%20-%20Nintendo%2C%20PlayStation%20y%20Xbox.md#74-cómo-se-estructura-un-acuerdo-de-porting-o-publishing)
> — que ya enlaza de vuelta aquí.

### 12.1 Colaboradores, socios y contratados: la diferencia importa antes de firmar nada

Tres relaciones que se parecen por fuera y son muy distintas en lo que implican:

| | **Contratado** (freelance) | **Colaborador** | **Socio** |
|---|---|---|---|
| A cambio de | Un precio pactado por una entrega concreta | Crédito, y a veces un % de ingresos futuros (*revenue share*) | Reparto real de propiedad y de decisiones |
| Decide sobre el juego | No, solo ejecuta lo encargado | Lo que se le delegue, nada más | Sí, en lo pactado |
| Riesgo si el juego no se vende | Ninguno: ya cobró por su trabajo | El que se haya pactado —normalmente ninguno si no hay *revenue share* firmado— | Todo el que le corresponda por su parte |
| Necesita, como mínimo | Encargo por escrito (§12.2) + cesión de derechos (§12.5) | Acuerdo por escrito de qué % y de qué ingresos, aunque sea informal entre amigos | Pacto de socios, y normalmente una figura legal (sociedad) |

**El error más caro es tratar un *revenue share* de palabra como si fuera gratis.** Si alguien
colabora esperando un porcentaje «cuando el juego venda», eso es un acuerdo económico real — y si
no está escrito, la única versión que existe es la de cada uno, y suelen ser distintas para
cuando hay dinero de por medio. Escríbelo aunque sea un correo de tres líneas: qué %, de qué
ingresos exactamente (brutos o después de la comisión de la tienda), durante cuánto tiempo y qué
pasa si el proyecto no se termina.

⚠️ **Constituir una sociedad, repartir participaciones o dar de alta a alguien como colaborador
son decisiones legales y fiscales que dependen de tu país**: fuera del alcance de esta
biblioteca, igual que el resto de §9. Lo que sí es universal es la regla de arriba: decide qué
relación tienes de verdad **antes** de que haya dinero encima de la mesa, no después.

### 12.2 El brief de encargo: qué lleva para no acabar en desastre

Un encargo de arte, música o traducción que sale mal casi nunca es por falta de talento del
profesional: es por un brief incompleto que deja huecos que cada parte rellena a su manera.
Mínimo, por escrito, antes de que nadie ponga un lápiz o abra un DAW:

- [ ] **Qué se entrega exactamente**: cuántas piezas, de qué tipo —«una hoja de animación
      completa con N *frames*», no «un sprite»; «una pista de 2 minutos», no «algo de música»—.
- [ ] **En qué formato**: `.png` con capas o plano, resolución exacta, paleta si la hay;
      `.wav`/`.ogg` a qué frecuencia; idioma origen y destino en una traducción.
- [ ] **Referencias concretas**, no adjetivos sueltos: «como esto, pero…» llega mucho más lejos
      que «estilo cartoon alegre».
- [ ] **Cuántas revisiones incluye el precio**, y qué pasa si hace falta una más.
- [ ] **Fecha de entrega**, y de qué depende que se cumpla —si tú tienes que aprobar un boceto
      antes de que siga, dilo—.
- [ ] **Precio y forma de pago**: por hitos en un encargo grande, la misma lógica que §5 de este
      documento ya pide para arte comprado; nunca «todo al final» en un encargo largo.
- [ ] **Cesión de derechos**, explícita, no dada por supuesta (§12.5).
- [ ] **Créditos**: cómo quiere aparecer la persona —nombre real, alias, o ninguno—, para el
      `CREDITS.md` de §9.2 y para los créditos del propio juego.

**Los originales, no solo el archivo final.** Pide el `.aseprite`/`.psd`/`.clip` de cada
ilustración y los *stems* de cada pista, no solo el PNG o el MP3 exportado — el mismo consejo que
§5 ya da para assets comprados, y aquí importa todavía más porque es trabajo hecho a medida.

### 12.3 Cómo se pide una prueba

Antes de comprometerte a un encargo grande, una **prueba pequeña y pagada** —una ilustración en
el estilo final, un *loop* corto, 300-500 palabras de traducción— resuelve en unas horas lo que
un brief perfecto no puede garantizar: si el estilo encaja de verdad, si la comunicación fluye y
si los plazos que se prometen se cumplen. **Se paga siempre**, aunque sea poco y aunque decidas
no seguir adelante: es trabajo real, y no pagarlo por ser «solo una prueba» es la forma más
rápida de que un buen profesional no quiera volver a trabajar contigo. Enmárcala como lo que es
—alcance cerrado, fecha corta—, no como el primer encargo real disfrazado de gratis.

### 12.4 Precios de referencia por rango

⚠️ **Sin verificar contra una fuente primaria de mercado**: son órdenes de magnitud amplios del
oficio, no tarifas comprobadas. Varían muchísimo por país, por experiencia del profesional, por
la complejidad real del estilo y por si compites por un encargo contra alguien que factura en una
divisa más débil que la tuya. Úsalos para no llegar en blanco a una negociación, no como precio
de catálogo.

| Encargo | Rango orientativo (⚠️) | Qué cambia el precio |
|---|---|---|
| Hoja de animación de un personaje (idle+andar+ataque, estilo simple) | Del orden de un centenar de euros a varios cientos | Número de *frames*, complejidad del estilo, variantes de color |
| Ilustración de fondo o escena (una pieza, sin animar) | Orden similar, algo más barato por pieza si se encargan varias juntas | Nivel de detalle, tamaño, si hay capas para *parallax* |
| Tema musical original (2-4 min) | Del orden de un centenar de euros por pista, más con revisiones o *stems* | Duración, instrumentación, si es adaptativo por capas ([04 · 26](../04%20-%20Recetas%20por%20g%C3%A9nero/26%20-%20M%C3%BAsica%20adaptativa%20por%20capas.md)) |
| Paquete de SFX (10-20 efectos cortos) | Del orden de decenas a un par de cientos de euros por lote | Grabados a medida frente a diseñados sobre bancos existentes |
| Traducción (por cada 1000 palabras) | Del orden de una a varias decenas de euros | Idioma de destino, urgencia, jerga de juego que exige contexto |
| **LQA de un idioma ya traducido** | Normalmente por hora, y menos que traducir de cero | Volumen de texto y si se revisa en contexto (jugando) o solo sobre el archivo |

**Si solo puedes pagar una prueba y un encargo pequeño, gástalos en lo que más veces ve el
jugador**: la hoja de animación del personaje principal y el tema de la zona inicial pesan más en
la percepción de calidad que un fondo secundario o un SFX que suena una vez.

### 12.5 Cesión de derechos: por qué «lo pagué» no es «es mío»

El malentendido más caro de toda la sección, y el más común: **pagar por un encargo no
transfiere automáticamente la propiedad intelectual de lo que se crea.** Lo que compras, salvo
que el contrato diga otra cosa, es exactamente lo que ese contrato diga — ni una modalidad de uso
más.

Verificado en el texto consolidado de la Ley de Propiedad Intelectual española (Real Decreto
Legislativo 1/1996), leído en el BOE el 06-09-2026 — ⚠️ **esto es derecho español**, y otras
jurisdicciones difieren en el detalle, aunque el principio general (cesión explícita, no
implícita) es común a la mayoría de sistemas de derecho de autor:

- **Artículo 43.1**: la cesión de derechos de explotación queda «limitada al derecho o derechos
  cedidos, a las modalidades de explotación expresamente previstas y al tiempo y ámbito
  territorial que se determinen». Si el contrato no dice que cedes el derecho a usar la
  ilustración en la *capsule* de Steam y en publicidad, en sentido estricto no lo tienes.
- **Artículo 43.2**: si no se menciona el tiempo, la cesión se limita a **cinco años**; si no se
  menciona el territorio, al **país donde se hizo la cesión**. Y si no se especifican las
  modalidades de explotación, la cesión se limita a lo «indispensable para cumplir la finalidad
  del contrato» — no a «todo lo que se me ocurra hacer con esto después».
- **Artículo 51** es la excepción que confirma la regla: para un **trabajador asalariado** (una
  relación laboral de verdad, no un freelance), a falta de pacto escrito **se presume** que los
  derechos de explotación se cedieron con el alcance necesario para la actividad habitual del
  empresario. Esa presunción **no existe** para un encargo a un contratado independiente: ahí,
  sin cesión explícita, manda el artículo 43 —limitado—, no el 51.

**En la práctica**: la cláusula de cesión del brief (§12.2) tiene que decir, sin ambigüedad, que
cedes o licencias el uso **comercial en el juego y en su publicidad** —*capsule*, tráiler,
capturas, redes—, y si quieres poder reutilizar la pieza en una secuela o en *merchandising*,
dilo también ahí. «Le pagué, así que es mío» no es una cláusula: es una suposición, y la ley por
defecto no la respalda.

### 12.6 LQA (revisión lingüística) frente a traducción automática

[04 · 21](../04%20-%20Recetas%20por%20g%C3%A9nero/21%20-%20Localizaci%C3%B3n%20e%20idiomas%20%28con%20traducci%C3%B3n%20por%20IA%29.md)
ya monta el sistema de traducción asistida por IA: la IA genera el borrador de los diez idiomas y
tú revisas el 10 % que no acierta. **LQA (*Linguistic Quality Assurance*) es exactamente ese paso
de revisión, hecho por una persona que sabe el idioma de destino y conoce el contexto del
juego**, y es un trabajo distinto de traducir de cero:

| | **Traducción** (por IA o humana) | **LQA** |
|---|---|---|
| Parte de | El texto fuente en español | El texto ya traducido |
| Comprueba | Que el significado pase a otro idioma | Que suene natural, que respete el tono del juego, que las `{variables}` sigan intactas y que el texto quepa en la UI ([04 · 21 §5](../04%20-%20Recetas%20por%20g%C3%A9nero/21%20-%20Localizaci%C3%B3n%20e%20idiomas%20%28con%20traducci%C3%B3n%20por%20IA%29.md#5--traducción-asistida-por-ia--el-flujo-moderno)) |
| Se hace mirando | El archivo de texto | Idealmente el juego en marcha, en contexto — no solo la lista de cadenas |
| Su equivalente en audio/voz | — | La escucha de [`13 · 24` §8](./24%20-%20Voz%2C%20diálogo%20y%20localización%20de%20audio.md#8--qa-de-voz): el mismo principio, aplicado al doblaje en vez de al texto |

**Un idioma «traducido» sin LQA no está terminado, está en borrador.** Encargar la revisión a
alguien distinto de quien tradujo —aunque sea por IA— es lo que atrapa los errores que el propio
autor de la traducción no ve en su texto: el mismo motivo por el que un desarrollador no debería
ser el único QA de su propio código ([13 · 10](./10%20-%20Testing%20y%20QA.md)).

---

## 13 · La salud del que hace el juego

`buscar.py --todo "burnout"` daba cero resultados en toda la biblioteca antes de esta sección. No
es un descuido menor: el motivo número uno por el que un proyecto de una persona no se termina no
es técnico. Lo que sigue es práctico, no un sermón: señales, decisiones y cuándo parar, con la
misma honestidad con la que el resto de este documento marca lo que no está verificado.

### 13.1 Jornadas y crunch: por qué sale caro incluso midiéndolo solo en resultado

*Crunch time* es trabajar más horas cerca de una fecha límite; *crunch culture* es cuando esa
sobrecarga deja de ser la excepción y se vuelve la norma esperada del proyecto — la distinción, y
las cifras que siguen, son de la entrada de Wikipedia sobre *crunch* en la industria del
videojuego (en inglés), consultada el 06-09-2026, que a su vez recoge una encuesta de la IGDA de
2004: **menos del 3 % de los desarrolladores encuestados dijo no hacer nada de trabajo extra, y de
los que sí lo hacían, casi la mitad no recibía compensación por ello.** Una encuesta de la
organización Take This en 2019, citada en la misma fuente, encontró que el **53 %** de los
desarrolladores considera el *crunch* «una parte esperada» del trabajo. Esto describe estudios
grandes, con un jefe que lo impone o lo normaliza — pero el mecanismo que importa a un proyecto de
una persona es idéntico: el jefe eres tú.

**Y no compensa ni siquiera midiéndolo solo en resultado**, que es el argumento con el que se
suele justificar. La misma fuente resume un análisis histórico de calidad de juegos frente a
horas de *crunch*: la disciplina y la organización del equipo importaban más que las horas
puestas para predecir si un juego salía bueno, y el *crunch*, en el mejor de los casos, produce
**rendimientos decrecientes** — a partir de cierto punto, una hora más no añade una hora más de
trabajo útil, añade errores que luego cuesta horas arreglar. El *death march* —*crunch* sostenido
durante meses, no solo la semana antes de lanzar— es la forma más dañina, documentada en casos
como los últimos seis a nueve meses de *Red Dead Redemption 2* en Rockstar Games o los nueve meses
de *Metroid Prime*; el declive y cierre de Core Design se atribuye en parte a años de *crunch*
continuado que fue minando al equipo hasta que la calidad de sus juegos se resintió.

**En solitario, la trampa es la misma y más difícil de ver porque no hay nadie que la señale desde
fuera**: sientes que vas retrasado → trabajas más horas → las decisiones se toman peor y aparecen
más *bugs* → hace falta más tiempo para arreglarlos → trabajas más horas todavía. La salida de ese
bucle no es «aguantar más»: es volver a §1.2 (multiplica por tres) y §1.5 (la matriz de recorte) —
casi siempre es un problema de alcance, no de esfuerzo.

### 13.2 Señales de agotamiento

La Organización Mundial de la Salud incluyó el *burnout* en la CIE-11 como **fenómeno
ocupacional** —no como enfermedad— y lo define con tres dimensiones, verificado en who.int
(comunicado del 28-05-2019, releído el 06-09-2026): **sensación de agotamiento de energía**,
**distancia mental o cinismo creciente hacia el propio trabajo**, y **sensación de menor eficacia
profesional**. Traducido a señales concretas de un proyecto personal:

- **Abrir el proyecto y sentir rechazo antes de haber tocado nada**, de forma sostenida durante
  semanas — no un mal día puntual.
- **Trabajar en tareas de relleno** (reorganizar carpetas, retocar un menú por quinta vez) en vez
  de en la tarea difícil que hace falta para avanzar de verdad: es evitación, no productividad.
- **Irritación desproporcionada** ante un comentario de *feedback* o un *bug* menor.
- **Síntomas físicos que no tenías antes**: dormir mal específicamente por el proyecto, tensión al
  pensar en él fuera de las horas de trabajo.
- **La sensación de que nada de lo que haces es suficientemente bueno**, incluso cuando lo mismo
  te habría parecido correcto hace unos meses — es la «menor eficacia profesional» de la
  definición de la OMS, no una evaluación objetiva de tu trabajo real.

**La diferencia con el cansancio normal es la duración y la causa.** Un fin de semana sin tocar el
proyecto arregla el cansancio de una semana dura. Si sigues agotado tras el descanso, o el
descanso ya no apetece porque ni siquiera desconecta la cabeza del proyecto, la señal es que el
problema no se resuelve durmiendo más, sino cambiando algo estructural: el alcance, el ritmo o, a
veces, el proyecto.

### 13.3 El proyecto que no acaba nunca

Todo §1 —alcance, matriz de recorte, *feature creep*— es prevención técnica. Esto es la parte que
la técnica no arregla: un proyecto que crece sin fin a veces no es un fallo de planificación, es
que **terminar da miedo**. Mientras el juego no está terminado, nadie puede juzgarlo; en cuanto
sale, sí. Añadir «una cosa más» es, a veces, una forma de posponer ese momento sin admitirlo ni
ante uno mismo.

No hay forma de comprobar esto desde fuera del propio criterio de quien lo vive, así que la
pregunta útil es concreta, no un diagnóstico: **si tuvieras que lanzar el juego dentro de cuatro
semanas con lo que hay hoy, ¿qué le harías?** Si la respuesta es una lista corta y factible,
hazla y lanza. Si la respuesta es «necesitaría rehacerlo todo», puede que el proyecto de verdad no
esté cerca — o puede que sea la ansiedad hablando, y solo la matriz de recorte de §1.5, aplicada
con honestidad, distingue una cosa de la otra.

### 13.4 Trabajar solo y el aislamiento

El desarrollo en solitario tiene un coste que rara vez se nombra: **nadie más ve el trabajo hasta
que lo enseñas**, y esa falta de contacto diario con gente que entiende el problema pesa, además
del propio trabajo. Tres mitigaciones baratas, ya cubiertas en otras partes de esta biblioteca:

- **El diario de desarrollo de §3.6** no es solo memoria técnica: escribir tres líneas cada
  sesión es, también, la única conversación que tiene el proyecto contigo cuando no hay nadie más.
- **Comunidades activas** donde enseñar avances y pedir ayuda concreta —no solo cuando algo se
  rompe— están catalogadas en
  [07 · 10 — Comunidades y dónde preguntar](../07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md).
  Un *devlog* quincenal, aunque lo lea poca gente, es contacto real con personas ajenas al
  proyecto, y las *builds* jugables de §3.4 ya dan material para publicarlo sin trabajo extra.
- **Un compañero de rendición de cuentas** (*accountability partner*) —otro desarrollador con
  quien compartir el objetivo semanal de §3.3 y confirmar si se cumplió— no hace el trabajo por
  ti, pero rompe el patrón de que solo tú sabes si el proyecto avanza.

### 13.5 Cuándo parar o cambiar de alcance

Señales concretas, no una sensación vaga, para decidir sin depender solo del estado de ánimo del
día:

- **Tres semanas seguidas en las que la frase de §3.3 («un objetivo por semana») ha sido falsa.**
  No es un problema de disciplina: es una señal medible de que el alcance de esa fase no encaja
  con el tiempo real disponible. Vuelve a §1.5.
- **El proyecto ya lleva más del doble de tu estimación multiplicada por tres** (§1.2) y sigue sin
  vertical slice. En ese punto, el factor de corrección ya no explica el retraso: el alcance sí.
- **Llevas más de un hito seguido posponiendo el mismo sistema** porque cada vez que lo tocas
  aparece algo peor de lo esperado: puede ser una decisión de arquitectura equivocada —revisa el
  ADR correspondiente, §3.5—, no falta de tiempo.

**El coste hundido no es una razón para seguir.** Los meses ya invertidos no vuelven ni
terminando ni abandonando: la única pregunta que importa es si, sabiendo lo que sabes hoy,
elegirías este alcance empezando de cero. Si la respuesta es no, recórtalo (§1.5) antes de
plantearte abandonar el proyecto entero — casi siempre hay una versión más pequeña que sí merece
la pena terminar.

**Y si de verdad hay que abandonarlo**, hazlo dejando algo: el postmortem de §8.5 se escribe
igual aunque el juego no llegue a lanzarse —la plantilla ya dice «aunque el juego haya ido mal»—,
y un proyecto sin terminar enseña casi tanto como uno terminado si te paras a mirarlo con
honestidad en vez de borrar la carpeta y no volver a hablar de ello.

### 13.6 «No me apetece hoy» frente a «esto ya no me interesa»

⚠️ No hay una prueba objetiva para esto: son criterios prácticos de esta biblioteca, no un
diagnóstico verificado contra ninguna fuente clínica. Tres preguntas que ayudan a distinguirlo sin
tomar una decisión grande en el peor momento del día:

1. **¿La resistencia desaparece a los diez minutos de haber empezado?** Si sí, era pereza de
   arrancar, no falta de interés — casi todo el mundo la siente con casi todas las tareas, y
   forzar los primeros diez minutos suele bastar.
2. **¿Es esta tarea concreta, o es el proyecto entero?** Odiar depurar un *bug* puntual un martes
   por la tarde no dice nada del proyecto. Sentir lo mismo ante cualquier tarea del proyecto,
   durante semanas, sí dice algo.
3. **¿Ha cambiado algo real, o solo ha pasado tiempo?** Si el juego que te ilusionaba hace un año
   ya no te dice nada ni imaginándolo terminado —no solo el trabajo de hoy—, es una señal distinta
   de estar simplemente cansado de una fase concreta (§13.2).

**No todo lo de aquí exige una decisión drástica.** La mayoría de los días malos son eso: días
malos, y se resuelven con un descanso, no con un replanteamiento del proyecto. Reserva las
decisiones grandes —recortar de verdad, cambiar de alcance, parar— para cuando la señal se repite
durante semanas, no para el primer día en que cuesta arrancar.

---

## Ver también

- [13 · 28 — De «hazme un juego» a una especificación: el protocolo de elicitación del agente](./28%20-%20De%20hazme%20un%20juego%20a%20una%20especificaci%C3%B3n%20-%20el%20protocolo%20de%20elicitaci%C3%B3n%20del%20agente.md) — cuándo las fases de §2 no aplican (sesión de agente en vez de calendario humano), nota en la cabecera de esa sección
- [13 · 01 — Diseño de juego: core loop, mecánicas, balance y dificultad](./01%20-%20Dise%C3%B1o%20de%20juego%20-%20core%20loop%2C%20mec%C3%A1nicas%2C%20balance%20y%20dificultad.md) — el bucle que aquí se manda construir primero, y qué medir para ajustarlo
- [13 · 06 — Arquitectura de un proyecto GameMaker](./06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md) — las decisiones estructurales que merecen un ADR
- [13 · 05 — UI y UX de juego](./05%20-%20UI%20y%20UX%20de%20juego.md) — los menús, la pausa y las opciones que la alfa tiene que cerrar
- [13 · 03 — Pixel art y resolución](./03%20-%20Pixel%20art%20y%20resoluci%C3%B3n.md) — decisiones que hay que tomar antes del vertical slice, porque después son carísimas
- [04 · 00 — Anatomía de un juego completo](../04%20-%20Recetas%20por%20g%C3%A9nero/00%20-%20Anatom%C3%ADa%20de%20un%20juego%20completo.md) — el temario de escenas y sistemas que la alfa debe cubrir
- [04 · 15 — Game feel y juice](../04%20-%20Recetas%20por%20g%C3%A9nero/15%20-%20Game%20feel%20y%20juice.md) — el trabajo del 25 % final · [04 · 27 — Accesibilidad](../04%20-%20Recetas%20por%20g%C3%A9nero/27%20-%20Accesibilidad.md) · [04 · 21 — Localización e idiomas](../04%20-%20Recetas%20por%20g%C3%A9nero/21%20-%20Localizaci%C3%B3n%20e%20idiomas%20%28con%20traducci%C3%B3n%20por%20IA%29.md)
- [04 · 20 — Servicios de plataforma](../04%20-%20Recetas%20por%20g%C3%A9nero/20%20-%20Servicios%20de%20plataforma%20%28logros%2C%20anuncios%2C%20compras%29.md) — logros, anuncios, compras y nube
- [05 · 02 — Publicar y exportar](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md) · [01 · 16 — Exportar y publicar](../01%20-%20Fundamentos/16%20-%20Exportar%20y%20publicar.md) · [01 · 15 — Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md)
- [05 · 05 — Entregar el juego: firmar, notarizar y subir a las tiendas](<../05 - Referencia/05 - Entregar el juego - firmar, notarizar y subir a las tiendas.md>) — el trámite técnico de Steam, macOS, Windows, Google Play y App Store que este documento asume resuelto en §6.8 y §9
- [13 · 25 — Legal de terceros: marcas, fan games y parodia](./25%20-%20Legal%20de%20terceros%20-%20marcas%2C%20fan%20games%20y%20parodia.md) · [13 · 26 — Comunidad propia: Discord, moderación y gestión de crisis](./26%20-%20Comunidad%20propia%20-%20Discord%2C%20moderaci%C3%B3n%20y%20gesti%C3%B3n%20de%20crisis.md) — el resto del legal de §9 (propiedad de terceros) y del post-lanzamiento de §7 (comunidad y crisis) que este documento no repite
- [07 · 13 — GM CLI](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) — `compile`, `package`, ResourceTool y los workflows de GitHub Actions
- [07 · 08 — itch.io: jams, assets y juegos](../07%20-%20Ecosistema/08%20-%20itch.io%20-%20jams%2C%20assets%20y%20juegos.md) · [12 · 06 — itch.io: assets, herramientas y jams](../12%20-%20Utilidades%20e%20integraciones/06%20-%20itch.io%20-%20assets%2C%20herramientas%20y%20jams.md)
- [07 · 09 — Asset packs y recursos gráficos](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md) (§1 es la tabla de licencias) · [07 · 10 — Comunidades y dónde preguntar](../07%20-%20Ecosistema/10%20-%20Comunidades%20y%20d%C3%B3nde%20preguntar.md) · [07 · 11 — Blogs, newsletters y podcasts](../07%20-%20Ecosistema/11%20-%20Blogs%2C%20newsletters%20y%20podcasts.md)
- [13 · 24 — Voz, diálogo y localización de audio](./24%20-%20Voz%2C%20di%C3%A1logo%20y%20localizaci%C3%B3n%20de%20audio.md) — LQA de voz (§8 de ese documento), enlazado desde §12.6 · [13 · 10 — Testing y QA](./10%20-%20Testing%20y%20QA.md) — por qué el propio autor no debería ser el único QA, base de §12.6
- [03 · 24 — Control de versiones con Git](../03%20-%20Cursos%20%28YouTube%29/24%20-%20DragoniteSpam%20-%20Getting%20Started%20-%20Control%20de%20Versiones%20con%20Git.md) · [03 · 12 — Exportar y publicar](../03%20-%20Cursos%20%28YouTube%29/12%20-%20Curso%202026%20-%20Sky%20LaRell%20Anderson%20-%20Parte%2012%20-%20Exportar%20y%20Publicar.md)
- [README §2 — Estado del ecosistema GameMaker hoy](../README.md) — en qué runtime y en qué canal estás publicando

---

## Fuentes

Todas consultadas el **6 de septiembre de 2026**.

**Steamworks (documentación oficial para socios)**
- Coming Soon — <https://partner.steamgames.com/doc/store/coming_soon> · «you must have a Coming Soon page up for at least two weeks before releasing»; «submit your request for review at least 7 business days before you want your page live»
- Releasing your game — <https://partner.steamgames.com/doc/store/releasing> · revisión de 3–5 días hábiles; «Approved titles will not release themselves»
- Store assets (capsules y capturas) — <https://partner.steamgames.com/doc/store/assets/standard>
- Steam Next Fest, consejos — <https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest/tips> · «Steam Next Fest only includes games with demos»; lista a prensa 10 días antes
- Precios y descuentos — <https://partner.steamgames.com/doc/store/pricing> · 30 días sin cambios tras el lanzamiento; topes de descuento por precio base
- Content Survey (clasificación y declaración de IA generativa) — <https://partner.steamgames.com/doc/gettingstarted/contentsurvey>
- Preguntas fiscales (W-8BEN, retención del 30 %, TIN/ITIN/EIN) — <https://partner.steamgames.com/doc/finance/taxfaq>

**GameMaker (oficial)**
- Licencias y precios — <https://gamemaker.io/en/get>
- «12 Key Steps To Market & Promote Your Indie Game», Ross Bramble, 19-03-2023 — <https://gamemaker.io/en/blog/market-an-indie-game> · entender el proyecto, contar tu historia, estudiar a los competidores, *elevator pitch*, comunidad, confianza, material de marketing, press kit, recomendaciones, descuentos, actualizaciones y DLC
- «IMPRESS with Indie Game Marketing» — <https://gamemaker.io/en/blog/impress-indie-marketing>
- Manual LTS 2026, `GM_version` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/OS_And_Compiler/GM_version.htm>
- Manual LTS 2026, `exception_unhandled_handler` — <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Debugging/exception_unhandled_handler.htm>

**Producción y alcance**
- Greg Donovan (Volition), *The Vertical Slice Challenge*, GDC 2015 — <https://gdcvault.com/play/1022328/The-Vertical-Slice> · transcripción íntegra en <https://archive.org/stream/GDC2015Donovan/GDC2015-Donovan_djvu.txt>

**Marketing**
- Chris Zukowski, *How To Market A Game* — <https://howtomarketagame.com/> · benchmarks en <https://howtomarketagame.com/benchmarks/>
- «When should I post my Steam coming-soon page?» — <https://howtomarketagame.com/2025/03/10/when-should-i-post-my-steam-coming-soon-page/>
- «How many wishlists should I have when I launch my game?» (actualizado en junio de 2026) — <https://howtomarketagame.com/2022/09/26/how-many-wishlists-should-i-have-when-i-launch-my-game/>
- Rami Ismail, presskit() — <https://dopresskit.com/>

**Clasificación por edades**
- IARC, cómo funciona — <https://www.globalratings.com/how-iarc-works/> · organismos participantes — <https://www.globalratings.com/participants/>

**Control de versiones: Git LFS (§4.1)**
- GitHub Docs, *About storage and bandwidth usage* — <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage> (06-09-2026) · cuotas gratuitas de 10 GiB (Free/Pro) y 250 GiB (Team/Enterprise Cloud) para almacenamiento y ancho de banda de Git LFS; facturación por uso al superarlas
- Manual oficial de `git lfs migrate` — <https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/man/git-lfs-migrate.adoc> (06-09-2026) · confirma que `import`/`export` reescriben el historial y exigen *force-push* coordinado
- Perforce, *Free Version Control Software* — <https://www.perforce.com/products/helix-core/free-version-control> (06-09-2026) · «Perforce P4 is free for up to 5 users and 20 workspaces»

**Trabajar con otras personas (§12)**
- Real Decreto Legislativo 1/1996, Ley de Propiedad Intelectual, texto consolidado — BOE, <https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930> (06-09-2026) · artículos 43 (transmisión *inter vivos*, cesión limitada a lo expresamente pactado) y 51 (presunción de cesión solo para trabajador asalariado), base de §12.5. ⚠️ Derecho español: otras jurisdicciones difieren en el detalle.

**Datos de menores — COPPA y RGPD (§9.3, 07-09-2026)**
- Federal Trade Commission, *Complying with COPPA: Frequently Asked Questions* — <https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions> · umbral de 13 años, consentimiento parental verificable, norma final revisada en vigor desde el 23-06-2025
- Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales, texto consolidado — BOE, <https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673> · artículo 7, umbral español de 14 años para el consentimiento propio del menor

**Salud del desarrollador (§13)**
- Wikipedia (en inglés), *Crunch (video games)* — <https://en.wikipedia.org/wiki/Crunch_(video_games)> (06-09-2026) · distinción *crunch time*/*crunch culture*, encuesta IGDA 2004, encuesta Take This 2019 (53 %), conclusión de rendimientos decrecientes, casos de *Red Dead Redemption 2*, *Metroid Prime* y Core Design — base de §13.1
- Organización Mundial de la Salud, *Burn-out an "occupational phenomenon": International Classification of Diseases* — <https://www.who.int/news/item/28-05-2019-burn-out-an-occupational-phenomenon-international-classification-of-diseases> (comunicado 28-05-2019, releído 06-09-2026) · definición oficial de las tres dimensiones del *burnout*, base de §13.2

**Verificado en local (06-09-2026)**
- `gm-cli init --no-interactive -t "Space Rocks" --toolchain GMS2@2026.0.0.23`: contenido real del `.gitignore` y del `.gitattributes` generados; `.gmcache` de 131 MB **no** ignorado (`git check-ignore -v .gmcache` sin salida)
- `gm-cli compile --errors-only --toolchain GMS2@2026.0.0.23` sobre los bloques de GML de §4.4 y §4.5: **código de salida 0, sin errores de sintaxis** (`--errors-only` no muestra `WARNING`, ver Trampa 8 de `12 · 09` §0)
- `python3 _indice/buscar.py` para cada símbolo usado: `GM_version`, `GM_build_date`, `GM_build_type`, `GM_runtime_version`, `date_datetime_string`, `exception_unhandled_handler`, `room_get_name`, `display_get_gui_width`, `display_get_gui_height`, `draw_set_halign`, `draw_set_valign`, `draw_set_colour`, `draw_set_alpha`, `draw_text`, `show_debug_message`, `clipboard_set_text`, `file_exists`, `file_delete`, `file_text_open_write`, `file_text_write_string`, `file_text_close`, `array_length`, `fa_right`, `fa_bottom`, `fa_left`, `fa_top`, `c_white`
