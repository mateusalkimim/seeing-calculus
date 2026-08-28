#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tira da tabela de traducao os blocos que a matriz nao tem mais.

Existe por causa de um achado de 2026-08-28: quatro paragrafos foram retirados
de uma pagina publicada, e continuaram no repositorio. A tabela de traducao
guarda o bloco pela chave do ORIGINAL; quando o original muda, a entrada velha
simplesmente fica — e nem sequer marcada como orfa, porque quem marca e o
tradutor com modelo, que so roda quando ha o que traduzir.

O efeito e que texto retirado por decisao de registro continua publicado, fora
da pagina, no arquivo de dados. Uma busca no repositorio acha; a pagina, nao.

Preservar o bloco orfao e bom para desfazer uma edicao. Nao serve para manter
publicado o que foi retirado de proposito -- e por isso este instrumento
existe, e por isso ele pede o motivo:

    python3 purgar_orfaos.py --motivo "registro interno, varredura 2026-08-28"
    python3 purgar_orfaos.py --listar     # so mostra, nao mexe

O que sai vai para `traducao/<nome>.purgado.json`, com data e motivo: some do
que se publica, nao do que se pode auditar.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def matriz_de(tabela, raiz):
    """O arquivo de que a tabela nasce -- html em pt/ ou markdown."""
    base = os.path.basename(tabela)[:-len(".en.json")]
    for cand in (os.path.join(raiz, "pt", base + ".html"),
                 os.path.join(raiz, base + ".md"),
                 os.path.join(raiz, "docs", base + ".md"),
                 os.path.join(raiz, base + ".html")):
        if os.path.exists(cand):
            return cand
    return None


def chaves_ativas(i18n, matriz):
    """As chaves que a matriz usa HOJE, pelo EXTRATOR.

    A 1a versao perguntava "que blocos estao pendentes contra uma tabela
    vazia?" e a resposta mentia: `aplicar` pula o que nao manda traduzir --
    citacao, bloco ja em ingles --, entao 115 traducoes VIVAS apareciam como
    orfas. Purgar por aquela lista teria apagado traducao boa, em silencio,
    num arquivo que ninguem reabre.

    A pergunta certa e "que blocos a matriz tem?", e quem responde e o
    extrator -- o mesmo que alimenta a tabela.
    """
    raw = io.open(matriz, encoding="utf-8").read()
    if matriz.endswith(".html"):
        blocos = [b[2] for b in i18n.extrair_de(raw)]
    else:
        bs = i18n.blocos_md(i18n.sem_troca_idioma(raw))
        if isinstance(bs, tuple):        # (blocos, cercas)
            bs = bs[0]
        blocos = [b[-1] if isinstance(b, (tuple, list)) else b for b in bs]
    return {i18n.chave(t) for t in blocos}, " ".join(raw.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz", nargs="?", default=os.getcwd())
    ap.add_argument("--motivo", default="")
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()
    raiz = os.path.abspath(a.raiz)

    sys.path.insert(0, raiz)
    try:
        import i18n
    except ImportError:
        print("i18n.py nao encontrado em %s" % raiz)
        return 1

    if not a.listar and not a.motivo.strip():
        print("Diga o motivo: --motivo \"...\". Purga sem motivo nao deixa rastro.")
        return 1

    total = 0
    for tabela in sorted(glob.glob(os.path.join(raiz, "traducao", "*.en.json"))):
        matriz = matriz_de(tabela, raiz)
        if not matriz:
            print("%-34s sem matriz — nao mexo" % os.path.relpath(tabela, raiz))
            continue
        d = json.load(io.open(tabela, encoding="utf-8"))
        blocos = d.get("blocos", {})
        vivas, matriz_norm = chaves_ativas(i18n, matriz)
        # DUAS vias, e so purga o que as duas condenam: a chave sumiu do
        # extrator E o texto inteiro nao esta mais na matriz. Uma via so ja
        # errou uma vez, e o erro dela apaga trabalho.
        orfas = [k for k in blocos
                 if k not in vivas
                 and " ".join((blocos[k].get("pt") or "").split()) not in matriz_norm]
        presas = [k for k in blocos if k not in vivas
                  and " ".join((blocos[k].get("pt") or "").split()) in matriz_norm]
        if presas:
            print("%-34s %d bloco(s) que a chave condena e o texto salva — nao mexo"
                  % (os.path.relpath(tabela, raiz), len(presas)))
        if not orfas:
            print("%-34s ok (%d blocos, 0 orfaos)"
                  % (os.path.relpath(tabela, raiz), len(blocos)))
            continue
        print("%-34s %d orfao(s) de %d" % (os.path.relpath(tabela, raiz),
                                           len(orfas), len(blocos)))
        for k in orfas[:4]:
            print("    %s  %s" % (k, " ".join((blocos[k].get("pt") or "").split())[:70]))
        if len(orfas) > 4:
            print("    ... e mais %d" % (len(orfas) - 4))
        total += len(orfas)
        if a.listar:
            continue

        # FORA do que se publica. A 1a versao gravava `traducao/<nome>.purgado
        # .json` ao lado da tabela: o texto saia da pagina e continuava no
        # repositorio publico, que e exatamente o defeito que este instrumento
        # existe para consertar. Agora vai para `.purgado/`, ignorado pelo git.
        dir_purga = os.path.join(raiz, ".purgado")
        os.makedirs(dir_purga, exist_ok=True)
        gi = os.path.join(raiz, ".gitignore")
        regras = io.open(gi, encoding="utf-8").read() if os.path.exists(gi) else ""
        if ".purgado/" not in regras:
            with io.open(gi, "a", encoding="utf-8") as fh:
                fh.write("\n# texto retirado por decisao de registro — auditavel, nao publicado\n.purgado/\n")
        saida = os.path.join(dir_purga,
                             os.path.basename(tabela).replace(".en.json", ".purgado.json"))
        antes = json.load(io.open(saida, encoding="utf-8")) if os.path.exists(saida) else []
        antes.append({"data": datetime.date.today().isoformat(),
                      "motivo": a.motivo.strip(),
                      "blocos": {k: blocos[k] for k in orfas}})
        io.open(saida, "w", encoding="utf-8").write(
            json.dumps(antes, ensure_ascii=False, indent=1, sort_keys=True))
        for k in orfas:
            del blocos[k]
        d["atualizado_em"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        io.open(tabela, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))

    print("\n%d bloco(s) %s" % (total, "listado(s)" if a.listar else "purgado(s)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
