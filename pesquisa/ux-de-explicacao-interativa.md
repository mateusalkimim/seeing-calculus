# UX de explicação interativa — levantamento de domínio

Pesquisa de base para o `seeing-calculus`. Não é spec e não é roteiro de
implementação: é o que a área já sabe, o que dela se aplica aqui, e o que ainda
precisa ser verificado contra fonte.

## Proveniência — leia isto antes do resto

Marcas, no molde da norma de notação que o autor mantém:

- `(m)` **medido aqui** — número obtido do próprio repositório;
- `(b)` **síntese** — inferência a partir do que está medido;
- `(c)` **a verificar** — afirmação que eu sustento de conhecimento, e que
  **não foi conferida contra fonte**. O acervo de que disponho não tem estante
  de educação nem de interação humano-computador.

⚠️ **Toda a seção bibliográfica é `(c)`.** Ela é útil como mapa de onde
procurar, e **não** como warrant. Este repositório publica figuras cuja
afirmação se confere com a régua; um documento de pesquisa dele não pode ter
padrão menor. A lista do fim diz o que verificaria cada ponto.

---

## 1. O que a medida daqui diz `(m)`

Levantado em 2026-08-27, sobre as oito fatias:

- **32 cores no total; apenas 10 presentes em todas.** As dez comuns são o
  cromo (fundos, texto, ouro de destaque). As **semânticas divergem**;
- **o mesmo terracota `#e8654f` carrega quatro papéis** ao longo da fila: `x`
  (par-vira-ponto), *cateto oposto* (o-triangulo), `x` de novo (a-distancia),
  *seno* (o-circulo, desenrolamento) e *a taxa* `f′` (taxa). O azul e o verde
  fazem o mesmo;
- **alturas de canvas entre 520 e 640 px** — a página salta de uma fatia para
  a outra;
- **metade tem tabela de leitura abaixo do desenho, metade não**;
- **nenhuma fatia tem navegação para a seguinte**, nem indicação de posição na
  fila. Cada uma é um beco sem saída.

**A conclusão que a medida força** `(b)`: a amarração entre as fatias que o
repositório afirma existir — "as cores são as mesmas de propósito" — é **local
e não global**. O par `o-triangulo → o-circulo` amarra de fato; o resto
contradiz. É o defeito que a própria série ensina a evitar: um significante,
vários significados, sem aviso.

---

## 2. A linhagem do gênero `(c)`

O que segue é **onde procurar**, não o que está provado.

**Bret Victor** é a raiz declarada do gênero. *Explorable Explanations* (2011)
propõe que o leitor possa manipular o modelo do autor em vez de só receber a
conclusão. *Up and Down the Ladder of Abstraction* é, na forma, a mesma coisa
que este repositório: o leitor sobe e desce entre o caso concreto e a regra
geral, e **a interface é a escada**. *Kill Math* argumenta que a notação
algébrica é uma interface de usuário ruim para a maioria das pessoas — tese
discutível e produtiva.

**Nicky Case** transformou aquilo em gênero praticável: *playable posts*, e o
*Parable of the Polygons* (com Vi Hart) como caso em que **a interação é o
argumento**, não sua ilustração.

**Distill.pub** estabeleceu o padrão de rigor para comunicação científica
interativa — cada controle existe porque a afirmação precisa dele.

**Red Blob Games (Amit Patel)** é o parente prático mais próximo: páginas
tutoriais em que **todo** diagrama é vivo e nenhum é enfeite.

**Mike Bostock** (*Visualizing Algorithms*, D3) e **Steven Wittens**
(acko.net, MathBox) marcam o teto de artesanato.

**3Blue1Brown** com uma ressalva que o próprio autor faz e que importa para a
tese: **animação pode produzir ilusão de entendimento** — assiste-se, acha-se
belo, e não se sabe fazer. É a diferença entre assistir e mexer, e as fatias
estão do lado de mexer.

**Seymour Papert**, *Mindstorms*, é a fundação teórica: raciocínio
**body-syntonic** — entende-se identificando-se com o objeto. As fatias já têm
um ponto que a pessoa move; ela **é** o ponto. Isso não foi projetado a partir
de Papert, e chegar no mesmo lugar por conta própria é sinal de que o caminho
é natural, não de que a teoria é dispensável.

---

## 3. A literatura da restrição — e por que ela importa mais aqui `(c)`

A exigência do autor foi: *"nada muito chamativo, nada que roube a atenção
do que está sendo ensinado"*.

**Isso não é preferência estética: é a conclusão empírica da área**, e tem
nome. O corpo de trabalho de **Richard Mayer** sobre aprendizagem multimídia
descreve um **princípio da coerência** — acrescentar material interessante mas
irrelevante **reduz** a aprendizagem, não é neutro. O efeito é chamado de
**seductive details**.

Dois outros princípios da mesma linhagem são diretamente acionáveis aqui:

- **contiguidade espacial** — o rótulo fica *junto* da coisa que nomeia, não em
  legenda separada;
- **sinalização** — destacar o essencial ajuda; destacar o acessório atrapalha.

E a **teoria de carga cognitiva** (Sweller) nomeia o custo do arranjo atual: o
**efeito de atenção dividida**, que aparece quando o leitor precisa integrar
duas fontes separadas no espaço. **As tabelas de leitura abaixo do canvas são
exatamente isso** `(b)` — o olho vai e volta, e o percurso não ensina nada.

---

## 4. O que fazer com isto, em ordem `(b)`

1. **um significado por cor, em toda a fila.** Onde o papel muda de fatia, a
   cor muda com aviso explícito — a regra R2 da norma de notação, aplicada à
   cor em vez de à letra;
2. ~~rótulo dentro do desenho~~ — **feito em 2026-08-27**, e o levantamento
   achou **um** caso real, não quatro: só no `o-circulo` havia elemento
   desenhado cujo nome existia apenas na tabela — `cosseno`, `seno` e `arco`.
   O leitor tinha de mapear "o segmento azul" para uma linha lá embaixo. Os
   três ganharam nome e comprimento colados no próprio traço, girando com o
   chão. **A tabela ficou**, porque ali a comparação *comprimento × razão*
   **é** o conteúdo, e isso uma tabela faz melhor que um desenho — contiguidade
   espacial não manda abolir tabela, manda não usar tabela para o que é
   rótulo;
3. **navegação e posição na fila** em cada fatia — hoje cada uma é um beco sem
   saída, e a ordem que a verificação garante não chega ao leitor;
4. ~~altura de canvas constante~~ — **feita em 2026-08-27**. As oito passam a
   ter moldura de **640** (a maior das composições, para nenhuma ser cortada), e
   **nenhuma coordenada de desenho foi tocada**: cada composição mantém a
   própria altura interna e é **centrada** na moldura por um `translate`. Mexer
   nas coordenadas para caber teria sido reescrever oito desenhos para resolver
   um problema de moldura.

Nada disto acrescenta elemento novo. Os quatro **removem** ruído ou **reaproveitam**
o que já existe, que é o que a coerência pede.

---

## 4b. A regra de cor, resolvida em 2026-08-27 `(m)`

A colisão medida na §1 foi corrigida com **uma frase**, e ela cobre a fila
inteira:

> **azul = ao longo da referência · terracota = perpendicular a ela.**

| cor | papel, e só ele |
|---|---|
| `#78c4ff` azul | `x` · cateto **adjacente** · **cosseno** |
| `#e8654f` terracota | `y` · cateto **oposto** · **seno** · a taxa `f′` |
| `#9b8ec4` violeta | **a curva** — o objeto sobre o qual se mede, que não é componente de nada |
| `#6fbf6a` verde | **o arco** |
| `#e8e2d6` creme | **hipotenusa** e **raio** — a coisa inteira |
| `#41638f` azul-escuro | **o chão**, a referência declarada |
| `#c9a266` ouro | a **tangente** — comprimento e reta — e o ângulo θ |

**Duas exceções declaradas**, porque exceção calada é o defeito que isto veio
corrigir:

- o **ouro** também é o destaque de interface (botão ativo, cursor). A colisão é
  fraca: cromo fica fora do canvas, e ninguém confunde um botão com uma reta;
- no **`o-encontro`** o cateto que sobe é dourado, não terracota — porque a tese
  daquela fatia é que ele **é** o segmento de tangente. A troca é o argumento, e
  está dita na própria página.

**A regra achou defeitos que ninguém tinha visto** `(m)`: o cateto "anda 1" era
creme na `taxa` e usava a cor da curva no `o-encontro`, onde a variável `--adj`
estava declarada e **morta**. Nos dois casos ele é o cateto adjacente. Uma regra
de cor que não acha nada não estava faltando.

⚠️ **Divergência com os decks, declarada**: as figuras do C1 usam
`x` = terracota e `y` = verde. Aqui `x` é azul e `y` é terracota, porque a
regra que unifica as oito fatias é *ao longo × perpendicular*, e ela é mais
forte que a convenção de eixo. **Os dois artefatos divergem de propósito**, e
quem usar os dois junto precisa saber.

---

## 5. A matemática como interface — o jeito certo e o errado `(b)`

Ideia do autor: usar os conceitos do próprio cálculo como material de
interação, para que no fim o aluno perceba *"então era isso que estava
acontecendo na minha tela"*.

**O jeito errado** é acrescentar movimento bonito que, por baixo, é uma
derivada. Isso é *seductive detail* com desculpa matemática: cobra atenção e
não ensina.

**O jeito certo**: toda transição **já tem** uma curva de tempo. Ela existe de
qualquer forma. Então não se acrescenta matemática — torna-se **honesta** a
matemática que já está lá, e revela-se **no fim**.

O botão *animar* já varre a um ritmo constante: isso já é uma derivada
constante. Uma transição com aceleração é um \(f'\) não constante — e na fatia
da taxa o aluno pode **apontar o instrumento para a própria animação do site**.

Custo de atenção: **zero**, porque a transição já existia. E a revelação vem
depois, nunca durante — durante seria a distração que o princípio da coerência
proíbe.

---

## 6. O que verificaria cada ponto

Nada disto está no acervo. Para tirar as marcas `(c)`:

| afirmação | o que a fecharia |
|---|---|
| princípio da coerência, *seductive details* | Mayer, *Multimedia Learning* (Cambridge) — e os artigos originais de Garner et al. sobre detalhes sedutores |
| atenção dividida, carga cognitiva | Sweller, Ayres & Kalyuga, *Cognitive Load Theory* |
| contiguidade espacial e sinalização | idem Mayer, capítulos por princípio |
| raciocínio body-syntonic | Papert, *Mindstorms*, cap. 2 |
| a tese da escada de abstração | Victor, *Up and Down the Ladder of Abstraction* (ensaio no site do autor) |
| interação como argumento | Case & Hart, *Parable of the Polygons*; ensaios do Distill |

**Enquanto essas marcas forem `(c)`, este documento orienta a produção e não
sustenta afirmação pública.** É a mesma regra que o `abstraction-ladder` aplica
a arestas, aplicada aqui a si mesmo.
