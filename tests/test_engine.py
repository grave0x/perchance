"""Unit tests for the perchance template engine."""

from perchance_toolkit.core.perchance_engine import (
    PerchanceEngine,
    PerchanceEval,
    _parse_model,
    _parse_item,
    _process_braces,
    _split_or_options,
    _weighted_choice,
)


# -- _parse_item tests -------------------------------------------------------


def test_parse_item_text() -> None:
    """Plain text line."""
    item = _parse_item("hello world")
    assert item["kind"] == "text"
    assert item["text"] == "hello world"
    assert item["weight"] == 1.0


def test_parse_item_text_with_weight() -> None:
    """Text with trailing ^weight."""
    item = _parse_item("hello world ^2.5")
    assert item["kind"] == "text"
    assert item["text"] == "hello world"
    assert item["weight"] == 2.5


def test_parse_item_weight_int() -> None:
    """Integer weight."""
    item = _parse_item("foo ^3")
    assert item["weight"] == 3.0


def test_parse_item_import() -> None:
    """Import expression."""
    item = _parse_item("{import:name-generator}")
    assert item["kind"] == "import"
    assert item["text"] == "{import:name-generator}"


def test_parse_item_expr() -> None:
    """Single bracket expression."""
    item = _parse_item("[randomize.selectOne]")
    assert item["kind"] == "expr"


def test_parse_item_assign() -> None:
    """Variable assignment."""
    item = _parse_item("x = hello")
    assert item["kind"] == "assign"


def test_parse_item_assign_with_brackets() -> None:
    """Assignment where value contains brackets — not an expr."""
    item = _parse_item("x = [output.selectOne]")
    assert item["kind"] == "assign"


# -- _parse_model tests ------------------------------------------------------


SAMPLE_MODEL = """name
  Alice
  Bob ^2
  Charlie
output
  Hello, [name.selectOne]!
"""


def test_parse_model_basic() -> None:
    """Parse a simple generator model."""
    sections, root_assignments = _parse_model(SAMPLE_MODEL)
    assert "name" in sections
    assert len(sections["name"]) == 3
    assert sections["name"][0]["text"] == "Alice"
    assert sections["name"][1]["weight"] == 2.0
    assert "output" in sections
    assert sections["output"][0]["text"] == "Hello, [name.selectOne]!"
    assert root_assignments == []


SAMPLE_WITH_DOLLAR_OUTPUT = """name
  Alice
$output
  [name.selectOne]
"""


def test_parse_model_dollar_output() -> None:
    """$output creates synthetic output section."""
    sections, _ = _parse_model(SAMPLE_WITH_DOLLAR_OUTPUT)
    assert "$output" in sections
    assert "output" in sections
    assert sections["output"] is sections["$output"]


SAMPLE_WITH_ROOT_ASSIGN = """r = 5
output
  value: [r]
"""


def test_parse_model_root_assignments() -> None:
    """Root-level assignments are captured."""
    sections, root_assignments = _parse_model(SAMPLE_WITH_ROOT_ASSIGN)
    assert len(root_assignments) == 1
    assert root_assignments[0]["kind"] == "assign"
    assert root_assignments[0]["text"] == "r = 5"
    assert "output" in sections


SAMPLE_WITH_COMMENTS = """// comment line
name
  # another comment
  Alice
  ' yet another
  Bob
output
  [name.selectOne]
"""


def test_parse_model_skips_comments() -> None:
    """Comment lines (//, #, ') are skipped."""
    sections, _ = _parse_model(SAMPLE_WITH_COMMENTS)
    assert len(sections["name"]) == 2
    assert sections["name"][0]["text"] == "Alice"
    assert sections["name"][1]["text"] == "Bob"


SAMPLE_WITH_CODE_BLOCK = """name
  Alice
```
code here
```
output
  [name.selectOne]
"""


def test_parse_model_skips_code_blocks() -> None:
    """Code blocks (```...```) are skipped."""
    sections, _ = _parse_model(SAMPLE_WITH_CODE_BLOCK)
    assert len(sections["name"]) == 1


# -- _weighted_choice tests --------------------------------------------------


def test_weighted_choice_deterministic() -> None:
    """Weighted choice with seed produces reproducible results."""
    import random
    rng = random.Random(42)
    items = [
        {"text": "a", "weight": 1, "kind": "text"},
        {"text": "b", "weight": 10, "kind": "text"},
        {"text": "c", "weight": 1, "kind": "text"},
    ]
    results = [_weighted_choice(items, rng)["text"] for _ in range(100)]
    # 'b' should dominate due to weight 10
    b_count = results.count("b")
    assert b_count > 60, f"Expected b > 60, got {b_count}"


# -- _split_or_options & _process_braces tests --------------------------------


def test_split_or_options_basic() -> None:
    """Basic pipe splitting."""
    assert _split_or_options("a|b|c") == ["a", "b", "c"]


def test_split_or_options_nested() -> None:
    """Nested braces preserved in split."""
    assert _split_or_options("{a|b}|c") == ["{a|b}", "c"]
    assert _split_or_options("a|{b|c}") == ["a", "{b|c}"]


def test_split_or_options_deep_nested() -> None:
    """Deeply nested braces."""
    assert _split_or_options("{a|{b|{c|d}}}") == ["{a|{b|{c|d}}}"]


def test_process_braces_or_expr() -> None:
    """OR-expression is resolved to one option."""
    engine = PerchanceEngine(seed=42)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    result = _process_braces("{hello|world}", engine, eval_scope)
    assert result in ("hello", "world")


def test_process_braces_range() -> None:
    """Range {min-max} is resolved to a number."""
    engine = PerchanceEngine(seed=1)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    result = _process_braces("{1-6}", engine, eval_scope)
    assert result.isdigit()
    assert 1 <= int(result) <= 6


def test_process_braces_nested_or() -> None:
    """Nested OR {a|{b|c}} resolves correctly."""
    engine = PerchanceEngine(seed=99)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    seen = set()
    for _ in range(100):
        result = _process_braces("{a|{b|c}}", engine, eval_scope)
        seen.add(result)
    assert seen == {"a", "b", "c"}, f"Got {seen}"


def test_process_braces_deeply_nested_or() -> None:
    """Deeply nested OR {x|{y|{z|w}}} resolves correctly."""
    engine = PerchanceEngine(seed=42)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    seen = set()
    for _ in range(200):
        result = _process_braces("{x|{y|{z|w}}}", engine, eval_scope)
        seen.add(result)
    assert seen == {"x", "y", "z", "w"}, f"Got {seen}"


def test_process_braces_literal() -> None:
    """Plain braces without pipe/range/import are kept as literal."""
    engine = PerchanceEngine(seed=42)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    result = _process_braces("just {text}", engine, eval_scope)
    assert result == "just {text}"


def test_process_braces_or_with_range_inside() -> None:
    """OR with range inside: {hello|{1-3}}."""
    engine = PerchanceEngine(seed=42)
    sections: dict = {}
    eval_scope = PerchanceEval(sections, engine)
    result = _process_braces("{hello|{1-3}}", engine, eval_scope)
    if result != "hello":
        assert result in ("1", "2", "3"), f"Got {result}"


# -- PerchanceEval tests (synchronous, no network) ----------------------------


def test_eval_assign_variable() -> None:
    """Assignment stores and returns the value."""
    engine = PerchanceEngine(seed=0)
    sections = {"output": [{"text": "[x]", "weight": 1, "kind": "text"}]}
    eval_scope = PerchanceEval(sections, engine)
    eval_scope._eval_to_text({"text": "x = 42", "weight": 1, "kind": "assign"})
    assert eval_scope._vars["x"] == 42


def test_eval_weighted_selection() -> None:
    """Section selection returns one of the items."""
    engine = PerchanceEngine(seed=1)
    sections = {
        "names": [
            {"text": "Alice", "weight": 1, "kind": "text"},
            {"text": "Bob", "weight": 1, "kind": "text"},
        ],
        "output": [
            {"text": "[names.selectOne]", "weight": 1, "kind": "text"},
        ],
    }
    result = engine._evaluate_with_scope(sections, [])
    assert result in ("Alice", "Bob")


def test_eval_method_chain() -> None:
    """Method chaining via _split_dot_chain."""
    parts = PerchanceEval._split_dot_chain("name.selectOne.joinItems")
    assert parts == ["name", "selectOne", "joinItems"]


def test_eval_split_dot_chain_with_args() -> None:
    """Dot splitting respects parens."""
    parts = PerchanceEval._split_dot_chain("name.selectMany(3).joinItems(\", \")")
    assert parts == ["name", "selectMany(3)", 'joinItems(", ")']


def test_eval_find_top_level_equals() -> None:
    """Top-level = detection ignores inside parens/strings."""
    idx = PerchanceEval._find_top_level_equals("x = 5")
    assert idx == 2
    idx = PerchanceEval._find_top_level_equals('x(f = g) = 5')
    assert idx == 9  # only the = outside parens (index 9)
