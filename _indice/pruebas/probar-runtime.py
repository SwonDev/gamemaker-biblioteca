#!/usr/bin/env python3
"""Regresiones de selección de runtime, aisladas de instalaciones y proyectos reales."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest import mock

INDICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(INDICE))


def cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre.replace("-", "_"), INDICE / (nombre + ".py"))
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo
    spec.loader.exec_module(modulo)
    return modulo


class SeleccionRuntime(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.cache = self.raiz / "runtimes-gms2"
        self.cache.mkdir()
        self.entorno = mock.patch.dict(os.environ)
        self.entorno.start()
        self.addCleanup(self.entorno.stop)
        os.environ.pop("GM_BIBLIOTECA_RUNTIME", None)

    def runtime(self, version):
        ruta = self.cache / ("runtime-" + version)
        ruta.mkdir()
        (ruta / "GmlSpec.xml").write_text("<GmlSpec/>\n", encoding="utf-8")
        return ruta

    def test_version_se_ordena_por_componentes_numericos(self):
        for version in ("2026.2", "2026.9", "2026.10"):
            self.runtime(version)
        for nombre in ("buscar", "construir-indices", "validar-proyecto"):
            with self.subTest(herramienta=nombre):
                modulo = cargar(nombre)
                modulo.RUNTIMES = str(self.cache)
                resultado = modulo.runtime_instalado()
                version = resultado[1] if isinstance(resultado, tuple) else resultado
                self.assertEqual(version, "2026.10")

    def test_eleccion_explicita_prevalece_sobre_cache_mas_nueva(self):
        self.runtime("2026.9")
        self.runtime("2026.10")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = "2026.9"
        for nombre in ("buscar", "construir-indices", "validar-proyecto"):
            with self.subTest(herramienta=nombre):
                modulo = cargar(nombre)
                modulo.RUNTIMES = str(self.cache)
                resultado = modulo.runtime_instalado()
                version = resultado[1] if isinstance(resultado, tuple) else resultado
                self.assertEqual(version, "2026.9")

    def biblioteca_aislada(self):
        raiz = self.raiz / "biblioteca"
        indice = raiz / "_indice"
        indice.mkdir(parents=True, exist_ok=True)
        (indice / "MAPA.json").write_text('{"carpetas": []}', encoding="utf-8")
        modulo = cargar("construir-indices")
        modulo.RAIZ, modulo.IND = str(raiz), str(indice)
        modulo.MANUAL = str(raiz / "09 - Manual oficial")
        modulo.CODIGO = str(raiz / "11 - Código descargado")
        modulo.RUNTIMES = str(self.cache)
        return modulo, indice

    def test_spec_y_fnames_proceden_del_runtime_seleccionado(self):
        for version in ("2026.10", "2026.11"):
            ruta = self.runtime(version)
            sufijo = version.replace(".", "_")
            (ruta / "GmlSpec.xml").write_text(
                f'<GmlSpec><Function Name="spec_{sufijo}"/></GmlSpec>', encoding="utf-8")
            (ruta / "fnames").write_text(f"fnames_{sufijo}#\n", encoding="utf-8")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = "2026.10"
        modulo, indice = self.biblioteca_aislada()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(modulo.main(), 0)
        datos = json.loads((indice / "simbolos.json").read_text())
        self.assertEqual(datos["meta"]["runtime"], "2026.10")
        self.assertEqual(set(datos["simbolos"]), {"spec_2026_10", "fnames_2026_10"})

    def test_eleccion_invalida_no_cae_a_otro_runtime_ni_escribe(self):
        self.runtime("2026.10")
        incompleto = self.raiz / "runtime-IDE-sin-spec"
        incompleto.mkdir()
        for eleccion in ("2099.0", str(self.raiz / "inexistente"), "", str(incompleto),
                         "~__gm_biblioteca_usuario_inexistente__/runtime"):
            with self.subTest(eleccion=eleccion):
                modulo, indice = self.biblioteca_aislada()
                (indice / "documentos.json").write_text('{"anterior": true}', encoding="utf-8")
                (indice / "simbolos.json").write_text(
                    '{"meta": {"runtime": "anterior"}, "simbolos": {"previo": {}}}', encoding="utf-8")
                antes = {p.name: p.read_bytes() for p in indice.iterdir()}
                os.environ["GM_BIBLIOTECA_RUNTIME"] = eleccion
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errores:
                    with self.assertRaises(SystemExit) as salida:
                        modulo.main()
                self.assertEqual(salida.exception.code, 2)
                self.assertIn("GM_BIBLIOTECA_RUNTIME", errores.getvalue())
                self.assertEqual({p.name: p.read_bytes() for p in indice.iterdir()}, antes)

    def test_spec_ausente_vacio_o_malformado_no_es_api_vacia(self):
        modulo = cargar("construir-indices")
        for contenido in (None, "<GmlSpec/>", "<GmlSpec><Function"):
            with self.subTest(contenido=contenido):
                ruta = self.raiz / "spec"
                ruta.mkdir(exist_ok=True)
                spec = ruta / "GmlSpec.xml"
                if contenido is not None:
                    spec.write_text(contenido, encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()) as errores:
                    with self.assertRaises(SystemExit) as salida:
                        modulo.extraer_gmlspec(str(ruta))
                self.assertEqual(salida.exception.code, 2)
                self.assertIn("GmlSpec.xml", errores.getvalue())

    def test_modulo_xml_roto_conserva_todos_los_indices_previos(self):
        runtime = self.runtime("2026.10")
        (runtime / "GmlSpec.xml").write_text(
            '<GmlSpec><Function Name="valida"/></GmlSpec>', encoding="utf-8")
        (runtime / "fnames").write_text("EXTRA#\n", encoding="utf-8")
        roto = runtime / "modulo"
        roto.mkdir()
        (roto / "GmlSpec.xml").write_text("<GmlSpec><Function", encoding="utf-8")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = str(runtime)
        modulo, indice = self.biblioteca_aislada()
        (indice / "documentos.json").write_text('{"anterior": true}', encoding="utf-8")
        (indice / "simbolos.json").write_text(
            '{"meta": {"runtime": "anterior"}, "simbolos": {"previo": {}}}', encoding="utf-8")
        antes = {p.name: p.read_bytes() for p in indice.iterdir()}
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errores:
            with self.assertRaises(SystemExit) as salida:
                modulo.main()
        self.assertEqual(salida.exception.code, 2)
        self.assertIn("GmlSpec.xml", errores.getvalue())
        self.assertEqual({p.name: p.read_bytes() for p in indice.iterdir()}, antes)

    def test_aviso_no_confunde_ultima_cache_con_runtime_del_proyecto(self):
        self.runtime("2026.10")
        modulo = cargar("buscar")
        modulo.RUNTIMES = str(self.cache)
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            modulo.avisar_si_caducado({"runtime": "2026.9"})
        self.assertIn("último disponible en caché", salida.getvalue())
        self.assertIn("no acredita el runtime activo del proyecto", salida.getvalue())
        self.assertNotIn("instalado es", salida.getvalue())
        os.environ["GM_BIBLIOTECA_RUNTIME"] = "2026.10"
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            modulo.avisar_si_caducado({"runtime": "2026.9"})
        self.assertIn("seleccionado mediante GM_BIBLIOTECA_RUNTIME", salida.getvalue())

    def test_directorio_ide_fuera_de_cache_es_fuente_de_ambas_listas(self):
        self.runtime("2026.100")
        ide = self.raiz / "IDE" / "runtime-2026.0.0.23"
        (ide / "Base").mkdir(parents=True)
        (ide / "Base" / "GmlSpec.xml").write_text(
            '<GmlSpec><Function Name="del_ide"/></GmlSpec>', encoding="utf-8")
        (ide / "fnames").write_text("EXTRA_IDE#\n", encoding="utf-8")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = str(ide)
        modulo, indice = self.biblioteca_aislada()
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            self.assertEqual(modulo.main(), 0)
        datos = json.loads((indice / "simbolos.json").read_text())
        self.assertEqual(set(datos["simbolos"]), {"del_ide", "EXTRA_IDE"})
        self.assertEqual(datos["meta"]["runtime"], "2026.0.0.23")
        self.assertIn("seleccionado mediante GM_BIBLIOTECA_RUNTIME", salida.getvalue())

    def test_directorio_sin_version_no_inventa_una_version(self):
        ide = self.raiz / "IDE propio"
        ide.mkdir()
        (ide / "GmlSpec.xml").write_text("<GmlSpec/>", encoding="utf-8")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = str(ide)
        modulo = cargar("runtime_biblioteca")
        elegido = modulo.seleccionar_runtime(str(self.cache))
        self.assertEqual(elegido.directorio, str(ide.resolve()))
        self.assertEqual(elegido.version, "directorio:" + str(ide.resolve()))

    def test_archivo_y_directorio_incompleto_no_cuentan_como_runtime_disponible(self):
        self.runtime("2026.10")
        (self.cache / "runtime-2026.999").write_text("no es un directorio", encoding="utf-8")
        (self.cache / "runtime-2026.100").mkdir()
        (self.cache / "runtime-invalido").mkdir()
        modulo = cargar("runtime_biblioteca")
        self.assertEqual(modulo.seleccionar_runtime(str(self.cache)).version, "2026.10")

    def test_fnames_ausente_conserva_indices_y_no_toma_otra_version(self):
        elegida = self.runtime("2026.10")
        (elegida / "GmlSpec.xml").write_text(
            '<GmlSpec><Function Name="valida"/></GmlSpec>', encoding="utf-8")
        otra = self.runtime("2026.11")
        (otra / "fnames").write_text("NO_REUTILIZAR#\n", encoding="utf-8")
        os.environ["GM_BIBLIOTECA_RUNTIME"] = "2026.10"
        modulo, indice = self.biblioteca_aislada()
        antes = {p.name: p.read_bytes() for p in indice.iterdir()}
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errores:
            with self.assertRaises(SystemExit) as salida:
                modulo.main()
        self.assertEqual(salida.exception.code, 2)
        self.assertIn("falta fnames", errores.getvalue())
        self.assertEqual({p.name: p.read_bytes() for p in indice.iterdir()}, antes)

    def test_ausencia_cache_es_indeterminada_y_no_inventa_runtime(self):
        modulo = cargar("runtime_biblioteca")
        self.assertIsNone(modulo.seleccionar_runtime(str(self.cache)))
        self.assertIsNone(modulo.seleccionar_runtime(str(self.raiz / "sin-cache")))
        aviso = modulo.aviso_indice({"runtime": "2026.9"}, None)
        self.assertIn("No se ha verificado el runtime del proyecto", aviso)

    def test_cli_invalido_sale_con_dos_y_diagnostico_en_las_tres_herramientas(self):
        raiz = self.raiz / "cli"
        indice = raiz / "_indice"
        indice.mkdir(parents=True)
        for nombre in ("runtime_biblioteca", "ambito", "argumentos", "buscar",
                       "construir-indices", "validar-proyecto", "validar-codigo-gml"):
            (indice / (nombre + ".py")).write_bytes((INDICE / (nombre + ".py")).read_bytes())
        entorno = dict(os.environ, GM_BIBLIOTECA_RUNTIME=str(self.raiz / "inexistente"),
                       PYTHONDONTWRITEBYTECODE="1")
        for nombre, argumentos in (("buscar", ["simbolo"]), ("construir-indices", []),
                                   ("validar-proyecto", [str(raiz)])):
            with self.subTest(herramienta=nombre):
                resultado = subprocess.run([sys.executable, str(indice / (nombre + ".py")), *argumentos],
                                           capture_output=True, text=True, env=entorno, timeout=10)
                self.assertEqual(resultado.returncode, 2, resultado.stderr)
                self.assertIn("GM_BIBLIOTECA_RUNTIME", resultado.stderr)
                self.assertNotIn("Traceback", resultado.stderr)
                self.assertFalse((indice / "documentos.json").exists())
                self.assertFalse((indice / "simbolos.json").exists())


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main()
