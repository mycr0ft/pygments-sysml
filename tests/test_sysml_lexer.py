"""Tests for the SysML Pygments lexer."""

import pytest
from pygments import highlight
from pygments.formatters import NullFormatter
from pygments.token import (
    Comment, Keyword, Name, Number, Operator, Punctuation, String, Whitespace,
)

from sysml_lexer import SysMLLexer


def tokenize(code):
    """Return list of (token_type, value) pairs for *code*."""
    return list(SysMLLexer().get_tokens(code))


# ---------------------------------------------------------------------------
# Registration  (requires the package entry-point to be installed)
# ---------------------------------------------------------------------------

def test_lexer_registered():
    """The lexer should be discoverable via pygments plugin mechanism
    when the package is installed.  If not installed, this test is skipped."""
    from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
    from pygments.util import ClassNotFound
    try:
        l1 = get_lexer_by_name("sysml")
    except ClassNotFound:
        pytest.skip("sysml lexer not installed as a pygments plugin")
    assert isinstance(l1, SysMLLexer)
    l2 = get_lexer_for_filename("model.sysml")
    assert isinstance(l2, SysMLLexer)


def test_lexer_aliases():
    lexer = SysMLLexer()
    assert lexer.aliases == ["sysml", "sysmlv2", "sysml-v2"]


def test_lexer_filenames():
    lexer = SysMLLexer()
    assert "*.sysml" in lexer.filenames
    assert "*.kerml" in lexer.filenames


# ---------------------------------------------------------------------------
# Whitespace
# ---------------------------------------------------------------------------

def test_whitespace():
    tokens = tokenize("  \t\n")
    assert all(t[0] is Whitespace for t in tokens)
    assert len(tokens) >= 1


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def test_single_line_comment():
    tokens = tokenize("// this is a comment\n")
    assert tokens[0][0] is Comment.Single
    assert "comment" in tokens[0][1]


def test_block_comment():
    tokens = tokenize("/* block */")
    assert any(t[0] is Comment.Multiline for t in tokens)
    assert any("block" in t[1] for t in tokens if t[0] is Comment.Multiline)


def test_block_comment_multiline():
    tokens = tokenize("/* line1\n   line2 */")
    assert any(t[0] is Comment.Multiline for t in tokens)
    assert any("line1" in t[1] for t in tokens)
    assert any("line2" in t[1] for t in tokens)


def test_doc_comment():
    tokens = tokenize("/** doc comment */")
    assert any(t[0] is Comment.Special for t in tokens)
    assert any("doc comment" in t[1] for t in tokens)


# ---------------------------------------------------------------------------
# String literals
# ---------------------------------------------------------------------------

def test_double_quoted_string():
    tokens = tokenize('"hello world"')
    assert any(t[0] is String for t in tokens)
    assert any("hello world" in t[1] for t in tokens)


def test_double_quoted_string_with_escape():
    tokens = tokenize('"hello\\nworld"')
    assert any(t[0] is String.Escape for t in tokens)


def test_single_quoted_string():
    tokens = tokenize("'hello world'")
    assert any(t[0] is String for t in tokens)
    assert any("hello world" in t[1] for t in tokens)


# ---------------------------------------------------------------------------
# Number literals
# ---------------------------------------------------------------------------

def test_integer():
    tokens = tokenize("42")
    assert tokens[0][0] is Number.Integer


def test_float():
    tokens = tokenize("3.14")
    assert tokens[0][0] is Number.Float
    tokens2 = tokenize("1e10")
    assert tokens2[0][0] is Number.Float


def test_hex():
    tokens = tokenize("0xFF")
    assert tokens[0][0] is Number.Hex


def test_binary():
    tokens = tokenize("0b1010")
    assert tokens[0][0] is Number.Bin


def test_octal():
    tokens = tokenize("0o777")
    assert tokens[0][0] is Number.Oct


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------

def test_decl_keyword():
    tokens = tokenize("part")
    assert tokens[0][0] is Keyword.Declaration


def test_ns_keyword():
    tokens = tokenize("package")
    assert tokens[0][0] is Keyword.Namespace


def test_type_keyword():
    tokens = tokenize("specializes")
    assert tokens[0][0] is Keyword.Type


def test_value_keyword():
    for kw in ("true", "false", "null"):
        tokens = tokenize(kw)
        assert tokens[0][0] is Keyword.Constant, f"{kw!r} not Keyword.Constant"


def test_doc_keyword():
    tokens = tokenize("doc")
    assert tokens[0][0] is Keyword.Reserved


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

def test_arrow_operator():
    tokens = tokenize("->")
    assert tokens[0][0] is Operator


def test_typing_colon():
    for op in (":>", ":>>", "::"):
        tokens = tokenize(op)
        assert tokens[0][0] is Operator, f"{op!r} not Operator"


def test_at_annotation():
    tokens = tokenize("@@")
    assert tokens[0][0] is Operator


# ---------------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------------

def test_punctuation():
    for p in "{}()[];,:#":
        tokens = tokenize(p)
        assert tokens[0][0] is Punctuation, f"{p!r} not Punctuation"


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

def test_identifier():
    tokens = tokenize("MyClass")
    assert tokens[0][0] is Name


def test_identifier_with_underscore():
    tokens = tokenize("my_attribute_1")
    assert tokens[0][0] is Name


# ---------------------------------------------------------------------------
# End-to-end: smoke test – highlight without errors
# ---------------------------------------------------------------------------

def test_highlight_smoke():
    code = r"""
package Demo {
    part def Vehicle {
        attribute mass : Real;
        port fuelIn : ~FuelPort;
    }
}
"""
    result = highlight(code, SysMLLexer(), NullFormatter())
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Sample from the lexer's __main__ block
# ---------------------------------------------------------------------------

def test_full_sample_tokenizes():
    import textwrap
    sample = textwrap.dedent("""\
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

                flow of Fuel from engine to fuelIn;

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

            enum def FuelType {
                enum Gasoline;
                enum Diesel;
                enum Electric;
            }

            allocation alloc1 : Allocation {
                allocate engine to physicalEngine;
            }
        }
    """)
    tokens = tokenize(sample)
    assert any(t[0] is Keyword.Namespace for t in tokens), "no namespace keyword"
    assert any(t[0] is Keyword.Declaration for t in tokens), "no declaration keyword"
    assert any(t[0] is Comment.Special for t in tokens), "no doc comment"
    assert any(t[0] is Comment.Single for t in tokens), "no single-line comment"
    assert any(t[0] is Comment.Multiline for t in tokens), "no block comment"
    assert any(t[0] is Number.Float for t in tokens), "no float"
    assert any(t[0] is Number.Integer for t in tokens), "no integer"
    assert any(t[0] is Operator for t in tokens), "no operator"
    assert any(t[0] is Punctuation for t in tokens), "no punctuation"
    assert any(t[0] is Name for t in tokens), "no identifier"
