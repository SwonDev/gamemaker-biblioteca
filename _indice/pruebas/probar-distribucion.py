#!/usr/bin/env python3
"""Instalación remota real en un home temporal; nunca modifica el usuario anfitrión."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--revision", required=True)
    p.add_argument("--recibo", type=Path)
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix="gm-distribucion-") as temporal:
        home = Path(temporal)/"usuario con espacios y ñ"
        biblioteca = home/".local/share/gamemaker-biblioteca"
        # Vaciar overrides propios de harnesses evita que salgan del fixture. HOME
        # conserva su valor; --home es la frontera pública del instalador.
        entorno = dict(os.environ)
        for variable in ("CLAUDE_CONFIG_DIR", "OPENCODE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME",
                         "PI_CODING_AGENT_DIR", "PI_CONFIG_DIR", "OMP_PROFILE", "PI_PROFILE",
                         "MINIMAX_DATA_DIR", "MAVIS_DATA_DIR", "DSH_HOME", "HERMES_HOME",
                         "HERMES_DATA_DIR_SUFFIX", "GENTLE_SHELL_HOME", "LOCALAPPDATA"):
            entorno.pop(variable, None)
        comando = [sys.executable, str(RAIZ/"instalar-remoto.py"), "--revision", a.revision,
                   "--home", str(home)]
        subprocess.run(comando, env=entorno, check=True)
        paquete = biblioteca/"_indice/skills/gamemaker-biblioteca"
        manifiesto = json.loads((paquete/"manifest.json").read_text(encoding="utf-8"))
        spec = importlib.util.spec_from_file_location("harnesses_distribucion", biblioteca/"_indice/harnesses.py")
        harnesses = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harnesses)
        destinos = {str(ruta) for _, ruta in harnesses.destinos(home, entorno).values()}
        for ruta in destinos:
            copia = Path(ruta)/"gamemaker-biblioteca"
            for nombre, huella in manifiesto["files"].items():
                assert hashlib.sha256((copia/nombre).read_bytes()).hexdigest() == huella, (ruta, nombre)
            assert json.loads((copia/"manifest.json").read_text(encoding="utf-8")) == manifiesto
        registro = home/".config/gamemaker-biblioteca/ruta"
        assert Path(registro.read_text(encoding="utf-8").strip()).resolve() == biblioteca.resolve()
        subprocess.run(comando, env=entorno, check=True)
        assert not list(home.rglob(".gamemaker-biblioteca-backups")), "La repetición creó copias innecesarias"
        assert not list(biblioteca.parent.glob("gamemaker-biblioteca-anterior-*"))
        distribucion = json.loads((biblioteca/".gamemaker-distribucion.json").read_text(encoding="utf-8"))
        recibo = {"plataforma": sys.platform, "python": sys.version.split()[0],
                  "distribucion": distribucion, "skill_version": manifiesto["version"],
                  "archivos": len(manifiesto["files"]), "destinos_unicos": len(destinos),
                  "segunda_instalacion": "sin cambios ni backups", "registro": True,
                  "resultado": "APTO", "limite": "Instalación real; no acredita selección por un modelo."}
        if a.recibo:
            a.recibo.write_text(json.dumps(recibo, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(recibo, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
