# «Enjambre» — especificación

> Escrita ANTES de crear el proyecto, como exige `13 · 28` y el paso 0 del flujo de la
> skill. El encargo llegó cerrado y **sin canal de vuelta** («haz un juego que demuestre
> la skill»), así que se aplican los valores por defecto de `13 · 28 §2.3` y **cada uno
> queda marcado `[DEFAULT]`** para que se pueda auditar qué decidió el usuario y qué
> asumí yo.

## 1 · Las ocho preguntas de arranque

| # | Pregunta | Respuesta | Origen |
|---|---|---|---|
| 1 | Género | Arena de disparo cenital de doble palanca (*twin-stick*) | `[DEFAULT]` — elegido por ser el que más enseña en pantalla: enemigos, partículas, sacudida, HUD |
| 2 | Alcance | Una sesión: un juego completo y corto, no una demo técnica | `[DEFAULT]` |
| 3 | Plataforma | macOS (arm64), teclado **y** mando | Del encargo (la máquina) |
| 4 | Arte | Pixel art propio generado por código, paleta cerrada de 16 colores | `[DEFAULT]` — la regla dura prohíbe entregar rectángulos |
| 5 | Sonido | Sintetizado por código en el arranque, sin archivos de terceros | `[DEFAULT]` |
| 6 | Idiomas | Español e inglés, completos, conmutables en caliente | `[DEFAULT]` — el auditor exige que no haya texto a pelo |
| 7 | Guardado | Récord y ajustes, con versión de esquema y checksum | `[DEFAULT]` |
| 8 | Criterio de cierre | El arco completo de `04 · 00` + `auditar-juego-completo.py` sin ✗ | Del encargo |

## 2 · GDD de una página

**Fantasía**: eres el último dron de escolta de una colmena caída; aguantas mientras puedas.

**Bucle**: mover (WASD / palanca izquierda) + apuntar y disparar (ratón / palanca derecha) →
matar enemigos → sube la oleada → más enemigos y más rápidos → mueres → récord.

**Tensión**: la munición no es infinita, se recarga sola pero despacio; los enemigos sueltan
celdas de energía que la devuelven. Quedarse quieto disparando no funciona: hay que recoger.

**Progresión dentro de la partida**: cada oleada añade un tipo. Oleada 1 rastreadores lentos;
3 aparecen los veloces; 5 los que se dividen al morir; cada 5 un enjambre denso.

**Fin**: tres vidas. Al morir, pantalla de derrota con la oleada alcanzada y si es récord.

## 3 · Sistemas y de dónde salen

| Sistema | Documento de la biblioteca | Reutiliza |
|---|---|---|
| Máquina de estados del juego | `04 · 02 §5.9` | `scr_state_machine.gml` |
| Pool de balas y enemigos | `04 · 03` | `scr_pool.gml` |
| Sacudida de cámara y *hit-stop* | `04 · 15` (game feel) | `scr_camera.gml` |
| Partículas y VFX | `04 · 39` | — |
| Guardado con versión y checksum | `01 · 14` | `scr_save_load.gml` |
| Idiomas | `04 · 21` | — |
| Entrada teclado + mando | `04 · 02`, `07 · 02` | `scr_input_buffer.gml` |
| Envoltorio de pantallas | `04 · 00`, `04 · 41` | — |

## 4 · Lo que NO va a tener, dicho por delante

Sin multijugador, sin logros de plataforma, sin niveles diseñados a mano (la arena es una),
sin narrativa ramificada. Son recortes de alcance conscientes, no olvidos.
