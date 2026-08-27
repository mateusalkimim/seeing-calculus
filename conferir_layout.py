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


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright ausente — não posso conferir o layout.", file=sys.stderr)
        return 2

    aqui = pathlib.Path(__file__).parent
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
        b.close()

    print()
    for a in achados:
        print(f"  ✗ {a}")
    print(f"  {len(fatias)} páginas · {len(achados)} achado(s)")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
