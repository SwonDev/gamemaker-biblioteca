#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probar-descubrimiento.py — simula tareas de LLM y comprueba que la biblioteca responde.

No prueba código: prueba **si un LLM que recibe una tarea de GameMaker encuentra lo que
necesita** con las herramientas del proyecto. Para cada tarea define qué debería aparecer
(un símbolo, un documento, un ejemplo real) y verifica que `buscar.py` lo devuelve.

    python3 _indice/probar-descubrimiento.py

Sale con 0 solo si todas las tareas se resuelven. Es la prueba de que el «contenedor» sirve
para lo que existe: que cualquiera pueda buscar lo que necesita y encontrarlo.
"""
import os, subprocess, sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida de este script vía subprocess), sys.stdout
# usa la página de códigos ANSI del sistema en vez de UTF-8 — y los símbolos ✗/⚠/→/…
# de este código no caben ahí: UnicodeEncodeError a mitad de ejecución. No verificado
# en Windows de verdad; aplica la solución estándar de Python 3.7+ (PEP 528 cubre la
# consola interactiva sola, no pipes ni redirecciones).
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUSCAR = os.path.join(RAIZ, "_indice", "buscar.py")


def salida(*args):
    r = subprocess.run([sys.executable, BUSCAR, *args], capture_output=True, text=True)
    return r.stdout


def _carpeta_instalada(nombre):
    ruta = os.path.join(RAIZ, nombre)
    if not os.path.isdir(ruta):
        return False
    return bool([e for e in os.listdir(ruta) if e not in ("_RUTAS.json", "_CATALOGO.md")])


MANUAL_INSTALADO = _carpeta_instalada("09 - Manual oficial")
CODIGO_INSTALADO = _carpeta_instalada("11 - Código descargado")

# Etiquetas de la salida de buscar.py que SOLO pueden aparecer si el manual espejado o el
# código descargado están instalados en esta máquina (ver verificar-enlaces.py). En un clon
# limpio sin reconstruir, exigirlas no prueba que el descubrimiento falle: prueba que una
# fuente opcional no está — eso ya lo dice actualizar.py en su propio paso, no hace falta
# repetirlo aquí como si fuera un fallo del buscador.
ETIQUETAS_MANUAL = {"manual (es)"}
ETIQUETAS_CODIGO = {"CÓDIGO real", "juegos_y_motores", "extensiones_oficiales",
                     "herramientas", "librerias", "plantillas_y_ejemplos"}

# El índice de símbolos se genera del GmlSpec.xml del runtime INSTALADO: en un clon
# recién bajado de GitHub, sin GameMaker en la máquina, no existe. Sin él `buscar.py`
# no puede dar la ficha de ninguna función, y diez de estas tareas fallaban con un
# «10 de 55 tareas sin resolver» que se lee como «la biblioteca está rota» cuando la
# verdad es «falta instalar GameMaker». Es el mismo perdón que ya se hace con el
# manual y el código descargado, que también son fuentes opcionales.
SIMBOLOS_INSTALADOS = os.path.isfile(os.path.join(RAIZ, "_indice", "simbolos.json"))


# Cada caso: (descripción de la tarea, argumentos de buscar.py, textos que DEBEN aparecer)
CASOS = [
    ("Quiero hacer que el jugador salte con margen de perdón",
     ["--todo", "coyote time"],
     ["BIBLIOTECA", "Plataformas 2D", "CÓDIGO real"]),

    ("¿Cómo dibujo un sprite rotado y escalado?",
     ["draw_sprite_ext"],
     ["draw_sprite_ext(sprite, subimg", "manual (es)"]),

    ("Necesito una máquina de estados sin objetos",
     ["--todo", "state_machine"],
     ["CÓDIGO real", "juegos_y_motores"]),

    ("¿Existe la función para bloquear el ratón?",
     ["window_mouse_set_locked"],
     ["window_mouse_set_locked(enable)", "manual (es)"]),

    ("Quiero publicar mi juego en la web",
     ["--todo", "gmcallback"],
     ["Interoperabilidad con la web", "07 - Funciones"]),

    ("¿Cuánto vale pi? El manual no me lo encuentra",
     ["pi"],
     ["explicada en la biblioteca", "21 - Constantes que el manual abrevia"]),

    ("Necesito un juego real de referencia para estudiar",
     ["--todo", "obj_player"],
     ["CÓDIGO real", "juegos_y_motores"]),

    ("¿Cómo sincronizo lógica con la música (juego de ritmo)?",
     ["--texto", "audio_sound_get_track_position"],
     ["Programación rítmica"]),

    ("Función inventada que no debe existir",
     ["funcion_falsa_inexistente_xyz"],
     ["NO existe"]),

    ("Un curso en vídeo en español para empezar de cero",
     ["--texto", "Alas de reptil"],
     ["Cursos en español"]),

    ("Quiero desarrollar un juego completo de principio a fin",
     ["--texto", "Anatomía de un juego completo"],
     ["Anatomía de un juego completo"]),

    ("¿Cómo pongo logros de Steam y anuncios?",
     ["--texto", "steam_set_achievement"],
     ["Servicios de plataforma"]),

    ("Quiero mi juego en varios idiomas, traducidos con IA",
     ["--texto", "traducción por IA"],
     ["Localización e idiomas"]),

    ("¿Cómo reproduzco un vídeo de intro?",
     ["video_open"],
     ["video_open(path)", "manual (es)"]),

    ("¿Dónde consigo sprites, música y assets gratis con licencia?",
     ["--texto", "Asset packs"],
     ["Asset packs y recursos gráficos"]),

    # ── Carpeta 13: el oficio, no solo el motor ──────────────────────────────
    ("Quiero diseñar un nivel que enseñe la mecánica sin texto",
     ["--texto", "kishōtenketsu"],
     ["Diseño de niveles"]),

    ("Necesito repartir árboles por el mapa sin que se amontonen",
     ["--todo", "Poisson"],
     ["Generación procedural avanzada"]),

    ("¿Qué resolución base uso para un juego en pixel art?",
     ["--texto", "escalado entero"],
     ["Pixel art y resolución"]),

    ("Agua 2D que salpica cuando el jugador cae dentro",
     ["--texto", "Verlet"],
     ["Físicas a mano y fluidos"]),

    ("¿Cómo estructuro el proyecto para que no se me vaya de las manos?",
     ["--texto", "Service Locator"],
     ["Arquitectura de un proyecto GameMaker"]),

    ("¿Cómo pruebo el juego de forma automática?",
     ["--texto", "GM-TestFramework"],
     ["Testing y QA"]),

    ("¿Cuánto debo abarcar? ¿Qué es un vertical slice?",
     ["--texto", "vertical slice"],
     ["Producción, alcance y lanzamiento"]),

    ("Quiero equilibrar la economía y la curva de dificultad",
     ["--texto", "curva de dificultad"],
     ["Diseño de juego"]),

    ("Una HUD que se vea bien en cualquier resolución y con mando",
     ["--texto", "safe area"],
     ["UI y UX de juego"]),

    ("Reproducir una Sequence por código",
     ["layer_sequence_create"],
     ["Animación de sprites"]),

    # ── Recetas nuevas de 04 ────────────────────────────────────────────────
    ("Golpes con hitbox y hurtbox para un beat 'em up",
     ["--texto", "hurtbox"],
     ["Combate cuerpo a cuerpo"]),

    ("IA de enemigos con árbol de comportamiento",
     ["--texto", "behavior tree"],
     ["árboles de comportamiento"]),

    ("Un joystick virtual para móvil",
     ["--texto", "joystick virtual"],
     ["Juegos para móvil"]),

    ("Cargar un modelo 3D y lanzar un rayo contra sus triángulos",
     ["--texto", "Möller"],
     ["3D en GameMaker"]),

    # ── Segunda auditoría: los ~30 documentos de 2026-09-06 ──────────────────
    ("Quiero tipos de daño, resistencias y veneno que quema con el tiempo",
     ["--texto", "efectos de estado"],
     ["Sistema de daño"]),

    ("Que los enemigos no me ataquen todos a la vez",
     ["--texto", "fichas de ataque"],
     ["Diseño de enemigos"]),

    ("Recargar el arma y que la bala atraviese a dos enemigos",
     ["--texto", "hitscan"],
     ["Combate a distancia"]),

    ("Mi personaje tiene que subir por una pendiente y agarrarse a un borde",
     ["--texto", "ledge grab"],
     ["Traversal en plataformas"]),

    ("Muchas unidades yendo al mismo sitio sin calcular A* para cada una",
     ["--texto", "campo de flujo"],
     ["Pathfinding avanzado"]),

    ("Una explosión que no parezca de asset gratis",
     ["--texto", "part_type_death"],
     ["VFX"]),

    ("Un shader que ponga al enemigo blanco al recibir el golpe",
     ["--texto", "hit flash"],
     ["Recetario de shaders"]),

    ("Menú de pausa que pare de verdad las partículas y las secuencias",
     ["--texto", "time_source_pause"],
     ["Transiciones, carga y pausa"]),

    ("Que los pasos suenen distinto según el suelo que piso",
     ["--texto", "pasos por material"],
     ["Audio reactivo al mundo"]),

    ("Generar un tono por código sin tener el sonido como asset",
     ["audio_create_buffer_sound"],
     ["audio_create_buffer_sound", "manual (es)"]),

    ("Escribir el documento de diseño para que un agente lo implemente",
     ["--texto", "one-pager"],
     ["El documento de diseño"]),

    ("Un árbol de habilidades con requisitos y respec",
     ["--texto", "respec"],
     ["Progresión"]),

    ("Comprobar que mi puzzle tiene solución y no una solución tonta",
     ["--texto", "Sokoban"],
     ["Diseño de puzzles"]),

    ("La cámara marea al saltar; quiero el marco de Keren",
     ["--texto", "camera window"],
     ["Cámaras de juego"]),

    ("Simular 10 000 combates para ver si el arma está rota",
     ["--texto", "Monte Carlo"],
     ["Balance por simulación"]),

    ("¿Cómo se traduce el patrón Flyweight a GML?",
     ["--texto", "Dirty Flag"],
     ["Catálogo de patrones"]),

    ("Quiero que la gente pueda hacer mods de mi juego",
     ["--texto", "Catspeak"],
     ["Modding"]),

    ("Crear una extensión nativa en C++ para Windows",
     ["--texto", "Creating_An_Extension"],
     ["extensión nativa"]),

    ("Un juego tipo Vampire Survivors con miles de enemigos",
     ["--texto", "bullet heaven"],
     ["Bullet heaven"]),

    ("Programar sin escribir código, con bloques",
     ["--texto", "Drag and Drop"],
     ["GML Visual"]),

    # ── Los tres fallos que hunden un "hazme un juego" ────────────────────────
    # Un agente falla casi siempre por lo mismo: se lanza a programar sin
    # especificación, entrega el bucle de juego sin envoltorio (menú, pausa,
    # guardado, créditos), se salta la historia si la había, y pone rectángulos
    # de colores donde debería haber sprites. Estas seis tareas comprueban que el
    # camino a la respuesta EXISTE y es encontrable — no que el agente lo tome,
    # pero sin ellas ni siquiera podría.

    ("Me han dicho solo «hazme un juego» y no sé qué preguntar antes de empezar",
     ["--texto", "elicitación"],
     ["protocolo de elicitación del agente"]),

    ("Tengo el bucle de juego; me falta el menú principal y el envoltorio",
     ["--texto", "menú principal"],
     ["Anatomía de un juego completo", "Continuar"]),

    ("El juego lleva una historia: necesito diálogos con ramas y decisiones",
     ["--texto", "diálogo ramificado"],
     ["Diseño narrativo y diálogos", "Chatterbox"]),

    ("Quiero varias partidas guardadas, con su ficha y su miniatura",
     ["--texto", "ranura de guardado"],
     ["scr_save_load.gml"]),

    ("No tengo ni un sprite y no pienso entregar rectángulos de colores",
     ["--texto", "escalera de prioridad"],
     ["Manual del agente de IA", "sin el rectángulo plano"]),

    ("¿Cómo sé que el juego está TERMINADO y no solo que funciona?",
     ["--texto", "lista MAESTRA"],
     ["Anatomía de un juego completo"]),
]


def main():
    fallos = 0
    sin_runtime = 0
    for desc, args, esperados in CASOS:
        # Una tarea que consulta un SÍMBOLO (sin modo, o con --todo) no puede
        # resolverse sin el índice: no es un fallo de la biblioteca, es una fuente
        # opcional que no está instalada.
        if not SIMBOLOS_INSTALADOS and (not args[0].startswith("--") or args[0] == "--todo"):
            sin_runtime += 1
            print(f"· {desc}  (necesita el índice de símbolos: instala GameMaker)")
            continue
        out = salida(*args)
        faltan = []
        for e in esperados:
            if e in out:
                continue
            if not MANUAL_INSTALADO and e in ETIQUETAS_MANUAL:
                continue
            if not CODIGO_INSTALADO and e in ETIQUETAS_CODIGO:
                continue
            faltan.append(e)
        if faltan:
            fallos += 1
            print(f"✗ {desc}")
            print(f"    buscar.py {' '.join(args)}")
            for f in faltan:
                print(f"    no apareció: «{f}»")
        else:
            print(f"✓ {desc}")

    print()
    if sin_runtime:
        print(f"· {sin_runtime} tarea(s) omitidas: necesitan _indice/simbolos.json, que sale")
        print("  del runtime instalado. Instala GameMaker y repite para probarlas.")
    if fallos:
        print(f"\033[1m{fallos} de {len(CASOS)} tareas sin resolver.\033[0m")
        return 1
    if sin_runtime:
        print(f"\033[1mLas {len(CASOS) - sin_runtime} tareas comprobables se resuelven.\033[0m "
              "Las demás esperan al runtime.")
        return 0
    print(f"\033[1mLas {len(CASOS)} tareas se resuelven.\033[0m "
          "Un LLM encuentra lo que necesita con las herramientas del proyecto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
