#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Põe (ou repõe) o bloco de TELEFONE em cada fatia. Bloco gerado, marcado.

## O defeito, medido

Num viewport de 360 px o layout está certo (`clientWidth = 360`), mas a página
inteira vai a **842 px** no `o-angulo` e a **1126 px** no `taxa`: a regra
`canvas{height:568px;width:auto}` — a altura comum, de 2026-08-27 — mantém a
altura e deixa a largura crescer. O `index.html`, que não tem canvas, fica
correto em 360. O desenho é que empurra a página.

E os alvos de toque medem **10 a 16 px**. A recomendação é 44 px (Apple) e
48 px (Android): num telefone, o controle do instrumento não se pega.

## Por que o TEXTO cresce

Encolher o desenho para caber resolve a página e quebra a leitura: o canvas tem
944 a 1240 px de largura interna, e a 308 px na tela um rótulo de 12 px vira
**4 px**. Ilegível é o mesmo que ausente.

Oito das nove fatias têm um `txt()` próprio, e com assinaturas DIFERENTES
(`txt(t,x,y,c,s,…)` na maioria, `txt(s,x,y,cor,t,al)` na `a-familia`, e a
`desenrolamento` não tem nenhum). Não há um ponto comum nelas — mas há no
navegador: **todo texto de canvas passa pelo `font` do contexto**. É lá que a
compensação entra, uma vez, igual para as nove.

## Só no telefone

A compensação e o CSS valem sob `innerWidth <= 820`. O layout de desktop, que
foi medido a pixel e aprovado, não é tocado — e o `conferir_layout.py` continua
medindo o que media, em 1900 px.

    python3 mobile.py            # repõe o bloco em pt/
    python3 mobile.py --dir en   # idem no derivado
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "<!-- telefone: GERADO por mobile.py, não editar à mão -->"
CORTE = 820          # o mesmo número no CSS e no JS: um lugar só decide

BLOCO = MARCA + """
<style>
@media (max-width: %(corte)dpx){
  /* o desenho passa a caber na largura: sem isto a pagina inteira vai a
     842-1126 px num telefone de 360, porque a altura comum e fixa e a largura
     cresce atras dela. */
  canvas{ height:auto !important; width:100%% !important; max-width:100%% !important; }
  body{ padding:14px 14px 32px; }
  /* FIGURA E CONTROLE NA MESMA TELA. Medido: o painel caia 118 a 174 px abaixo
     da dobra nas quatro fatias conferidas, porque a prosa de entrada ocupa
     580 a 840 px antes do desenho. Num instrumento cujo sentido e "voce mexe e
     a figura responde", o controle fora da tela quebra a alca.
     O "Faca:" desce para DEPOIS do painel -- no telefone se ve primeiro o que
     mexer, e a instrucao fica logo abaixo. A ordem do DOM nao muda (leitor de
     tela continua lendo na ordem escrita). */
  body{ display:flex; flex-direction:column; }
  /* `min-width:0` NAO e detalhe: filho de flex nasce com `min-width:auto` e
     RECUSA encolher abaixo do proprio conteudo. Foi o meu `display:flex` que
     levou o indice a 670 px num telefone de 360 -- o transbordo classico de
     flexbox, introduzido pelo conserto do transbordo. */
  body > *{ order:5; min-width:0; max-width:100%%; }
  /* a folga e apertada de proposito, e o INGLES e quem manda: o mesmo titulo
     quebra em mais linhas em ingles, e o painel do `o-angulo` caia 19 px
     abaixo da dobra so no `en/`. Quem dimensiona e o idioma mais longo. */
  body > h1{ order:0; font-size:23px; line-height:1.15; margin:0 0 1px; }
  body > .sub{ order:1; font-size:12.5px; line-height:1.4; margin-bottom:5px; }
  body > canvas{ order:2; }
  body > .painel{ order:3; margin-top:10px; }
  body > .faca{ order:4; margin-top:14px; }
  /* alvo de toque: media 44 px, que e a recomendacao da Apple; o Android pede
     48. Antes daqui o menor alvo media 10 px. */
  input[type=range]{ width:100%% !important; height:44px; }
  /* o checkbox tambem e alvo: media 13 px na `desenrolamento` */
  input[type=checkbox]{ width:26px; height:26px; }
  .painel label{ width:100%%; min-height:44px; display:flex; align-items:center; }
  .painel{ gap:10px; padding:12px; }
  button{ min-height:44px; padding:11px 16px; font-size:14px; }
  /* a nav media 18 px de alvo: o <a> e que precisa da altura, nao o ponto */
  /* a seta sozinha (`←`/`→`, na 1a e na ultima fatia) media 22 px de largura:
     alvo tem DUAS dimensoes. */
  nav.fila a{ padding:13px 6px; display:inline-block; min-height:44px;
              min-width:44px; text-align:center; box-sizing:border-box; }
  /* a nav QUEBRA em vez de esticar: com 9 pontos, duas setas e 44 px de alvo
     em cada, ela nao cabe em 360 px numa linha so -- e esticar a nav estica a
     folha. A contagem ("5 de 9") desce para a propria linha. */
  nav.fila{ flex-wrap:wrap; row-gap:2px; }
  nav.fila .meio{ order:3; flex:1 0 100%%; justify-content:flex-start; }
  nav.fila .passos{ display:inline-flex; align-items:center; min-height:44px;
                    flex-wrap:wrap; }
  nav.fila .passos i{ transform:scale(1.35); margin:0 2px; }
  table.l td, table.l th{ padding:7px 12px 7px 0; }
  /* CONTEUDO LARGO ROLA NA PROPRIA CAIXA. O `<pre>` da arvore de leitura nao
     quebra linha: ele mede 670 px fixos e levava a pagina inteira junto, em
     qualquer telefone. Arte ASCII nao se reflui -- se ela nao cabe, quem rola
     e ela, nao a folha. Vale para tabela larga pela mesma razao. */
  pre{ overflow-x:auto; max-width:100%%; -webkit-overflow-scrolling:touch; }
  table.l{ display:block; overflow-x:auto; max-width:100%%; }
  .caixa{ max-width:100%%; }
  .painel{ margin-bottom:4px; }
  /* a FAIXA DE IDIOMA e o rodape sao meus, e eram os ultimos alvos pequenos da
     pagina: o link media 113x18 e o botao de fechar 21x19. Instrumento que
     cobra 44 px dos outros tem de caber na propria regra. */
  #faixa-idioma{ padding:8px 10px; }
  #faixa-idioma a{ display:inline-block; padding:12px 10px; min-height:44px;
                   box-sizing:border-box; }
  #faixa-idioma button{ min-width:44px; min-height:44px; font-size:22px; }
  footer a{ display:inline-block; padding:11px 2px; min-height:44px;
            box-sizing:border-box; }
}
</style>
<script>/* GERADO: telefone (mobile.py) -- nao traduzir, nao editar */%(marca)s
(function(){
  if (window.innerWidth > %(corte)d) return;      // desktop nao e tocado
  var cv = document.querySelector('canvas');
  if (!cv) return;
  var proto = CanvasRenderingContext2D.prototype;
  var desc = Object.getOwnPropertyDescriptor(proto, 'font');
  if (!desc || !desc.set || proto.__fonteAjustada) return;
  proto.__fonteAjustada = true;
  function fator(){
    var r = cv.getBoundingClientRect();
    if (!r.width) return 1;
    // o quanto o desenho encolheu, limitado: acima de 2.6 o rotulo passa a
    // cobrir o desenho que ele explica.
    return Math.max(1, Math.min(2.6, cv.width / r.width));
  }
  Object.defineProperty(proto, 'font', {
    configurable: true,
    get: function(){ return desc.get.call(this); },
    set: function(v){
      var f = fator();
      if (f > 1.02) {
        v = String(v).replace(/([0-9.]+)px/, function(m, n){
          return (Math.round(parseFloat(n) * f * 10) / 10) + 'px';
        });
      }
      desc.set.call(this, v);
    }
  });
  // o desenho e refeito quando a tela gira ou muda de largura
  var t; addEventListener('resize', function(){
    clearTimeout(t); t = setTimeout(function(){
      window.dispatchEvent(new Event('itaca:redesenhar'));
      var i = document.querySelector('input[type=range]');
      if (i) i.dispatchEvent(new Event('input', {bubbles:true}));
    }, 120);
  });
})();
</script>"""


def remover(raw):
    i = raw.find(MARCA)
    if i == -1:
        return raw
    # `find`, NAO `rfind`: rfind acha o ultimo </script> do ARQUIVO -- o da
    # propria fatia -- e reinjetar apagaria tudo entre o bloco e o fim do corpo.
    fim = raw.find("</script>", i)
    if fim == -1:
        return raw
    return raw[:i].rstrip("\n") + "\n" + raw[fim + len("</script>"):].lstrip("\n")


def injetar(raw):
    """Antes de </head>: o CSS tem de chegar antes da 1a pintura, e o patch do
    contexto antes de o script da fatia desenhar."""
    raw = remover(raw)
    bloco = BLOCO % {"corte": CORTE, "marca": ""}
    m = re.search(r"</head\s*>", raw, re.I)
    if not m:
        return raw
    return raw[:m.start()] + bloco + "\n" + raw[m.start():]


def main():
    d = "pt"
    if "--dir" in sys.argv:
        d = sys.argv[sys.argv.index("--dir") + 1]
    pasta = os.path.join(AQUI, d) if os.path.isdir(os.path.join(AQUI, d)) else AQUI
    n = 0
    for arq in sorted(os.listdir(pasta)):
        # o index TAMBEM entra: ele nao tem canvas (o JS ja se guarda disso),
        # mas tem alvo de toque, faixa de idioma e rodape como qualquer fatia.
        if not arq.endswith(".html"):
            continue
        p = os.path.join(pasta, arq)
        s = open(p, encoding="utf-8").read()
        novo = injetar(s)
        if novo != s:
            open(p, "w", encoding="utf-8").write(novo)
        n += 1
    print("bloco de telefone em %d fatia(s) de %s/" % (n, d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
