# pygments-sysml

A [Pygments](https://pygments.org/) syntax highlighter for **SysML v2** textual notation (`.sysml` / `.kerml` files).

Derived from the ANTLR4 grammar at [daltskin/sysml-v2-grammar](https://github.com/daltskin/sysml-v2-grammar), which tracks the OMG SysML v2 specification (release 2026-01).

## Installation

```bash
pip install pygments-sysml   # once published to PyPI
# or directly:
pip install .
```

## Usage

### Command line (via Pygments `pygmentize`)

```bash
pygmentize -l sysml model.sysml
pygmentize -l sysml -f html -O full -o model.html model.sysml
```

### Python API

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter, Terminal256Formatter
from sysml_lexer import SysMLLexer

code = open("model.sysml").read()

# Terminal output
print(highlight(code, SysMLLexer(), Terminal256Formatter(style="monokai")))

# HTML output
html = highlight(code, SysMLLexer(), HtmlFormatter(style="github-dark"))
```

### Sphinx / MyST

In `conf.py`, just import the lexer before Sphinx starts:

```python
from sysml_lexer import SysMLLexer  # noqa: F401 — registers itself
```

Then in your `.rst` or `.md`:

    ```sysml
    package Demo {
        part def Vehicle { attribute mass : Real; }
    }
    ```

### LaTeX (minted)

To use this lexer with the [`minted`](https://github.com/gpoore/minted) package in LaTeX:

1. Install the lexer package alongside Pygments (which `minted` already requires):
   ```bash
   pip install pygments-sysml
   ```

2. Use `sysml` as the language in your `minted` block:
   ```latex
   \documentclass{article}
   \usepackage{minted}

   \begin{document}

   \begin{minted}{sysml}
   package Demo {
       part def Vehicle {
           attribute mass   : Real;
           attribute length : Real;
           port fuelIn      : ~FuelPort;
       }
   }
   \end{minted}

   \end{document}
   ```

3. Compile with `-shell-escape`:
   ```bash
   pdflatex -shell-escape document.tex
   ```

### MkDocs

With the [`mkdocs-pygments`](https://github.com/mkdocs/mkdocs-pygments) plugin (included by default in MkDocs Material):

1. Install the lexer package in the same environment as MkDocs:
   ```bash
   pip install pygments-sysml
   ```

2. The lexer is auto-discovered by Pygments — just start using `sysml` fenced code blocks in your Markdown:

   ````markdown
   ```sysml
   package Demo {
       part def Vehicle {
           attribute mass : Real;
       }
   }
   ```
   ````

3. If you use a custom `mkdocs.yml` with the Pygments plugin:
   ```yaml
   markdown_extensions:
     - pymdownx.highlight:
         use_pygments: true
   ```

No extra configuration is needed — the entry point registered in `pyproject.toml` makes Pygments find the lexer automatically at runtime.

## Token mapping

| ANTLR grammar token category | Pygments token |
|---|---|
| Declaration keywords (`part`, `action`, `attribute` …) | `Keyword.Declaration` |
| Namespace keywords (`package`, `import`, `library` …) | `Keyword.Namespace` |
| Type-system keywords (`specializes`, `redefines`, `subsets` …) | `Keyword.Type` |
| Value literals (`true`, `false`, `null`) | `Keyword.Constant` |
| Doc/annotation keywords (`doc`, `comment`, `rep` …) | `Keyword.Reserved` |
| Operators (`->`, `::`, `:>`, `:>>`, `@@`, …) | `Operator` |
| `/* … */` block comments | `Comment.Multiline` |
| `/** … */` doc comments | `Comment.Special` |
| `// …` line comments | `Comment.Single` |
| Double-quoted strings | `String` |
| Integers / floats / hex / binary | `Number.*` |
| Identifiers | `Name` |

## Tuning / extending

- **Add missing keywords**: add them to the appropriate tuple near the top of `sysml_lexer.py`.
- **Contextual keywords**: SysML v2 has words that are keywords only in certain positions (e.g. `to`, `of`, `by`). They are classified as `Keyword.Type` here; if you need them to be plain `Name` in other contexts, switch to a stateful lexer with Pygments `using()` or `combined()` states.
- **Style overrides**: any Pygments style works. The token hierarchy means `Keyword` styles cascade to all keyword sub-types, so minimal custom CSS is needed.

## License

MIT — lexer code © 2026 Jon R. Fox.  
SysML v2 grammar © OMG / J Dalton, MIT licence.
