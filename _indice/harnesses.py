#!/usr/bin/env python3
"""Destinos nativos de instrucciones; no lee proveedores ni credenciales."""
import argparse
import os
from pathlib import Path
import re
import shutil
import sys

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

def normalizar_perfil(valor):
    # trim() de ECMAScript: incluye BOM, excluye U+0085 que Python strip() acepta.
    blancos_ecma = "\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
    nombre = (valor or "").strip(blancos_ecma)
    if not nombre or nombre == "default":
        return None
    if (not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", nombre) or
            nombre.endswith(".") or
            re.fullmatch(r"(?:con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", nombre, re.I)):
        raise ValueError("Perfil OMP inválido; usa su nombre validado o --destino.")
    return nombre


def destinos(home, entorno=None, validar_omp=False):
    e = os.environ if entorno is None else entorno
    h = Path(home)
    def base(variable, defecto):
        return Path(e.get(variable) or str(h/defecto)).expanduser()
    omp_config = e.get("PI_CONFIG_DIR") or ".omp"
    omp = h/omp_config.lstrip("/\\")
    try:
        perfil = normalizar_perfil(e["OMP_PROFILE"] if "OMP_PROFILE" in e else e.get("PI_PROFILE"))
    except ValueError:
        if validar_omp:
            raise
        perfil = None
    envdir = e.get("PI_CODING_AGENT_DIR")
    try:
        perfil_pi = normalizar_perfil(e.get("PI_PROFILE"))
    except ValueError:
        perfil_pi = None
    # OMP descarta el override heredado que ya correspondía al perfil Pi.
    if not perfil and perfil_pi and envdir == str(omp/"profiles"/perfil_pi/"agent"):
        envdir = None
    omp_agent = omp/"profiles"/perfil/"agent" if perfil else Path(envdir or str(omp/"agent")).absolute()
    sufijo = e.get("HERMES_DATA_DIR_SUFFIX", "")
    hermes_default = Path(e.get("LOCALAPPDATA") or str(h/"AppData/Local"))/("hermes"+sufijo) if sys.platform == "win32" else h/(".hermes"+sufijo)
    hermes_home = (e.get("HERMES_HOME") or "").strip()
    hermes = Path(os.path.expandvars(hermes_home)).expanduser() if hermes_home else hermes_default
    return {
        "agents": ((), h/".agents/skills"),
        "claude": (("claude",), h/".claude/skills"),
        "codex": (("codex", "codex-deepseek"), base("CODEX_HOME", ".codex")/"skills"),
        "opencode": (("opencode",), h/".config/opencode/skills"),
        "qwen": (("qwen",), h/".qwen/skills"),
        "kimi": (("kimi",), h/".kimi-code/skills"),
        "gemini": (("gemini",), h/".gemini/skills"),
        "copilot": (("copilot",), h/".copilot/skills"),
        "cursor": (("cursor-agent", "agent"), h/".cursor/skills"),
        "cline": (("cline",), h/".cline/skills"),
        "pi": (("pi",), base("PI_CODING_AGENT_DIR", ".pi/agent")/"skills"),
        "omp": (("omp",), omp_agent/"skills"),
        "minimax": (("mcode",), Path(e.get("MINIMAX_DATA_DIR") or e.get("MAVIS_DATA_DIR") or str(h/".minimax"))/"skills"),
        "dsh": (("dsh", "deepseek"), base("DSH_HOME", ".dsh")/"skills"),
        "hermes": (("hermes",), hermes/"skills"),
        "gentle-shell": (("gentle-shell",), base("GENTLE_SHELL_HOME", ".gentle-shell/agent")/"skills"),
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--harness")
    p.add_argument("--listar", action="store_true")
    a = p.parse_args()
    requiere_omp = not a.listar and (a.harness == "omp" or (not a.harness and shutil.which("omp")))
    try:
        opciones = destinos(a.home, validar_omp=requiere_omp)
    except ValueError as error:
        p.error(str(error))
    if a.harness and a.harness not in opciones:
        p.error("Harness desconocido: " + a.harness)
    omp_config = os.environ.get("PI_CONFIG_DIR", "")
    if requiere_omp and \
            (Path(omp_config).is_absolute() or omp_config.startswith("~")):
        p.error("PI_CONFIG_DIR debe ser relativo al home; para otra raíz usa PI_CODING_AGENT_DIR absoluto o --destino.")
    for nombre, (comandos, ruta) in opciones.items():
        if a.harness and a.harness != nombre:
            continue
        if a.listar:
            print(f"{nombre}\t{ruta}")
        elif a.harness or not comandos or any(shutil.which(c) for c in comandos):
            if any(c in str(ruta) for c in ("\n", "\r", "\t")):
                p.error("El destino contiene un salto de línea o tabulador.")
            print(ruta)

if __name__ == "__main__":
    main()
