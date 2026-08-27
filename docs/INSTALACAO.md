# Instalação

Não há instalação para **usar**. As oito fatias são páginas HTML autocontidas:
baixe o repositório e abra o `index.html`. Elas funcionam offline, sem servidor
e sem dependência.

## Usar

### Windows

1. baixe o repositório — botão **Code → Download ZIP** no GitHub, ou
   `git clone https://github.com/mateusalkimim/seeing-calculus.git`;
2. extraia, se baixou o ZIP;
3. **duplo clique** em `index.html`.

Qualquer navegador moderno serve. Não abra pelo Internet Explorer.

### Linux

```bash
git clone https://github.com/mateusalkimim/seeing-calculus.git
cd seeing-calculus
xdg-open index.html
```

### macOS

```bash
git clone https://github.com/mateusalkimim/seeing-calculus.git
cd seeing-calculus
open index.html
```

### Sem baixar nada

<https://mateusalkimim.github.io/seeing-calculus/>

## Desenvolver

Só quem for **editar** as fatias precisa disto.

| Ferramenta | Para quê | Versão testada |
|---|---|---|
| Python 3 | rodar o portão e o gerador do índice | 3.12 |
| Node | o portão usa `node --check` para validar o JS de cada fatia | 24 |

Nenhum pacote de terceiro: os dois scripts usam só a biblioteca padrão.

```bash
python3 auditar_fatias.py --controle   # o portão + o controle negativo
python3 gerar_indice.py                # regera o index.html
```

**O `index.html` é derivado.** Ele é escrito pelo `gerar_indice.py` a partir do
manifesto, do título e da chamada de cada fatia. Editá-lo à mão é o defeito, não
o atalho: a próxima geração apaga.

## Acrescentar uma fatia

1. escreva o HTML autocontido, com o bloco `TESE DESTA FATIA` no topo do
   `<script>`;
2. ponha o manifesto na segunda linha do arquivo:

   ```html
   <!-- fatia: nome-da-fatia | ordem: N | declara: θ tg | empresta: — -->
   ```

   `declara` são os símbolos pelos quais ela responde; `empresta` são os que ela
   gasta com aviso e que alguma fatia **posterior** define;
3. renumere as ordens para continuarem `1..N` sem buraco;
4. `python3 auditar_fatias.py --controle` — tem de dar **PASSA**;
5. `python3 gerar_indice.py`.

O portão reprova se a fatia gastar símbolo que nenhuma fatia anterior declarou,
se um empréstimo nunca for pago, se houver declaração ociosa, se algo carregar
recurso externo, ou se o JavaScript não compilar.
