#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confere o layout das fatias num navegador de verdade.

As fatias afirmam quatro coisas sobre a página: a prosa é uma coluna só, com
todos os blocos na MESMA borda esquerda; o desenho fica num quadro contido, com
a proporção da própria composição; os controles pertencem ao desenho e ficam
alinhados com ele, não com a página; e nada transborda na horizontal. Afirmação sem
instrumento é promessa — este é o instrumento.

O erro que ele existe para não deixar voltar: num monitor de 1900 px o desenho
abria com 1848 x 954 px, e o título e o texto viravam legenda de uma figura
gigante. Medida de CSS no arquivo não pega isso: só o navegador sabe quanto
uma caixa mede depois de montada.

Precisa do playwright e de um chromium. Sem eles, sai com código 2 e diz que
não pôde conferir — nunca devolve "ok" por ausência de prova:

    CHROME=/caminho/do/chrome python3 conferir_layout.py
"""
import glob
import os
import pathlib
import sys

LARGURA = 1900          # o monitor largo, que é onde o defeito aparecia
TETO_ALTURA = 620       # o desenho não pode passar disto na tela
PROSA = ("h1", ".sub", ".faca", ".notas")

# O telefone entrou na régua em 2026-08-27. Três tamanhos reais, não um.
TELEFONES = (("Android pequeno", 360, 740), ("iPhone", 390, 844),
             ("telefone grande", 414, 896))
ALVO_MIN = 44           # a recomendação da Apple; o Android pede 48

TELA_MEDE = """() => {
  // `clientWidth`, NAO `innerWidth`. Quando o desenho empurra a folha, o
  // proprio `innerWidth` estica junto (842 num telefone de 360) e a subtracao
  // da ZERO: a sonda mediria o defeito contra uma regua que o defeito move.
  // O `clientWidth` do documento fica no viewport de layout, 360, e nao mente.
  const de=document.documentElement, b=document.body;
  const vw=de.clientWidth;
  let menor=1e9, menorQ='';
  for (const el of document.querySelectorAll('button,input,a,select')){
    // LINK DENTRO DE FRASE NÃO É BOTÃO: engordá-lo para 44 px quebraria a
    // entrelinha do parágrafo, e a regra de tamanho de alvo o isenta.
    if (el.tagName==='A' && el.closest('p, .notas, li, td')) continue;
    // input dentro de <label> tem o RÓTULO inteiro como alvo.
    const lab = el.closest('label');
    const r = (lab && el.tagName==='INPUT') ? lab.getBoundingClientRect()
                                            : el.getBoundingClientRect();
    if (r.width<1 || r.height<1) continue;
    const m = Math.min(r.width, r.height);
    if (m<menor){ menor=m; menorQ = el.tagName + (el.id?'#'+el.id:''); }
  }
  const vazam=[];
  for (const el of document.querySelectorAll('body *')){
    const r=el.getBoundingClientRect();
    if (r.right > vw+1 && r.width > 4)
      vazam.push(el.tagName + (el.className?'.'+String(el.className).split(' ')[0]:''));
  }
  const pn=document.querySelector('.painel');
  const pr=pn?pn.getBoundingClientRect():null;
  return { overflowX: Math.max(de.scrollWidth,b.scrollWidth)-vw,
           larguraTotal: Math.max(de.scrollWidth,b.scrollWidth),
           menorAlvo: Math.round(menor===1e9?999:menor), menorQual: menorQ,
           vazam: [...new Set(vazam)].slice(0,4),
           painel: !!pn,
           painelNaTela: pr ? pr.bottom <= window.innerHeight : true,
           painelAbaixo: pr ? Math.round(pr.bottom - window.innerHeight) : 0 };
}"""


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright ausente — não posso conferir o layout.", file=sys.stderr)
        return 2

    raiz = pathlib.Path(__file__).parent
    # As fatias saíram da raiz quando o sítio virou bilíngue: na raiz ficaram a
    # porta e os stubs. Sem esta linha a verificação mediria os STUBS — páginas de
    # três linhas que passam em tudo e não dizem nada sobre a fatia.
    d = "pt"
    if "--dir" in sys.argv:
        d = sys.argv[sys.argv.index("--dir") + 1]
    aqui = raiz / d if (raiz / d).is_dir() else raiz
    exe = os.environ.get("CHROME", "")
    fatias = sorted(p for p in glob.glob(str(aqui / "*.html")))
    achados = []

    with sync_playwright() as pw:
        try:
            b = pw.chromium.launch(executable_path=exe or None, args=["--no-sandbox"])
        except Exception as e:
            print(f"chromium ausente — não posso conferir. Use CHROME=/caminho. ({e})",
                  file=sys.stderr)
            return 2
        pg = b.new_page(viewport={"width": LARGURA, "height": 1000})
        for p in fatias:
            nome = pathlib.Path(p).stem
            pg.goto(pathlib.Path(p).as_uri())
            pg.wait_for_timeout(400)
            m = pg.evaluate(
                """(sel) => {
                  const cx = s => { const e=document.querySelector(s); if(!e) return null;
                    const r=e.getBoundingClientRect();
                    return {l:Math.round(r.left), w:Math.round(r.width),
                            h:Math.round(r.height)}; };
                  const prosa = {}; sel.forEach(s => { const v=cx(s); if(v) prosa[s]=v; });
                  return {prosa, cv: cx('canvas'),
                          ctl: ['.painel','#fns','#resp','.leitura']
                                 .map(s=>[s,cx(s)]).filter(p=>p[1]),
                          rola: document.documentElement.scrollWidth > window.innerWidth+1,
                          janela: window.innerWidth};
                }""", list(PROSA))
            esq = sorted({v["l"] for v in m["prosa"].values()})
            if len(esq) > 1:
                achados.append(f"{nome}: a prosa tem {len(esq)} bordas esquerdas {esq} "
                               f"— a coluna deveria ser uma só")
            if m["rola"]:
                achados.append(f"{nome}: a página rola na horizontal")
            cv = m["cv"]
            if cv:
                # centrado: a sobra dos dois lados tem de ser igual
                dir_ = m["janela"] - cv["l"] - cv["w"]
                if abs(cv["l"] - dir_) > 2:
                    achados.append(f"{nome}: o desenho não está centrado "
                                   f"(sobra {cv['l']} à esquerda e {dir_} à direita)")
                for sel, c in m["ctl"]:
                    if abs(c["l"] - cv["l"]) > 2 or abs(c["w"] - cv["w"]) > 2:
                        achados.append(f"{nome}: {sel} está em x={c['l']} com "
                                       f"{c['w']} px, e o desenho em x={cv['l']} "
                                       f"com {cv['w']} — controle solto do quadro")
                if cv["h"] > TETO_ALTURA:
                    achados.append(f"{nome}: o desenho tem {cv['h']} px de altura "
                                   f"(teto {TETO_ALTURA}) — ele volta a engolir a folha")
            print(f"  {nome:<18} prosa em x={esq[0] if esq else '—'} · "
                  f"desenho {cv['w'] if cv else '—'}x{cv['h'] if cv else '—'}")

        # ---- o TELEFONE, que este verificação nunca tinha olhado ----
        # A régua acima mede um monitor de 1900 px. O defeito de telefone é
        # outro e foi medido em 2026-08-27: num viewport de 360 a página ia a
        # 842–1126 px, porque `canvas{height:568px;width:auto}` mantém a altura
        # e deixa a largura crescer; e o menor alvo de toque media 10 px.
        print()
        for rot, lw, lh in TELEFONES:
            pgm = b.new_page(viewport={"width": lw, "height": lh},
                             device_scale_factor=3, is_mobile=True, has_touch=True)
            for p in fatias:
                nome = pathlib.Path(p).stem
                pgm.goto(pathlib.Path(p).as_uri())
                pgm.wait_for_timeout(500)
                t = pgm.evaluate(TELA_MEDE)
                if t["overflowX"] > 1:
                    achados.append(f"{nome} [{rot}]: a página vai a "
                                   f"{t['larguraTotal']} px num viewport de {lw} "
                                   f"— o desenho empurra a folha")
                if t["vazam"]:
                    achados.append(f"{nome} [{rot}]: transborda — "
                                   + ", ".join(t["vazam"][:3]))
                if t["menorAlvo"] < ALVO_MIN:
                    achados.append(f"{nome} [{rot}]: alvo de toque de "
                                   f"{t['menorAlvo']} px em {t['menorQual']} "
                                   f"(mínimo {ALVO_MIN})")
                if t["painel"] and not t["painelNaTela"]:
                    achados.append(f"{nome} [{rot}]: o controle cai "
                                   f"{t['painelAbaixo']} px abaixo da primeira "
                                   f"tela — a figura responde onde não se vê")
            print(f"  {rot:<16} {len(fatias)} páginas conferidas")
            pgm.close()
        b.close()

    print()
    for a in achados:
        print(f"  ✗ {a}")
    print(f"  {len(fatias)} páginas · {len(achados)} achado(s)")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
