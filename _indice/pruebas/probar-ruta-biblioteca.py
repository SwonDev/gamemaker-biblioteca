#!/usr/bin/env python3
"""Ejecuta el sondeo distribuido: ruta explícita, copia y alias a otra biblioteca."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[2]
TEXTO = (RAIZ/"_indice/skills/gamemaker-biblioteca/references/entorno-y-fuentes.md").read_text(encoding="utf-8")


class RutaBiblioteca(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.a, self.b = self.base/"biblioteca A", self.base/"biblioteca B ñ"
        for root in [self.a, self.b]:
            (root/"_indice").mkdir(parents=True)
            (root/"_indice/buscar.py").touch()
        self.real = self.base/"claude/skills/gamemaker-biblioteca"
        self.real.mkdir(parents=True)
        (self.real.parent/".gamemaker-biblioteca-ruta").write_text(str(self.a), encoding="utf-8")
        self.logica = self.base/"qwen/skills/gamemaker-biblioteca"
        self.logica.parent.mkdir(parents=True)
        (self.logica.parent/".gamemaker-biblioteca-ruta").write_text(str(self.b), encoding="utf-8")

    def sondear(self, skill, explicita=""):
        entorno = dict(os.environ, GM_PRUEBA_SKILL=str(skill), GM_BIBLIOTECA=explicita)
        if sys.platform == "win32":
            shell = shutil.which("pwsh") or shutil.which("powershell")
            self.assertTrue(shell, "La prueba Windows requiere PowerShell nativo")
            cuerpo = re.search(r"```powershell\n(.*?)```", TEXTO, re.S).group(1)
            script = '[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); $SkillDir=$env:GM_PRUEBA_SKILL\n'+cuerpo+'\nWrite-Output "BIB_PROBE=$BIB"'
            args = [shell, "-NoProfile", "-NonInteractive", "-Command", script]
        else:
            cuerpo = re.search(r"```sh\n(.*?)```", TEXTO, re.S).group(1)
            args = ["bash", "-c", 'SKILL_DIR="$GM_PRUEBA_SKILL"\n'+cuerpo+'\nprintf "BIB_PROBE=%s\\n" "$BIB"']
        r = subprocess.run(args, env=entorno, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        return next(l.removeprefix("BIB_PROBE=") for l in r.stdout.splitlines() if l.startswith("BIB_PROBE="))

    def test_copia_consulta_su_ruta_adyacente(self):
        self.assertEqual(self.sondear(self.real), str(self.a))

    def test_override_explicito_prevalece(self):
        self.assertEqual(self.sondear(self.real, str(self.b)), str(self.b))

    def test_alias_conserva_ruta_logica_antes_de_resolver_enlace(self):
        try:
            self.logica.symlink_to(self.real, target_is_directory=True)
        except OSError:
            self.skipTest("El sistema no permite crear symlinks")
        self.assertEqual(self.sondear(self.logica), str(self.b))


if __name__ == "__main__":
    unittest.main(verbosity=2)
