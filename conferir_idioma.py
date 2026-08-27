#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O portao de IDIOMA: mede o texto da pagina, nunca o nome do arquivo.

Existe por causa de um episodio real: numa apresentacao foi levado o deck em
INGLES, e so se percebeu na hora de projetar. Os dois arquivos moravam na mesma
pasta e o nome diferia em dois caracteres. Nome de arquivo se confia ate o dia
em que ele engana, e esse dia ja chegou.

O teste e de PALAVRAS-FUNCAO -- `que · nao · para · com` contra
`the · and · of · with`. Elas aparecem em qualquer assunto e nao se traduzem
sozinhas. Termo tecnico nao serviria: *vetor* e *vector* se parecem, e *matrix*
aparece nos dois.

Mede tambem o que o modelo entrega quando ninguem confere: ingles BRITANICO.
`colour`, `behaviour`, `-ise` reprovam -- o pedido foi en-US.

    python3 conferir_idioma.py            # confere pt/ e en/
    python3 conferir_idioma.py --controle # e o controle negativo
"""
import argparse
import glob
import json
import os
import re
import sys

import i18n

# A SONDA DE en-GB VEM DO i18n.py, nao e copiada. Este arquivo teve uma copia
# propria por uma hora, eu corrigi o falso positivo de `-ise` num lado so, e o
# portao reprovou `raise` e `rise` em paginas boas. Molde herda o defeito, e
# copia de sonda herda o defeito velho.

AQUI = os.path.dirname(os.path.abspath(__file__))

PT = re.compile(r"\b(que|n[aã]o|para|com|uma|pelo|pela|dos|das|nas|nos|"
                r"ao|aos|isso|onde|quando|sao|est[aá])\b", re.I)
EN = re.compile(r"\b(the|and|of|with|that|for|from|which|when|where|"
                r"this|these|into|about)\b", re.I)
GB = i18n._EN_GB          # UMA sonda, no i18n.py -- ver nota abaixo


def texto_de(html):
    """So o que o leitor le: fora <style>, <script>, a FAIXA e as tags.

    A faixa sai porque ela e deliberadamente bilingue -- a faixa da pagina
    inglesa fala portugues, para ser entendida por quem precisa dela. Medi-la
    dava `pt=2` em toda pagina de `en/`, um residuo que nao e defeito e que
    treina quem le a ignorar o numero.
    """
    s = i18n.remover_faixa(html)
    # CITACAO NAO CONTA NA MEDIDA. Ela esta no idioma da FONTE, nao no da
    # pagina: o abstraction-ladder cita Petzold e SICP no ingles original, e a
    # pagina PORTUGUESA dele mede `pt=66 en=311` -- a medida certa levando a
    # conclusao errada. <blockquote> e <cite> saem; o que sobra e a voz de quem
    # escreve, que e o que a pergunta "em que idioma esta esta pagina" quer.
    s = re.sub(r"<(blockquote|cite)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<(style|script)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    return re.sub(r"<[^>]+>", " ", s)


def medir(html):
    t = texto_de(html)
    return len(PT.findall(t)), len(EN.findall(t))


def _tabelas(dir_traducao):
    """{texto_pt: registro} de todos os blocos conhecidos."""
    fora = {}
    if not os.path.isdir(dir_traducao):
        return fora
    for arq in os.listdir(dir_traducao):
        if arq.endswith(".json"):
            try:
                t = json.load(open(os.path.join(dir_traducao, arq), encoding="utf-8"))
            except Exception:
                continue
            for b in t.get("blocos", {}).values():
                fora[b.get("pt", "").strip()] = b
    return fora


def nao_traduzidos(pt_html, en_html, tabela):
    """Texto que ficou em portugues na pagina inglesa -- pelo REGISTRO.

    Tres sondas tentaram isto e as duas primeiras erraram:

      1. palavras-funcao: deu VERDE com a navegacao inteira em portugues,
         porque "O par vira ponto" nao tem `que`, nem `nao`, nem `para`;
      2. texto identico nos dois idiomas: pegou a navegacao, e passou a acusar
         as CITACOES -- que sao identicas de direito, por serem o ingles
         original (§7). Baixar o limiar as liberava e devolvia o ponto cego.

    O sinal exato nao esta no texto, esta na TABELA: ela sabe, bloco a bloco,
    o que foi traduzido, o que atravessou por ja ser ingles, e o que nunca foi
    extraido. Sonda que adivinha pelo texto sempre vai errar num dos lados; a
    que le o registro nao precisa adivinhar.
    """
    def nos(h):
        h = i18n.remover_faixa(h)
        h = re.sub(r"<(style|script|code)\b.*?</\1>", " ", h, flags=re.S | re.I)
        return set(t.strip() for t in re.split(r"<[^>]+>", h) if t.strip())

    achados = []
    for t in nos(pt_html) & nos(en_html):
        palavras = re.findall(r"[A-Za-zÀ-ÿ]{2,}", t)
        if len(palavras) < 3 or not any(p[0].islower() for p in palavras):
            continue
        reg = tabela.get(t)
        if reg is None:
            # nao esta no registro: ou e fragmento de um bloco maior (o pai foi
            # traduzido e o filho aparece solto na varredura), ou nunca foi
            # extraido. So acusa se nao couber dentro de nenhum bloco conhecido.
            if any(t in k for k in tabela):
                continue
            achados.append("%s  [nunca extraido]" % t[:60])
        elif reg.get("ja_en"):
            continue                      # §7: citacao, ingles original
        elif (reg.get("en") or "").strip() == t:
            if not i18n.ja_em_ingles(t):
                achados.append("%s  [modelo devolveu o original]" % t[:60])
    return sorted(achados)


def conferir(pasta, esperado):
    achados = []
    if not os.path.isdir(pasta):
        return ["%s nao existe" % pasta]
    for arq in sorted(os.listdir(pasta)):
        if not arq.endswith(".html"):
            continue
        html = open(os.path.join(pasta, arq), encoding="utf-8").read()
        pt, en = medir(html)
        idioma = "PT" if pt > en else ("EN" if en > pt else "?")
        marca = "ok " if idioma == esperado else "NAO"
        print("  %s %-22s %-3s (pt=%-4d en=%-4d)" % (marca, arq, idioma, pt, en))
        if idioma != esperado:
            achados.append("%s/%s esta em %s, esperado %s" % (
                os.path.basename(pasta), arq, idioma, esperado))
        if esperado == "EN":
            for g in set(m.group(0).lower() for m in GB.finditer(texto_de(html))):
                achados.append("%s/%s: en-GB '%s'" % (
                    os.path.basename(pasta), arq, g))
        if esperado == "EN":
            gemeo = os.path.join(os.path.dirname(pasta), "pt", arq)
            if os.path.exists(gemeo):
                tab = _tabelas(os.path.join(os.path.dirname(pasta), "traducao"))
                for t in nao_traduzidos(open(gemeo, encoding="utf-8").read(),
                                        html, tab):
                    achados.append("%s/%s: nao traduzido -- %r" % (
                        os.path.basename(pasta), arq, t[:60]))
        lang = re.search(r'<html[^>]*\slang="([^"]+)"', html)
        if lang:
            decl = lang.group(1).lower()
            certo = decl.startswith("pt") if esperado == "PT" else decl.startswith("en")
            if not certo:
                achados.append("%s/%s: lang=\"%s\" contradiz o texto medido"
                               % (os.path.basename(pasta), arq, decl))
    return achados


def controle():
    """O controle negativo -- sem ele o portao nao vale nada.

    Uma pagina em portugues submetida como se fosse inglesa TEM de reprovar. Um
    portao que nunca se viu reprovar e uma etiqueta, nao um portao.
    """
    amostra = ("<html lang='en'><body><p>a taxa que nao existe aqui, para "
               "cada uma das curvas com o mesmo passo</p></body></html>")
    pt, en = medir(amostra)
    if pt > en:
        print("  ok  pagina PT submetida como EN: reprovaria (pt=%d en=%d)" % (pt, en))
    else:
        print("  NAO controle negativo FALHOU: pt=%d en=%d" % (pt, en))
        return 1
    ingles = ("<html lang='en'><body><p>the rate that does not exist here, "
              "for each of the curves with the same step</p></body></html>")
    pt2, en2 = medir(ingles)
    if en2 <= pt2:
        print("  NAO controle positivo FALHOU: pt=%d en=%d" % (pt2, en2))
        return 1
    print("  ok  pagina EN de verdade: passaria (pt=%d en=%d)" % (pt2, en2))
    gb = "the colour of the centre, analysed by the neighbour"
    if not GB.search(gb):
        print("  NAO o teste de en-GB nao pega 'colour/centre/analysed'")
        return 1
    print("  ok  en-GB detectado na frase de controle")
    return 0


def conferir_markdown(raiz):
    """Confere cada par `X.md` / `X.en.md`.

    Repositorio sem GitHub Pages nao tem `pt/` nem `en/` -- ele tem README, e o
    README E a pagina. Sem esta passagem o portao dizia "pt/ nao existe" e
    passava por cima do unico texto publicado que o repositorio tem.
    """
    achados = []
    pares = []
    for base in sorted(glob.glob(os.path.join(raiz, "*.md"))
                       + glob.glob(os.path.join(raiz, "docs", "*.md"))):
        if base.endswith(".en.md") or os.path.basename(base).startswith("LICENSE"):
            continue
        if base.endswith(".en.md"):
            continue
        ing = os.path.join(os.path.dirname(base), i18n.nome_em_ingles(base))
        if ing != base and os.path.exists(ing):
            pares.append((base, ing))
    if not pares:
        # SILENCIO NAO E APROVACAO. Se ha tabela de traducao e nao ha par
        # `X.md`/`X.en.md`, o build nao rodou -- e o portao dizia "ok" por nao
        # ter o que conferir, que e o falso verde mais barato de produzir.
        if os.path.isdir(os.path.join(raiz, "traducao")):
            achados.append("ha tabelas em traducao/ e nenhum par X.md/X.en.md: "
                           "o build nao produziu o ingles")
        else:
            print("  (nada a conferir: sem traducao/)")
        return achados
    tab = _tabelas(os.path.join(raiz, "traducao"))
    for pt_f, en_f in pares:
        pt_txt = open(pt_f, encoding="utf-8").read()
        en_txt = open(en_f, encoding="utf-8").read()
        for nome, txt, esperado in ((os.path.basename(pt_f), pt_txt, "PT"),
                                    (os.path.basename(en_f), en_txt, "EN")):
            corpo = i18n.sem_troca_idioma(txt)
            corpo = re.sub(r"```.*?```", " ", corpo, flags=re.S)
            corpo = re.sub(r"\S*[./]\S*", " ", corpo)
            pt_n, en_n = len(PT.findall(corpo)), len(EN.findall(corpo))
            idioma = "PT" if pt_n > en_n else ("EN" if en_n > pt_n else "?")
            print("  %s %-26s %-3s (pt=%-4d en=%-4d)"
                  % ("ok " if idioma == esperado else "NAO", nome, idioma, pt_n, en_n))
            if idioma != esperado:
                achados.append("%s esta em %s, esperado %s" % (nome, idioma, esperado))
            if esperado == "EN":
                # so o britanismo NOVO: o README cita prompts de geracao de
                # imagem que ja vinham em ingles com `grey` dentro. Manter o
                # que estava citado e fidelidade, nao escolha de grafia.
                ja_tinha = set(x.lower() for x in GB.findall(pt_txt))
                for g in set(m.group(0).lower() for m in GB.finditer(corpo)):
                    if g not in ja_tinha:
                        achados.append("%s: en-GB '%s'" % (nome, g))
        for t in nao_traduzidos(pt_txt, en_txt, tab):
            achados.append("%s: %s" % (os.path.basename(en_f), t))
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controle", action="store_true")
    ap.add_argument("--pt", default=os.path.join(AQUI, "pt"))
    ap.add_argument("--en", default=os.path.join(AQUI, "en"))
    a = ap.parse_args()
    if a.controle:
        print("controle:")
        return controle()
    achados = []
    if os.path.isdir(a.pt):
        print("pt/ (esperado PT):")
        achados += conferir(a.pt, "PT")
        print("en/ (esperado EN):")
        achados += conferir(a.en, "EN")
    print("markdown:")
    achados += conferir_markdown(AQUI)
    if achados:
        print("\nREPROVADO (%d):" % len(achados))
        for x in achados:
            print("  · %s" % x)
        return 1
    print("\nok: cada pagina esta no idioma da pasta em que mora")
    return 0


if __name__ == "__main__":
    sys.exit(main())
