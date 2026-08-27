#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PORTA: quem chega na raiz e mandado para o idioma que ele le.

POR QUE IDIOMA E NAO PAIS. GitHub Pages e hospedagem estatica -- nao ha
servidor, nao ha regra de redirecionamento, e o pais de quem acessa so se
descobre mandando o IP do visitante para um servico de terceiro, em tempo de
execucao. Isso custaria dependencia externa (que o proprio portao das fatias
barra), o IP de quem le saindo da pagina, latencia antes da 1a pintura e um
modo de falha sem resposta definida. O navegador ja entrega `navigator.languages`
de graca, e ela responde a pergunta melhor: em que lingua esta pessoa le.
Brasileiro em Lisboa continua recebendo portugues.

TRES REGRAS QUE O DESENHO SEGUE:

  1. a escolha do leitor VENCE a deteccao, e fica gravada (localStorage);
  2. so a RAIZ redireciona. Pagina funda recebe uma FAIXA, nao um salto: quem
     recebeu um link de uma fatia especifica quer aquela fatia, e buscador que
     e jogado de um idioma para outro indexa errado;
  3. sem JavaScript a porta continua servindo -- os dois links ficam visiveis.

Os STUBS da raiz existem porque as URLs antigas ja sairam para o mundo (o perfil
do GitHub aponta para elas). `o-angulo.html` continua respondendo, e leva para
`pt/o-angulo.html` -- exatamente o que aquela URL sempre serviu.

    python3 gerar_porta.py
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

DETECTOR = """(function(){
  var d='en';
  try{ var f=localStorage.getItem('sc-lang'); if(f==='pt'||f==='en'){ %s } }catch(e){}
  var L=(navigator.languages&&navigator.languages.length)?navigator.languages
        :[navigator.language||''];
  for(var i=0;i<L.length;i++){ if(/^pt/i.test(L[i])){ d='pt'; break; } }
  %s
})();"""

PORTA = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seeing Calculus — Ver o Calculo</title>
<link rel="alternate" hreflang="pt-BR" href="pt/">
<link rel="alternate" hreflang="en" href="en/">
<link rel="alternate" hreflang="x-default" href="en/">
<script>
%s
</script>
<style>
  body{margin:0;background:#0a1424;color:#e8e2d6;font-family:Inter,system-ui,sans-serif;
       display:flex;min-height:100vh;align-items:center;justify-content:center}
  .p{text-align:center;padding:30px}
  h1{font-family:Cormorant,Georgia,serif;font-weight:600;font-size:30px;margin:0 0 6px}
  .s{color:#5b6b86;font-size:14px;margin:0 0 22px}
  a{display:inline-block;margin:6px;padding:10px 20px;border-radius:5px;
    background:#24374f;color:#e8e2d6;text-decoration:none;font-size:14px}
  a:hover{background:#c9a266;color:#0a1424}
</style>
</head>
<body>
<div class="p">
  <h1>Seeing Calculus</h1>
  <p class="s">Instrumentos interativos &middot; Interactive instruments</p>
  <a href="pt/">Ler em portugues</a>
  <a href="en/">Read in English</a>
</div>
</body>
</html>
"""

STUB = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>%s</title>
<link rel="canonical" href="pt/%s">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=pt/%s">
<script>location.replace('pt/%s'+location.hash);</script>
</head>
<body><p><a href="pt/%s">%s &rarr;</a></p></body>
</html>
"""


def main():
    fonte = os.path.join(AQUI, "pt")
    if not os.path.isdir(fonte):
        raise SystemExit("sem pt/ -- nao ha o que servir")

    det = DETECTOR % ("location.replace(f+'/'+location.hash); return;",
                      "location.replace(d+'/'+location.hash);")
    open(os.path.join(AQUI, "index.html"), "w", encoding="utf-8").write(PORTA % det)

    n = 0
    for arq in sorted(os.listdir(fonte)):
        if not arq.endswith(".html") or arq == "index.html":
            continue
        titulo = arq[:-5].replace("-", " ")
        open(os.path.join(AQUI, arq), "w", encoding="utf-8").write(
            STUB % (titulo, arq, arq, arq, arq, titulo))
        n += 1
    print("porta: index.html + %d stub(s) de URL antiga" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
