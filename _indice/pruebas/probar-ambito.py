#!/usr/bin/env python3
"""Regresiones de búsqueda y validación con un repositorio privado anidado."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

INDICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(INDICE))

def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre.replace("-", "_"), INDICE/(nombre+".py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m

class AmbitoReal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.r = Path(self.tmp.name)
        self.c = self.r/"13 - Diseño"
        self.c.mkdir()
        (self.c/"normal.md").write_text("# Público\n```gml\nvar _dato = 1;\n```\n", encoding="utf-8")
        self.privado = self.c/"repositorio"
        (self.privado/".git").mkdir(parents=True)
        (self.privado/"camara.md").write_text("# Privado\nMARCADOR_PRIVADO\n```gml\nerror_privado();\n```\n", encoding="utf-8")
        self.fuera = tempfile.TemporaryDirectory()
        self.addCleanup(self.fuera.cleanup)
        self.externo = Path(self.fuera.name)/"externo.md"
        self.externo.write_text("MARCADOR_PRIVADO", encoding="utf-8")
        (self.c/"enlace.md").symlink_to(self.externo)
        (self.c/"alias.md").symlink_to(self.privado/"camara.md")
        (self.r/"README.md").symlink_to(self.privado/"camara.md")

    def test_busqueda_no_lee_repositorio_anidado(self):
        m = cargar("buscar")
        m.RAIZ = m._RAIZ = str(self.r)
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            rc = m.grep([self.c.name], "MARCADOR_PRIVADO", [".md"])
        self.assertEqual(rc, 1)
        self.assertNotIn("camara.md:", salida.getvalue())
        self.assertEqual(m._buscar_en([self.c.name], "MARCADOR_PRIVADO", [".md"]), (0, []))

    def test_busqueda_conserva_documento_publico(self):
        m = cargar("buscar")
        m.RAIZ = m._RAIZ = str(self.r)
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(m.grep([self.c.name], "Público", [".md"]), 0)
        self.assertIn("normal.md:1:", salida.getvalue())

    def test_corpus_registrado_conserva_clone_legitimo(self):
        corpus = self.r/"11 - Código descargado"
        legitimo = corpus/"librerias/ejemplo"
        (legitimo/".git").mkdir(parents=True)
        (legitimo/"real.gml").write_text("ejemplo_real();", encoding="utf-8")
        (corpus/"_RUTAS.json").write_text(json.dumps({"Ejemplo":"librerias/ejemplo"}), encoding="utf-8")
        privado = corpus/"ajeno"
        (privado/".git").mkdir(parents=True)
        (privado/"secreto.gml").write_text("ejemplo_privado();", encoding="utf-8")
        m = cargar("buscar")
        m.RAIZ = m._RAIZ = str(self.r)
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(m.grep([corpus.name], "ejemplo_", [".gml"]), 0)
        self.assertIn("real.gml", salida.getvalue())
        self.assertNotIn("secreto.gml", salida.getvalue())

    def test_regex_invalida_no_declara_ausencia(self):
        m = cargar("buscar")
        m.RAIZ = str(self.r)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.grep([self.c.name], "[", [".md"]), 2)
            for buscar in (m._buscar_en, m._buscar_en3):
                m._RAIZ = str(self.r)
                with self.assertRaises(SystemExit) as error:
                    buscar([self.c.name], "[", [".md"])
                self.assertEqual(error.exception.code, 2)

    def test_alias_de_raiz_no_lee_proyecto_privado(self):
        from ambito import archivos_del_ambito, rutas_no_publicables
        self.assertEqual(rutas_no_publicables(self.r,["README.md"]),["README.md"])
        self.assertEqual(list(archivos_del_ambito(self.r,["README.md"],[".md"])),[])

    def test_compilacion_no_extrae_codigo_privado(self):
        m = cargar("validar-compilacion-docs")
        m.RAIZ, m.CARPETAS = str(self.r), [self.c.name]
        bloques = m.extraer_bloques()
        self.assertEqual(len(bloques), 1)
        self.assertIn("normal.md", bloques[0].ruta)

    def test_nombres_no_corrige_archivos_privados(self):
        m = cargar("actualizar")
        m.RAIZ = str(self.r)
        self.assertEqual(m.revisar_nombres(), [])

    def test_indice_no_incorpora_documentos_privados(self):
        m = cargar("construir-indices")
        m.RAIZ = str(self.r)
        docs = m.documentos_es()
        self.assertTrue(any("normal.md" in d["ruta"] for d in docs))
        self.assertFalse(any("repositorio" in d["ruta"] for d in docs))
        self.assertFalse(any("enlace.md" in d["ruta"] for d in docs))
        self.assertFalse(any("alias.md" in d["ruta"] for d in docs))

if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main()
