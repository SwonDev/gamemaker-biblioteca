#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Añade pares EN→ES a la memoria de traducción. Lee JSON por stdin."""
import os, sys, json

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida de este script vía subprocess), sys.stdout
# usa la página de códigos ANSI del sistema en vez de UTF-8 — y los símbolos ✗/⚠/→/…
# de este código no caben ahí: UnicodeEncodeError a mitad de ejecución. No verificado
# en Windows de verdad; aplica la solución estándar de Python 3.7+ (PEP 528 cubre la
# consola interactiva sola, no pipes ni redirecciones).
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SC = os.path.dirname(os.path.abspath(__file__))
TM = os.path.join(SC, "tm_es.json")
tm = json.load(open(TM, encoding="utf-8")) if os.path.exists(TM) else {}
nuevos = json.load(sys.stdin)
antes = len(tm)
tm.update(nuevos)
json.dump(tm, open(TM, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print(f"memoria: {antes} → {len(tm)} unidades (+{len(tm)-antes})")
