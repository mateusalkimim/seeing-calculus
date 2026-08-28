#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o index.html a partir das PRÓPRIAS fatias.

Nada aqui é digitado à mão duas vezes. A ordem, o nome, a descrição e os
símbolos de cada fatia saem do arquivo dela — do manifesto
`<!-- fatia: … | ordem: N | declara: … | empresta: … -->`, do `<title>` e do
parágrafo de chamada. Quem edita uma fatia edita o índice junto, sem saber.

É o mesmo princípio do `gerar_mapa.py` do math-prerequisite-map: a página
publicada é DERIVADA, e editar o HTML gerado é o defeito, não o atalho.

Roda:  python3 gerar_indice.py
"""
import html
import os
import re
import sys

_RAIZ = os.path.dirname(os.path.abspath(__file__))
# As fatias passaram a morar em `pt/` quando o sitio virou bilingue (a porta e
# os stubs de URL antiga ficaram na raiz). O gerador segue a fonte: se `pt/`
# existe, e ali que ele le e escreve. Sem isso ele geraria um indice vazio na
# raiz e nada acusaria -- diretorio sem fatia nao e erro, e so um diretorio.
AQUI = os.path.join(_RAIZ, "pt") if os.path.isdir(os.path.join(_RAIZ, "pt")) else _RAIZ
SAIDA = os.path.join(AQUI, "index.html")

MANIFESTO = re.compile(
    r"<!--\s*fatia:\s*(?P<nome>[\w-]+)\s*\|\s*ordem:\s*(?P<ordem>\d+)"
    r"\s*\|\s*declara:\s*(?P<declara>[^|]*)"
    r"(?:\|\s*empresta:\s*(?P<empresta>[^-]*))?-->")

# A ORDEM DE LEITURA É UMA FILA; a DEPENDÊNCIA é que tem dois ramos.
# Corrigido em 2026-08-27: a taxa estava em 2º e era a única fatia com dívida
# declarada — ela gastava "tangente", secante, área e duas funções
# trigonométricas antes de qualquer uma ser definida. Desceu para 7º e a dívida
# zerou. Ela continua NÃO DEPENDENDO da trigonometria (inclinação existe sem
# ângulo); o que ela empresta é VOCABULÁRIO, não lógica — e por isso a palavra
# "tangente" precisa estar desambiguada antes.
CORRENTE = {
    "par-vira-ponto": "raiz",
    "o-angulo": "medida", "o-triangulo": "medida", "a-distancia": "medida",
    "o-circulo": "medida", "desenrolamento": "medida",
    "taxa": "função", "o-encontro": "encontro",
}
COR = {"raiz": "#c9a266", "função": "#78c4ff", "medida": "#e8654f", "encontro": "#6fbf6a"}



POR_EXTENSO = {6: 'seis', 7: 'sete', 8: 'oito', 9: 'nove', 10: 'dez',
               11: 'onze', 12: 'doze'}

def ler_fatias():
    fatias = []
    for arq in sorted(os.listdir(AQUI)):
        if not arq.endswith(".html") or arq == "index.html":
            continue
        fonte = open(os.path.join(AQUI, arq), encoding="utf-8").read()
        m = MANIFESTO.search(fonte)
        if not m:
            print(f"  ⚠ {arq}: sem manifesto — fora do índice", file=sys.stderr)
            continue
        t = re.search(r"<title>(.*?)</title>", fonte, re.S)
        sub = re.search(r'<p class="sub">(.*?)</p>', fonte, re.S)
        limpo = lambda x: " ".join(html.unescape(re.sub(r"<[^>]+>", "", x)).split())
        titulo = limpo(t.group(1)) if t else arq
        # o título traz "Nome — explicação"; separo nos dois
        nome, _, expl = titulo.partition("—")
        chamada = limpo(sub.group(1)) if sub else ""
        # a primeira frase da chamada basta para o índice
        primeira = re.split(r"(?<=[.!?])\s+", chamada)[0] if chamada else ""
        fatias.append({
            "arquivo": arq, "chave": m.group("nome"), "ordem": int(m.group("ordem")),
            "nome": nome.strip(), "explica": expl.strip(), "chamada": primeira,
        })
    fatias.sort(key=lambda f: f["ordem"])
    return fatias


TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ver o cálculo — {quantas} instrumentos, em ordem</title>
<style>
  :root{{ --fundo:#0a1424; --creme:#e8e2d6; --fraco:#5b6b86; --ouro:#c9a266;
         --cartao:#0d1c30; --borda:#1e3050; }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--fundo);color:var(--creme);
       font-family:Inter,-apple-system,"Segoe UI",system-ui,sans-serif;
       padding:44px 26px 60px;line-height:1.6}}
  .caixa{{max-width:820px;margin:0 auto}}
  h1{{font-family:Cormorant,Georgia,"Times New Roman",serif;font-weight:600;
     font-size:44px;margin:0 0 6px;letter-spacing:.2px}}
  .lede{{color:#b9c4d4;font-size:16px;max-width:760px;margin:0 0 6px;text-align:justify;hyphens:auto}}
  .nota{{color:var(--fraco);font-size:13.5px;max-width:760px;margin:14px 0 0;text-align:justify;hyphens:auto}}
  h2{{font-family:Cormorant,Georgia,serif;font-size:25px;margin:44px 0 10px;
     font-weight:600}}
  ol{{list-style:none;padding:0;margin:18px 0 0;counter-reset:f}}
  li{{counter-increment:f;margin:0 0 12px}}
  a.fatia{{display:flex;gap:18px;align-items:baseline;text-decoration:none;color:inherit;
          background:var(--cartao);border:1px solid var(--borda);border-left-width:4px;
          border-radius:6px;padding:15px 18px;transition:border-color .12s}}
  a.fatia:hover{{border-color:var(--ouro)}}
  a.fatia::before{{content:counter(f);font-variant-numeric:tabular-nums;color:var(--fraco);
                  font-size:15px;min-width:20px}}
  .corpo{{flex:1}}
  .nome{{font-family:Cormorant,Georgia,serif;font-size:22px;font-weight:600}}
  .explica{{color:var(--ouro);font-size:13.5px;margin-top:1px}}
  .chamada{{color:#9fadc0;font-size:13.5px;margin-top:7px}}
  pre.arvore{{background:var(--cartao);border:1px solid var(--borda);border-radius:6px;
             padding:18px;overflow-x:auto;color:#9fadc0;font-size:13px;line-height:1.5}}
  footer{{margin-top:56px;padding-top:20px;border-top:1px solid var(--borda);
         color:var(--fraco);font-size:13px}}
  footer a{{color:var(--ouro)}}
  code{{background:#132440;padding:1px 6px;border-radius:3px;font-size:13px;color:var(--ouro)}}
</style>
</head>
<body>
<div class="caixa">

<h1>Ver o cálculo</h1>
<p class="lede">{Quantas} instrumentos, em ordem. Cada um mostra <b>uma</b> coisa, e cada um
abre sozinho no navegador — sem instalação, sem rede, sem conta.</p>
<p class="lede">Não são ilustrações do que um texto já disse. São o lugar onde a
afirmação pode ser <b>conferida com a régua</b>: quando duas coisas têm o mesmo
comprimento, elas têm o mesmo comprimento na tela, e você mede.</p>

<h2>A ordem</h2>
<ol>
{cartoes}
</ol>

<h2>Por que esta ordem, e não outra</h2>
<p class="nota">Uma dimensão só tem posição — não há para onde curvar. É a segunda que
desbloqueia a forma, e é por isso que <b>o par vira ponto</b> é a raiz e não um começo
entre outros: até um ângulo precisa de duas dimensões para existir. Depois da raiz, a
árvore abre em dois ramos que só se encontram no fim.</p>
<pre class="arvore">{arvore}</pre>
<p class="nota">Dependência e ordem de leitura não são a mesma coisa, e vale separar. A
<b>taxa</b> não depende da trigonometria — inclinação existe sem ângulo nenhum. Mas ela
gasta a palavra <b>tangente</b>, que nomeia duas coisas, e essa ambiguidade precisa estar
desfeita antes. Por isso a fila a põe em sétimo, embora o grafo de dependência a mantenha
num ramo próprio.</p>
<p class="nota">Isso não foi teoria: com a taxa em segundo, ela era a <b>única fatia com
dívida declarada</b> na verificação — gastava seno, cosseno e π antes de qualquer um ser
definido. Descendo para sétimo, a dívida zerou. A verificação viu o que o argumento não tinha
visto.</p>

<h2>Como isto se verifica</h2>
<p class="nota">Cada fatia declara, num manifesto legível por máquina, a sua ordem e os
símbolos pelos quais responde. O <code>auditar_fatias.py</code> cobra: nenhum símbolo
gasto sem vir da própria fatia ou de uma <b>anterior</b>; nenhum empréstimo sem alguém
depois pagá-lo; nenhuma declaração ociosa; nenhum pedido de rede. E roda com
<b>controle negativo</b> — injeta defeitos e exige que sejam pegos, porque zero achados
só significa alguma coisa se a verificação provar que sabe reprovar.</p>
<p class="nota">Este índice também é gerado: ele lê a ordem e a descrição das próprias
fatias. Editar o HTML gerado é o defeito, não o atalho.</p>

<footer>
<b>Ver o cálculo</b> — Mateus Alkimim.<br>
Código sob <b>MIT</b>; conteúdo sob
<a href="https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br">CC BY-SA 4.0</a>
(veja <code>LICENSE</code> e <code>LICENSE-CONTENT</code>).<br>
Reusar é livre, inclusive comercialmente; derivar exige manter a mesma licença e dar
crédito.
</footer>

</div>
</body>
</html>
"""

ARVORE = """   ORDEM DE LEITURA — uma fila

   par-vira-ponto → o ângulo → o triângulo → a distância → o círculo
                  → o desenrolamento → a taxa → o encontro


   DEPENDÊNCIA — dois ramos, e só aqui a árvore existe

                    par-vira-ponto
              ┌───────────┴───────────┐
           a taxa      o ângulo → o triângulo → a distância → o círculo
              │                    → o desenrolamento
              └───────────┬───────────┘
                     o encontro

   A taxa não DEPENDE da trigonometria: inclinação existe sem ângulo. Mas ela
   gasta a palavra "tangente", e essa palavra precisa estar desambiguada antes.
   Por isso a fila a põe tarde, e o ramo continua sendo verdade."""


NAV_CSS = """
<style>
  nav.fila{display:flex;align-items:center;gap:14px;max-width:1100px;margin:0 auto 26px;
           padding:0 0 12px;border-bottom:1px solid #1e3050;font-size:12.5px;
           font-family:Inter,-apple-system,"Segoe UI",system-ui,sans-serif}
  nav.fila a{color:#5b6b86;text-decoration:none;transition:color .12s}
  nav.fila a:hover{color:#c9a266}
  nav.fila .meio{flex:1;display:flex;align-items:center;justify-content:center;gap:10px}
  nav.fila .passos{display:flex;gap:3px}
  nav.fila .passos i{width:16px;height:3px;border-radius:2px;background:#1e3050;display:block}
  nav.fila .passos i.aqui{background:#c9a266}
  nav.fila .onde{color:#7f8ea4;font-variant-numeric:tabular-nums}
  nav.fila .vazio{visibility:hidden}
</style>"""


def bloco_nav(fatias, i):
    """A navegação de UMA fatia, derivada da ORDEM dos manifestos.

    Injetada em bloco marcado: reordenar as fatias reescreve todas de uma vez.
    Vai inline, e não num nav.js, porque cada fatia abre SOZINHA — é propriedade
    declarada no README, e um arquivo solto por e-mail tem de continuar
    funcionando.
    """
    n = len(fatias)
    ant = fatias[i - 1] if i > 0 else None
    pro = fatias[i + 1] if i < n - 1 else None
    passos = "".join(
        f'<i class="aqui" title="{html.escape(f["nome"])}"></i>' if k == i
        else f'<i title="{k+1}. {html.escape(f["nome"])}"></i>'
        for k, f in enumerate(fatias))
    esq = (f'<a href="{ant["arquivo"]}">← {html.escape(ant["nome"])}</a>'
           if ant else '<a class="vazio">←</a>')
    dir_ = (f'<a href="{pro["arquivo"]}">{html.escape(pro["nome"])} →</a>'
            if pro else '<a class="vazio">→</a>')
    return (f"<!-- nav: GERADO por gerar_indice.py · não editar à mão -->\n"
            f"{NAV_CSS}\n"
            f'<nav class="fila">{esq}'
            f'<span class="meio"><span class="passos">{passos}</span>'
            f'<a class="onde" href="index.html">{i+1} de {n} · as {POR_EXTENSO.get(n, n)} fatias</a>'
            f'</span>{dir_}</nav>\n'
            f"<!-- /nav -->")


MARCA_INI = "<!-- nav: GERADO"
MARCA_FIM = "<!-- /nav -->"


def injetar_nav(fatias):
    """Reescreve o bloco de nav em cada fatia. Idempotente."""
    for i, f in enumerate(fatias):
        caminho = os.path.join(AQUI, f["arquivo"])
        s = open(caminho, encoding="utf-8").read()
        novo = bloco_nav(fatias, i)
        if MARCA_INI in s:
            a = s.index(MARCA_INI); b = s.index(MARCA_FIM) + len(MARCA_FIM)
            s = s[:a] + novo + s[b:]
        else:
            m = re.search(r"<body>\s*", s)
            if not m:
                print(f"  ⚠ {f['arquivo']}: sem <body>, nav não injetada", file=sys.stderr)
                continue
            s = s[:m.end()] + novo + "\n\n" + s[m.end():]
        open(caminho, "w", encoding="utf-8").write(s)
    return len(fatias)


def main():
    fatias = ler_fatias()
    if not fatias:
        print("nenhuma fatia com manifesto — nada a gerar"); return 1
    esperado = list(range(1, len(fatias) + 1))
    if [f["ordem"] for f in fatias] != esperado:
        print(f"ordens fora de sequência: {[f['ordem'] for f in fatias]}"); return 1

    cartoes = []
    for f in fatias:
        cor = COR[CORRENTE.get(f["chave"], "raiz")]
        cartoes.append(
            f'  <li><a class="fatia" href="{f["arquivo"]}" style="border-left-color:{cor}">'
            f'<div class="corpo"><div class="nome">{html.escape(f["nome"])}</div>'
            f'<div class="explica">{html.escape(f["explica"])}</div>'
            f'<div class="chamada">{html.escape(f["chamada"])}</div></div></a></li>')

    with open(SAIDA, "w", encoding="utf-8") as fh:
        q = POR_EXTENSO.get(len(fatias), str(len(fatias)))
        fh.write(TEMPLATE.format(cartoes="\n".join(cartoes),
                                 arvore=html.escape(ARVORE),
                                 quantas=q, Quantas=q.capitalize()))
    n = injetar_nav(fatias)
    print(f"index.html gerado — {len(fatias)} fatias, ordem 1..{len(fatias)}")
    print(f"navegação injetada em {n} fatia(s), derivada da mesma ordem")
    for f in fatias:
        print(f"   {f['ordem']}  {f['nome']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
