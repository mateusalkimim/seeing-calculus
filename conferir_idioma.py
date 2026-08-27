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
    s = re.sub(r"<(style|script)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    return re.sub(r"<[^>]+>", " ", s)


def medir(html):
    t = texto_de(html)
    return len(PT.findall(t)), len(EN.findall(t))


def nao_traduzidos(pt_html, en_html):
    """Texto de tela IDENTICO nos dois idiomas -- a sonda que nao depende de
    palavra-funcao.

    Ela existe porque a de palavras-funcao deu VERDE, duas vezes, numa pagina
    cuja navegacao inteira estava em portugues: "O par vira ponto" nao tem
    `que`, nem `nao`, nem `para`. Titulo e rotulo sao justamente o texto que
    aquela sonda nao enxerga -- e sao o texto que mais aparece na tela.

    Comparar o texto bruto nao serve (numero, simbolo e nome proprio coincidem
    de direito). Exige-se duas palavras e uma delas com 4+ letras: `pi` e
    `sin x` passam livres, `O par vira ponto` nao.
    """
    def nos(h):
        h = i18n.remover_faixa(h)
        h = re.sub(r"<(style|script|code)\b.*?</\1>", " ", h, flags=re.S | re.I)
        return set(t.strip() for t in re.split(r"<[^>]+>", h) if t.strip())
    iguais = []
    for t in nos(pt_html) & nos(en_html):
        palavras = re.findall(r"[A-Za-zÀ-ÿ]{2,}", t)
        # tres palavras, e uma delas em minuscula: nome proprio coincide de
        # direito ("— Mateus Alkimim."), e `<code>` guarda nome de arquivo.
        if (len(palavras) >= 3 and any(len(p) >= 4 for p in palavras)
                and any(p[0].islower() for p in palavras)):
            iguais.append(t)
    return sorted(iguais)


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
                for t in nao_traduzidos(open(gemeo, encoding="utf-8").read(), html):
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
    print("pt/ (esperado PT):")
    achados += conferir(a.pt, "PT")
    print("en/ (esperado EN):")
    achados += conferir(a.en, "EN")
    if achados:
        print("\nREPROVADO (%d):" % len(achados))
        for x in achados:
            print("  · %s" % x)
        return 1
    print("\nok: cada pagina esta no idioma da pasta em que mora")
    return 0


if __name__ == "__main__":
    sys.exit(main())
