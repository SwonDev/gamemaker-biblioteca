#!/usr/bin/env python3
"""Regresiones de prosa visible y atributos técnicos HTML."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

IND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IND))
spec = importlib.util.spec_from_file_location("actualizador", IND/"actualizar.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Ortografia(unittest.TestCase):
    def evaluar(self, texto):
        with tempfile.TemporaryDirectory() as directorio:
            (Path(directorio)/"README.md").write_text(texto, encoding="utf-8")
            with patch.object(mod, "RAIZ", directorio):
                return mod.revisar_ortografia()

    def test_ruta_tecnica_html_no_es_prosa(self):
        self.assertEqual(self.evaluar('<img src="iconos/metodo.svg" alt="Método">'), [])

    def test_prosa_visible_sigue_revisada(self):
        self.assertEqual(self.evaluar('<strong>metodo</strong>'), [("README.md", ["metodo"])])

    def test_alt_es_texto_visible_para_lectores(self):
        self.assertEqual(self.evaluar('<img src="iconos/metodo.svg" alt="metodo">'), [("README.md", ["metodo"])])


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main()
