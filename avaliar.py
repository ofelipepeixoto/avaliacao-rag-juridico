"""Avalia seleção de trechos; não avalia texto gerado por modelo."""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent / "dados"
COMUNS = {"qual", "quando", "quanto", "como", "que", "quem", "existe", "em", "de", "da", "do", "por", "o", "a", "e", "um", "uma", "contrato"}
EQUIVALENCIAS = {"comeca": "inicio", "cancelar": "rescisao"}  # definidas antes da reserva


def carregar(nome):
    return json.loads((RAIZ / nome).read_text(encoding="utf-8"))


def termos(texto, expandir=False):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    palavras = set(re.findall(r"[a-z0-9]+", texto)) - COMUNS
    return {EQUIVALENCIAS.get(p, p) if expandir else p for p in palavras}


def recuperar(pergunta, expandir=False, documentos=None):
    documentos = carregar("contrato_ficticio.json") if documentos is None else documentos
    consulta = termos(pergunta, expandir)
    candidatos = [(len(consulta & termos(d["texto"], expandir)), d["id"]) for d in documentos]
    candidatos.sort(key=lambda c: (-c[0], c[1]))
    return candidatos[0][1] if candidatos and candidatos[0][0] else None


def medir(casos, expandir=False):
    linhas = []
    for caso in casos:
        obtido = recuperar(caso["pergunta"], expandir)
        linhas.append({**caso, "obtido": obtido, "acertou": obtido == caso["esperado"]})
    categorias = {c: {"acertos": sum(l["acertou"] for l in linhas if l["categoria"] == c),
                      "total": sum(l["categoria"] == c for l in linhas)}
                  for c in sorted({l["categoria"] for l in linhas})}
    return {"acertos": sum(l["acertou"] for l in linhas), "total": len(linhas),
            "por_categoria": categorias, "casos": linhas}


if __name__ == "__main__":
    for conjunto in ("desenvolvimento.json", "reserva.json"):
        casos = carregar(conjunto)
        for nome, expandir in (("literal", False), ("equivalencias", True)):
            resultado = medir(casos, expandir)
            print(f"{conjunto} / {nome}: {resultado['acertos']}/{resultado['total']}")
            for linha in resultado["casos"]:
                if not linha["acertou"]:
                    print(f"  ERRO {linha['categoria']}: {linha['pergunta']} -> {linha['obtido']} (esperado {linha['esperado']})")
