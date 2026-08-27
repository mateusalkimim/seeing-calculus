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

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "index.html")

MANIFESTO = re.compile(
    r"<!--\s*fatia:\s*(?P<nome>[\w-]+)\s*\|\s*ordem:\s*(?P<ordem>\d+)"
    r"\s*\|\s*declara:\s*(?P<declara>[^|]*)"
    r"(?:\|\s*empresta:\s*(?P<empresta>[^-]*))?-->")

CORRENTE = {  # a que ramo da árvore cada fatia pertence — ver o README
    "par-vira-ponto": "raiz", "taxa": "função",
    "o-angulo": "medida", "o-triangulo": "medida", "a-distancia": "medida",
    "o-circulo": "medida", "desenrolamento": "encontro", "o-encontro": "encontro",
}
COR = {"raiz": "#c9a266", "função": "#78c4ff", "medida": "#e8654f", "encontro": "#6fbf6a"}


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
<title>Ver o cálculo — oito instrumentos, em ordem</title>
<style>
  :root{{ --fundo:#0a1424; --creme:#e8e2d6; --fraco:#5b6b86; --ouro:#c9a266;
         --cartao:#0d1c30; --borda:#1e3050; }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--fundo);color:var(--creme);
       font-family:Inter,-apple-system,"Segoe UI",system-ui,sans-serif;
       padding:44px 26px 60px;line-height:1.6}}
  .caixa{{max-width:980px;margin:0 auto}}
  h1{{font-family:Cormorant,Georgia,"Times New Roman",serif;font-weight:600;
     font-size:44px;margin:0 0 6px;letter-spacing:.2px}}
  .lede{{color:#b9c4d4;font-size:16px;max-width:760px;margin:0 0 6px}}
  .nota{{color:var(--fraco);font-size:13.5px;max-width:760px;margin:14px 0 0}}
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
<p class="lede">Oito instrumentos, em ordem. Cada um mostra <b>uma</b> coisa, e cada um
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
<p class="nota">O que é livre é o ramo: a taxa pode vir antes ou depois da corrente da
medida. O que não é livre é a raiz.</p>

<h2>Como isto se verifica</h2>
<p class="nota">Cada fatia declara, num manifesto legível por máquina, a sua ordem e os
símbolos pelos quais responde. O <code>auditar_fatias.py</code> cobra: nenhum símbolo
gasto sem vir da própria fatia ou de uma <b>anterior</b>; nenhum empréstimo sem alguém
depois pagá-lo; nenhuma declaração ociosa; nenhum pedido de rede. E roda com
<b>controle negativo</b> — injeta defeitos e exige que sejam pegos, porque zero achados
só significa alguma coisa se o portão provar que sabe reprovar.</p>
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

ARVORE = """                    par-vira-ponto            a raiz
              ┌───────────┴───────────┐
           a taxa       o ângulo → o triângulo → a distância → o círculo
              └───────────┬───────────┘
              o desenrolamento → o encontro"""


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
        fh.write(TEMPLATE.format(cartoes="\n".join(cartoes), arvore=html.escape(ARVORE)))
    print(f"index.html gerado — {len(fatias)} fatias, ordem 1..{len(fatias)}")
    for f in fatias:
        print(f"   {f['ordem']}  {f['nome']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
