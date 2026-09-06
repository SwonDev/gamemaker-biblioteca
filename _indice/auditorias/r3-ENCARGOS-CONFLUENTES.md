# Encargos que piden dos o más auditorías a la vez

> Cuando dos auditores independientes marcan el mismo hueco, sube de prioridad: no es la manía
> de un dominio, es un agujero real. Esta es la cola de redacción de la tercera ronda.

## 🔴 1 · La última milla de publicación comercial
**Lo piden:** `r3-plataformas-legal.md` (encargos de Steam y macOS) y `r3-herramientas-pipeline.md`
(hueco grave nº 1). La biblioteca sabe compilar y sabe programar compras dentro de la app, pero
no sabe **entregar el juego**.

Un solo documento, en `05 - Referencia/`: alta de la aplicación en Steamworks, depósitos y
lanzamientos, subir con `steamcmd`, ramas beta y claves; firma y **notarización en macOS**
(`codesign`, `notarytool`, *stapler*, y qué pasa si no lo haces); firma en Windows y el aviso de
SmartScreen; `butler` para itch.io (ya cubierto en `07`: enlazar, no repetir); App Bundle firmado
para Google Play y la ficha de privacidad; TestFlight y revisión en App Store.

## 🔴 2 · Herramientas externas de perfilado
**Lo pide:** `r3-rendimiento.md` (hueco grave nº 1). Cero menciones de RenderDoc, Instruments o
Android Profiler en toda la biblioteca. Qué se puede y qué no se puede ver desde fuera de
GameMaker, y cuándo compensa. Destino: ampliar `01 - Fundamentos/15`.

## 🔴 3 · Marcas registradas, *fan games* y parodia
**Lo pide:** `r3-plataformas-legal.md`. Riesgo invisible: un agente al que le piden «un homenaje a
X» no tiene hoy ninguna advertencia. Destino: `13 - …/20 - Modelo de negocio, monetización y ética`.

## 🟠 4 · Citas cruzadas rotas detectadas de paso
- `13/01` remite a `01/15` para «el profiler» y allí no está.
- `01/01 §5` promete los Workspaces y no los desarrolla.
- `08/22` línea 33: el comentario dice «en bucle» y contradice la firma real de
  `skeleton_animation_set` (lo detectó `r3-arte-animacion.md`); produciría animaciones rotas.
- `04/28` y `13/03` no se enlazan entre sí en el tema de DPI y *letterbox*.
