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
    """Blocos-folha com offsets no texto cru (herdado do traduzir_epub.py)."""

    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self._linhas = [0]
        for m in re.finditer("\n", raw):
            self._linhas.append(m.end())
        self.blocos = []
        self.attrs = []          # (ini, fim, nome_do_atributo)
        self._pilha = []
        self._pula = 0
        self._em_nav = 0

    def _off(self):
        ln, col = self.getpos()
        return self._linhas[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "code"):
            self._pula += 1
        if not self._pula and not self._em_nav:
            for nome, valor in attrs:
                if nome in ATRIBUTOS and valor and not SEM_LETRA.match(valor):
                    alvo = '%s="%s"' % (nome, valor)
                    p = self.raw.find(alvo, self._off())
                    if p != -1:
                        ini = p + len(nome) + 2
                        self.attrs.append((ini, ini + len(valor), nome))
        # `a` e `span` sao INLINE dentro de prosa e BLOCO quando estao soltos.
        # A nav e feita de ancoras soltas, e como `a` nao estava na lista o
        # texto delas nunca foi extraido: a pagina inglesa saiu com a navegacao
        # em portugues e o portao de palavras-funcao deu VERDE, porque titulo
        # ("O par vira ponto") nao tem palavra-funcao. Por-los na lista sem esta
        # condicao seria pior: um <a> dentro de um <p> faria o paragrafo deixar
        # de ser folha, e a prosa sairia picada em pedacos.
        eh_bloco = tag in BLOCOS or (tag in INLINE_SOLTO and not self._pilha)
        if eh_bloco and not self._pula and not self._em_nav:
            ini = self.raw.index(">", self._off()) + 1
            if self._pilha:
                self._pilha[-1][2] = True
            self._pilha.append([tag, ini, False])

    def handle_endtag(self, tag):
        if tag in ("style", "script", "code"):
            self._pula = max(self._pula - 1, 0)
        if (tag in BLOCOS or tag in INLINE_SOLTO) and self._pilha \
                and self._pilha[-1][0] == tag:
            t, ini, tem_filho = self._pilha.pop()
            if not tem_filho:
                self.blocos.append((ini, self._off()))


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
        limpo = re.sub(r"&[#\w]+;", "x", re.sub(r"<[^>]+>", "", cru))
        if not SEM_LETRA.match(limpo):
            itens.append((ini, fim, cru, "prosa"))
    for ini, fim, nome in p.attrs:
        itens.append((ini, fim, raw[ini:fim], "attr:" + nome))
    for ini, fim, txt, traduz in _literais_js(raw):
        if traduz:
            itens.append((ini, fim, txt, "js"))
        elif re.search(r"[A-Za-zÀ-ÿ]{3}", txt):
            descartados.append(txt)
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
    return sorted(re.findall(r"\d+", re.sub(r"<[^>]+>", "", t)))


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
                    r"practise[sd]?|grey|whilst|amongst|towards|learnt|"
                    r"organis\w*|analys\w*|recognis\w*|realis\w*|emphasis[ei]\w*|"
                    r"minimis\w*|maximis\w*|normalis\w*|visualis\w*|summaris\w*|"
                    r"criticis\w*|prioritis\w*|standardis\w*|specialis\w*|"
                    r"generalis\w*|characteris\w*|modelling|labelled|"
                    r"travelling|cancelled)\b", re.I)

# So palavra portuguesa SEM homografo em ingles. Fora: a, e, o, do, da, no, na,
# ao, um, se, de, em, por, ou -- todas colidem.
_PT_SOBRA = re.compile(r"\b(que|n[aã]o|para|com|uma|pelo|pela|dos|das|nas|nos|"
                       r"aos|isso|aqui|onde|quando|voc[eê]|tamb[eé]m|ent[aã]o|"
                       r"j[aá]|est[aá]|s[aã]o|mais|muito|seu|sua|foi|tem|pode|"
                       r"cada|sobre|entre|porque|assim|ainda|depois|antes|"
                       r"mesmo|outro|toda?|pelos|pelas|fica|vira|olhe|veja)\b",
                       re.I)

# `ã õ ç` nao existem em palavra inglesa: acusam sozinhos, sem lista.
_PT_LETRA = re.compile(r"[a-zA-Z][ãõç]|[ãõç][a-zA-Z]")


def qa_bloco(en, pt, tipo):
    """(ok, [motivos]). Vazio = passou."""
    m = []
    if not en.strip():
        return False, ["vazio"]
    if _numeros(en) != _numeros(pt):
        m.append("numeros: %s != %s" % (_numeros(pt), _numeros(en)))
    if _tags(en) != _tags(pt):
        m.append("tags alteradas")
    if _refs(en) != _refs(pt):
        m.append("href/src alterados")
    if _simbolos(en) != _simbolos(pt):
        m.append("simbolos matematicos alterados")
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
    g = _EN_GB.search(visivel)
    if g:
        m.append("en-GB: %s" % g.group(0))
    p = _PT_SOBRA.search(visivel) or _PT_LETRA.search(visivel)
    if p:
        m.append("sobrou portugues: %s" % p.group(0))
    razao = len(en) / max(len(pt), 1)
    if not (0.45 <= razao <= 2.2):
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
            if ja_em_ingles(texto):
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
        limpo = re.sub(r"&[#\w]+;", "x", re.sub(r"<[^>]+>", "", cru))
        if not SEM_LETRA.match(limpo):
            itens.append((ini, fim, cru, "prosa"))
    for ini, fim, nome in p.attrs:
        itens.append((ini, fim, raw[ini:fim], "attr:" + nome))
    for ini, fim, txt, traduz in _literais_js(raw):
        if traduz:
            itens.append((ini, fim, txt, "js"))
    return sorted(itens)


# --------------------------- a faixa de idioma ---------------------------
# Pagina funda recebe FAIXA, nao salto. Quem recebeu o link de uma fatia
# especifica quer aquela fatia -- e buscador jogado de um idioma para outro
# indexa errado. A faixa nao busca nada na rede (o portao [7] das fatias barra
# recurso externo, e com razao: elas abrem offline por contrato).

MARCA_FAIXA = "<!-- faixa-idioma: gerada por i18n.py, nao editar -->"

_FAIXA = MARCA_FAIXA + """
<div id="faixa-idioma" hidden style="position:fixed;top:0;left:0;right:0;
 z-index:99;background:#c9a266;color:#0a1424;font:13px/1.4 Inter,system-ui,
 sans-serif;padding:7px 12px;display:flex;gap:10px;justify-content:center;
 align-items:center">
<span>%(convite)s</span>
<a href="%(alvo)s" style="color:#0a1424;font-weight:600">%(acao)s</a>
<button onclick="this.parentNode.hidden=true" aria-label="%(fechar)s"
 style="background:none;border:0;color:#0a1424;cursor:pointer;font-size:15px">&times;</button>
</div>
<script>%(marca)s
(function(){try{
  var f=localStorage.getItem('sc-lang');
  if(f==='%(este)s')return;
  var L=(navigator.languages&&navigator.languages.length)?navigator.languages
        :[navigator.language||''];
  var pt=false; for(var i=0;i<L.length;i++){ if(/^pt/i.test(L[i])){pt=true;break;} }
  if(f!=='%(outro)s' && pt!==%(quer)s)return;
  document.getElementById('faixa-idioma').hidden=false;
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
