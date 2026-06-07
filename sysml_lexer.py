"""
SysML Pygments Lexer
====================
Derived from the ANTLR4 grammar by daltskin/sysml-v2-grammar
(https://github.com/daltskin/sysml-v2-grammar), which is itself
an automatic translation of the OMG SysML v2 KEBNF specification
grammar (release tag 2026-01).

Usage
-----
Standalone::

    from sysml_lexer import SysMLLexer
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    code = open("model.sysml").read()
    print(highlight(code, SysMLLexer(), HtmlFormatter()))

As a registered Pygments plugin — add to pyproject.toml::

    [project.entry-points."pygments.lexers"]
    sysml = "sysml_lexer:SysMLLexer"

License: MIT
"""

from pygments.lexer import RegexLexer, bygroups, words, include
from pygments.token import (
    Text, Whitespace, Comment, Keyword, Name, String,
    Number, Punctuation, Operator, Error, Literal,
)

__all__ = ["SysMLLexer"]


# ---------------------------------------------------------------------------
# Token-category helpers (aliases for readability below)
# ---------------------------------------------------------------------------
KW   = Keyword
KWD  = Keyword.Declaration   # declaration keywords  (part def, action def …)
KWT  = Keyword.Type          # type-system keywords  (redefines, subsets …)
KWN  = Keyword.Namespace     # namespace keywords    (package, library …)
KWR  = Keyword.Reserved      # reserved / special    (about, doc, rep …)


class SysMLLexer(RegexLexer):
    """
    Pygments lexer for SysML v2 textual notation.

    Covers the full keyword set from the daltskin/sysml-v2-grammar ANTLR4
    lexer grammar, which tracks the OMG SysML v2 specification.
    """

    name     = "SysML"
    aliases  = ["sysml", "sysmlv2", "sysml-v2"]
    filenames = ["*.sysml", "*.kerml"]
    mimetypes = ["text/x-sysml"]

    # -----------------------------------------------------------------------
    # Keyword sets  (extracted from SysMLv2Lexer.g4)
    # -----------------------------------------------------------------------

    # Primary declaration keywords
    _decl_keywords = (
        "abstract", "action", "actor", "alias", "all", "allocation",
        "analysis", "as", "attribute", "bind", "calc", "case",
        "concern", "connect", "connection", "constraint", "def",
        "defined", "dependency", "do", "else", "end", "entry",
        "enum", "exhibit", "exit", "expose", "filter", "first",
        "flow", "fork", "frame", "if", "implies", "in", "include",
        "individual", "inout", "item", "join", "language", "merge",
        "message", "metadata", "occurrence", "out", "parallel",
        "part", "perform", "port", "private", "protected", "public",
        "readonly", "ref", "render", "rendering", "rep", "require",
        "requirement", "return", "satisfy", "send", "snapshot",
        "stake", "stakeholder", "state", "subject", "succession",
        "then", "timeslice", "transition", "until", "use", "variation",
        "verification", "verify", "view", "viewpoint", "when",
        "while", "write",
    )

    # Namespace / structural keywords
    _ns_keywords = (
        "import", "library", "namespace", "package", "standard",
    )

    # Type-system / specialisation keywords
    _type_keywords = (
        "about", "by", "conjugates", "conjugated", "differences",
        "disjoint", "featured", "features", "from", "hastype",
        "intersects", "istype", "of", "ordered", "redefines",
        "references", "renames", "specializes", "subclassifier",
        "subsets", "typed", "unions", "variation",
    )

    # Boolean / value literals that are keywords in SysML v2
    _value_keywords = (
        "true", "false", "null",
    )

    # Occurrence / temporal keywords
    _occurrence_keywords = (
        "at", "during", "start",
    )

    # Annotation / documentation keywords
    _doc_keywords = (
        "comment", "doc", "locale", "rep",
    )

    # -----------------------------------------------------------------------
    # Token rules
    # -----------------------------------------------------------------------
    tokens = {
        "root": [
            # --- Whitespace ------------------------------------------------
            (r"\s+", Whitespace),

            # --- Comments --------------------------------------------------
            # Single-line  //
            (r"//.*?$", Comment.Single),
            # Documentation  /** … */  (must precede block comment rule)
            (r"/\*\*", Comment.Special, "doc_comment"),
            # Block  /* … */
            (r"/\*", Comment.Multiline, "block_comment"),

            # --- String literals -------------------------------------------
            # Regular double-quoted strings
            (r'"', String, "string_dq"),
            # Single-quoted strings (used in some annotation bodies)
            (r"'", String, "string_sq"),

            # --- Number literals -------------------------------------------
            # Real / float (must come before integer rule)
            (r"\d[\d_]*\.\d[\d_]*(?:[eE][+\-]?\d[\d_]*)?", Number.Float),
            (r"\d[\d_]*[eE][+\-]?\d[\d_]*", Number.Float),
            # Integer (decimal, hex 0x…, binary 0b…, octal 0o…)
            (r"0[xX][0-9a-fA-F][\w]*", Number.Hex),
            (r"0[bB][01][\w]*",         Number.Bin),
            (r"0[oO][0-7][\w]*",        Number.Oct),
            (r"\d[\d_]*",               Number.Integer),

            # --- Keywords (longest-match: must come before Name rule) -------
            (
                words(_decl_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword.Declaration,
            ),
            (
                words(_ns_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword.Namespace,
            ),
            (
                words(_type_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword.Type,
            ),
            (
                words(_value_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword.Constant,
            ),
            (
                words(_occurrence_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword,
            ),
            (
                words(_doc_keywords, prefix=r"\b", suffix=r"\b"),
                Keyword.Reserved,
            ),

            # --- Multi-character operators (must precede single-char) -------
            # Arrows and connectors
            (r"->|<-|=>|~>",              Operator),
            # Comparison / equality
            (r"[=!<>]=?",                 Operator),
            # Range
            (r"\.\.",                     Operator),
            # Metaclass / annotation  @@
            (r"@@",                       Operator),
            # Namespace separator
            (r"::",                       Operator),
            # Typing colon  :>  (specialisation)
            (r":>",                       Operator),
            # Subsetting  :>>
            (r":>>",                      Operator),
            # Conjugation  ~
            (r"~",                        Operator),
            # Arithmetic
            (r"[+\-*/%^&|]",             Operator),
            # Single dot (feature access)
            (r"\.",                       Operator),
            # At-sign (used in occurrence expressions)
            (r"@",                        Operator),

            # --- Punctuation -----------------------------------------------
            (r"[{}()\[\];:,#]",           Punctuation),

            # --- Identifiers and qualified names ----------------------------
            # Restricted names  'foo bar'  (backtick-quoted in some tools,
            # but SysML v2 uses single-quotes around names with spaces)
            (r"`[^`]*`",                  Name),
            # Unrestricted names enclosed in single-quotes (KerML style)
            # already handled in string_sq state above; overlaps resolved
            # by ordering — ordinary unquoted names follow.
            (r"[A-Za-z_\u00C0-\u00FF][\w\u00C0-\u00FF]*", Name),

            # Catch-all for any unrecognised character
            (r".",                         Error),
        ],

        # -------------------------------------------------------------------
        # Block comment state  /* … */
        # -------------------------------------------------------------------
        "block_comment": [
            (r"[^*/]+",   Comment.Multiline),
            (r"\*/",      Comment.Multiline, "#pop"),
            (r"[*/]",     Comment.Multiline),
        ],

        # -------------------------------------------------------------------
        # Doc comment state  /** … */
        # -------------------------------------------------------------------
        "doc_comment": [
            (r"[^*/]+",   Comment.Special),
            (r"\*/",      Comment.Special, "#pop"),
            (r"[*/]",     Comment.Special),
        ],

        # -------------------------------------------------------------------
        # Double-quoted string state
        # -------------------------------------------------------------------
        "string_dq": [
            # Escape sequences: \n \t \\ \" \uXXXX etc.
            (r'\\(?:[nrtbf\\"\'\\]|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})',
             String.Escape),
            (r'[^"\\]+', String),
            (r'"',        String, "#pop"),
        ],

        # -------------------------------------------------------------------
        # Single-quoted string state (annotation body / locale strings)
        # -------------------------------------------------------------------
        "string_sq": [
            (r"\\(?:[nrtbf\\'\"\\]|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})",
             String.Escape),
            (r"[^'\\]+", String),
            (r"'",        String, "#pop"),
        ],
    }


# ---------------------------------------------------------------------------
# Quick self-test  (run: python sysml_lexer.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import textwrap
    from pygments import highlight
    from pygments.formatters import Terminal256Formatter

    SAMPLE = textwrap.dedent("""\
        /**
         * A simple vehicle model demonstrating SysML v2 textual notation.
         */
        package Demo {
            import ScalarValues::*;

            /** Vehicle part definition */
            part def Vehicle {
                // Physical attributes
                attribute mass   : Real;
                attribute length : Real;

                // Ports for connections
                port fuelIn  : ~FuelPort;
                port powerOut : ElectricalPort;

                // Subsystems
                part engine  : Engine [1];
                part chassis : Chassis [1];

                // Internal flow
                flow of Fuel from engine to fuelIn;

                // Constraint
                constraint massConstraint { mass < 5000.0 [kg] }
            }

            part def Engine specializes PowerSource {
                attribute power : Real;
                attribute efficiency : Real = 0.85;
                attribute on : Boolean = false;
            }

            action def StartEngine {
                in  part eng : Engine;
                out attribute started : Boolean;
                then perform eng.ignite();
            }

            requirement def SafetyRequirement {
                subject vehicle : Vehicle;
                doc /* The vehicle shall not exceed maximum speed. */
                satisfy by vehicle.speed <= 250 [km/h];
            }

            // Enumeration
            enum def FuelType {
                enum Gasoline;
                enum Diesel;
                enum Electric;
            }

            // Allocate subsystem to physical component
            allocation alloc1 : Allocation {
                allocate engine to physicalEngine;
            }
        }
    """)

    print(highlight(SAMPLE, SysMLLexer(), Terminal256Formatter(style="monokai")))
    print("Lexer name:", SysMLLexer.name)
    print("Aliases:   ", SysMLLexer.aliases)
    print("Extensions:", SysMLLexer.filenames)
