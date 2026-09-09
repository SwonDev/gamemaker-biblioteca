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


def _vivo(pid, sistema=None):
    """¿Existe ese proceso? Sin matarlo, que es más difícil de lo que parece.

    🔴 **En POSIX, `os.kill(pid, 0)` pregunta; en Windows, MATA.** La documentación de
    Python lo dice sin adornos: en Windows, `os.kill(pid, sig)` con cualquier señal que
    no sea `CTRL_C_EVENT` o `CTRL_BREAK_EVENT` llama a `TerminateProcess` con `sig` como
    código de salida. Es decir, la forma canónica de preguntar «¿sigue vivo?» en Linux y
    Mac **termina el proceso** en Windows.

    Aquí eso sería lo peor posible: esta función decide si un cerrojo está huérfano. En
    Windows habría matado al proceso que legítimamente tenía la carpeta de trabajo —una
    compilación de otra persona— para después quedarse con ella.

    El equivalente en Windows es `OpenProcess` con `PROCESS_QUERY_LIMITED_INFORMATION`,
    que solo consulta. `sistema` existe para poder probar las dos ramas desde cualquier
    máquina; en uso normal se deduce sola.
    """
    if not isinstance(pid, int) or pid <= 0:
        return False
    if sistema is None:
        sistema = os.name
    if sistema == "nt":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_INVALID_PARAMETER = 87
        try:
            k32 = ctypes.windll.kernel32          # noqa: F821 (solo existe en Windows)
        except AttributeError:
            return True                            # no se puede consultar: se respeta
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if h:
            k32.CloseHandle(h)
            return True
        # 87 = «parámetro no válido» es lo que devuelve un PID que ya no existe.
        # Cualquier otro error (5, acceso denegado) significa que existe y no es nuestro.
        return k32.GetLastError() != ERROR_INVALID_PARAMETER
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

        # 5 bis · La rama de Windows no puede llamar a `os.kill`: allí eso MATA.
        #         Se comprueba desde cualquier sistema pidiendo la rama a mano y
        #         vigilando que `os.kill` no se toca. Sin esta prueba, el fallo solo
        #         aparecería en Windows y en forma de proceso muerto ajeno.
        import os as _os
        _kill_real = _os.kill
        _llamadas = []

        def _kill_espia(*a, **k):
            _llamadas.append(a)
            return _kill_real(*a, **k)

        _os.kill = _kill_espia
        try:
            _vivo(999999, sistema="nt")
        except Exception:
            pass
        finally:
            _os.kill = _kill_real
        revisar("la rama de Windows NUNCA llama a os.kill (allí MATA)",
                _llamadas == [], "llamó %d vez(ces)" % len(_llamadas))

        _llamadas.clear()
        _os.kill = _kill_espia
        try:
            _vivo(os.getpid(), sistema="posix")
        finally:
            _os.kill = _kill_real
        revisar("y la de POSIX sí lo usa, con la señal 0",
                len(_llamadas) == 1 and _llamadas[0][1] == 0, str(_llamadas))

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
    print("\n✓ Las 9 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(autoprueba() if "--autoprueba" in sys.argv else 0)
