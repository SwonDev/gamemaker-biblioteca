#!/usr/bin/env python3
"""Regresiones del contrato público del sincronizador, sobre paquetes temporales."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

IND = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sincronizador", IND / "sincronizar-skill.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Sincronizacion(unittest.TestCase):
    def setUp(self):
        silencio = contextlib.redirect_stdout(io.StringIO())
        silencio.__enter__()
        self.addCleanup(silencio.__exit__, None, None, None)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.raiz = self.base / "biblioteca"
        self.ind = self.raiz / "_indice"
        self.skill = self.ind / "skills/gamemaker-biblioteca"
        self.refs = self.skill / "references"
        self.refs.mkdir(parents=True)
        (self.ind / "MAPA.json").write_text(json.dumps({"carpetas": []}), encoding="utf-8")
        (self.skill / "SKILL.md").write_text(
            '---\nname: gamemaker-biblioteca\ndescription: "GameMaker GML .yyp gm-cli hazme un juego no compila"\n---\n'
            '<!-- SKILL-VERSION: r1 -->\n# Biblioteca\n', encoding="utf-8")
        self.destino = self.base / "usuario/.agents/skills/gamemaker-biblioteca"
        valores = {"RAIZ": str(self.raiz), "IND": str(self.ind), "SKILL": str(self.skill),
                   "REFS": str(self.refs), "GENERADO": str(self.refs / "indice-documentos.md"),
                   "AGENTS_GENERADO": str(self.skill / "AGENTS.md")}
        for nombre, valor in valores.items():
            p = patch.object(mod, nombre, valor)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(mod.os.path, "expanduser", side_effect=lambda s: str(self.base / "usuario" / s.removeprefix("~/")))
        p.start()
        self.addCleanup(p.stop)

    def copiar(self):
        mod.generar_indice()
        mod.generar_agents_md()
        self.destino.parent.mkdir(parents=True)
        shutil.copytree(self.skill, self.destino)

    def estado_generico(self):
        return next(l for l in mod.estado_enlaces() if "Genérico ~/.agents" in l)

    def test_yaml_invalido_impide_exito(self):
        (self.skill / "SKILL.md").write_text('---\nname: x\ndescription: [sin cierre\n---\n# T\n', encoding="utf-8")
        self.assertNotEqual(mod.main(), 0)

    def test_frontmatter_ausente_impide_exito(self):
        (self.skill / "SKILL.md").write_text('# Sin metadatos\n', encoding="utf-8")
        self.assertNotEqual(mod.main(), 0)

    def test_parser_ausente_impide_exito(self):
        with patch.dict(sys.modules, {"yaml": None}):
            self.assertNotEqual(mod.main(), 0)

    def test_nombre_ausente_impide_exito(self):
        archivo = self.skill / "SKILL.md"
        archivo.write_text(archivo.read_text(encoding="utf-8").replace("name: gamemaker-biblioteca\n", ""), encoding="utf-8")
        self.assertNotEqual(mod.main(), 0)

    def test_referencia_local_canonica_ausente_impide_exito(self):
        archivo = self.skill / "SKILL.md"
        archivo.write_text(archivo.read_text(encoding="utf-8") + "\nLee `references/ausente.md`.\n", encoding="utf-8")
        self.assertNotEqual(mod.main(), 0)

    def test_copia_completa_se_reconoce(self):
        self.copiar()
        self.assertIn("copia al día", self.estado_generico())

    def test_referencia_modificada_no_esta_al_dia(self):
        self.copiar()
        (self.destino / "references/indice-documentos.md").write_text('Documento antiguo\n', encoding="utf-8")
        self.assertNotIn("copia al día", self.estado_generico())

    def test_referencia_ausente_no_esta_al_dia(self):
        self.copiar()
        (self.destino / "references/indice-documentos.md").unlink()
        self.assertNotIn("copia al día", self.estado_generico())

    def test_agents_modificado_no_esta_al_dia(self):
        self.copiar()
        (self.destino / "AGENTS.md").write_text('Instrucciones antiguas\n', encoding="utf-8")
        self.assertNotIn("copia al día", self.estado_generico())

    def test_referencia_extra_no_esta_al_dia(self):
        self.copiar()
        (self.destino / "references/obsoleta.md").write_text('Instrucción retirada\n', encoding="utf-8")
        self.assertNotIn("copia al día", self.estado_generico())


if __name__ == "__main__":
    unittest.main(verbosity=2)
