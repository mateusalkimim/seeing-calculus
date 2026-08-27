#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constroi `en/` a partir de `pt/` e das tabelas de `traducao/`.

O ingles e DERIVADO. Editar um arquivo de `en/` e o defeito, nao o atalho --
pela mesma razao que editar o `index.html` gerado e: na correcao seguinte do
portugues, a edicao some sem aviso, ou pior, sobrevive so num idioma.

REPROVA em vez de publicar meio traduzido. Um paragrafo em portugues no meio de
uma pagina em ingles nao trava nada, nao acende nada, e so aparece quando um
leitor de fora ja esta lendo. O padrao e falhar; `--permitir-pendente` existe
para inspecao local e marca cada bloco pendente no HTML.

    python3 gerar_en.py                    # constroi, ou reprova dizendo o que falta
    python3 gerar_en.py --permitir-pendente
"""
import argparse
import os
import sys

import i18n

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "pt")
DESTINO = os.path.join(AQUI, "en")
TRADUCAO = os.path.join(AQUI, "traducao")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--permitir-pendente", action="store_true")
    ap.add_argument("--fonte", default=FONTE)
    ap.add_argument("--destino", default=DESTINO)
    ap.add_argument("--traducao", default=TRADUCAO)
    a = ap.parse_args()

    if not os.path.isdir(a.fonte):
        raise SystemExit("sem %s -- o portugues e a fonte deste build" % a.fonte)
    os.makedirs(a.destino, exist_ok=True)

    total_pend, feitos = 0, 0
    for arq in sorted(os.listdir(a.fonte)):
        if not arq.endswith(".html"):
            continue
        raw = open(os.path.join(a.fonte, arq), encoding="utf-8").read()
        tab = i18n.ler_tabela(i18n.caminho_tabela(arq, a.traducao))
        en, pend = i18n.aplicar(raw, tab)
        if pend:
            total_pend += len(pend)
            print("%-24s %d bloco(s) sem traducao:" % (arq, len(pend)))
            for k, pt, tipo in pend[:6]:
                print("   [%s] %s  %s" % (tipo, k, pt.strip()[:64]))
            if len(pend) > 6:
                print("   ... e mais %d" % (len(pend) - 6))
            if not a.permitir_pendente:
                continue
            for k, pt, tipo in pend:
                en = en.replace(pt, "<!--PENDENTE-->" + pt, 1)
        en = i18n.injetar_faixa(en, "en", arq)
        open(os.path.join(a.destino, arq), "w", encoding="utf-8").write(en)
        # a faixa do lado portugues tambem e DERIVADA, e por isso e reposta
        # aqui: um so lugar decide como ela e nos dois idiomas.
        pt_com_faixa = i18n.injetar_faixa(raw, "pt", arq)
        open(os.path.join(a.fonte, arq), "w", encoding="utf-8").write(pt_com_faixa)
        feitos += 1

    if total_pend and not a.permitir_pendente:
        print("\nREPROVADO: %d bloco(s) sem traducao. O ingles nao foi "
              "publicado.\nPreencha as tabelas de %s e rode de novo."
              % (total_pend, os.path.basename(a.traducao)))
        return 1
    print("\n%d pagina(s) em %s%s" % (feitos, a.destino,
          "  [COM %d PENDENTE(S) MARCADO(S)]" % total_pend if total_pend else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
