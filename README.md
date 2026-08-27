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
python3 gerar_indice.py                # regera o index e a navegação das nove
```

Passo a passo por sistema operacional em [`docs/INSTALACAO.md`](docs/INSTALACAO.md).

## O que tem aqui

**Uma cor, um papel** — a regra que amarra as nove: *azul = ao longo da
referência* (`x`, cateto adjacente, cosseno) · *terracota = perpendicular a ela*
(`y`, cateto oposto, seno, a taxa). As exceções estão declaradas em
[`pharo/ux-de-explicacao-interativa.md`](pharo/ux-de-explicacao-interativa.md),
que também traz o levantamento de domínio por trás das decisões de interface.

```
index.html            a porta — GERADO por gerar_indice.py, não editar à mão
par-vira-ponto.html   ┐
taxa.html             │
o-angulo.html         │
o-triangulo.html      ├ as nove fatias, na ordem do manifesto de cada uma
a-distancia.html      │
o-circulo.html        │
desenrolamento.html   │
o-encontro.html       │
a-familia.html        ┘
gerar_indice.py       lê as fatias, escreve o index E injeta a navegação
auditar_fatias.py     o portão: ordem, herança de símbolo, rede, JS
conferir_layout.py    o outro portão: a coluna, o quadro do desenho, o transbordo
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

A **navegação** de cada fatia é gerada da mesma ordem — anterior, posição na
fila, próxima — e injetada num bloco marcado. Reordenar as fatias reescreve as
nove de uma vez, e o portão reprova se a posição anunciada divergir do
manifesto. Ela vai **inline**, e não num `nav.js`, porque cada fatia **abre
sozinha**: um arquivo solto por e-mail tem de continuar funcionando.

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

O que está de pé: as **nove** fatias, o portão com controle negativo, o índice
gerado, e a licença por camada.

A nona, **a família** (2026-08-27), fecha um par com a **taxa**: aquela vai de
*regra para curva* — escolhe-se o nome num botão e vê-se o desenho; esta vai de
*curva para regra* — a curva aparece **sem nome**, e quem levanta a taxa é o
leitor, arrastando. Escolher o nome num menu e ver a taxa é reconhecimento com a
resposta dada; a direção inversa é a que não dá para decorar. O passo `h` é
regulável de propósito: nas famílias ele quase não muda a resposta, no bico e no
salto muda tudo — e é assim que a fatia mostra, sem dizer, que **medir não
prova**. As onze curvas de família foram conferidas em código: classificar cada
uma só pelo que a taxa medida faz devolve o rótulo certo nas onze, estável entre
`h = 0,03` e `h = 0,6`. A estação irmã, no deck, é a **Estação 5 · a família** do
C2, que paga o item v do registro da §1.2b da norma de notação.

O que falta, declarado em vez de escondido:

- ~~cada fatia era um beco sem saída~~ — **resolvido em 2026-08-27**: navegação
  e posição na fila, geradas da mesma ordem que o portão cobra;
- ~~rótulos vivendo só na tabela~~ — **resolvido em 2026-08-27** no
  `o-circulo`, o único caso: cosseno, seno e arco passaram a ter nome colado no
  traço;
- ~~a página saltava entre fatias~~ — **resolvido em 2026-08-27**: moldura de
  640 nas oito primeiras, com cada composição centrada e intocada;
- **a fusão.** As oito são fatias de propósito — pequenas e nítidas, para se
  fundirem bem depois. A primeira sobreposição examinada foi *a onda* do
  `o-circulo` × o `desenrolamento`. Eu cortei a onda por ela zerar o chão, e o
  **autor reverteu** — com razão, e por um motivo que a minha análise não
  alcançava: a onda é **recurso metodológico**, ela forma a imagem mental do
  fenômeno, e ver a curva *sendo desenhada* enriquece o entendimento. Coerência
  estrutural não é a única régua de uma folha didática. Ao repor apareceu o que
  o corte tinha escondido: **a versão antiga nunca desenhou a curva
  progressivamente** — pintava a senoide inteira de uma vez, e o `rastro` estava
  declarado e nunca usado, com a prosa afirmando um comportamento que o código
  não tinha. Agora a curva é traçada de −6,2 até o ângulo de agora: animar
  desenha, arrastar o ângulo faz o traço avançar e recuar. As duas folhas ficam,
  e a diferença está dita nas duas: aqui a **imagem** do fenômeno, com o eixo
  comprimido e declarado; no `desenrolamento`, a mesma passagem **em escala**,
  com arco e tangente. Os próximos contatos a examinar são o triângulo desenhado
  no `o-circulo` × `o-triangulo`, e a reta tangente, que aparece em três folhas;
- ~~o ponto T sai da moldura~~ — **resolvido em 2026-08-27**, e o conserto virou
  conteúdo. O corte antigo era `|r·tg| < 2,6`: a tangente simplesmente
  **desaparecia** quando ficava grande, que é exatamente quando ela está fazendo
  o que a folha quer mostrar. Uma varredura de 73.200 combinações mediu o T fora
  da moldura em **23% delas** — todas com a tangente sumindo calada. Agora ela é
  cortada **na borda**, com ponta de seta e o valor à mostra: o corte deixou de
  esconder a assíntota e passou a mostrá-la. A varredura confirma 0 pontos fora
  do quadro depois do corte;
- ~~o ramo da ordem~~ — **resolvido em 2026-08-27.** A taxa desceu de segundo
  para sétimo e as três dívidas declaradas dela zeraram. O que resta é a
  distinção, agora escrita: dependência tem dois ramos, leitura é uma fila;
- ~~a folha ocupava o monitor inteiro~~ — **resolvido em 2026-08-27**, e a
  correção veio do autor com a tela na mão. Num monitor de 1900 px o desenho
  abria com **1848 × 954** e o título e o texto viravam legenda de uma figura
  gigante; o texto de cima dizia a tese e parava, sem dizer o que fazer com as
  mãos. Agora quem manda é a prosa: uma medida só (`--col`, 620 px, cerca de 80
  caracteres por linha) para o título e todos os blocos de texto — larguras
  diferentes com margem automática dariam bordas esquerdas desalinhadas —, texto
  **justificado e centrado**, e o desenho num quadro de **1100 × 568**. Cada
  folha ganhou um bloco **Faça**, que nomeia um por um os controles que
  existem nela;
- ~~o quadro do desenho era o mesmo nas nove~~ — **resolvido em 2026-08-27.**
  Era 1240 × 640 em todas, e para uma composição quase quadrada isso deixava
  centenas de pixels de vazio dos dois lados. Agora **cada fatia tem a proporção
  do próprio desenho**, e o número não é palpite: um navegador varre todos os
  controles de cada folha e mede o que a composição de fato ocupa; o quadro é
  esse retângulo com 28 px de folga. O vazio caiu de 43% para 15% no
  `par-vira-ponto`, e de 38% para 16% no `o-triangulo`. Na tela a **altura é
  fixa** (568 px) e é a largura que conta a forma — de 658 px na mais quadrada a
  1100 px nas de gráfico —, e os controles ficam alinhados com o quadro, não com
  a página. A medida também corrigiu duas suposições minhas: o `o-circulo`
  *parecia* pequeno e na verdade usa 1226 dos 1240 px; e as cinco fatias largas
  enchem o quadro **por construção**, porque desenham grandezas que vão ao
  infinito e são cortadas de propósito na borda;
- o `conferir_layout.py` mede tudo isso num navegador de verdade — coluna,
  centramento, proporção, controles e transbordo — e tem controle negativo:
  desfazer a largura da página reproduz os 954 px, e soltar os controles do
  quadro reprova. Ele nunca devolve "ok" por ausência de prova;
- **QA visual humano.** Os dois portões medem o que é mecânico. Nenhuma fatia foi
  julgada por olho humano contra uma régua estética, e isso não se automatiza;
- **nenhum teste de aprendizagem.** Não se mediu se alguém aprende mais com
  isto. A afirmação deste repositório é sobre o que as figuras *mostram*, não
  sobre efeito medido em estudante.

## Procedência

Nasceu em 2026-08-26/27 como um conjunto de fatias dentro do material da
Hipátia, e saiu para repositório próprio no mesmo movimento em que ganhou norma
e portão.
