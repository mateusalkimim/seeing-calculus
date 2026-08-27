# Ver o cálculo

**Oito instrumentos interativos, em ordem.** Cada um mostra *uma* coisa, abre
sozinho no navegador e funciona **offline** — sem instalação, sem rede, sem
conta.

No ar em <https://mateusalkimim.github.io/seeing-calculus/>.

## O que isto é, e o que não é

Não são ilustrações do que um texto já disse. São o lugar onde a afirmação pode
ser **conferida com a régua**: quando duas coisas têm o mesmo comprimento, elas
têm o mesmo comprimento na tela, e você mede.

Um exemplo do que isso quer dizer na prática. A folha `o-encontro` afirma que a
derivada é a tangente do ângulo que a reta tangente faz com o eixo. Em vez de
escrever a igualdade e pedir fé, ela desenha o círculo e a curva **na mesma
escala e sobre a mesma linha do zero** — e então o segmento de tangente do
círculo e o cateto do triângulo sobre a curva *são* dois comprimentos iguais em
pixels. Medidos: 113 e 111, e a diferença é o disco na ponta de um deles.

## A ordem, e por que ela não é livre

Uma dimensão só tem posição — não há para onde curvar. É a segunda que
desbloqueia a forma, e é por isso que **o par vira ponto** é a raiz e não um
começo entre outros: até um ângulo precisa de duas dimensões para existir.

```
                    par-vira-ponto            a raiz
              ┌───────────┴───────────┐
           a taxa       o ângulo → o triângulo → a distância → o círculo
              └───────────┬───────────┘
              o desenrolamento → o encontro
```

Depois da raiz a árvore abre em dois ramos — função e medida — que só se
encontram no fim. O que é livre é o ramo: a taxa pode vir antes ou depois da
corrente da medida. **A raiz não é livre.**

| | fatia | o que mostra |
|---|---|---|
| 1 | `par-vira-ponto` | duas retas numéricas viram um plano; o gráfico é o rastro dos encontros |
| 2 | `taxa` | como a saída muda quando a entrada anda; a secante virando tangente |
| 3 | `o-angulo` | medir uma abertura; graus, radianos, e de onde cai o π |
| 4 | `o-triangulo` | oposto e adjacente dependem de **qual** ângulo; daí o *co* de cosseno |
| 5 | `a-distancia` | o círculo é gerado por uma condição, e a condição é Pitágoras |
| 6 | `o-circulo` | seno, cosseno e tangente como **comprimentos**, sobre um chão que se escolhe |
| 7 | `desenrolamento` | o círculo virando gráfico: a altura não muda, a entrada muda de lugar |
| 8 | `o-encontro` | onde os dois ramos se juntam |

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

## Procedência

Nasceu em 2026-08-26/27 como um conjunto de fatias dentro do material da
Hipátia, e saiu para repositório próprio no mesmo movimento em que ganhou norma
e portão. Nenhuma delas usa biblioteca de terceiro: são canvas e aritmética.
