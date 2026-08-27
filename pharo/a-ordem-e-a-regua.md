# A ordem e a régua

Duas ideias que este repositório destila, e que não são espec de implementação:
elas valem para qualquer material didático visual e sobreviveriam se todo o
código aqui fosse jogado fora.

## 1. A raiz de uma sequência visual não é escolha

É tentador tratar a ordem de um curso como preferência pedagógica. Em parte é.
Mas há um degrau em que ela deixa de ser: quando um conceito **precisa** de
outro para sequer existir.

O caso aqui é limpo. Um ângulo é a abertura entre duas semirretas que saem do
mesmo vértice. Em **uma** dimensão existem duas direções e nada entre elas — não
há para onde abrir. Logo **um ângulo já exige duas dimensões**, e qualquer fatia
sobre ângulo pressupõe o plano.

A consequência é que "o que é o plano" não pode ser uma fatia entre outras: é a
raiz, e nenhuma linearização honesta a tira de primeiro. O resto da árvore
*continua* sendo escolha — dois ramos independentes podem ser percorridos em
qualquer ordem — e a diferença entre as duas coisas tem de estar escrita, porque
tratar escolha como necessidade endurece o material à toa, e tratar necessidade
como escolha o quebra.

**Como se descobre isto:** perguntando de cada conceito *"em que dimensão isto
existe?"* e não *"em que ordem eu aprendi?"*.

## 2. Uma figura didática deve poder ser conferida com a régua

A diferença entre ilustrar e demonstrar não está no capricho do desenho — está
em se a afirmação da figura é **medível na própria figura**.

Uma figura que diz "a derivada é a tangente do ângulo" e desenha as duas coisas
em painéis com escalas independentes está pedindo fé. A mesma figura, com os
dois painéis dividindo a **mesma escala e a mesma linha do zero**, transforma a
igualdade em dois segmentos de comprimento igual — e aí o leitor confere.

Três consequências práticas:

- **a escala compartilhada é a afirmação**, não uma comodidade de layout. Quem
  separa em escalas independentes "para caber melhor" destrói o argumento e
  mantém a beleza, que é o pior resultado possível;
- **desenhar direto o que deveria ser resultado de uma construção esconde a
  passagem.** Marcar um ponto onde duas retas se cruzam, sem desenhar as duas
  retas, dá o resultado e some com a razão;
- **a figura pode afirmar o que não é verdade sem mentir em nenhum pixel** —
  basta desenhar duas coisas lado a lado e deixar o leitor supor uma relação.
  Foi o risco de pôr um círculo ao lado do gráfico de uma função qualquer: o
  círculo gera o seno e não gera x², e a proximidade sozinha sugeriria que sim.

**Como se testa:** perguntando *"qual medida na tela ficaria errada se a
afirmação fosse falsa?"*. Se a resposta for "nenhuma", a figura ilustra — e é
legítimo, desde que não se apresente como prova.

## Onde estas duas se encontram

As duas respondem à mesma pergunta por lados diferentes: **o que autoriza uma
figura a afirmar alguma coisa?** A primeira diz que ela não pode gastar o que o
leitor ainda não tem. A segunda, que o que ela gasta tem de estar verificável no
próprio desenho.

O portão deste repositório mecaniza a primeira — herança de símbolo, ordem sem
buraco, empréstimo pago. A segunda **não se mecaniza**: ela é julgamento, e por
isso está aqui, escrita, e não numa medida automática.
