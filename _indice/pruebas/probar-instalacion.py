#!/usr/bin/env python3
"""Regresiones del instalador sobre una biblioteca temporal; nunca cambia HOME."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[2]

class Instalador(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.bib = self.base / "biblioteca"
        self.bib.mkdir()
        shutil.copy2(RAIZ / "instalar.sh", self.bib)
        ind = self.bib / "_indice"
        ind.mkdir()
        shutil.copy2(RAIZ / "_indice/sincronizar-skill.py", ind)
        shutil.copy2(RAIZ / "_indice/MAPA.json", ind)
        shutil.copytree(RAIZ / "_indice/skills", ind / "skills")
        # El fixture solo valida el contrato del instalador; no recorre documentos.
        (ind / "sincronizar-skill.py").write_text(
            "import sys,yaml\nfrom pathlib import Path\np=Path(__file__).parent/'skills/gamemaker-biblioteca/SKILL.md'\n"
            "v=yaml.safe_load(p.read_text().split('---')[1])\nsys.exit(0 if v.get('name')=='gamemaker-biblioteca' else 1)\n",
            encoding="utf-8")
        self.bin = self.base / "bin"
        self.bin.mkdir()
        (self.bin / "python3").symlink_to(sys.executable)
        self.entorno = dict(os.environ, PATH=str(self.bin)+os.pathsep+os.environ["PATH"])
        self.dest = self.base / "destino"
        # Aislar incluso el instalador antiguo que ignoraba --destino. No se cambia HOME.
        archivo = self.bib / "instalar.sh"
        texto = archivo.read_text(encoding="utf-8")
        texto = texto.replace("$HOME", str(self.base / "usuario"))
        texto = texto.replace("~/.config", str(self.base / "usuario/.config"))
        archivo.write_text(texto, encoding="utf-8")

    def ejecutar(self, *args):
        return subprocess.run(["bash", str(self.bib / "instalar.sh"), *args],
                              env=self.entorno, capture_output=True, text=True)

    def test_opcion_desconocida_no_es_exito(self):
        r = self.ejecutar("--desconocida", "--destino", str(self.dest))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(self.dest.exists())

    def test_copia_completa_sin_indices(self):
        r = self.ejecutar("--destino", str(self.dest))
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        for p in (self.bib / "_indice/skills/gamemaker-biblioteca").rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(), (self.dest / "gamemaker-biblioteca" / p.relative_to(self.bib / "_indice/skills/gamemaker-biblioteca")).read_bytes())
        self.assertIn("no se han regenerado", r.stdout.lower())

    def test_reinstalacion_conserva_copia(self):
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("trabajo previo", encoding="utf-8")
        r = self.ejecutar("--destino", str(self.dest))
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        notas = list((self.dest / ".gamemaker-biblioteca-backups").rglob("nota.txt"))
        self.assertEqual(len(notas), 1)
        self.assertEqual(notas[0].read_text(), "trabajo previo")

    def test_yaml_invalido_conserva_destino(self):
        viejo = self.dest / "gamemaker-biblioteca"
        viejo.mkdir(parents=True)
        (viejo / "nota.txt").write_text("conservar", encoding="utf-8")
        (self.bib / "_indice/skills/gamemaker-biblioteca/SKILL.md").write_text("---\nname: [roto\n---\n", encoding="utf-8")
        r = self.ejecutar("--destino", str(self.dest))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((viejo / "nota.txt").read_text(), "conservar")

    def test_indices_fallidos_conservan_destino(self):
        (self.bib / "_indice/construir-indices.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        r = self.ejecutar("--indices", "--destino", str(self.dest))
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.dest.exists())

    def test_comprobar_no_instala(self):
        r = self.ejecutar("--comprobar", "--destino", str(self.dest))
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertFalse(self.dest.exists())

    def test_enlace_y_origen_protegido(self):
        r = self.ejecutar("--enlace", "--destino", str(self.dest))
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
        self.assertTrue((self.dest / "gamemaker-biblioteca").is_symlink())
        origen = self.bib / "_indice/skills"
        r = self.ejecutar("--destino", str(origen))
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue((origen / "gamemaker-biblioteca/SKILL.md").is_file())

    def test_destino_dentro_del_origen_no_copia_recursivamente(self):
        base = self.bib / "_indice/skills/gamemaker-biblioteca/subcarpeta"
        r = self.ejecutar("--destino", str(base))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(base.exists())

if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        sys.argv = sys.argv[:1]
    unittest.main()
