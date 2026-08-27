#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O portão das FATIAS — os instrumentos interativos sob a norma de notação.

A `norma-de-notacao.md` §0b.7 (emenda ratificada em 2026-08-27) pôs os
instrumentos interativos sob a norma e declarou, na mesma frase, que **o portão
de um instrumento ainda não existe**. Este é ele.

O que ele NÃO faz, e é decisão da emenda: não mede margem, CPL nem subocupação.
Aquilo é medida de página impressa e não se transporta para uma tela com
controle.

O que ele mede:

  [1] R5        quantificador e sinal de lógica fora do texto de tela —
                ∀ ∃ ⇒ ⇔ ⊂ ↦ ∈ e as formas em LaTeX. Falha dura.
  [2] MANIFESTO cada fatia declara nome, ordem e os símbolos pelos quais
                responde, numa linha legível por máquina. Sem ela não há como
                verificar herança. Falha dura.
  [3] ORDEM     as ordens formam 1..N sem buraco e sem repetição — herança só
                significa alguma coisa se a fila for única. Falha dura.
  [4] HERANÇA   todo símbolo gasto no texto de tela está declarado pela própria
                fatia, emprestado por ela com aviso, ou declarado por uma fatia
                ANTERIOR. Herdar de quem vem depois não é herdar, é supor.
                Falha dura.
  [5] DÍVIDA    todo símbolo que uma fatia declara EMPRESTADO é definido por
                alguma fatia posterior. Empréstimo que ninguém paga é buraco.
                Falha dura.
  [6] OCIOSO    símbolo declarado e não gasto. Declarar a mais silencia o
                portão sem melhorar a fatia. Falha dura.
  [7] REDE      nenhum recurso EXTERNO carregado — @import, src, <link>, url()
                em CSS, fetch. As fatias abrem offline por contrato. Um
                `<a href>` para fora NÃO conta: link é coisa que o leitor
                clica, não coisa que a página busca — e a licença precisa
                estar clicável na via mais usada. Falha dura.
  [8] JS        o script passa no `node --check`. Falha dura.
  [9] NAV       a fatia carrega o bloco de navegação GERADO, e a posição que
                ele anuncia bate com a `ordem` do manifesto. A nav é derivada
                (gerar_indice.py a injeta); se alguém apagá-la ou editá-la à
                mão, a fila que o portão garante deixa de chegar ao leitor — e
                é quebra silenciosa, porque a página continua abrindo. Falha
                dura.
  [10] TESE      o topo do <script> traz o marcador `TESE DESTA FATIA`, seguido
                do que ela existe para dizer e do que a destruiria. O portão NÃO
                julga a tese — ele verifica que existe uma, sob um marcador
                fixo. Medir a palavra não é medir a coisa; o que este item mede
                é conformidade com a convenção, e é só isso que ele promete.
                Aviso, não falha.

CONTROLE NEGATIVO (§0b.5 da norma de rótulos, que vale aqui sem emenda): zero
achados só conta se o portão provar que sabe reprovar. `--controle` injeta um
defeito de cada classe numa cópia em memória e exige que cada um seja pego.

Roda:  python3 auditar_fatias.py            # audita as fatias
       python3 auditar_fatias.py --controle # + o controle negativo
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
# As fatias saíram da raiz quando o sítio virou bilíngue: `pt/` é a fonte, `en/`
# é derivado, e na raiz ficaram a porta e os stubs das URLs antigas. Sem esta
# linha o portão auditava os STUBS — e reprovava as nove por "sem manifesto",
# que é verdade sobre um stub de redirect e não diz nada sobre a fatia.
# `--dir` permite auditar o inglês: `python3 auditar_fatias.py --dir en`.
_ARG = None
for _i, _a in enumerate(sys.argv):
    if _a == "--dir" and _i + 1 < len(sys.argv):
        _ARG = sys.argv[_i + 1]
FATIAS = (os.path.join(AQUI, _ARG) if _ARG
          else (os.path.join(AQUI, "pt") if os.path.isdir(os.path.join(AQUI, "pt"))
                else AQUI))

# R5, com os símbolos nomeados na norma e as formas em LaTeX
BANIDOS = {
    "∀": "para todo", "∃": "existe", "⇒": "implica", "⇔": "se e só se",
    "⊂": "está contido", "↦": "leva em", "∈": "pertence a",
    r"\forall": "\\forall", r"\exists": "\\exists", r"\Rightarrow": "\\Rightarrow",
    r"\iff": "\\iff", r"\subset": "\\subset", r"\mapsto": "\\mapsto",
    r"\in ": "\\in",
}

# Os símbolos que o portão sabe procurar, com FRONTEIRA DE PALAVRA. O padrão
# ingênuo `sen` casa dentro de "desenho" e "desenrolamento" — foi assim que a
# primeira auditoria à mão inflou a dívida, em 2026-08-27.
# A tabela conhece as DUAS grafias. `sen` é a grafia portuguesa do seno e `sin`
# a inglesa — o mesmo símbolo, e trocá-lo é notação, não tradução (norma de
# tradução §8). Sem as chaves inglesas o portão reprovava a fatia derivada por
# "declara 'sin' e não gasta", com `sin θ` escrito na figura: defeito do
# instrumento, não da página.
SIMBOLOS = {
    "θ": r"θ", "π": r"π", "f′": r"f\s?′", "tg": r"\btg\b|\btan\b",
    "sen": r"\bsen\b|\bseno\b|\bsin\b|\bsine\b",
    "cos": r"\bcos\b|\bcosseno\b|\bcosine\b",
    "Δ": r"Δ", "S¹": r"S¹", "ℝ": r"ℝ", "√": r"√", "∞": r"∞",
}

# `sin` e `sen` são O MESMO SÍMBOLO em duas grafias, e a chave é UMA — o
# manifesto da fatia derivada em inglês diz `sin`, e aqui ele volta a `sen`.
# Tentei antes pôr as duas como chaves distintas apontando para o mesmo regex:
# aí toda fatia passou a "gastar" as duas, e o português inteiro reprovou por
# herança. Grafia alternativa se CANONIZA; duplicar a chave inventa um símbolo.
CANONICO = {"sin": "sen", "sine": "sen", "tan": "tg", "cosine": "cos"}

MANIFESTO = re.compile(
    r"<!--\s*fatia:\s*(?P<nome>[\w-]+)\s*\|\s*ordem:\s*(?P<ordem>\d+)"
    r"\s*\|\s*declara:\s*(?P<declara>[^|]*)"
    r"(?:\|\s*empresta:\s*(?P<empresta>[^-]*))?-->")


def tela(fonte):
    """O texto que o leitor vê: sem <script>, sem <style>, sem marcação."""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fonte, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def script(fonte):
    m = re.search(r"<script>(.*?)</script>", fonte, re.S)
    return m.group(1) if m else ""


def simbolos_gastos(texto):
    return {k for k, p in SIMBOLOS.items() if re.search(p, texto)}


def ler(caminho):
    fonte = open(caminho, encoding="utf-8").read()
    m = MANIFESTO.search(fonte)
    man = None
    if m:
        lista = lambda s: {CANONICO.get(x.strip(), x.strip())
                          for x in (s or "").split()
                          if x.strip() and x.strip() != "—"}
        man = {"nome": m.group("nome"), "ordem": int(m.group("ordem")),
               "declara": lista(m.group("declara")),
               "empresta": lista(m.group("empresta"))}
    return fonte, man


def auditar(arquivos, checar_js=True):
    """Devolve (achados, fatias). Achado = (arquivo, código, mensagem)."""
    achados, fatias = [], []
    for caminho, fonte in arquivos:
        nome = os.path.basename(caminho)
        m = MANIFESTO.search(fonte)
        if not m:
            achados.append((nome, "MANIFESTO", "sem a linha <!-- fatia: … -->"))
            continue
        lista = lambda s: {CANONICO.get(x.strip(), x.strip())
                          for x in (s or "").split()
                          if x.strip() and x.strip() != "—"}
        man = {"arquivo": nome, "nome": m.group("nome"), "ordem": int(m.group("ordem")),
               "declara": lista(m.group("declara")), "empresta": lista(m.group("empresta"))}
        t = tela(fonte)
        man["gasta"] = simbolos_gastos(t)
        fatias.append(man)

        for s, trad in BANIDOS.items():
            if s in t:
                achados.append((nome, "R5", f"símbolo banido {s!r} no texto de tela "
                                            f"— traduzir para {trad!r}"))
        # link NAO conta: <a href> e coisa que o leitor clica. O que quebra o
        # offline e RECURSO CARREGADO. Regex sem classe de aspas de proposito:
        # o `.?` cobre a aspa simples, a dupla ou a ausencia dela.
        # `de` OU `of`: a posição é o número, e ele não muda de idioma.
        m_nav = re.search(r'class="onde"[^>]*>(\d+)\s+(?:de|of)\s+(\d+)', fonte)
        if "<!-- nav: GERADO" not in fonte:
            achados.append((nome, "NAV", "sem o bloco de navegação — rode gerar_indice.py"))
        elif not m_nav:
            achados.append((nome, "NAV", "bloco de navegação sem a posição declarada"))
        elif int(m_nav.group(1)) != man["ordem"]:
            achados.append((nome, "NAV",
                            f"a nav anuncia posição {m_nav.group(1)} e o manifesto diz "
                            f"{man['ordem']} — a fila e a página discordam"))

        carrega = re.search(r"@import"
                            r"|src\s*=\s*.?https?://"
                            r"|<link[^>]+href\s*=\s*.?https?://"
                            r"|url\(\s*.?https?://"
                            r"|fetch\s*\(|XMLHttpRequest", fonte)
        if carrega:
            achados.append((nome, "REDE",
                            f"carrega recurso externo ({carrega.group(0)[:28]!r}); "
                            f"a fatia tem de abrir offline"))
        if checar_js:
            js = script(fonte)
            if not js:
                achados.append((nome, "JS", "sem bloco <script>"))
            else:
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                                 encoding="utf-8") as f:
                    f.write(js); tmp = f.name
                r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
                os.unlink(tmp)
                if r.returncode:
                    achados.append((nome, "JS", r.stderr.strip().split("\n")[0]))
            if "TESE DESTA FATIA" not in js:
                achados.append((nome, "TESE",
                                "aviso: falta o marcador 'TESE DESTA FATIA' no topo do <script>"))

    ordens = sorted(f["ordem"] for f in fatias)
    if fatias and ordens != list(range(1, len(fatias) + 1)):
        achados.append(("(conjunto)", "ORDEM",
                        f"as ordens não formam 1..{len(fatias)} sem buraco: {ordens}"))

    fatias.sort(key=lambda f: f["ordem"])
    disponivel = set()
    for f in fatias:
        pode = disponivel | f["declara"] | f["empresta"]
        for s in sorted(f["gasta"] - pode):
            achados.append((f["arquivo"], "HERANÇA",
                            f"gasta {s!r} sem declarar, e nenhuma fatia anterior o declara"))
        for s in sorted((f["declara"] | f["empresta"]) - f["gasta"]):
            achados.append((f["arquivo"], "OCIOSO",
                            f"declara {s!r} e não gasta — declarar a mais só silencia o portão"))
        disponivel |= f["declara"]

    for i, f in enumerate(fatias):
        depois = set().union(*[g["declara"] for g in fatias[i + 1:]]) if fatias[i + 1:] else set()
        for s in sorted(f["empresta"] - depois):
            achados.append((f["arquivo"], "DÍVIDA",
                            f"empresta {s!r} e nenhuma fatia posterior o declara"))
    return achados, fatias


def controle_negativo():
    """O portão sabe reprovar? Injeta um defeito de cada classe e exige o achado."""
    base = open(os.path.join(FATIAS, "o-triangulo.html"), encoding="utf-8").read()
    casos = [
        ("R5", base.replace("<h1>O triângulo</h1>",
                            "<h1>O triângulo</h1><p>seja x ∈ ℝ</p>")),
        ("REDE", base.replace("<style>", '<style>@import url("http://x.y/z.css");')),
        ("JS", base.replace("(function(){", "(function(){ if( ")),
        ("MANIFESTO", re.sub(r"<!--\s*fatia:.*?-->", "", base, flags=re.S)),
        ("OCIOSO", re.sub(r"(declara:[^|]*)", r"\1 ∞ ", base, count=1)),
        ("NAV", re.sub(r'(class="onde"[^>]*>)\d+', r"\g<1>99", base, count=1)),
    ]
    print("\ncontrole negativo — o portão precisa REPROVAR cada um destes:")
    ok = True
    for codigo, corrompido in casos:
        ach, _ = auditar([(f"<controle {codigo}>", corrompido)], checar_js=(codigo == "JS"))
        pegou = any(a[1] == codigo for a in ach)
        print(f"   {'✓' if pegou else '✗'} {codigo:10s} "
              f"{'pego' if pegou else 'PASSOU DESPERCEBIDO — o portão não vale'}")
        ok &= pegou
    return ok


def main():
    # o index.html é DERIVADO (gerar_indice.py) e não é fatia: ele não tem
    # manifesto porque não gasta símbolo próprio — ele cita os das outras.
    nomes = sorted(f for f in os.listdir(FATIAS)
                   if f.endswith(".html") and f != "index.html"
                   and not f.startswith("seminario"))
    arquivos = [(os.path.join(FATIAS, n), open(os.path.join(FATIAS, n), encoding="utf-8").read())
                for n in nomes]
    achados, fatias = auditar(arquivos)

    print(f"portão das fatias — {len(fatias)} instrumento(s) sob a norma-de-notacao §0b.7\n")
    print(f"  {'ordem':>5}  {'fatia':22s} {'declara':22s} {'empresta':16s} gasta")
    for f in fatias:
        j = lambda s: " ".join(sorted(s)) or "—"
        print(f"  {f['ordem']:>5}  {f['nome']:22s} {j(f['declara']):22s} "
              f"{j(f['empresta']):16s} {j(f['gasta'])}")

    duros = [a for a in achados if not a[2].startswith("aviso")]
    avisos = [a for a in achados if a[2].startswith("aviso")]
    print()
    for arq, cod, msg in duros:
        print(f"  FALHA  [{cod}] {arq}: {msg}")
    for arq, cod, msg in avisos:
        print(f"  aviso  [{cod}] {arq}: {msg}")
    if not duros:
        print("  nenhuma falha dura.")

    ok_controle = True
    if "--controle" in sys.argv:
        ok_controle = controle_negativo()
        if not ok_controle:
            print("\n  ⚠️  ZERO ACHADOS NÃO VALE: o controle negativo não passou.")

    print()
    if duros or not ok_controle:
        print("REPROVA"); return 1
    print("PASSA" + ("" if "--controle" in sys.argv
                     else "  (sem controle negativo — rode com --controle)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
