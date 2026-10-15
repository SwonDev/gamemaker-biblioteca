#!/usr/bin/env python3
"""Contrato del bootstrap con transporte simulado; el recibo remoto usa descarga real."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("bootstrap", RAIZ/"instalar-remoto.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def archivo(entradas, commit="a"*40):
    flujo = io.BytesIO()
    with ZipFile(flujo, "w") as z:
        z.comment = commit.encode("ascii")
        for nombre, datos in entradas:
            z.writestr(nombre, datos)
    return flujo.getvalue()


class Bootstrap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.lib = self.base/"con espacios y ñ/biblioteca"
        self.usuario = self.base/"usuario"
        self.commit = "a"*40
        # El instalador mínimo permite probar la promoción sin tocar rutas reales.
        self.zip = archivo([("repo/instalar.py", "import sys\nraise SystemExit(0)\n"),
                            ("repo/README.md", "Documentación española\n")])
        self.silencio = contextlib.ExitStack()
        self.silencio.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.silencio.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.addCleanup(self.silencio.close)

    def ejecutar(self, *args):
        with patch.object(mod, "descargar", return_value=self.zip):
            return mod.main(["--home", str(self.usuario), "--biblioteca", str(self.lib), *args])

    def test_descarga_promueve_y_conserva_wip_anterior(self):
        self.lib.mkdir(parents=True)
        (self.lib/"mi-nota.md").write_text("Conservar")
        self.assertEqual(self.ejecutar(), 0)
        self.assertTrue((self.lib/"instalar.py").is_file())
        copia = list(self.lib.parent.glob("gamemaker-biblioteca-anterior-*/biblioteca/mi-nota.md"))
        self.assertEqual(len(copia), 1)
        self.assertEqual(copia[0].read_text(encoding="utf-8"), "Conservar")
        self.assertEqual(json.loads((self.lib/".gamemaker-distribucion.json").read_text(encoding="utf-8"))["commit"], self.commit)

    def test_repeticion_identica_no_crea_backup(self):
        self.assertEqual(self.ejecutar(), 0)
        self.assertEqual(self.ejecutar(), 0)
        self.assertEqual(list(self.lib.parent.glob("gamemaker-biblioteca-anterior-*")), [])

    def test_comprobar_no_promueve_ni_registra(self):
        self.assertEqual(self.ejecutar("--comprobar"), 0)
        self.assertFalse(self.lib.exists())
        self.assertFalse(self.usuario.exists())

    def test_revision_invalida_no_descarga(self):
        with patch.object(mod, "descargar") as red, self.assertRaises(SystemExit):
            mod.main(["--revision", "../../fuera", "--home", str(self.usuario)])
        red.assert_not_called()

    def test_sha_no_identificable_no_promueve(self):
        with patch.object(mod, "descargar", return_value=archivo([("repo/instalar.py", "")], commit="no-es-sha")):
            self.assertEqual(mod.main(["--biblioteca", str(self.lib)]), 1)
        self.assertFalse(self.lib.exists())

    def test_sha_solicitado_no_coincide_no_promueve(self):
        self.assertEqual(self.ejecutar("--revision", "b"*40), 1)
        self.assertFalse(self.lib.exists())

    def test_paquete_corrupto_conserva_biblioteca(self):
        self.lib.mkdir(parents=True)
        (self.lib/"nota").write_text("Conservar")
        self.zip = b"no es zip"
        self.assertEqual(self.ejecutar(), 1)
        self.assertEqual((self.lib/"nota").read_text(encoding="utf-8"), "Conservar")

    def test_validacion_fallida_no_reemplaza(self):
        self.lib.mkdir(parents=True)
        (self.lib/"nota").write_text("Conservar")
        self.zip = archivo([("repo/instalar.py", "raise SystemExit(7)\n")])
        self.assertEqual(self.ejecutar(), 1)
        self.assertEqual((self.lib/"nota").read_text(encoding="utf-8"), "Conservar")

    def test_fallo_del_plan_restaura_biblioteca_antes_de_instalar(self):
        self.lib.mkdir(parents=True)
        (self.lib/"nota").write_text("Conservar")
        self.zip = archivo([("repo/instalar.py", "import sys\nraise SystemExit(7 if '--comprobar' in sys.argv else 0)\n")])
        self.assertEqual(self.ejecutar(), 1)
        self.assertEqual((self.lib/"nota").read_text(encoding="utf-8"), "Conservar")

    def test_actualizacion_real_con_enlace_a_biblioteca_estable(self):
        entradas = [("repo/instalar.py", (RAIZ/"instalar.py").read_bytes()),
                    ("repo/_indice/harnesses.py", (RAIZ/"_indice/harnesses.py").read_bytes())]
        paquete = RAIZ/"_indice/skills/gamemaker-biblioteca"
        entradas += [("repo/_indice/skills/gamemaker-biblioteca/"+p.relative_to(paquete).as_posix(), p.read_bytes())
                     for p in paquete.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        self.zip = archivo(entradas)
        # Windows puede no permitir symlinks; el resto del recorrido es nativo en CI.
        try:
            prueba = self.base/"probe-enlace"
            prueba.symlink_to(self.base, target_is_directory=True)
            prueba.unlink()
        except OSError:
            self.skipTest("El sistema no concede creación de enlaces simbólicos")
        self.assertEqual(self.ejecutar("--harness", "codex", "--enlace"), 0)
        enlace = self.usuario/".agents/skills/gamemaker-biblioteca"
        self.assertTrue(enlace.is_symlink())
        self.commit = "b"*40
        self.zip = archivo(entradas+[("repo/README.md", "Nueva revisión\n")], commit=self.commit)
        self.assertEqual(self.ejecutar("--harness", "codex", "--enlace"), 0)
        self.assertTrue(enlace.is_symlink())
        self.assertEqual(enlace.resolve(), (self.lib/"_indice/skills/gamemaker-biblioteca").resolve())
        self.assertEqual((self.lib/"README.md").read_text(encoding="utf-8"), "Nueva revisión\n")

    def test_extraccion_rechaza_escapes_y_nombres_incompatibles(self):
        for nombre in ["repo/../../fuera", "/fuera", "repo/C:/fuera", "repo/a\\b", "repo/CON.txt", "repo/a."]:
            with self.subTest(nombre=nombre), self.assertRaises(ValueError):
                mod.extraer(archivo([(nombre, "contenido")]), self.base/"salida")

    def test_extraccion_rechaza_enlaces_y_doble_raiz(self):
        enlace = ZipInfo("repo/enlace")
        enlace.create_system = 3
        enlace.external_attr = 0o120777 << 16
        for paquete in [archivo([(enlace, "../../fuera")]), archivo([("a/x", "1"), ("b/x", "2")])]:
            with self.assertRaises(ValueError):
                mod.extraer(paquete, self.base/"salida")


if __name__ == "__main__":
    unittest.main(verbosity=2)
