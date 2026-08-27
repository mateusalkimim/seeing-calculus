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
import glob
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

    # `pt/` so existe em repositorio COM sitio. Um repositorio sem GitHub Pages
    # tem README, e o README e a pagina -- abortar aqui fazia o build morrer
    # antes de chegar ao markdown, em dois repositorios inteiros.
    total_pend, feitos = 0, 0
    tem_sitio = os.path.isdir(a.fonte)
    if tem_sitio:
        os.makedirs(a.destino, exist_ok=True)
    for arq in (sorted(os.listdir(a.fonte)) if tem_sitio else []):
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

    # ---- os documentos markdown: o README e o que estiver em docs/ ----
    # No GitHub o README e a porta de entrada, e num repositorio SEM Pages ele
    # e a unica pagina que existe. `docs/` vai junto porque o README aponta
    # para la -- mandar o leitor de ingles para uma pagina em portugues e o
    # mesmo defeito, uma casa adiante. `pharo/` NAO entra: e material interno
    # de pesquisa, e traduzi-lo e outra decisao, do autor.
    # README, os markdown da RAIZ (o relativity-paradox-lab guarda a
    # `FUNDAMENTACAO-CIENTIFICA.md` la) e `docs/`. Varrer so README e docs/
    # deixaria um documento publicado de fora, sem ninguem acusar.
    docs = [os.path.join(AQUI, "README.md")]
    for f in sorted(glob.glob(os.path.join(AQUI, "*.md"))
                    + glob.glob(os.path.join(AQUI, "docs", "*.md"))):
        if (f.endswith(".en.md") or f in docs
                or os.path.basename(f).startswith("LICENSE")):
            continue
        docs.append(f)
    em_ingles = {}
    for doc in docs:
        if not os.path.exists(doc):
            continue
        rel = os.path.relpath(doc, AQUI)
        raw = open(doc, encoding="utf-8").read()
        # basename, igual ao tradutor: nomear a tabela de um jeito aqui e de
        # outro la faria o build procurar um arquivo que o tradutor nunca
        # escreveu, e reprovar por "sem traducao" o que estava traduzido.
        tab = i18n.ler_tabela(i18n.caminho_tabela(doc, a.traducao))
        if not tab.get("blocos"):
            # DOCUMENTO SEM TABELA E PENDENCIA, NAO AUSENCIA. Pular calado fez
            # o `docs/INSTALACAO.md` de um repositorio ficar so em portugues
            # sem que o build dissesse uma palavra -- o arquivo existe, o
            # leitor de ingles chega nele, e nada acusava.
            total_pend += 1
            print("%-24s SEM TRADUCAO (nenhum bloco na tabela)" % rel)
            continue
        en_md, pend, cercas = i18n.aplicar_md(i18n.sem_troca_idioma(raw), tab)
        if pend:
            total_pend += len(pend)
            print("%-24s %d bloco(s) sem traducao" % (rel, len(pend)))
            for k, pt, tipo in pend[:4]:
                print("   %s  %s" % (k, pt.strip()[:64].replace("\n", " ")))
            continue
        alvo = doc[:-3] + ".en.md"
        em_ingles[rel] = os.path.relpath(alvo, AQUI)
        open(alvo, "w", encoding="utf-8").write(
            i18n.troca_idioma_md(en_md, "en", os.path.basename(doc)))
        open(doc, "w", encoding="utf-8").write(
            i18n.troca_idioma_md(raw, "pt", os.path.basename(alvo)))
        # conta so a cerca que AINDA mede portugues -- avisar sobre toda
        # cerca, inclusive as ja traduzidas, e ruido que ensina a ignorar o
        # aviso.
        sobrando = sum(1 for _, _, mio in i18n.cercas_traduziveis(en_md))
        print("%s%s" % (os.path.relpath(alvo, AQUI),
                        "  [%d cerca(s) ainda em portugues: realinhe a mao]"
                        % sobrando if sobrando else ""))
    # o documento em ingles aponta para o VIZINHO em ingles, quando ele existe.
    # Sem isto o leitor de ingles e mandado de volta para o portugues no 1o
    # clique, e a traducao vale so ate a borda do arquivo.
    for rel, ing in em_ingles.items():
        alvo = os.path.join(AQUI, ing)
        t = open(alvo, encoding="utf-8").read()
        for outro, outro_en in em_ingles.items():
            t = t.replace("](%s)" % outro.replace(os.sep, "/"),
                          "](%s)" % outro_en.replace(os.sep, "/"))
        open(alvo, "w", encoding="utf-8").write(t)

    if total_pend and not a.permitir_pendente:
        print("\nREPROVADO: %d bloco(s) sem traducao. O ingles nao foi "
              "publicado.\nPreencha as tabelas de %s e rode de novo."
              % (total_pend, os.path.basename(a.traducao)))
        return 1
    if tem_sitio:
        print("\n%d pagina(s) em %s%s" % (feitos, a.destino,
              "  [COM %d PENDENTE(S) MARCADO(S)]" % total_pend if total_pend else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
