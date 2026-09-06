#!/usr/bin/env python3
"""Añade pares inglés→español a celdas_es.json leyendo un JSON por la entrada estándar."""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.join(AQUI, "celdas_es.json")
memo = json.load(open(MEM, encoding="utf-8")) if os.path.exists(MEM) else {}
antes = len(memo)
memo.update(json.load(sys.stdin))
json.dump(memo, open(MEM, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print(f"celdas_es.json: {antes} → {len(memo)} (+{len(memo) - antes})")
