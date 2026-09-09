#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cerrojo de carpeta de trabajo para las herramientas que compilan de verdad.

**Por qué existe.** Cuatro herramientas de `_indice/` construyen un proyecto de
GameMaker desechable en una ruta FIJA de `$HOME` (`gm_prueba_docs`,
`gm_prueba_scripts`, `gm_prueba_ejecucion`, `gm_prueba_trampas`). La ruta es fija
a propósito: `--conservar` la inspecciona después, y una semilla cacheada evita
volver a crear el andamiaje en cada pasada.

El problema aparece cuando **dos ejecuciones se solapan** — dos terminales, o
`actualizar.py` mientras alguien lanza el validador a mano. Se pisan los archivos
a media compilación, y lo que sale no es un error claro:

    ✗ Se encontraron errores de compilación:
    (…y ni un solo error listado)

Es decir, un **falso rojo**: acusa a la documentación de tener GML roto cuando lo
único roto era la carrera entre dos procesos. Perseguir ese fantasma cuesta una
tarde. Y `actualizar.py`, al recibir ese exit 1, lo traducía además a un tercer
mensaje distinto («no se pudo comprobar la compilación»), con lo que ni siquiera
quedaba el rastro del síntoma real.

**Cómo lo resuelve.** `os.mkdir` es atómico en POSIX y en Windows: o lo creas tú,
o ya existía. Eso basta para un cerrojo entre procesos sin dependencias. Dentro se
deja el PID y la hora, para poder distinguir un cerrojo VIVO de uno **huérfano**
—el que deja un proceso que murió a lo bruto (Ctrl-C, kill, corte de luz)—. Un
cerrojo huérfano que no se pueda recuperar solo sería peor que el problema
original: convertiría un fallo transitorio en uno permanente que exige borrar una
carpeta a mano.
"""

import errno
import json
import os
import time

__all__ = ["Cerrojo", "CerrojoOcupado"]


class CerrojoOcupado(Exception):
    """Otra ejecución viva tiene la carpeta de trabajo."""

    def __init__(self, ruta, pid, desde):
        self.ruta, self.pid, self.desde = ruta, pid, desde
        super().__init__(f"«{ruta}» está en uso por el proceso {pid} desde {desde}")


def _vivo(pid):
    """¿Existe ese proceso? `signal 0` no envía nada: solo pregunta."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True          # existe, pero es de otro usuario
    except OSError:
        return True          # ante la duda, se respeta el cerrojo
    return True


class Cerrojo:
    """Cerrojo entre procesos sobre una carpeta de trabajo.

    Se usa como gestor de contexto:

        with Cerrojo(PROY):
            ...construir y compilar...

    Si otra ejecución viva lo tiene, lanza `CerrojoOcupado`, que quien llama debe
    convertir en un exit **2** («no se pudo comprobar»), nunca en un exit 1
    («hay errores»): no se ha mirado nada, así que no se puede acusar a nadie.
    """

    def __init__(self, ruta_trabajo, espera=0.0):
        self.ruta = os.path.abspath(ruta_trabajo) + ".lock"
        self.espera = espera
        self.mio = False

    def _datos(self):
        try:
            with open(os.path.join(self.ruta, "dueño.json"), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def _intentar(self):
        try:
            os.mkdir(self.ruta)
        except FileExistsError:
            return False
        except OSError as e:                      # p. ej. el padre no existe
            if e.errno == errno.ENOENT:
                os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
                return self._intentar()
            raise
        with open(os.path.join(self.ruta, "dueño.json"), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(),
                       "desde": time.strftime("%Y-%m-%d %H:%M:%S")}, f)
        self.mio = True
        return True

    def adquirir(self):
        limite = time.time() + self.espera
        while True:
            if self._intentar():
                return self
            d = self._datos()
            pid = d.get("pid")
            if not _vivo(pid):
                # Huérfano: su dueño ya no existe. Se recoge y se reintenta UNA vez;
                # si en ese hueco lo coge otro, se trata como ocupado normal.
                self.liberar(forzar=True)
                if self._intentar():
                    return self
                d = self._datos()
            if time.time() >= limite:
                raise CerrojoOcupado(os.path.splitext(self.ruta)[0],
                                     d.get("pid", "?"), d.get("desde", "?"))
            time.sleep(0.2)

    def liberar(self, forzar=False):
        if not (self.mio or forzar):
            return
        try:
            os.remove(os.path.join(self.ruta, "dueño.json"))
        except OSError:
            pass
        try:
            os.rmdir(self.ruta)
        except OSError:
            pass
        self.mio = False

    def __enter__(self):
        return self.adquirir()

    def __exit__(self, *_):
        self.liberar()
        return False


def autoprueba():
    import subprocess
    import sys
    import tempfile

    fallos = []

    def revisar(nombre, ok, detalle=""):
        if ok:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    with tempfile.TemporaryDirectory() as tmp:
        trabajo = os.path.join(tmp, "proy")

        # 1 · Se coge y se suelta.
        c = Cerrojo(trabajo)
        c.adquirir()
        revisar("el cerrojo se adquiere", os.path.isdir(trabajo + ".lock"))
        c.liberar()
        revisar("y se libera", not os.path.exists(trabajo + ".lock"))

        # 2 · El segundo NO entra mientras el primero lo tiene.
        with Cerrojo(trabajo):
            try:
                Cerrojo(trabajo).adquirir()
                revisar("un segundo proceso NO entra", False, "entró")
            except CerrojoOcupado as e:
                revisar("un segundo proceso NO entra", e.pid == os.getpid(),
                        "pid %s" % e.pid)
        revisar("y al salir del `with` queda libre", not os.path.exists(trabajo + ".lock"))

        # 3 · Un cerrojo HUÉRFANO (dueño muerto) se recupera solo. Este es el caso
        #     que decide si el cerrojo ayuda o estorba: sin esto, un Ctrl-C dejaría
        #     la herramienta inutilizable hasta borrar una carpeta a mano.
        muerto = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"],
                                capture_output=True, text=True)
        pid_muerto = int(muerto.stdout.strip())
        os.makedirs(trabajo + ".lock")
        with open(os.path.join(trabajo + ".lock", "dueño.json"), "w", encoding="utf-8") as f:
            json.dump({"pid": pid_muerto, "desde": "hace mucho"}, f)
        try:
            c2 = Cerrojo(trabajo)
            c2.adquirir()
            revisar("un cerrojo huérfano se recupera solo", True)
            c2.liberar()
        except CerrojoOcupado:
            revisar("un cerrojo huérfano se recupera solo", False, "sigue bloqueado")

        # 4 · Un cerrojo corrupto (sin dueño legible) tampoco atasca para siempre.
        os.makedirs(trabajo + ".lock")
        try:
            c3 = Cerrojo(trabajo)
            c3.adquirir()
            revisar("un cerrojo sin dueño legible se recupera", True)
            c3.liberar()
        except CerrojoOcupado:
            revisar("un cerrojo sin dueño legible se recupera", False, "sigue bloqueado")

        # 5 · `espera` da margen en vez de rendirse al instante.
        with Cerrojo(trabajo):
            t0 = time.time()
            try:
                Cerrojo(trabajo, espera=0.5).adquirir()
                revisar("con `espera` reintenta antes de rendirse", False, "entró")
            except CerrojoOcupado:
                revisar("con `espera` reintenta antes de rendirse",
                        time.time() - t0 >= 0.45, "%.2fs" % (time.time() - t0))

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 7 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(autoprueba() if "--autoprueba" in sys.argv else 0)
