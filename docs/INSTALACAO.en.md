<!-- idioma: linha gerada por i18n.py -->
> [!NOTE]
> ### 🇧🇷 **[Leia esta página em português →](INSTALACAO.md)**

# Installation

There is no installation to **use**. The nine slices are self-contained HTML pages:  
download the repository and open the `index.html`. They work offline, without a server  
and without dependencies.

## Use

### Windows

1. download the repository — **Code → Download ZIP** button on GitHub, or  
   `git clone https://github.com/mateusalkimim/seeing-calculus.git`;  
2. extract, if you downloaded the ZIP;  
3. **double-click** on `index.html`.

Any modern browser will do. Do not open it with Internet Explorer.

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

### Without Downloading Anything

<https://mateusalkimim.github.io/seeing-calculus/>

## Develop

Only those who are **editing** the slices need this.

| Tool | For What | Version Tested |
|---|---|---|
| Python 3 | run the check and the index generator | 3.12 |
| Node | the check uses `node --check` to validate the JS of each slice | 24 |

No third-party packages: both scripts use only the standard library.

```bash
python3 auditar_fatias.py --controle   # the check + the negative control  
python3 gerar_indice.py                # regenerates the index.html
```

**The `index.html` is derived.** It is written by `gerar_indice.py` from the manifest, the title, and the call of each slice. Editing it by hand is the bug, not the shortcut: the next generation overwrites it.

## Add a Slice

1. write self-contained HTML, with the block `THESE SLICE` at the top of the  
   `<script>`;  
2. put the manifest on the second line of the file:

```html
   <!-- slice: nome-da-fatia | order: N | declares: θ tg | borrows: — -->
   ```

`declares` are the symbols it responds to; `borrows` are the ones it uses with a warning and that some **subsequent** slice defines;  
3. renumber the orders to continue `1..N` without gaps;  
4. `python3 auditar_fatias.py --controle` — it must give **PASS**;  
5. `python3 gerar_indice.py`.

The check fails if a slice spends a symbol that no earlier slice declared, if a loan is never repaid, if there is an idle declaration, if anything loads an external resource, or if the JavaScript does not compile.