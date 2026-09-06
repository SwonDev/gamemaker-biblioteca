# 21 · Vinyl — audio avanzado (guía en español)

> **Vinyl** (de @jujuadams) es una capa de audio de alto nivel para GameMaker: mezcladores por
> etiqueta, fundidos, **ducking** (bajar la música cuando habla alguien), y **sincronía con el
> beat** de la música. Resuelve lo que el audio nativo deja en tus manos. Guía en español con la
> API verificada contra el código en `11 - Código descargado/librerias/audio/Vinyl`.

> 🔎 **Versión, comprobada el 6 de septiembre de 2026** contra
> `api.github.com/repos/JujuAdams/Vinyl/releases`:
>
> | Canal | Versión | Publicada |
> |---|---|---|
> | Estable (sin sufijo alfa/beta) | **6.3.4** | 2026-01-28 |
> | Más reciente (beta) | **6.4.2-beta** | 2026-06-03 — añade el *beat tracker* (`VinylGetBPM`, `VinylGetBeatThisStep`, `VinylGetBeatCount`, `VinylGetBeatDistance`, `VinylAttachBeatTracker`) y `VinylGetTrackPosition`, y ya viene compilada para GameMaker LTS 2026 |
>
> ⚠️ GitHub marca `6.4.2-beta` con `"prerelease": false` en la API pese a su nombre — parece un
> descuido del autor al publicarla, no una promoción oficial a estable. Para producción, `6.3.4`
> es la apuesta segura; si el juego ya necesita sincronía con el beat (funciones de la sección 4
> de abajo), `6.4.2-beta` es la única versión que las trae. El repositorio clonado en
> `11 - Código descargado/librerias/audio/Vinyl/` no lleva un número de versión propio: contrasta
> la API de arriba en cada instalación nueva.

---

## Por qué Vinyl y no `audio_play_sound`

El audio nativo reproduce sonidos; gestionar volúmenes por categoría, fundidos suaves, prioridad
entre voces y sincronía con la música lo escribes tú. Vinyl trae todo eso hecho, con nombres de
**etiqueta** (music, sfx, ui, voice) en vez de manejar IDs de bus a mano.

---

## 1 · Reproducir y parar

```gml
/// reproducir un sonido (Vinyl gestiona la instancia por ti)
voz = VinylPlay(snd_disparo);

/// con fundido de entrada (música que entra suave)
musica = VinylPlayFadeIn(snd_musica_nivel, 2.0);   // 2 s de fade-in

/// reproducir en un "bus"/etiqueta concreto (para controlar su volumen aparte)
VinylPlayOn("sfx", snd_explosion);

VinylStop(voz);                 // parar una instancia
VinylStopAll();                 // parar todo
VinylIsPlaying(musica);         // ¿sigue sonando?
```

---

## 2 · Volumen por etiqueta (el mezclador)

En vez de ajustar cada sonido, ajustas **grupos por nombre**. Esto es lo que conecta con el menú
de opciones ([25 · Opciones](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md)).

```gml
/// el jugador baja los efectos al 50 % en Opciones
VinylMixSetGain("sfx", 0.5, 0.2);        // etiqueta, ganancia, tiempo de fundido

/// volumen maestro (todo)
VinylMasterSetGain(0.8, 0);

/// ajustar una instancia concreta (un sonido que se aleja)
VinylSetGain(voz, 0.3, 1.0);             // baja a 0.3 en 1 s
VinylSetPitch(voz, 1.2);                  // tono más agudo
```

> 💡 **Las etiquetas ("music", "sfx", "ui", "voice") son la clave de Vinyl.** Un menú de opciones
> con sliders de música/efectos/voz se conecta con `VinylMixSetGain(etiqueta, valor)` — una línea
> por slider, sin tocar cada sonido.

---

## 3 · Ducking: bajar la música cuando habla alguien

El *ducking* atenúa automáticamente un grupo cuando suena otro de más prioridad —la música baja
sola mientras un personaje habla, y vuelve al terminar. Vinyl lo trae integrado (`VinylDucker*`);
se configura por prioridad de etiqueta.

> 🔺 **El ducking es lo que hace que el diálogo se entienda sin bajar la música a mano.** Das más
> prioridad a "voice" que a "music", y Vinyl agacha la música cada vez que suena una voz. Es
> detalle de producción que separa un juego pulido de uno amateur.

---

## 4 · Sincronía con el beat (música rítmica)

Vinyl puede rastrear el **compás** de la música, para sincronizar efectos visuales o mecánicas
con ella —lo que en [19 · Programación rítmica](../04%20-%20Recetas%20por%20género/19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md)
hacíamos a mano con `audio_sound_get_track_position`, Vinyl lo da resuelto:

```gml
/// Create — decirle a Vinyl el BPM y engancharle un rastreador de beats
VinylAttachBeatTracker(musica, 128);      // 128 BPM

/// Step — ¿ha caído un beat este frame?
if (VinylGetBeatThisStep(musica)) {
    pulso = 1;                             // el HUD late con la música
}
var _beat = VinylGetBeatCount(musica);    // en qué beat vamos
var _dist = VinylGetBeatDistance(musica); // cuánto falta para el siguiente (0..1)
```

> 💡 **`VinylGetBeatThisStep` es más fiable que calcular la posición de pista a mano**, porque
> Vinyl compensa la latencia del hilo de audio. Para un juego de ritmo serio, es la vía buena.

---

## La API esencial (verificada en el código)

| Función | Qué hace |
|---|---|
| `VinylPlay(sonido)` / `VinylPlayFadeIn` / `VinylPlayOn(etiqueta, sonido)` | Reproducir |
| `VinylStop` / `VinylStopAll` / `VinylResume` | Parar / reanudar |
| `VinylIsPlaying(instancia)` | ¿Suena? |
| `VinylSetGain` / `VinylSetPitch` | Volumen / tono de una instancia |
| `VinylMixSetGain(etiqueta, gain, tiempo)` | Volumen de un grupo |
| `VinylMasterSetGain` | Volumen maestro |
| `VinylFadeOut` | Fundido de salida |
| `VinylAttachBeatTracker` / `VinylGetBeatThisStep` / `VinylGetBeatCount` / `VinylGetBPM` | Sincronía con el beat |
| `VinylDucker*` | Ducking automático |

> 🔺 **No están en `buscar.py`** (librería, no runtime). Verifica en
> `11 - Código descargado/librerias/audio/Vinyl/scripts/`.

---

## Ver también

- [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — el audio nativo que Vinyl envuelve
- [26 · Música adaptativa por capas](../04%20-%20Recetas%20por%20género/26%20-%20Música%20adaptativa%20por%20capas.md) — vertical layering, que Vinyl facilita con blending
- [19 · Programación rítmica](../04%20-%20Recetas%20por%20género/19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md) — la sincronía con el beat a mano vs con Vinyl
- [25 · Menú de opciones](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — los sliders de volumen conectados a `VinylMixSetGain`
- Repo oficial: <https://github.com/JujuAdams/Vinyl>
