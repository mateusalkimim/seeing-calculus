#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A maquinaria de idioma das fatias: achar o texto, conferir, reinjetar.

Determinista de ponta a ponta -- nao chama modelo, nao pede rede, nao pede GPU.
Quem clona este repositorio reconstroi o ingles inteiro com o que esta aqui; o
que mora fora (na casa de quem escreveu) e so a chamada ao modelo que PREENCHE
a tabela. Traducao e obra derivada; o instrumento que a aplica nao pode ser.

O `en/` NAO E COPIA. E derivado do `pt/` mais `traducao/<fatia>.en.json`, pela
razao que a casa ja aprendeu uma vez: "um gerador traduzido vira um segundo
original que diverge em silencio na primeira correcao". Copia editavel de nove
paginas e nove chances de a correcao entrar so num idioma.

A TABELA E CHAVEADA POR HASH DO ORIGINAL. Editar a fatia em portugues invalida
so os blocos mexidos, e o build REPROVA em vez de publicar pagina meio em
portugues -- que e o defeito que so aparece diante do leitor.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from html.parser import HTMLParser

# Blocos-folha. `button` e `label` entram porque num instrumento o controle E
# texto de tela; `nav` nao entra -- ela e DERIVADA (gerar_indice.py a injeta) e
# a `nav` TAMBEM entra: eu a excluira alegando que o gerador do indice a
# escreveria em ingles, e esse gerador nunca existiu -- o resultado foi uma
# pagina inglesa com a navegacao inteira em portugues, que o portao de
# palavras-funcao nao ve (titulo nao tem palavra-funcao).
# `footer`/`header`/`div` entram porque texto de tela nem sempre vem embrulhado
# num <p>: o rodape de licenca deste repositorio e texto solto dentro de
# <footer>, e por isso nunca foi extraido -- a pagina inglesa saiu com a licenca
# em portugues. A regra de FOLHA protege: um <div> que contem outro bloco nao e
# folha, entao wrapper nao vira bloco.
# `pre` sai da lista de PULAR: no traduzir_epub.py `<pre>` e codigo, aqui e
# DIAGRAMA -- a arvore de ordem de leitura do indice tem rotulos em portugues.
BLOCOS = {"p", "li", "blockquote", "figcaption", "dt", "dd", "caption",
          "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "title",
          "button", "label", "summary", "option",
          "footer", "header", "aside", "section", "article", "div", "pre"}
# Inline dentro de prosa, bloco quando solto -- ver a nota em handle_starttag.
INLINE_SOLTO = {"a", "span"}
ATRIBUTOS = ("alt", "title", "aria-label", "placeholder")
SEM_LETRA = re.compile(r"^[\W\d\s]*$")

# NOTACAO, nao traducao -- a lista e a do figuras_en.py da Hipatia. `sen` e a
# grafia PORTUGUESA do seno; em ingles o simbolo e `sin`. Trocar o simbolo nao
# e traduzir texto, e usar a convencao do idioma de chegada. Vale inclusive
# para o manifesto (`empresta: sen cos`), senao o portao audita simbolo que a
# pagina em ingles nao tem.
NOTACAO_EN = (("sen", "sin"), ("tg", "tan"), ("arcsen", "arcsin"),
              ("arctg", "arctan"), ("cotg", "cot"))

# --------------------------- extracao ---------------------------

class _Blocos(HTMLParser):
    """Blocos com offsets, INCLUSIVE o texto solto entre filhos de bloco.

    A 1a versao (herdada do traduzir_epub.py) so pegava bloco-FOLHA -- um <p>
    que contivesse outro bloco era ignorado inteiro. Num livro isso quase nunca
    acontece; numa pagina de instrumento acontece o tempo todo:

        <div>por dentro — peças da mesma camada:<details>…</details></div>

    O texto "por dentro — peças da mesma camada:" e filho direto de um <div>
    que TEM filho de bloco, e por isso nunca era extraido. A pagina inglesa
    saiu com ele em portugues e nenhum aviso apareceu -- foi a sonda de texto
    identico que o encontrou, depois de o portao de idioma dar verde.

    Agora cada bloco devolve o seu conteudo MENOS o dos filhos de bloco: a
    folha devolve tudo (nao tem filho), e o pai devolve so o que e dele.
    """

    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self._linhas = [0]
        for m in re.finditer("\n", raw):
            self._linhas.append(m.end())
        self.blocos = []       # (ini, fim) dos trechos traduziveis
        self.attrs = []        # (ini, fim, nome_do_atributo)
        self._pilha = []       # [tag, conteudo_ini, outer_ini, [filhos]]
        self._pula = 0
        self._pulado_ini = None

    def _off(self):
        ln, col = self.getpos()
        return self._linhas[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "code", "svg"):
            # Pular NAO BASTA: o bloco que contem o <svg> continua com ele
            # dentro do proprio conteudo, e devolve o grafo inteiro como um
            # bloco de texto. O contêiner pulado tem de ser RECORTADO do pai,
            # como se fosse um filho de bloco.
            # RECORTA so o que e contêiner de BLOCO. `<code>` e INLINE: ele
            # vive dentro da frase, e recorta-lo parte o elemento que o
            # envolve. `<p><b>Em <code>sen x / x</code> o zero e um buraco</b>`
            # virava dois pedacos com o <b> aberto num e fechado no outro --
            # fragmento invalido, que o modelo tentou consertar sozinho.
            # SO marca se houver bloco ABERTO para recortar. Sem isto o
            # <style> do <head> (que fecha com a pilha vazia) deixava o offset
            # GRUDADO, e o primeiro </code> dentro de um paragrafo la embaixo
            # o consumia: o recorte ia do <head> ate ali e engolia o paragrafo
            # inteiro. Ele nao saia traduzido e nao era reportado como
            # pendente -- sumia do registro, que e a pior forma de falhar.
            if not self._pula and tag != "code" and self._pilha:
                self._pulado_ini = self._off()
            self._pula += 1
        if not self._pula:
            for nome, valor in attrs:
                if nome in ATRIBUTOS and valor and not SEM_LETRA.match(valor):
                    alvo = '%s="%s"' % (nome, valor)
                    p = self.raw.find(alvo, self._off())
                    if p != -1:
                        ini = p + len(nome) + 2
                        self.attrs.append((ini, ini + len(valor), nome))
        # `a`/`span` sao inline dentro de prosa e bloco quando soltos: por-los
        # sempre na lista picaria a prosa em pedacos no meio da frase.
        eh_bloco = tag in BLOCOS or (tag in INLINE_SOLTO and not self._pilha)
        if eh_bloco and not self._pula:
            outer = self._off()
            self._pilha.append([tag, self.raw.index(">", outer) + 1, outer, []])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._pilha and self._pilha[-1][0] == tag:
            self._pilha.pop()

    def handle_endtag(self, tag):
        if tag in ("style", "script", "code", "svg"):
            self._pula = max(self._pula - 1, 0)
            if not self._pula:
                # zera SEMPRE, mesmo sem consumir: offset que sobrevive ao
                # contêiner que o gerou vira recorte fantasma mais adiante.
                if self._pilha and self._pulado_ini is not None:
                    fim = self.raw.find(">", self._off())
                    self._pilha[-1][3].append(
                        (self._pulado_ini, len(self.raw) if fim == -1 else fim + 1))
                self._pulado_ini = None
        if (tag in BLOCOS or tag in INLINE_SOLTO) and self._pilha \
                and self._pilha[-1][0] == tag:
            t, cont_ini, outer_ini, filhos = self._pilha.pop()
            cont_fim = self._off()
            outer_fim = self.raw.find(">", cont_fim)
            outer_fim = cont_fim if outer_fim == -1 else outer_fim + 1
            if self._pilha:
                self._pilha[-1][3].append((outer_ini, outer_fim))
            # o conteudo MENOS os filhos de bloco
            pos = cont_ini
            for f_ini, f_fim in sorted(filhos):
                if f_ini > pos:
                    self.blocos.append((pos, f_ini))
                pos = max(pos, f_fim)
            if cont_fim > pos:
                self.blocos.append((pos, cont_fim))


# CLASSIFICACAO DE LITERAL DE JS -- e aqui que mora o risco do instrumento.
#
# Duas heuristicas de FORMA falharam em 2026-08-27, na propria sonda, e a
# segunda falhou depois de eu ja ter consertado a primeira:
#   1. `'parar'` (rotulo de botao) caiu no regex de identificador;
#   2. `oposto`, `adjacente`, `hipotenusa`, `parabola`, `seno`, `exponencial`
#      -- rotulos DESENHADOS no canvas, vindos de tabela de dados -- caiam
#      todos, e `parabola` caia porque `\w` do Python e Unicode e engoliu o
#      acento que deveria te-la salvado.
#
# A licao e a do figuras_en.py: "string sem traducao sai desenhada em portugues
# e e reportada -- nunca silenciada". Entao o PADRAO SE INVERTE. Todo literal
# com letra e CANDIDATO A TEXTO DE TELA; so sai fora o que se pode EXCLUIR POR
# MEDIDA, nao por aparencia:
#
#   - o texto e um `id=` ou `class=` que existe no proprio HTML (o literal e um
#     seletor -- da para conferir, nao para adivinhar);
#   - e nome declarado no proprio script (`const X`, `let X`, `function X`);
#   - e cor, url, arquivo, numero com unidade, ou palavra-chave de CSS/DOM de
#     uma lista fechada.
#
# O que sobra entra na tabela como candidato. Classificar errado para MAIS custa
# uma revisao de uma linha, uma unica vez, e ela fica gravada pela chave de hash.
# Classificar errado para MENOS poe portugues na pagina em ingles, calado.
_ACENTO = re.compile(r"[áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ]")
_CODIGO = (
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),           # cor
    re.compile(r"^(rgba?|hsla?)\("),
    re.compile(r"^[.#][\w-]+$"),                  # seletor
    re.compile(r"://"),                           # url
    re.compile(r"\.(html|js|css|json|png|svg|woff2?)$", re.I),
    re.compile(r"^\d[\d\s.,:%-]*(px|em|rem|deg|s|ms|fr|vh|vw)?$"),
    re.compile(r"(sans-serif|monospace|serif)$"),
    re.compile(r"^\s*$"),
)
# lista FECHADA de palavra de CSS/DOM. Fechada de proposito: lista aberta volta
# a ser heuristica de forma, que e o que falhou duas vezes.
_PALAVRA_DOM = {
    "2d", "utf-8", "butt", "round", "square", "left", "right", "center",
    "top", "bottom", "middle", "start", "end", "alphabetic", "hanging",
    "ideographic", "source-over", "lighter", "destination-out", "copy",
    "transparent", "none", "block", "flex", "grid", "inline", "inline-block",
    "hidden", "visible", "auto", "absolute", "relative", "fixed", "sticky",
    "pointer", "default", "grab", "grabbing", "crosshair", "move",
    "click", "input", "change", "mousemove", "mousedown", "mouseup",
    "mouseleave", "mouseenter", "touchstart", "touchmove", "touchend",
    "pointerdown", "pointermove", "pointerup", "pointerleave", "wheel",
    "resize", "load", "keydown", "keyup", "scroll", "contextmenu",
    "DOMContentLoaded", "class", "id", "style", "width", "height", "div",
    "span", "button", "canvas", "img", "a", "p", "true", "false", "px",
    "bold", "normal", "italic", "checked", "disabled", "value", "beforeend",
}


def _nomes_declarados(corpo):
    return set(re.findall(r"\b(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)",
                          corpo))


def _ids_do_html(raw):
    ids = set(re.findall(r'\bid="([^"]+)"', raw))
    for c in re.findall(r'\bclass="([^"]+)"', raw):
        ids.update(c.split())
    return ids


def _e_codigo(txt, ids, nomes):
    """Exclusao POR MEDIDA. Na duvida devolve False -- e o literal vira
    candidato a texto de tela, que e o erro barato."""
    t = txt.strip()
    if len(t) < 2 or not re.search(r"[A-Za-zÀ-ÿ]", t):
        return True
    if t in ids or t in nomes or t in _PALAVRA_DOM:
        return True
    if t.lower() in _PALAVRA_DOM:
        return True
    for r in _CODIGO:
        if r.search(t):
            return True
    # identificador ASCII puro que NAO e palavra de tela conhecida: so exclui
    # se tambem for camelCase ou tiver _ / $ -- `oposto` nao e nada disso.
    if re.match(r"^[A-Za-z_$][A-Za-z0-9_$]*$", t) and re.search(r"[_$]|[a-z][A-Z]", t):
        return True
    return False


# Contexto VISIVEL, e SO O ARGUMENTO QUE E O TEXTO. A 1a versao marcava do
# marcador ate o `;`, e num `txt('a taxa nao existe aqui', x, y, '#41577a', 12,
# 'center')` isso poe a COR e o ALINHAMENTO dentro do span -- traduzir
# `'center'` quebra o desenho em silencio. O texto de uma chamada de desenho e
# o 1o argumento; o de uma propriedade de tela e o lado direito da atribuicao.
_DESENHA = re.compile(r"\b(?:fillText|strokeText|txt)\s*\(")
_ATRIBUI = re.compile(r"\.(?:textContent|innerText|innerHTML|placeholder|title|"
                      r"ariaLabel|alt)\s*=")


def _spans_visiveis(corpo):
    """Trechos em que um literal e, por construcao, texto de tela."""
    spans = []
    for m in _DESENHA.finditer(corpo):
        # do "(" ate a virgula de topo: so o 1o argumento
        prof, i = 1, m.end()
        while i < len(corpo) and prof:
            c = corpo[i]
            if c in "([{":
                prof += 1
            elif c in ")]}":
                prof -= 1
                if not prof:
                    break
            elif c == "," and prof == 1:
                break
            i += 1
        spans.append((m.end(), i))
    for m in _ATRIBUI.finditer(corpo):
        fim = len(corpo)
        for c in (";", "\n"):
            j = corpo.find(c, m.end())
            if j != -1:
                fim = min(fim, j)
        spans.append((m.end(), fim))
    return spans


def _literais_js(raw):
    """(ini, fim, texto, traduzir?) de cada literal dentro de <script>."""
    out = []
    ids = _ids_do_html(raw)
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", raw, re.S | re.I):
        base = m.start(1)
        corpo = m.group(1)
        # BLOCO GERADO NAO E CONTEUDO. O script de telefone trouxe
        # `'input[type=range]'`, `'font'` e `'itaca:redesenhar'` para a tabela
        # de traducao -- codigo meu virando pendencia de traducao em dez
        # arquivos. Quem gera se identifica; quem extrai respeita.
        if "GERADO:" in corpo[:200]:
            continue
        # tira comentarios para nao traduzir a TESE nem o cabecalho de codigo
        mascara = list(corpo)
        for c in re.finditer(r"//[^\n]*|/\*.*?\*/", corpo, re.S):
            for i in range(c.start(), c.end()):
                mascara[i] = "\x00"
        mascarado = "".join(mascara)
        spans = _spans_visiveis(mascarado)
        nomes = _nomes_declarados(mascarado)
        for lit in re.finditer(r"'([^'\\\n]*)'|\"([^\"\\\n]*)\"", mascarado):
            txt = lit.group(1) if lit.group(1) is not None else lit.group(2)
            ini = base + lit.start() + 1
            visivel = any(a <= lit.start() < b for a, b in spans)
            if not re.search(r"[A-Za-zÀ-ÿ]{2}", txt):
                traduz = False          # sem duas letras nao ha o que traduzir
            elif visivel:
                traduz = True           # contexto de tela vence a aparencia
            else:
                traduz = not _e_codigo(txt, ids, nomes)
            out.append((ini, ini + len(txt), corpo[lit.start() + 1:lit.end() - 1],
                        traduz))
    return out


# O SVG e PULADO como contêiner e lido por dentro, exatamente como o <script>.
# Sem isso o <svg> inteiro do mapa -- 1629x1906, 55 rotulos, centenas de
# coordenadas -- entrou como UM bloco e voltou do modelo truncado a 5% do
# tamanho, com 36 numeros perdidos. Um grafo nao se traduz; os ROTULOS dele
# sim, e sao 55.
def _textos_svg(raw):
    out = []
    for m in re.finditer(r"<svg\b.*?</svg>", raw, re.S | re.I):
        base = m.start()
        for t in re.finditer(r"<text\b[^>]*>(.*?)</text>", m.group(0), re.S | re.I):
            dentro = t.group(1)
            if re.search(r"[A-Za-zÀ-ÿ]{2}", re.sub(r"<[^>]+>", "", dentro)):
                ini = base + t.start(1)
                out.append((ini, ini + len(dentro), dentro, "svg"))
    return out


def chave(texto):
    return hashlib.sha1(texto.strip().encode("utf-8")).hexdigest()[:10]


def extrair(caminho):
    """[(ini, fim, texto, tipo)] -- tudo que e texto de tela, com offsets."""
    raw = remover_faixa(open(caminho, encoding="utf-8").read())
    p = _Blocos(raw)
    p.feed(raw)
    itens, descartados = [], []
    for ini, fim in p.blocos:
        cru = raw[ini:fim]
        # comentario nao e texto de tela: ninguem le, e traduzi-lo gasta GPU
        # e ainda faz o QA acusar tag alterada.
        sem_comentario = re.sub(r"<!--.*?-->", " ", cru, flags=re.S)
        limpo = re.sub(r"&[#\w]+;", "x", re.sub(r"<[^>]+>", "", sem_comentario))
        if not SEM_LETRA.match(limpo):
            itens.append((ini, fim, cru, "prosa"))
    for ini, fim, nome in p.attrs:
        itens.append((ini, fim, raw[ini:fim], "attr:" + nome))
    for ini, fim, txt, traduz in _literais_js(raw):
        if traduz:
            itens.append((ini, fim, txt, "js"))
        elif re.search(r"[A-Za-zÀ-ÿ]{3}", txt):
            descartados.append(txt)
    itens.extend(_textos_svg(raw))
    itens.sort()
    return raw, itens, descartados


# --------------------------- tabela ---------------------------
# Chaveada por hash do ORIGINAL. Guarda o `pt` junto do `en` de proposito: a
# tabela fica legivel no diff, e quem revisa ve o par sem abrir a fatia.

def caminho_tabela(caminho_html, dir_traducao=None):
    base = os.path.splitext(os.path.basename(caminho_html))[0]
    d = dir_traducao or os.path.join(os.path.dirname(caminho_html), "traducao")
    return os.path.join(d, base + ".en.json")


def ler_tabela(caminho):
    if os.path.exists(caminho):
        return json.load(open(caminho, encoding="utf-8"))
    return {"fatia": os.path.basename(caminho).split(".")[0],
            "idioma": "en-US", "blocos": {}}


def gravar_tabela(caminho, tab):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tab["atualizado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(tab, f, ensure_ascii=False, indent=1, sort_keys=True)


# --------------------------- QA ---------------------------

def _numeros(t):
    # O separador de milhar sai ANTES da contagem: o ingles escreve `2,484 px`
    # onde o portugues escreve `2484 px`, e as duas grafias sao o mesmo numero.
    # Sem isto o QA reprovava a traducao por escrever numero como se escreve em
    # ingles -- que era exatamente o que se pediu.
    limpo = re.sub(r"<[^>]+>", "", t)
    limpo = re.sub(r"(?<=\d)[,.](?=\d\d\d\b)", "", limpo)
    return sorted(re.findall(r"\d+", limpo))


# Numero POR EXTENSO conta como o numero. `2 semanas` -> `two weeks` e
# traducao correta, e `século XIX` -> `19th century` tambem: o primeiro perde o
# digito, o segundo ganha um. Comparar multiset de digitos acusava os dois.
_EXTENSO = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
            "eleven": "11", "twelve": "12", "hundred": "100",
            "thousand": "1000", "first": "1", "second": "2", "third": "3"}


def _numeros_perdidos(en, pt):
    """Numeros do original que NAO reaparecem na traducao.

    A checagem e de MAO UNICA de proposito. Numero que some e informacao
    perdida -- uma medida, uma contagem, uma versao. Numero que APARECE quase
    sempre e a lingua de chegada escrevendo o que o original dizia de outro
    jeito (algarismo romano, ordinal, extenso). Exigir igualdade nos dois
    sentidos reprovava a traducao correta.
    """
    alvo = _numeros(pt)
    if not alvo:
        return []
    tem = list(_numeros(en))
    for p, d in _EXTENSO.items():
        for _ in re.findall(r"\b%s\b" % p, en, re.I):
            tem.append(d)
    faltam = []
    for n in alvo:
        if n in tem:
            tem.remove(n)
        else:
            faltam.append(n)
    return faltam


def _tags(t):
    # A tag INTEIRA, com atributos -- multiset de NOMES deixou passar <em</em>
    # e aspas abertas em 112 blocos do Petzold (medicao 2026-07-18). Mas o
    # espaco DENTRO da tag nao e conteudo: o modelo devolve `value="0.62"  >`
    # e a tag continua sendo a mesma tag. Comparar cru acusou 13 blocos bons.
    return sorted(re.sub(r"\s+", " ", x).strip()
                  for x in re.findall(r"<[^>]+>", t))


def _refs(t):
    return sorted(re.findall(r'(?:href|src)="([^"]*)"', t))


def _simbolos(t):
    # simbolo matematico nao se traduz -- e a mesma coisa nos dois idiomas.
    return sorted(re.findall(r"[\u03b1-\u03c9\u0391-\u03a9\u221a\u00b0\u00d7\u00b7\u2212\u2192\u2260\u2264\u2265\u222b\u2211]", t))


# en-US e requisito declarado do operador -- e as duas sondas abaixo sao LISTAS
# FECHADAS porque a versao por PADRAO acusou ingles correto:
#   · `\w+ise` casou com **raise**, **otherwise**, **precise**, **exercise**;
#   · a lista de palavra-funcao portuguesa casou com **no** ("no side moves"),
#     e casaria com **do**, **da**, **a**, **e** -- homografos entre os dois
#     idiomas.
# Sonda que acusa o certo e tao ruim quanto sonda que deixa passar o errado:
# ela treina quem le a ignorar o vermelho.
_EN_GB = re.compile(r"\b(colours?|colour\w*|behaviour\w*|centres?|centred|"
                    r"metres?|litres?|favourite\w*|neighbour\w*|labour\w*|"
                    r"programme\w*|catalogue\w*|analogue\w*|defence|licence|"
                    r"practise[sd]?|grey|whilst|amongst|learnt|"
                    # O SUFIXO PRECISA SER FECHADO. `analys\w*` casou com
                    # **analysis** 19 vezes no mapa -- e `analysis` e o
                    # substantivo correto nas duas variantes; o que muda e o
                    # VERBO (analyse/analyze). `organis\w*` casaria com
                    # **organism** pelo mesmo motivo. Terminacao aberta num
                    # teste de grafia sempre acaba pegando a palavra certa.
                    r"(?:organis|analys|recognis|realis|emphasis|minimis|"
                    r"maximis|normalis|visualis|summaris|criticis|prioritis|"
                    r"standardis|specialis|generalis|characteris)"
                    r"(?:e|es|ed|ing|ation|ations)|"
                    r"modelling|labelled|travelling|cancelled)\b", re.I)

# So palavra portuguesa SEM homografo em ingles. Fora: a, e, o, do, da, no, na,
# ao, um, se, de, em, por, ou -- todas colidem.
_PT_SOBRA = re.compile(r"\b(que|n[aã]o|para|com|uma|pelo|pela|dos|das|nas|nos|"
                       r"aos|isso|aqui|onde|quando|voc[eê]|tamb[eé]m|ent[aã]o|"
                       r"j[aá]|est[aá]|s[aã]o|mais|muito|seu|sua|foi|tem|pode|"
                       r"cada|sobre|entre|porque|assim|ainda|depois|antes|"
                       r"mesmo|outro|toda?|pelos|pelas|fica|vira|olhe|veja)\b",
                       re.I)

# `ã õ ç` nao existem em palavra inglesa: acusam sozinhos, sem lista.
_ACENTO_PT = re.compile(r"[áéíóúâêôãõçÁÉÍÓÚÂÊÔÃÕÇ]")
_PT_LETRA = re.compile(r"[a-zA-Z][ãõç]|[ãõç][a-zA-Z]")
_LATEX = re.compile(r"\\\(|\\\[|\\Delta|\\frac|\\pi\\b|\\theta|\\sqrt")


# A lingua de CHEGADA. `en` e o padrao; o modulo e o mesmo nas duas direcoes,
# e quem inverte e quem chama (o README do PERFIL nasce em ingles).
PARA = "en"

# Palavra-funcao INGLESA sem homografo em portugues -- a sonda espelhada, para
# quando o alvo e o portugues. Procurar "portugues sobrando" numa traducao PARA
# o portugues seria acusar o proprio objetivo.
_EN_SOBRA = re.compile(r"\b(the|and|of|with|that|which|from|this|these|those|"
                       r"into|about|they|their|there|been|would|should|could|"
                       r"will|have|has|was|were|when|where|while|through|"
                       r"between|because|however|therefore)\b", re.I)


def sobrou_ingles(texto):
    """Duas ocorrencias, pela mesma razao da sonda espelhada: nome proprio e
    termo de oficio que se usa em ingles no Brasil (pipeline, compositing,
    open-source) aparecem uma vez e ficam."""
    achados = [m.group(1) for m in _EN_SOBRA.finditer(texto)]
    return achados[0] if len(achados) >= 2 else None


def sobrou_a_lingua_de_partida(texto):
    return sobrou_ingles(texto) if PARA == "pt" else sobrou_portugues(texto)


def sobrou_portugues(texto):
    """O que denuncia portugues num texto que devia estar em ingles.

    Uma ocorrencia solta NAO basta, e a razao apareceu em nome proprio: `hã` de
    **Maranhão** (sobrenome de autor citado) e `pã` de **Galpão** (nome de um
    asset) sao portugues que FICA -- nome nao se traduz. Tentei antes descontar
    os trechos identicos ao original, e foi pior: remover pedaco do meio emenda
    o texto e inventa fronteira de palavra (`parabola` virou `para bola`).

    O sinal certo e o que separa nome mantido de bloco nao traduzido:
      · palavra-funcao portuguesa aparece DUAS vezes ou mais -- nome proprio e
        um, texto em portugues e muitos;
      · ou um ACENTO portugues em palavra que comeca em MINUSCULA -- nome
        proprio e capitalizado (Maranhão, Galpão, Ceará), prosa nao. O ingles
        quase nao usa acento, e `parábola` solta precisava ser pega.
    """
    achados = [m.group(1) for m in _PT_SOBRA.finditer(texto)]
    if len(achados) >= 2:
        return achados[0]
    for m in re.finditer(r"\b([a-z][\wà-ÿ]*[áéíóúâêôãõçà][\wà-ÿ]*)", texto):
        return m.group(1)
    return None


def qa_bloco(en, pt, tipo):
    """(ok, [motivos]). Vazio = passou."""
    m = []
    if not en.strip():
        return False, ["vazio"]
    faltam = _numeros_perdidos(en, pt)
    if faltam:
        m.append("numero perdido: %s" % faltam)
    if _tags(en) != _tags(pt):
        m.append("tags alteradas")
    if _refs(en) != _refs(pt):
        m.append("href/src alterados")
    if _simbolos(en) != _simbolos(pt):
        m.append("simbolos matematicos alterados")
    # LaTeX INVENTADO. O modelo trocou `<code>Δf/h</code>` por `\( \Delta f/h
    # \)`. Estas paginas nao carregam MathJax por contrato -- o portao das
    # fatias barra recurso externo -- entao a formula apareceria como texto
    # cru na tela. Passou por todas as outras medidas: as tags batiam em
    # numero, o idioma media ingles, o comprimento era plausivel.
    if _LATEX.search(en) and not _LATEX.search(pt):
        m.append("LaTeX inventado (a pagina nao carrega MathJax)")
    # AS SONDAS DE IDIOMA LEEM SO O QUE O LEITOR LE. Varrer o HTML cru acusou
    # `border-left-color` como en-GB (e `colou?r` ainda casava com o `color`
    # AMERICANO, que e o certo), e acusou portugues em `class="nao"` e em
    # `href="par-vira-ponto.html"` -- nomes de classe e caminhos de arquivo NAO
    # se traduzem, e por isso mesmo nao se medem.
    # `<code>` sai junto: o conteudo dele nao se traduz (regra herdada do
    # traduzir_epub.py) e por isso nao se mede. O nome da fatia `par-vira-ponto`
    # dentro de um <code> acusou "sobrou portugues: vira" em tres blocos bons.
    visivel = re.sub(r"<code\b.*?</code>", " ", en, flags=re.S | re.I)
    visivel = re.sub(r"<[^>]+>", " ", visivel)
    # So acusa en-GB NOVO. O README do relativity-paradox-lab cita prompts de
    # geracao de imagem que ja vinham em ingles, com `grey` dentro: manter o
    # que estava citado e fidelidade, nao britanismo. Palavra que ja existia no
    # original nao e escolha do tradutor.
    gb_pt = set(x.lower() for x in _EN_GB.findall(pt))
    for g in ([] if PARA == "pt" else _EN_GB.finditer(visivel)):
        if g.group(0).lower() not in gb_pt:
            m.append("en-GB: %s" % g.group(0))
            break
    p = sobrou_a_lingua_de_partida(visivel)
    if p:
        m.append("sobrou portugues: %s" % p)
    # A razao so vale com texto suficiente: "Conjuntos" -> "Sets" da 0.44x e
    # esta certo; "nos" -> "students" da 2.67x e esta errado -- e nenhum dos
    # dois se decide pelo comprimento. Abaixo de 24 caracteres a medida e ruido.
    razao = len(en) / max(len(pt), 1)
    if len(pt) >= 24 and not (0.45 <= razao <= 2.2):
        m.append("comprimento %.2fx do original" % razao)
    return (not m), m




# --------------------------- aplicacao ---------------------------

def _manifesto_en(raw):
    """Traduz a NOTACAO do manifesto -- `empresta: sen cos` -> `sin cos`.

    So no manifesto, e so com fronteira de palavra. Aplicar a lista solta no
    texto inteiro corromperia palavra inglesa que contem a sequencia (`sense`,
    `present`): a troca de simbolo e cirurgica por natureza.
    """
    m = re.search(r"<!--\s*fatia:.*?-->", raw, re.S)
    if not m:
        return raw
    linha = m.group(0)
    novo = linha
    for pt, en in NOTACAO_EN:
        novo = re.sub(r"(?<![\w])%s(?![\w])" % re.escape(pt), en, novo)
    return raw[:m.start()] + novo + raw[m.end():]


def _escapar_js(en, delim):
    """Escapa o delimitador dentro de um literal de JS.

    O ingles vive de apostrofo -- `don't`, `it's`, `doesn't` -- e as strings
    destas fatias sao delimitadas por aspa simples. `nota:'rate zero — the
    derivative doesn't see constant'` fecha a string no `doesn` e o resto vira
    sintaxe invalida: a pagina abre e o instrumento nao roda. Foi o portao [8]
    (node --check) que pegou, e nenhuma sonda de idioma pegaria -- o texto esta
    em ingles perfeito.
    """
    if delim not in ("'", '"'):
        delim = "'"
    en = en.replace("\\", "\\\\")
    en = en.replace(delim, "\\" + delim)
    return en.replace("\n", " ")


def _codigo_en(raw):
    """Notacao dentro de <code>: `sen(x)/x` vira `sin(x)/x`.

    O conteudo de <code> nao se TRADUZ -- mas notacao nao e traducao (§8), e
    uma pagina em ingles exibindo `sen(x)` esta com a grafia errada, nao com um
    termo estrangeiro. Fronteira de palavra, so dentro do <code>.
    """
    def troca(m):
        dentro = m.group(1)
        for pt, en in NOTACAO_EN:
            dentro = re.sub(r"(?<![\w])%s(?![\w])" % re.escape(pt), en, dentro)
        return m.group(0).replace(m.group(1), dentro)
    return re.sub(r"<code\b[^>]*>(.*?)</code>", troca, raw, flags=re.S | re.I)


def aplicar(raw, tabela):
    """(html_en, pendentes). Reinjeta por offset, de tras para frente.

    A faixa de idioma sai antes e volta depois (o build a repoe): ela e
    derivada, e deixa-la no texto faria a propria faixa virar bloco de tabela.

    De tras para frente porque offset calculado no original so continua valido
    enquanto nada antes dele mudou de tamanho -- e a traducao quase sempre muda.
    """
    raw = remover_faixa(raw)
    itens = extrair_de(raw)
    pendentes = []
    for ini, fim, texto, tipo in sorted(itens, reverse=True):
        b = tabela.get("blocos", {}).get(chave(texto))
        en = b.get("en") if b else None
        # Bloco REPROVADO no QA nao se publica. Ele tem traducao gravada -- e
        # por isso que sem esta linha ele passaria: `en` existe, e o build
        # nunca perguntaria se ela presta. `qa` guarda os motivos; enquanto
        # estiverem la, o bloco vale como pendente e o build reprova.
        if b and b.get("qa") not in (None, "ok"):
            en = None
        if en and tipo == "js":
            en = _escapar_js(en, raw[ini - 1] if ini else "'")
        if not en:
            # §7: bloco que JA mede ingles atravessa intocado e nao e pendencia.
            # E o caso da citacao copiada da fonte -- retraduzi-la fabricaria o
            # original, e o conferidor de citacoes deixaria de bater.
            if ja_na_lingua_de_chegada(texto):
                continue
            motivo = tipo
            if b and b.get("qa") not in (None, "ok"):
                motivo = "%s · QA: %s" % (tipo, "; ".join(b["qa"])[:60])
            pendentes.append((chave(texto), texto, motivo))
            continue
        raw = raw[:ini] + en + raw[fim:]
    raw = _codigo_en(raw)
    raw = _manifesto_en(raw)
    raw = re.sub(r'(<html[^>]*\slang=")[^"]*(")', r"\1en\2", raw, count=1)
    return raw, pendentes


def extrair_de(raw):
    """Como `extrair`, mas a partir do texto ja lido."""
    raw = remover_faixa(raw)
    p = _Blocos(raw)
    p.feed(raw)
    itens = []
    for ini, fim in p.blocos:
        cru = raw[ini:fim]
        # comentario nao e texto de tela: ninguem le, e traduzi-lo gasta GPU
        # e ainda faz o QA acusar tag alterada.
        sem_comentario = re.sub(r"<!--.*?-->", " ", cru, flags=re.S)
        limpo = re.sub(r"&[#\w]+;", "x", re.sub(r"<[^>]+>", "", sem_comentario))
        if not SEM_LETRA.match(limpo):
            itens.append((ini, fim, cru, "prosa"))
    for ini, fim, nome in p.attrs:
        itens.append((ini, fim, raw[ini:fim], "attr:" + nome))
    for ini, fim, txt, traduz in _literais_js(raw):
        if traduz:
            itens.append((ini, fim, txt, "js"))
    itens.extend(_textos_svg(raw))
    return sorted(itens)


# --------------------------- a faixa de idioma ---------------------------
# Pagina funda recebe FAIXA, nao salto. Quem recebeu o link de uma fatia
# especifica quer aquela fatia -- e buscador jogado de um idioma para outro
# indexa errado. A faixa nao busca nada na rede (o portao [7] das fatias barra
# recurso externo, e com razao: elas abrem offline por contrato).

MARCA_FAIXA = "<!-- faixa-idioma: gerada por i18n.py, nao editar -->"

_FAIXA = MARCA_FAIXA + """
<div id="faixa-idioma" style="display:none;position:fixed;top:0;left:0;right:0;
 z-index:99;background:#c9a266;color:#0a1424;font:13px/1.4 Inter,system-ui,
 sans-serif;padding:7px 12px;gap:10px;justify-content:center;
 align-items:center">
<span>%(convite)s</span>
<a href="%(alvo)s" style="color:#0a1424;font-weight:600">%(acao)s</a>
<button onclick="this.parentNode.style.display='none'" aria-label="%(fechar)s"
 style="background:none;border:0;color:#0a1424;cursor:pointer;font-size:15px;padding:2px 6px;line-height:1">&times;</button>
</div>
<script>%(marca)s
(function(){try{
  var f=localStorage.getItem('sc-lang');
  if(f==='%(este)s')return;
  var L=(navigator.languages&&navigator.languages.length)?navigator.languages
        :[navigator.language||''];
  var pt=false; for(var i=0;i<L.length;i++){ if(/^pt/i.test(L[i])){pt=true;break;} }
  if(f!=='%(outro)s' && pt!==%(quer)s)return;
  document.getElementById('faixa-idioma').style.display='flex';
}catch(e){}})();
document.querySelector('#faixa-idioma a').addEventListener('click',function(){
  try{localStorage.setItem('sc-lang','%(outro)s');}catch(e){}
});
</script>"""

_TEXTOS = {
    "pt": {"convite": "This page is in Portuguese.", "acao": "Read in English",
           "fechar": "close", "alvo": "../en/%s", "este": "pt", "outro": "en",
           "quer": "false"},
    "en": {"convite": "Esta pagina esta em ingles.", "acao": "Ler em portugues",
           "fechar": "fechar", "alvo": "../pt/%s", "este": "en", "outro": "pt",
           "quer": "true"},
}


def injetar_faixa(raw, idioma, arquivo):
    """Poe (ou repoe) a faixa logo depois do <body>. Idempotente."""
    raw = remover_faixa(raw)
    t = dict(_TEXTOS[idioma])
    t["alvo"] = t["alvo"] % arquivo
    t["marca"] = ""
    bloco = _FAIXA % t
    # ANTES de </body>, nao depois de <body>: posta no topo, ela punha o
    # <script> dela na frente do script da fatia, e o portao [10] procura o
    # marcador `TESE DESTA FATIA` no topo do PRIMEIRO <script> -- as nove
    # fatias passaram a avisar que perderam a tese que nunca perderam.
    # A faixa e `position:fixed`; onde ela mora no DOM nao muda onde ela aparece.
    m = re.search(r"</body\s*>", raw, re.I)
    if m:
        return raw[:m.start()] + bloco + "\n" + raw[m.start():]
    return raw + "\n" + bloco


def remover_faixa(raw):
    i = raw.find(MARCA_FAIXA)
    if i == -1:
        return raw
    fim = raw.find("</script>", i)
    if fim == -1:
        return raw
    return raw[:i].rstrip("\n") + raw[fim + len("</script>"):]


# --------------------------- o que JA esta em ingles ---------------------------
# §7 da norma de traducao: citacao nao entra no tradutor. No abstraction-ladder
# os trechos de Petzold e SICP sao o INGLES ORIGINAL, conferidos caractere a
# caractere contra o acervo -- retraduzir um deles fabrica a fonte e quebra o
# `conferir_citacoes.py`. Aqui isso nao e regra de nome de arquivo nem lista a
# manter: e MEDIDA no proprio bloco, pelas mesmas palavras-funcao do portao de
# idioma. Bloco que ja mede ingles atravessa intocado.

_F_PT = re.compile(r"\b(que|n[aã]o|para|com|uma|pelo|pela|dos|das|nas|nos|"
                   r"ao|aos|isso|onde|quando|s[aã]o|est[aá]|do|da|de|em|"
                   r"por|se|mais|como)\b", re.I)
_F_EN = re.compile(r"\b(the|and|of|with|that|for|from|which|when|where|"
                   r"this|these|into|about|is|are|it|as|to|in|be|can)\b", re.I)


def ja_na_lingua_de_chegada(texto):
    """O bloco ja esta na lingua para a qual estamos traduzindo?

    O desvio da §7 (citacao atravessa intocada) tem de conhecer a DIRECAO. Ao
    traduzir para o portugues, "ja esta em ingles" e o oposto de um desvio: e a
    descricao do trabalho a fazer. Sem esta funcao, 12 dos 25 blocos do README
    do perfil seriam marcados como "atravessam intocados" -- metade do perfil
    ficaria em ingles, e o build diria que esta completo.
    """
    if PARA == "pt":
        limpo = re.sub(r"<[^>]+>", " ", texto)
        pt, en = len(_F_PT.findall(limpo)), len(_F_EN.findall(limpo))
        return pt >= 3 and pt >= 2 * max(en, 1)
    return ja_em_ingles(texto)


def ja_em_ingles(texto):
    """True so quando o bloco mede ingles COM FOLGA.

    O empate nao decide nada: rotulo curto ("o arco") mede pt=1 en=0 e frase
    curta em ingles mede pt=0 en=1, e nos dois casos a margem e ruido. Exigir
    tres ocorrencias e o dobro do outro idioma mantem a passagem livre so para
    o que e inequivocamente ingles -- que e o caso de uma citacao de livro.
    """
    limpo = re.sub(r"<[^>]+>", " ", texto)
    pt, en = len(_F_PT.findall(limpo)), len(_F_EN.findall(limpo))
    return en >= 3 and en >= 2 * max(pt, 1)


# --------------------------- markdown ---------------------------
# O README e a porta de entrada do repositorio, e no GitHub ele e a primeira
# coisa que qualquer pessoa le. Nao e HTML: o separador de blocos aqui e a
# linha em branco, e a cerca de codigo tem de ficar de fora.
#
# A cerca de codigo guarda ARTE ASCII neste acervo (a arvore de ordem de
# leitura), e arte ASCII se realinha a mao -- traduzir os rotulos desloca as
# caixas de desenho. Ela sai da traducao e e RELATADA, nunca silenciada.

_CERCA = re.compile(r"^(```|~~~)", re.M)


def blocos_md(raw):
    """[(ini, fim, texto)] de cada bloco de markdown fora das cercas."""
    # marca as faixas de cerca para pular
    cercas, aberta = [], None
    for m in _CERCA.finditer(raw):
        if aberta is None:
            aberta = m.start()
        else:
            fim = raw.find("\n", m.end())
            cercas.append((aberta, len(raw) if fim == -1 else fim + 1))
            aberta = None
    if aberta is not None:
        cercas.append((aberta, len(raw)))

    def em_cerca(p):
        return any(a <= p < b for a, b in cercas)

    out, pos = [], 0
    for m in re.finditer(r"\n[ \t]*\n", raw):
        ini, fim = pos, m.start()
        pos = m.end()
        if fim > ini and not em_cerca(ini):
            t = raw[ini:fim]
            if re.search(r"[A-Za-zÀ-ÿ]{2}", t):
                out.append((ini, fim, t))
    if pos < len(raw) and not em_cerca(pos):
        t = raw[pos:]
        if re.search(r"[A-Za-zÀ-ÿ]{2}", t):
            out.append((pos, len(raw), t))
    return out, cercas


def _links_md(t):
    return sorted(re.findall(r"\]\(([^)]*)\)", t))


def reparar_links_md(en, pt):
    """Devolve ao link o alvo do original.

    O modelo traduziu `](docs/INSTALACAO.md)` para `](docs/INSTALLATION.md)` --
    um arquivo que nao existe. Caminho e URL nao sao texto: sao endereco, e
    endereco traduzido e link quebrado. Quando a CONTAGEM bate, o conserto e
    posicional e seguro; quando nao bate, isto nao repara nada e o QA reprova.
    """
    alvos = re.findall(r"\]\(([^)]*)\)", pt)
    if len(alvos) != len(re.findall(r"\]\(([^)]*)\)", en)):
        return en
    it = iter(alvos)
    return re.sub(r"(\]\()([^)]*)(\))",
                  lambda m: m.group(1) + next(it) + m.group(3), en)


def qa_md(en, pt):
    """(ok, motivos). Como o qa_bloco, com o alvo do link no lugar da tag."""
    m = []
    if not en.strip():
        return False, ["vazio"]
    faltam = _numeros_perdidos(en, pt)
    if faltam:
        m.append("numero perdido: %s" % faltam)
    if _links_md(en) != _links_md(pt):
        m.append("alvo de link alterado")
    if _simbolos(en) != _simbolos(pt):
        m.append("simbolos matematicos alterados")
    # A sonda de idioma le so PROSA: alvo de link e trecho em crase sao
    # endereco e codigo. `github.com` acusava "sobrou portugues: com" e
    # `par-vira-ponto` acusava "vira" -- vermelho falso em bloco correto.
    prosa = re.sub(r"\]\([^)]*\)", "]", en)
    prosa = re.sub(r"`[^`]*`", " ", prosa)
    prosa = re.sub(r"https?://\S+|\S*[./_]\S*", " ", prosa)
    gb_pt = set(x.lower() for x in _EN_GB.findall(pt))
    for g in ([] if PARA == "pt" else _EN_GB.finditer(prosa)):
        if g.group(0).lower() not in gb_pt:
            m.append("en-GB: %s" % g.group(0))
            break
    p = sobrou_a_lingua_de_partida(prosa)
    if p:
        m.append("sobrou portugues: %s" % p)
    razao = len(en) / max(len(pt), 1)
    if len(pt) >= 24 and not (0.45 <= razao <= 2.2):
        m.append("comprimento %.2fx do original" % razao)
    return (not m), m


def cercas_traduziveis(raw):
    """[(ini, fim, conteudo)] das cercas que tem texto humano em portugues.

    Cerca de codigo nao se traduz -- mas o COMENTARIO dentro dela e texto que
    alguem le, e a coluna de descricao de uma arvore de arquivos tambem. Deixar
    a cerca inteira de fora punha `# o portão, com controle negativo` numa
    pagina em ingles. O que fica de fora e o comando, o caminho e o simbolo.
    """
    _, cercas = blocos_md(raw)
    out = []
    for a, b in cercas:
        corpo = raw[a:b]
        miolo = re.sub(r"^(```|~~~)[^\n]*\n", "", corpo)
        miolo = re.sub(r"\n?(```|~~~)\s*$", "", miolo)
        # URL fora antes do teste: `github.com` casa com a palavra `com`, e a
        # cerca do `git clone` entrava como se tivesse portugues dentro.
        # mesma sonda do QA, e pelo mesmo motivo: `par-vira-ponto.html` casa
        # com a palavra `vira` e `github.com` com `com`. Nome de arquivo nao e
        # prosa, e uma ocorrencia solta nao denuncia idioma.
        prosa = re.sub(r"https?://\S+|\S*[./_]\S*", " ", miolo)
        if sobrou_portugues(prosa):
            ini = a + (len(corpo) - len(miolo) - len(corpo) + len(corpo))
            ini = raw.index(miolo, a)
            out.append((ini, ini + len(miolo), miolo))
    return out


def aplicar_md(raw, tabela):
    """(markdown_en, pendentes, cercas_nao_traduzidas)."""
    blocos, cercas = blocos_md(raw)
    pendentes = []
    # as cercas primeiro, de tras para frente (offsets do texto original)
    for ini, fim, miolo in sorted(cercas_traduziveis(raw), reverse=True):
        b = tabela.get("blocos", {}).get(chave(miolo))
        en = b.get("en") if b else None
        if b and b.get("qa") not in (None, "ok"):
            en = None
        if en:
            raw = raw[:ini] + en + raw[fim:]
            blocos, cercas = blocos_md(raw)
        else:
            pendentes.append((chave(miolo), miolo, "cerca"))
    for ini, fim, texto in sorted(blocos, reverse=True):
        b = tabela.get("blocos", {}).get(chave(texto))
        en = b.get("en") if b else None
        if b and b.get("qa") not in (None, "ok"):
            en = None
        if not en:
            if ja_na_lingua_de_chegada(texto):
                continue
            pendentes.append((chave(texto), texto, "md"))
            continue
        raw = raw[:ini] + en + raw[fim:]
    return raw, pendentes, len(cercas)


# A troca de idioma do README e uma LINHA no topo, nao uma pagina de porta: no
# GitHub o README aparece embutido, sem HTML nosso e sem JavaScript nenhum, e
# um link e a unica coisa que funciona ali.

# INGLES PRIMEIRO, PORTUGUES A UM CLIQUE. Decisao do operador em 2026-08-27:
# o GitHub renderiza `README.md` e e o que qualquer visitante ve -- entao e ali
# que mora o INGLES, que abre o mundo. O portugues nao fica de fora: ele fica a
# um clique, no `README.pt-BR.md`, para quem le melhor na propria lingua.
#
# O que NAO muda: o portugues continua sendo a FONTE que se escreve, e o ingles
# continua sendo derivado. O que mudou e qual dos dois ocupa o nome que o
# GitHub abre sozinho.
# A TROCA DE IDIOMA E DECLARADA, VISIVEL E INCONFUNDIVEL -- exigencia do
# operador, e uma linha em italico nao era isso. Aqui ela e um `> [!NOTE]`, o
# alerta nativo do GitHub: renderiza como caixa com borda colorida e icone, e
# nao depende de imagem externa nenhuma (badge de terceiro some quando o proxy
# do GitHub falha, e ai o "botao" vira texto alternativo).
# Onde o alerta nao e suportado ele degrada para citacao em negrito -- ainda
# grande, ainda obvio, ainda clicavel.
MARCA_MD = "<!-- idioma: linha gerada por i18n.py -->"
_LINHA_MD = {
    # a pagina em PORTUGUES oferece o ingles, na lingua de quem vai clicar
    "pt": MARCA_MD + "\n> [!NOTE]\n> ### 🌍 **[Read this page in English →](%s)**\n",
    # a pagina em INGLES oferece o portugues, em portugues
    "en": MARCA_MD + "\n> [!NOTE]\n> ### 🇧🇷 **[Leia esta página em português →](%s)**\n",
}

# SO O README troca de nome. Os outros documentos seguem em `<nome>.en.md`:
# o pedido foi sobre a pagina que o GitHub abre sozinha, e `docs/INSTALACAO.md`
# ainda por cima e exigido por esse nome pelo protocolo de distribuicao.
NOME_EN = {"README.pt-BR.md": "README.md"}


def nome_em_ingles(caminho):
    base = os.path.basename(caminho)
    return NOME_EN.get(base, base[:-3] + ".en.md")


def sem_troca_idioma(raw):
    """Tira o bloco de troca de idioma: da marca ate a linha em branco.

    Contar LINHAS era fragil -- o bloco tinha duas, virou tres ao virar
    callout, e um bloco de tres removido pela metade se acumularia a cada
    build. A fronteira e a linha em branco, que nao muda com o desenho.
    """
    if MARCA_MD not in raw:
        return raw
    i = raw.index(MARCA_MD)
    m = re.search(r"\n[ \t]*\n", raw[i:])
    fim = i + m.end() if m else len(raw)
    return raw[:i] + raw[fim:]


def troca_idioma_md(raw, idioma, vizinho=None):
    padrao = "README.en.md" if idioma == "pt" else "README.md"
    return (_LINHA_MD[idioma] % (vizinho or padrao)
            + "\n" + sem_troca_idioma(raw).lstrip("\n"))


def limpar_cerca(en):
    """Tira a cerca de fechamento que o modelo devolve junto.

    Pediu-se o MIOLO da cerca e ele devolve o miolo mais o ``` do fim -- duas
    vezes em dois repositorios. Reinjetado assim, o markdown ganha uma cerca
    aberta e o resto do documento vira bloco de codigo. E mecanico: se a
    ultima linha e so a cerca, ela sai.
    """
    linhas = en.split("\n")
    while linhas and re.fullmatch(r"\s*(```|~~~)\s*", linhas[-1] or ""):
        linhas.pop()
    return "\n".join(linhas)


def qa_cerca(en, pt):
    """QA de cerca: o que NAO e texto humano tem de sair identico.

    Compara as linhas ignorando o que vem depois de `#` (o comentario) e a
    coluna de descricao. Se um comando mudou, reprova -- comando traduzido e
    comando quebrado, e ninguem descobre lendo.
    """
    m = []
    if not en.strip():
        return False, ["vazio"]
    if len(en.split("\n")) != len(pt.split("\n")):
        m.append("numero de linhas mudou: %d -> %d"
                 % (len(pt.split("\n")), len(en.split("\n"))))
    # ARTE ASCII nao tem comando: toda linha e texto humano, e a checagem de
    # "o que nao e comentario tem de sair identico" reprovaria justamente a
    # traducao correta. Diagrama se reconhece pelas caixas de desenho.
    diagrama = bool(re.search(r"[┌┐└┘├┤┬┴─│→]", pt))
    for a, b in ([] if diagrama else zip(pt.split("\n"), en.split("\n"))):
        # O que esta entre <> num comando e PLACEHOLDER -- descricao do que
        # o leitor deve pôr ali, nao literal a digitar. `<arquivo .env fora do
        # repo>` tem de virar `<.env file outside the repo>`; compara-lo como
        # comando reprovava justamente a traducao que se queria.
        ca = re.sub(r"<[^>]*>", "<>", a.split("#")[0]).strip()
        cb = re.sub(r"<[^>]*>", "<>", b.split("#")[0]).strip()
        # a coluna de descricao comeca depois de 2+ espacos; fora dela, igual
        ca, cb = re.split(r"\s{2,}", ca)[0], re.split(r"\s{2,}", cb)[0]
        if ca != cb:
            m.append("comando/caminho alterado: %r -> %r" % (ca[:34], cb[:34]))
            break
    if _EN_GB.search(en):
        m.append("en-GB")
    # nome de arquivo e caminho saem antes do teste: `par-vira-ponto.html`
    # casava com a palavra `vira`, e `github.com` com `com`. Endereco nao e
    # prosa, e medi-lo so produz vermelho falso.
    prosa = re.sub(r"https?://\S+|\S*[./_]\S*", " ", en)
    if sobrou_portugues(prosa):
        m.append("sobrou portugues: %s" % sobrou_portugues(prosa))
    return (not m), m
