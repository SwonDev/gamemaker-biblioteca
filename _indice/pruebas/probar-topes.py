#!/usr/bin/env python3
"""Comprueba los topes del runner con procesos inertes, sin GameMaker."""
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

spec = importlib.util.spec_from_file_location(
    "runner_contratos", Path(__file__).with_name("probar-contratos-r47.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@unittest.skipUnless(os.name == "posix", "El runner y sus grupos requieren POSIX")
class Topes(unittest.TestCase):
    def test_salida_correcta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = runner.ejecutar([sys.executable, "-c", "print('resultado')"],
                                    tmp, Path(tmp)/"salida.log", os.environ.copy(), 5)
            self.assertEqual(salida.strip(), "resultado")

    def test_salida_erronea_no_es_verde(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "Código 7"):
                runner.ejecutar([sys.executable, "-c", "raise SystemExit(7)"],
                               tmp, Path(tmp)/"salida.log", os.environ.copy(), 5)

    def test_timeout_termina_hijo_que_ignora_sigterm(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            hijo = (
                "import os,signal,time,pathlib; "
                "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                "pathlib.Path('hijo.pid').write_text(str(os.getpid())); time.sleep(30)"
            )
            padre = (
                "import os,subprocess,sys,time,pathlib; "
                "pathlib.Path('grupo.pid').write_text(str(os.getpid())); "
                "subprocess.Popen([sys.executable,'-c',sys.argv[1]]); time.sleep(30)"
            )
            try:
                with self.assertRaisesRegex(RuntimeError, "Tope"):
                    runner.ejecutar([sys.executable, "-c", padre, hijo], tmp,
                                   carpeta/"salida.log", os.environ.copy(), 1)
                self.assertTrue((carpeta/"hijo.pid").is_file(), "El hijo no llegó a estar listo")
                pid = int((carpeta/"hijo.pid").read_text())
                for _ in range(40):
                    estado = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)],
                                            capture_output=True, text=True).stdout.strip()
                    if not estado or estado.startswith("Z"):
                        break
                    time.sleep(0.05)
                self.assertTrue(not estado or estado.startswith("Z"), "El hijo sigue ejecutándose")
            finally:
                if (carpeta/"grupo.pid").exists():
                    try:
                        os.killpg(int((carpeta/"grupo.pid").read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main()
