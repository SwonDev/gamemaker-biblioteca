#!/usr/bin/env python3
"""Contrato del instalador portable en fixtures, sin HOME ni configuraciones reales."""
import hashlib
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[2]
VARIABLES_RAIZ = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "OPENCODE_CONFIG_DIR", "XDG_CONFIG_HOME",
                  "PI_CODING_AGENT_DIR", "PI_CONFIG_DIR", "OMP_PROFILE", "PI_PROFILE",
                  "MINIMAX_DATA_DIR", "MAVIS_DATA_DIR", "DSH_HOME", "HERMES_HOME",
                  "HERMES_DATA_DIR_SUFFIX", "GENTLE_SHELL_HOME", "LOCALAPPDATA")


class Instalador(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="gm-instalacion-")
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name)
        self.bib = self.base / "Biblioteca con ñ y espacios"
        self.bib.mkdir()
        self.home = self.base / "usuario"
        self.dest = self.base / "destino"
        self.paquete = self.bib / "_indice/skills/gamemaker-biblioteca"
        self.paquete.mkdir(parents=True)
        (self.paquete / "references").mkdir()
        (self.paquete / "SKILL.md").write_text(
            '---\nname: gamemaker-biblioteca\ndescription: "GameMaker y GML"\n---\n'
            '<!-- SKILL-VERSION: r1 · 2026-10-15 -->\n# Biblioteca\n', encoding="utf-8")
        (self.paquete / "references/consulta.md").write_text("Consulta verificable.\n", encoding="utf-8")
        self.manifestar()
        for nombre in ("instalar.py", "instalar.sh", "instalar.ps1"):
            fuente = RAIZ / nombre
            if fuente.exists():
                shutil.copy2(fuente, self.bib / nombre)
        shutil.copy2(RAIZ / "_indice/harnesses.py", self.bib / "_indice/harnesses.py")
        self.entorno = {k: v for k, v in os.environ.items() if k not in VARIABLES_RAIZ}
        self.entorno["PYTHONDONTWRITEBYTECODE"] = "1"

    def manifestar(self):
        archivos = {p.relative_to(self.paquete).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.paquete.rglob("*") if p.is_file() and p.name != "manifest.json"}
        (self.paquete / "manifest.json").write_text(json.dumps({"schema": 1,
            "name": "gamemaker-biblioteca", "version": "r1 · 2026-10-15", "files": archivos}), encoding="utf-8")

    def ejecutar(self, *args):
        return subprocess.run([sys.executable, "-I", "-S", str(self.bib / "instalar.py"),
                               "--home", str(self.home), *args], env=self.entorno,
                              capture_output=True, text=True)

    def test_instala_paquete_sin_dependencias_ni_motor(self):
        resultado = self.ejecutar("--destino", str(self.dest))
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        for archivo in self.paquete.rglob("*"):
            if archivo.is_file():
                self.assertEqual(archivo.read_bytes(),
                    (self.dest / "gamemaker-biblioteca" / archivo.relative_to(self.paquete)).read_bytes())
        self.assertFalse(self.home.exists())
        self.assertEqual((self.dest / ".gamemaker-biblioteca-ruta").read_text(), str(self.bib.resolve()))

    def test_defecto_instala_todos_y_registra_sin_duplicar_codex(self):
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        for relativa in (".agents/skills", ".claude/skills", ".config/opencode/skills",
                         ".qwen/skills", ".kimi-code/skills", ".gemini/skills", ".copilot/skills",
                         ".cursor/skills", ".cline/skills", ".pi/agent/skills", ".omp/agent/skills",
                         ".minimax/skills", ".dsh/skills", ".gentle-shell/agent/skills",
                         "AppData/Local/hermes/skills" if sys.platform == "win32" else ".hermes/skills"):
            self.assertTrue((self.home / relativa / "gamemaker-biblioteca/SKILL.md").is_file(), relativa)
        self.assertFalse((self.home / ".codex").exists())
        self.assertEqual((self.home / ".config/gamemaker-biblioteca/ruta").read_text(), str(self.bib.resolve()))

    def test_codex_elegido_es_canonico_y_encuentra_biblioteca(self):
        resultado = self.ejecutar("--harness", "codex")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((self.home / ".agents/skills/gamemaker-biblioteca/SKILL.md").is_file())
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.home / ".claude").exists())
        self.assertTrue((self.home / ".config/gamemaker-biblioteca/ruta").is_file())

    def test_destino_puede_solicitar_registro(self):
        resultado = self.ejecutar("--destino", str(self.dest), "--registrar")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual((self.home / ".config/gamemaker-biblioteca/ruta").read_text(), str(self.bib.resolve()))

    def test_reinstalacion_identica_no_toca_copia_ni_crea_backup(self):
        self.assertEqual(self.ejecutar("--destino", str(self.dest)).returncode, 0)
        archivo = self.dest / "gamemaker-biblioteca/SKILL.md"
        antes = archivo.stat()
        sidecar = self.dest / ".gamemaker-biblioteca-ruta"
        sidecar_antes = sidecar.stat()
        resultado = self.ejecutar("--destino", str(self.dest))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(archivo.stat().st_mtime_ns, antes.st_mtime_ns)
        self.assertEqual(archivo.stat().st_ino, antes.st_ino)
        self.assertEqual(sidecar.stat().st_mtime_ns, sidecar_antes.st_mtime_ns)
        self.assertEqual(sidecar.stat().st_ino, sidecar_antes.st_ino)
        self.assertFalse((self.dest / ".gamemaker-biblioteca-backups").exists())

    def test_reinstalacion_distinta_conserva_trabajo_y_limpia_temporal(self):
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("Trabajo anterior con ñ.", encoding="utf-8")
        resultado = self.ejecutar("--destino", str(self.dest))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        notas = list((self.dest / ".gamemaker-biblioteca-backups").rglob("nota.txt"))
        self.assertEqual(len(notas), 1)
        self.assertEqual(notas[0].read_text(), "Trabajo anterior con ñ.")
        self.assertEqual(list(self.dest.glob(".gm-skill.*")), [])

    def test_paquete_modificado_no_reemplaza_ni_registra(self):
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("Conservar", encoding="utf-8")
        (self.paquete / "references/consulta.md").write_text("Alterado", encoding="utf-8")
        resultado = self.ejecutar("--destino", str(self.dest), "--registrar")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual((viejo / "nota.txt").read_text(), "Conservar")
        self.assertFalse(self.home.exists())
        self.assertFalse((self.dest / ".gamemaker-biblioteca-backups").exists())

    def test_manifiesto_ausente_extra_y_revision_falsa_no_instalan(self):
        manifiesto = self.paquete / "manifest.json"
        original = manifiesto.read_text()
        for caso in ("ausente", "extra", "revision"):
            with self.subTest(caso=caso):
                manifiesto.write_text(original, encoding="utf-8")
                if caso == "ausente":
                    manifiesto.unlink()
                elif caso == "extra":
                    (self.paquete / "extra.md").write_text("No declarado", encoding="utf-8")
                else:
                    (self.paquete / "extra.md").unlink(missing_ok=True)
                    datos = json.loads(original)
                    datos["version"] = "r0"
                    manifiesto.write_text(json.dumps(datos), encoding="utf-8")
                resultado = self.ejecutar("--destino", str(self.dest))
                self.assertNotEqual(resultado.returncode, 0)
                self.assertFalse(self.dest.exists())

    def test_rutas_de_manifiesto_no_escapan(self):
        manifiesto = self.paquete / "manifest.json"
        original = json.loads(manifiesto.read_text())
        for nombre in ("../fuera", "/fuera", "references/../../fuera", "..\\fuera", "C:/fuera"):
            with self.subTest(nombre=nombre):
                datos = dict(original, files=dict(original["files"], **{nombre: "0" * 64}))
                manifiesto.write_text(json.dumps(datos), encoding="utf-8")
                resultado = self.ejecutar("--destino", str(self.dest))
                self.assertNotEqual(resultado.returncode, 0)
                self.assertFalse(self.dest.exists())

    def test_comprobar_no_escribe_ni_deriva_indices(self):
        antes = {p.relative_to(self.bib): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.bib.rglob("*") if p.is_file()}
        resultado = self.ejecutar("--comprobar", "--indices")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        despues = {p.relative_to(self.bib): (p.read_bytes(), p.stat().st_mtime_ns)
                   for p in self.bib.rglob("*") if p.is_file()}
        self.assertEqual(antes, despues)
        self.assertFalse(self.home.exists())

    def test_comprobar_paquete_valida_sin_escrituras_ni_indices(self):
        antes = {p.relative_to(self.bib): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.bib.rglob("*") if p.is_file()}
        resultado = self.ejecutar("--comprobar-paquete", "--indices")
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        despues = {p.relative_to(self.bib): (p.read_bytes(), p.stat().st_mtime_ns)
                   for p in self.bib.rglob("*") if p.is_file()}
        self.assertEqual(antes, despues)
        self.assertFalse(self.home.exists())

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_comprobar_paquete_omite_alias_externo_pero_comprobar_plan_lo_rechaza(self):
        estable = self.base / "biblioteca-estable"
        estable.mkdir()
        (estable / "SKILL.md").write_text("Revisión anterior", encoding="utf-8")
        self.dest.mkdir()
        alias = self.dest / "gamemaker-biblioteca"
        alias.symlink_to(estable, target_is_directory=True)
        resultado = self.ejecutar("--comprobar-paquete", "--enlace", "--destino", str(self.dest))
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        resultado = self.ejecutar("--comprobar", "--enlace", "--destino", str(self.dest))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("fuera del plan", resultado.stderr)
        self.assertTrue(alias.is_symlink())
        self.assertEqual((estable / "SKILL.md").read_text(), "Revisión anterior")
        self.assertFalse(self.home.exists())

    def test_comprobar_paquete_rechaza_manifiesto_y_selectores_invalidos(self):
        for args in (("--harness", "inexistente"), ("--desconocida",),
                     ("--harness", "claude", "--destino", str(self.dest))):
            resultado = self.ejecutar("--comprobar-paquete", *args)
            self.assertEqual(resultado.returncode, 2)
            self.assertFalse(self.home.exists())
        self.entorno["OMP_PROFILE"] = "../fuera"
        resultado = self.ejecutar("--comprobar-paquete", "--harness", "omp")
        self.assertEqual(resultado.returncode, 2)
        self.entorno.pop("OMP_PROFILE")
        (self.paquete / "references/consulta.md").write_text("Contenido alterado", encoding="utf-8")
        resultado = self.ejecutar("--comprobar-paquete")
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("SHA-256", resultado.stderr)
        self.assertFalse(self.home.exists())

    def test_destinos_solapados_no_crean_ninguna_instalacion(self):
        anidado = self.home / ".agents/skills/gamemaker-biblioteca/config-claude"
        self.entorno["CLAUDE_CONFIG_DIR"] = str(anidado)
        resultado = self.ejecutar()
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("se solapan", resultado.stderr)
        self.assertFalse(self.home.exists())

    def test_dos_bibliotecas_conservan_ruta_por_destino_y_backup_global(self):
        biblioteca_b = self.base / "Biblioteca B"
        shutil.copytree(self.bib, biblioteca_b)
        resultado = self.ejecutar("--harness", "claude")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        sidecar_a = self.home / ".claude/skills/.gamemaker-biblioteca-ruta"
        fecha_a = sidecar_a.stat().st_mtime_ns
        comando_b = [sys.executable, "-I", "-S", str(biblioteca_b / "instalar.py"),
                     "--home", str(self.home), "--harness", "codex"]
        resultado = subprocess.run(comando_b, env=self.entorno, capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        sidecar_b = self.home / ".agents/skills/.gamemaker-biblioteca-ruta"
        self.assertEqual(sidecar_a.read_text(), str(self.bib.resolve()))
        self.assertEqual(sidecar_b.read_text(), str(biblioteca_b.resolve()))
        registro = self.home / ".config/gamemaker-biblioteca/ruta"
        self.assertEqual(registro.read_text(), str(biblioteca_b.resolve()))
        backups = list(registro.parent.glob("ruta-anterior.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), str(self.bib.resolve()))
        self.assertIn("ruta global de biblioteca cambia", resultado.stdout)
        fecha_b, fecha_global = sidecar_b.stat().st_mtime_ns, registro.stat().st_mtime_ns
        resultado = subprocess.run(comando_b, env=self.entorno, capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(sidecar_a.stat().st_mtime_ns, fecha_a)
        self.assertEqual(sidecar_b.stat().st_mtime_ns, fecha_b)
        self.assertEqual(registro.stat().st_mtime_ns, fecha_global)
        self.assertEqual(len(list(registro.parent.glob("ruta-anterior.*"))), 1)
        for relativa in (".claude/skills", ".agents/skills"):
            copia = self.home / relativa / "gamemaker-biblioteca"
            archivos = {p.relative_to(copia).as_posix() for p in copia.rglob("*") if p.is_file()}
            self.assertEqual(archivos, {"SKILL.md", "references/consulta.md", "manifest.json"})

    def test_indices_fallidos_no_cambian_instalaciones(self):
        (self.bib / "_indice/construir-indices.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        resultado = self.ejecutar("--indices", "--destino", str(self.dest))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(self.dest.exists())
        self.assertFalse(self.home.exists())

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_alias_preexistentes_conservados_y_copia_compartida_actualizada(self):
        claude = self.home / ".claude/skills/gamemaker-biblioteca"
        claude.mkdir(parents=True)
        (claude / "nota.txt").write_text("Anterior", encoding="utf-8")
        aliases = []
        for relativa in (".config/opencode/skills", ".qwen/skills", ".kimi-code/skills"):
            alias = self.home / relativa / "gamemaker-biblioteca"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(claude, target_is_directory=True)
            aliases.append(alias)
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((claude / "SKILL.md").is_file())
        for alias in aliases:
            self.assertTrue(alias.is_symlink())
            self.assertEqual(alias.readlink(), claude)
            self.assertEqual((alias.parent / ".gamemaker-biblioteca-ruta").read_text(), str(self.bib.resolve()))
        self.assertEqual(len(list(self.home.rglob(".gamemaker-biblioteca-backups/copia.*/gamemaker-biblioteca/nota.txt"))), 1)

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_alias_aislado_fuera_del_plan_no_rompe_enlace_ni_destino(self):
        compartida = self.base / "compartida"
        compartida.mkdir()
        (compartida / "nota.txt").write_text("Conservar", encoding="utf-8")
        self.dest.mkdir()
        alias = self.dest / "gamemaker-biblioteca"
        alias.symlink_to(compartida, target_is_directory=True)
        resultado = self.ejecutar("--destino", str(self.dest))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertTrue(alias.is_symlink())
        self.assertEqual((compartida / "nota.txt").read_text(), "Conservar")

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_enlace_canonico_conservado(self):
        self.assertEqual(self.ejecutar("--enlace", "--destino", str(self.dest)).returncode, 0)
        alias = self.dest / "gamemaker-biblioteca"
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.resolve(), self.paquete.resolve())
        self.assertEqual(self.ejecutar("--destino", str(self.dest)).returncode, 0)
        self.assertTrue(alias.is_symlink())
        self.assertFalse((self.dest / ".gamemaker-biblioteca-backups").exists())

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_alias_identico_no_modifica_referente_aunque_se_pida_enlace(self):
        compartida = self.base / "compartida"
        shutil.copytree(self.paquete, compartida)
        self.dest.mkdir()
        alias = self.dest / "gamemaker-biblioteca"
        alias.symlink_to(compartida, target_is_directory=True)
        resultado = self.ejecutar("--enlace", "--destino", str(self.dest))
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue(alias.is_symlink())
        self.assertFalse(compartida.is_symlink())
        self.assertEqual(alias.readlink(), compartida)

    def test_destino_anidado_rechazado_antes_de_crear(self):
        destino = self.paquete / "subcarpeta"
        resultado = self.ejecutar("--destino", str(destino))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(destino.exists())

    def test_overrides_de_raiz_y_perfil_omp(self):
        for selector, variable, segmento in (("claude", "CLAUDE_CONFIG_DIR", "skills"),
                ("opencode", "OPENCODE_CONFIG_DIR", "skills"), ("dsh", "DSH_HOME", "skills"),
                ("pi", "PI_CODING_AGENT_DIR", "skills")):
            with self.subTest(selector=selector):
                datos = self.home / ("datos-" + selector)
                self.entorno[variable] = str(datos)
                resultado = self.ejecutar("--harness", selector)
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertTrue((datos / segmento / "gamemaker-biblioteca/SKILL.md").is_file())
                self.entorno.pop(variable)
        self.entorno.update(OMP_PROFILE="  pruebas  ", PI_PROFILE="otro")
        resultado = self.ejecutar("--harness", "omp")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((self.home / ".omp/profiles/pruebas/agent/skills/gamemaker-biblioteca/SKILL.md").is_file())

    def test_home_explicito_no_escribe_override_externo(self):
        externa = self.base / "no-autorizada"
        self.entorno["DSH_HOME"] = str(externa)
        resultado = self.ejecutar("--harness", "dsh")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(externa.exists())
        self.assertFalse(self.home.exists())

    @unittest.skipIf(os.name == "nt", "El enlace nativo requiere permiso específico en Windows.")
    def test_home_explicito_no_registra_fuera_por_enlace(self):
        externa = self.base / "configuracion-ajena"
        externa.mkdir()
        self.home.mkdir()
        (self.home / ".config").symlink_to(externa, target_is_directory=True)
        resultado = self.ejecutar("--harness", "codex")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertEqual(list(externa.iterdir()), [])
        self.assertFalse((self.home / ".agents").exists())

    def test_argumentos_y_perfil_invalidos_no_escriben(self):
        for args in (("--desconocida",), ("--harness", "inexistente"),
                     ("--harness", "claude", "--destino", str(self.dest))):
            resultado = self.ejecutar(*args)
            self.assertEqual(resultado.returncode, 2)
            self.assertFalse(self.home.exists())
        for perfil in ("../fuera", "CON", "MAYUSCULAS", "a" * 65):
            self.entorno["OMP_PROFILE"] = perfil
            resultado = self.ejecutar("--harness", "omp")
            self.assertEqual(resultado.returncode, 2)
            self.assertFalse(self.home.exists())

    def test_listar_no_exige_manifiesto_y_no_instala(self):
        (self.paquete / "manifest.json").unlink()
        resultado = self.ejecutar("--listar-harnesses")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("codex\t" + str(self.home / ".agents/skills"), resultado.stdout)
        self.assertFalse(self.home.exists())

    def test_detectar_incluye_app_sin_cli_por_directorio(self):
        self.entorno["PATH"] = str(self.base / "sin-binarios")
        (self.home / ".cursor/skills").mkdir(parents=True)
        resultado = self.ejecutar("--detectar")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((self.home / ".cursor/skills/gamemaker-biblioteca/SKILL.md").is_file())
        self.assertTrue((self.home / ".agents/skills/gamemaker-biblioteca/SKILL.md").is_file())
        self.assertFalse((self.home / ".claude").exists())

    def test_fallo_promocion_restaura_anterior_y_limpia_temporal(self):
        spec = importlib.util.spec_from_file_location("instalador_fixture", self.bib / "instalar.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("Conservar", encoding="utf-8")
        reemplazar = os.replace
        def fallo_unico(origen, destino):
            if Path(origen).parent.name.startswith(".gm-skill."):
                raise OSError("Fallo de promoción inyectado")
            return reemplazar(origen, destino)
        with patch.object(modulo.os, "replace", side_effect=fallo_unico), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            resultado = modulo.main(["--home", str(self.home), "--destino", str(self.dest)])
        self.assertEqual(resultado, 1)
        self.assertEqual((viejo / "nota.txt").read_text(), "Conservar")
        self.assertEqual(list(self.dest.glob(".gm-skill.*")), [])

    def test_doble_fallo_conserva_backup_y_paquete_preparado(self):
        spec = importlib.util.spec_from_file_location("instalador_doble_fallo", self.bib / "instalar.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("Recuperable", encoding="utf-8")
        reemplazar = os.replace
        def fallo_salida(origen, destino):
            if Path(destino).resolve() == viejo.resolve():
                raise OSError("Fallo de disco inyectado")
            return reemplazar(origen, destino)
        errores = io.StringIO()
        with patch.object(modulo.os, "replace", side_effect=fallo_salida), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            resultado = modulo.main(["--home", str(self.home), "--destino", str(self.dest)])
        self.assertEqual(resultado, 1)
        backups = list((self.dest / ".gamemaker-biblioteca-backups").rglob("nota.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "Recuperable")
        preparados = list(self.dest.glob(".gm-skill.*/gamemaker-biblioteca/manifest.json"))
        self.assertEqual(len(preparados), 1)
        self.assertIn(str(backups[0].parent.resolve()), errores.getvalue())
        self.assertIn(str(preparados[0].parent.resolve()), errores.getvalue())

    def test_perfil_omp_vacio_preserva_override_o_descarta_derivado_pi(self):
        configurado = self.home / "omp-personalizado"
        self.entorno.update(OMP_PROFILE="", PI_PROFILE="otro", PI_CODING_AGENT_DIR=str(configurado))
        resultado = self.ejecutar("--harness", "omp")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((configurado / "skills/gamemaker-biblioteca/SKILL.md").is_file())
        derivado = self.home / ".omp/profiles/otro/agent"
        self.entorno["PI_CODING_AGENT_DIR"] = str(derivado)
        resultado = self.ejecutar("--harness", "omp")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((self.home / ".omp/agent/skills/gamemaker-biblioteca/SKILL.md").is_file())
        self.assertFalse(derivado.exists())

    def test_config_omp_absoluta_no_bloquea_otro_harness(self):
        self.entorno["PI_CONFIG_DIR"] = str(self.home / "config")
        resultado = self.ejecutar("--harness", "omp")
        self.assertEqual(resultado.returncode, 2)
        self.assertFalse(self.home.exists())
        resultado = self.ejecutar("--harness", "dsh")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_hermes_sufijo_literal_y_home_configurado(self):
        self.entorno["HERMES_DATA_DIR_SUFFIX"] = "-pruebas"
        resultado = self.ejecutar("--harness", "hermes")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        relativa = "AppData/Local/hermes-pruebas" if sys.platform == "win32" else ".hermes-pruebas"
        self.assertTrue((self.home / relativa / "skills/gamemaker-biblioteca/SKILL.md").is_file())
        configurado = self.home / "hermes-propio"
        self.entorno["HERMES_HOME"] = str(configurado)
        resultado = self.ejecutar("--harness", "hermes")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertTrue((configurado / "skills/gamemaker-biblioteca/SKILL.md").is_file())


if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main(verbosity=2)
