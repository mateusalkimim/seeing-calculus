# Ver o cálculo — `seeing-calculus`

**Oito instrumentos interativos que constroem, em ordem, o chão visual do
cálculo.** Cada um mostra *uma* coisa, abre com dois cliques no navegador e
funciona **offline**: são `canvas` e aritmética, **sem biblioteca de terceiro,
sem rede, sem conta e sem servidor**. Nada sai da sua máquina — não há o que
sair, porque não há para onde.

A garantia que interessa: eles não ilustram o que um texto já disse, eles
deixam a afirmação ser **conferida com a régua**. Quando `o-encontro` diz que a
derivada é a tangente do ângulo, ele desenha o círculo e a curva **na mesma
escala e sobre a mesma linha do zero** — e então os dois comprimentos que a
igualdade compara *são* dois comprimentos iguais em pixels. Medidos: 113 e 111,
e a diferença é o disco na ponta de um deles.

## Início rápido

Não há instalação. Baixe e abra:

```bash
git clone https://github.com/mateusalkimim/seeing-calculus.git
cd seeing-calculus
xdg-open index.html          # Linux · no Windows, duplo clique no index.html
```

Ou use direto no ar: <https://mateusalkimim.github.io/seeing-calculus/>.

Para conferir o repositório (precisa de Python 3 e Node, só para isso):

```bash
python3 auditar_fatias.py --controle   # o portão, com controle negativo
python3 gerar_indice.py                # regera o index.html a partir das fatias
```

Passo a passo por sistema operacional em [`docs/INSTALACAO.md`](docs/INSTALACAO.md).

## O que tem aqui

```
index.html            a porta — GERADO por gerar_indice.py, não editar à mão
par-vira-ponto.html   ┐
taxa.html             │
o-angulo.html         │
o-triangulo.html      ├ as oito fatias, na ordem do manifesto de cada uma
a-distancia.html      │
o-circulo.html        │
desenrolamento.html   │
o-encontro.html       ┘
gerar_indice.py       lê as fatias e escreve o index
auditar_fatias.py     o portão: ordem, herança de símbolo, rede, JS
pharo/                o conhecimento destilado — por que a ordem é essa
docs/INSTALACAO.md    passo a passo por SO
LICENSE               MIT, para o código
LICENSE-CONTENT       CC BY-SA 4.0, para o conteúdo
```

## A ordem, e por que ela não é livre

Uma dimensão só tem posição — não há para onde curvar. É a segunda que
desbloqueia a forma, e é por isso que **o par vira ponto** é a raiz e não um
começo entre outros: até um ângulo precisa de duas dimensões para existir.

```
ORDEM DE LEITURA — uma fila

par-vira-ponto → o ângulo → o triângulo → a distância → o círculo
               → o desenrolamento → a taxa → o encontro
```

**Dependência e ordem de leitura não são a mesma coisa**, e separá-las é o que
faz esta fila ser honesta. A **taxa** não *depende* da trigonometria — inclinação
existe sem ângulo nenhum, e o grafo de dependência a mantém num ramo próprio.
Mas ela **gasta a palavra tangente**, que nomeia dois objetos, e essa ambiguidade
precisa estar desfeita antes. Por isso a fila a põe em sétimo.

```
DEPENDÊNCIA — dois ramos, e só aqui a árvore existe

                    par-vira-ponto
              ┌───────────┴───────────┐
           a taxa      o ângulo → o triângulo → a distância → o círculo
              │                    → o desenrolamento
              └───────────┬───────────┘
                     o encontro
```

Isto não foi decidido por argumento: com a taxa em segundo, ela era a **única
fatia com dívida declarada** no portão — gastava seno, cosseno e π antes de
qualquer um ser definido. Descendo para sétimo, a dívida zerou, e nenhuma fatia
deve nada a quem vem depois. **O portão viu o que o argumento não tinha visto.**

| | fatia | o que mostra |
|---|---|---|
| 1 | `par-vira-ponto` | duas retas numéricas viram um plano; o gráfico é o rastro dos encontros |
| 2 | `o-angulo` | medir uma abertura; graus, radianos, e de onde cai o π |
| 3 | `o-triangulo` | oposto e adjacente dependem de **qual** ângulo; daí o *co* de cosseno |
| 4 | `a-distancia` | o círculo é gerado por uma condição, e a condição é Pitágoras |
| 5 | `o-circulo` | seno, cosseno e tangente como **comprimentos**, sobre um chão que se escolhe |
| 6 | `desenrolamento` | o círculo virando gráfico: a altura não muda, a entrada muda de lugar |
| 7 | `taxa` | como a saída muda quando a entrada anda; a secante virando tangente |
| 8 | `o-encontro` | onde os dois sentidos da palavra *tangente* se encontram |

| | fatia | o que mostra |
|---|---|---|
| 1 | `par-vira-ponto` | duas retas numéricas viram um plano; o gráfico é o rastro dos encontros |
| 2 | `o-angulo` | medir uma abertura; graus, radianos, e de onde cai o π |
| 3 | `o-triangulo` | oposto e adjacente dependem de **qual** ângulo; daí o *co* de cosseno |
| 4 | `a-distancia` | o círculo é gerado por uma condição, e a condição é Pitágoras |
| 5 | `o-circulo` | seno, cosseno e tangente como **comprimentos**, sobre um chão que se escolhe |
| 6 | `desenrolamento` | o círculo virando gráfico: a altura não muda, a entrada muda de lugar |
| 7 | `taxa` | como a saída muda quando a entrada anda; a secante virando tangente |
| 8 | `o-encontro` | onde os dois sentidos da palavra *tangente* se encontram |

## O lugar no ciclo maior

Estas fatias são material da **Hipátia**, o componente de ensino do sistema
Ítaca, e nasceram ao lado de uma série de seminários sobre visão computacional
e geometria da imagem. A **norma** que as governa não mora aqui: é a
`norma-de-notacao.md` da Hipátia, §0b.7, que declarou instrumento interativo
como material didático e definiu o que este portão cobra. **O instrumento saiu
para cá; a regra ficou lá.**

O parente próximo é o
[math-prerequisite-map](https://github.com/mateusalkimim/math-prerequisite-map),
de onde vieram o molde deste repositório e a escolha de licença.

## Proveniência e garantias

- **Nada de terceiro aqui dentro.** Nenhuma biblioteca, nenhum framework,
  nenhum ativo baixado. Cada fatia é HTML, CSS e JavaScript escritos para ela,
  desenhando em `canvas`.
- **Zero rede, por contrato e por portão.** O `auditar_fatias.py` reprova
  qualquer `@import`, `src`, `<link>`, `url()` ou `fetch` externo. Um `<a href>`
  clicável é permitido — link é coisa que o leitor escolhe seguir, não coisa
  que a página busca sozinha.
- **Sem telemetria, sem cookie, sem armazenamento.** As fatias não guardam nem
  transmitem nada.
- **Sem dado de cliente, sem material sob NDA, sem segredo.** Não há chave,
  token nem caminho de máquina versionado aqui.

## Como isto se verifica

Cada fatia declara, num manifesto legível por máquina, a sua ordem e os símbolos
pelos quais responde:

```html
<!-- fatia: o-triangulo | ordem: 4 | declara: θ tg sen cos | empresta: — -->
```

O portão cobra:

```bash
python3 auditar_fatias.py --controle
```

Nenhum símbolo gasto sem vir da própria fatia ou de uma **anterior** — herdar de
quem vem depois não é herdar, é supor. Nenhum empréstimo sem alguém depois
pagá-lo. Nenhuma declaração ociosa, que serviria só para silenciar o portão.
Nenhum pedido de rede. E **controle negativo**: o portão injeta defeitos numa
cópia e exige que sejam pegos, porque zero achados só significa alguma coisa se
ele provar que sabe reprovar.

O `index.html` é **gerado** de `gerar_indice.py`, que lê a ordem e a descrição
das próprias fatias. Editar o HTML gerado é o defeito, não o atalho.

## Licença

Código sob **MIT** (`LICENSE`). Conteúdo — texto, figuras, o desenho das
demonstrações — sob **CC BY-SA 4.0** (`LICENSE-CONTENT`).

Reusar é livre, inclusive comercialmente. Derivar exige **manter a mesma
licença** e dar crédito.

O share-alike protege a *expressão*; não protege a ideia, e não se pretende que
proteja. O que crava autoria de um método é a publicação datada — e é por isso
que este repositório existe em vez de uma pasta no disco.

## Estado, e o que falta

O que está de pé: as oito fatias, o portão com controle negativo, o índice
gerado, e a licença por camada.

O que falta, declarado em vez de escondido:

- **a fusão.** As oito são fatias de propósito — pequenas e nítidas, para se
  fundirem bem depois. A fusão ainda não aconteceu, e tem uma pergunta aberta:
  a chave *a onda* do `o-circulo` faz o que o `desenrolamento` faz, e dois
  arquivos desenhando a mesma coisa divergem em silêncio;
- ~~o ramo da ordem~~ — **resolvido em 2026-08-27.** A taxa desceu de segundo
  para sétimo e as três dívidas declaradas dela zeraram. O que resta é a
  distinção, agora escrita: dependência tem dois ramos, leitura é uma fila;
- **QA visual humano.** O portão mede o que é mecânico. Nenhuma fatia foi
  julgada por olho humano contra uma régua estética, e isso não se automatiza;
- **nenhum teste de aprendizagem.** Não se mediu se alguém aprende mais com
  isto. A afirmação deste repositório é sobre o que as figuras *mostram*, não
  sobre efeito medido em estudante.

## Procedência

Nasceu em 2026-08-26/27 como um conjunto de fatias dentro do material da
Hipátia, e saiu para repositório próprio no mesmo movimento em que ganhou norma
e portão.
