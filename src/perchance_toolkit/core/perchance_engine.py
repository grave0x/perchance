"""Pure-Python evaluator for the perchance template language.

Fetches generator data via curl_cffi (bypasses Cloudflare), parses the
line-based template DSL, and produces output by evaluating sections with
weighted random selection, method chaining, and recursive imports.
"""

from __future__ import annotations

import json
import logging
import random
import re
from typing import Any, Optional
from urllib.parse import unquote

from curl_cffi import requests

log = logging.getLogger(__name__)

_METHOD_RE = re.compile(r"(\w+)\((.*)\)")


# -- Helpers ----------------------------------------------------------------


def _fetch_generator_data(gen_id: str) -> dict:
    """Fetch raw generator JSON from perchance.org via curl_cffi."""
    log.debug("Fetching generator data for '%s'", gen_id)
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", gen_id) or gen_id
    resp = requests.get(
        f"https://perchance.org/{safe}",
        impersonate="chrome120",
        timeout=15,
    )
    resp.raise_for_status()
    log.debug("Fetched %d bytes for '%s'", len(resp.text), gen_id)

    match = re.search(
        r'<script[^>]*id=["\']preloaded-generator-data["\'][^>]*>(.*?)</script>',
        resp.text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"Could not find generator data for '{gen_id}'")

    raw = unquote(match.group(1).strip())
    data = json.loads(raw)
    model_len = len(data.get("modelText", ""))
    log.debug("Parsed generator '%s': modelText=%d chars, %d top-level keys",
              gen_id, model_len, len(data))
    return data


# -- Template parser --------------------------------------------------------

Item = dict[str, Any]  # {text, weight, kind}


def _parse_model(text: str) -> tuple[dict[str, list[Item]], list[Item]]:
    """Parse perchance modelText into named sections + root-level assignments.

    Returns ``(sections, root_assignments)`` where ``root_assignments``
    are assignment items (``r = ...``) that appear at column 0.
    """
    sections: dict[str, list[Item]] = {}
    root_assignments: list[Item] = []
    current_name = ""
    current_items: list[Item] = []
    in_code_block = False

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        # Track code blocks (```...```)
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Skip comments
        if not stripped or stripped.startswith(("//", "#", "'")):
            continue

        if indent == 0:
            # Save previous section
            if current_name and current_items:
                sections[current_name] = current_items
                log.debug("  section '%s': %d items",
                          current_name, len(current_items))
            current_name = ""
            current_items = []

            # Root-level assignment?
            item = _parse_item(stripped)
            if item["kind"] == "assign":
                root_assignments.append(item)
                log.debug("  root-assign: %s", item["text"][:60])
                continue

            # Otherwise it's a section header
            current_name = stripped.split()[0]  # first word = section name
        else:
            current_items.append(_parse_item(stripped))

    if current_name and current_items:
        sections[current_name] = current_items
        log.debug("  section '%s': %d items", current_name, len(current_items))

    log.debug("_parse_model: %d sections, %d root assignments",
              len(sections), len(root_assignments))

    # Create synthetic `output` section if only `$output` exists
    if "$output" in sections and "output" not in sections:
        sections["output"] = sections["$output"]

    return sections, root_assignments


def _parse_item(text: str) -> Item:
    """Parse a single item line, extracting weight and kind."""
    weight = 1.0
    # Trailing `^number` = weight
    wm = re.search(r"\^(\d+(?:\.\d+)?)\s*$", text)
    if wm:
        weight = float(wm.group(1))
        text = text[: wm.start()].strip()

    text = text.strip()
    kind = "text"

    if text.startswith("{import:"):
        kind = "import"
    elif re.fullmatch(r"\[.*?\]", text) and not re.search(r"\]\[", text):
        # Single `[expr]` — not a concatenation of multiple expressions
        kind = "expr"
    elif "=" in text and not re.match(r"\[.*?\]", text):
        # Variable assignment (not inside brackets)
        # But only if `=` is at the top level (not inside brackets)
        bare = re.sub(r"\[.*?\]", "", text)
        if "=" in bare:
            kind = "assign"

    return {"text": text, "weight": weight, "kind": kind}


# -- Value wrappers for evaluation -----------------------------------------


class _SectionRef:
    """Reference to a section that hasn't been resolved yet.

    Methods like ``selectOne`` / ``selectMany`` operate on these.
    ``joinItems`` / ``titleCase`` etc. resolve them first.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"SectionRef({self.name})"


class _ListVal:
    """List value that can be joined / iterated over."""

    def __init__(self, items: list[str]) -> None:
        self.items = items

    def __repr__(self) -> str:
        return f"ListVal({self.items})"


# -- Core evaluator --------------------------------------------------------


class PerchanceEval:
    """Evaluate perchance expressions with method chaining."""

    def __init__(self, sections: dict, engine: PerchanceEngine) -> None:
        self._sections = sections
        self._engine = engine
        self._vars: dict[str, Any] = {}

    # -- Text-level evaluation -------------------------------------------

    def evaluate(self, text: str) -> str:
        """Evaluate a string with perchance syntax:
        - ``[expressions]`` — method chains, section refs
        - ``{min-max}`` — numeric ranges
        - ``{a|b|c}`` — OR-expressions (not {import:...})
        """
        log.debug("  evaluate: %r", text[:120])
        result = text
        # Handle {min-max} ranges — must not contain `|`
        result = re.sub(
            r"\{(?:(\d+)\s*-\s*(\d+))\}",
            lambda m: str(
                self._engine.random.randint(int(m.group(1)), int(m.group(2)))
            ),
            result,
        )
        # Handle {import:...} — skip, handled by item kind
        # Handle {a|b|c} OR-expressions (not import, not range)
        def _replace_or(m: re.Match) -> str:
            options = [o.strip() for o in m.group(1).split("|")]
            return self.evaluate(self._engine.random.choice(options))

        result = re.sub(r"\{(?!import:)([^}]+)\}", _replace_or, result)

        # Handle [expressions]
        parts = re.split(r"(\[.*?\])", result)
        result_parts: list[str] = []
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                result_parts.append(self._eval_expr(part[1:-1]))
            else:
                result_parts.append(part)
        result = "".join(result_parts)

        # Handle remaining {import:...} blocks embedded in text
        result = re.sub(
            r"\{import:([^}]+)\}",
            lambda m: self._engine.evaluate_import(m.group(0)),
            result,
        )

        return result

    def evaluate_list(self, text: str) -> list[str]:
        """Evaluate a string that should produce a list."""
        raw = self.evaluate(text)
        return [x.strip() for x in raw.split() if x.strip()]

    # -- Expression evaluation -------------------------------------------

    def _eval_expr(self, expr: str) -> str:
        """Evaluate a single expression into a final string."""
        result = self._eval_value(expr.strip())
        return self._stringify(result)

    def _eval_value(self, expr: str) -> Any:
        """Evaluate an expression to a possibly-typed value (SectionRef, list, str)."""
        # Variable assignment: `x = value` (top-level `=` only)
        assign_i = self._find_top_level_equals(expr)
        if assign_i >= 0:
            var_name = expr[:assign_i].strip()
            value_expr = expr[assign_i + 1 :].strip()
            value = self._eval_value(value_expr)
            # If the value is a SectionRef, store it so methods work on it
            self._vars[var_name] = value
            return value

        # Unwrap brackets: [randomize.selectOne] -> randomize.selectOne
        # Blocks inside [ ] prevent _split_dot_chain from working correctly.
        if expr.startswith("[") and expr.endswith("]"):
            return self._eval_value(expr[1:-1])

        # Split on `.` for method chaining
        parts = self._split_dot_chain(expr)

        # First part: section name, variable, import, literal
        base = self._resolve_base(parts[0].strip())

        # Chain methods
        result = base
        for method_call in parts[1:]:
            result = self._apply_method(result, method_call.strip())

        return result

    def _resolve_base(self, token: str) -> Any:
        """Resolve a token — returns str, int, float, SectionRef, or _ListVal."""
        # Quoted string literal
        if token.startswith(('"', "'")) and token.endswith(token[0]):
            return token[1:-1]

        # Variable reference
        if token in self._vars:
            return self._vars[token]

        # {import:name}
        if token.startswith("{import:") and token.endswith("}"):
            gen_name = token[8:-1]
            return self._engine.evaluate(gen_name)

        # {a|b|c} OR-expression (evaluate one random option)
        if token.startswith("{") and token.endswith("}") and "|" in token:
            inner = token[1:-1]
            options = [o.strip() for o in inner.split("|")]
            chosen = self._engine.random.choice(options)
            # Re-evaluate the chosen option (may contain [expr])
            return self.evaluate(chosen)

        # Number literal
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                pass

        # Section reference (default)
        return _SectionRef(token)

    # -- Method resolution ----------------------------------------------

    def _resolve_arg(self, raw: str) -> Any:
        """Resolve a method argument — could be literal, variable ref, or section ref."""
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
            return raw[1:-1]
        if raw in self._vars:
            return self._vars[raw]
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                pass
        # Section reference (for things like selectMany(sectionName))
        return _SectionRef(raw)

    def _resolve_to_int(self, raw: Any) -> int:
        """Resolve a value to an integer (unwrapping SectionRef)."""
        if isinstance(raw, _SectionRef):
            item_text = self._select_one(raw.name)
            return int(item_text)
        if isinstance(raw, str):
            if raw in self._sections:
                return int(self._select_one(raw))
            return int(raw)
        return int(raw)

    def _resolve_to_string(self, raw: Any) -> str:
        """Resolve to a plain string."""
        if isinstance(raw, _SectionRef):
            return self._select_one(raw.name)
        return str(raw)

    def _apply_method(self, value: Any, method_call: str) -> Any:
        """Apply a method like ``selectOne``, ``selectMany(n)``, etc."""
        m = _METHOD_RE.match(method_call)
        if m:
            method = m.group(1)
            args_str = m.group(2)
            args = [self._resolve_arg(a) for a in args_str.split(",") if a.strip()]
        else:
            method = method_call
            args = []

        match method:
            # -- Section-reference methods (operate on SectionRef) --
            case "selectOne":
                if isinstance(value, _SectionRef):
                    return self._select_one(value.name)
                return str(value)

            case "selectMany":
                count = self._resolve_to_int(args[0]) if args else 1
                if isinstance(value, _SectionRef):
                    items = self._select_many(value.name, count)
                else:
                    items = self._select_many(str(value), count)
                return _ListVal(items)

            case "selectUnique":
                count = self._resolve_to_int(args[0]) if args else 1
                if isinstance(value, _SectionRef):
                    items = self._select_unique(value.name, count)
                else:
                    items = self._select_unique(str(value), count)
                return _ListVal(items)

            # -- String methods --
            case "joinItems":
                sep = self._resolve_to_string(args[0]) if args else " "
                if isinstance(value, _ListVal):
                    return sep.join(value.items)
                return str(value)

            case "titleCase":
                return self._resolve_to_string(value).title()

            case "upperCase":
                return self._resolve_to_string(value).upper()

            case "lowerCase":
                return self._resolve_to_string(value).lower()

            case _:
                # Unknown method → treat as named sub-item selector
                # e.g. ``this.short`` where ``short`` is an item name in the section.
                items = self._sections.get(str(value), [])
                if isinstance(value, _SectionRef) and items:
                    named = [
                        it for it in items
                        if it["text"] == method_call or it["text"].lstrip("[").rstrip("]") == method_call
                    ]
                    if named:
                        return self._eval_to_text(self._engine.random.choice(named))
                return self._resolve_to_string(value)

    # -- Selection helpers ----------------------------------------------

    def _select_one(self, section_name: str) -> str:
        """Pick one random weighted item from a section, text only."""
        items = self._sections.get(section_name, [])
        if not items:
            return section_name

        chosen = _weighted_choice(items, self._engine.random)
        return self._eval_to_text(chosen)

    def _select_many(self, section_name: str, count: int) -> list[str]:
        """Pick multiple random weighted items (may repeat)."""
        items = self._sections.get(section_name, [])
        if not items:
            return []

        results = []
        for _ in range(count):
            if not items:
                break
            chosen = _weighted_choice(items, self._engine.random)
            results.append(self._eval_to_text(chosen))
        return results

    def _select_unique(self, section_name: str, count: int) -> list[str]:
        """Pick multiple random weighted items (without replacement)."""
        items = list(self._sections.get(section_name, []))
        if not items:
            return []

        results = []
        for _ in range(count):
            if not items:
                break
            chosen = _weighted_choice(items, self._engine.random)
            results.append(self._eval_to_text(chosen))
            items.remove(chosen)
        return results

    def _eval_to_text(self, item: Item) -> str:
        """Evaluate a parsed item to its text output."""
        kind = item.get("kind", "text")
        text = item["text"]

        match kind:
            case "expr":
                # Strip brackets and evaluate inner expression
                inner = text.strip("[]")
                return self._stringify(self._eval_value(inner))
            case "import":
                return self._engine.evaluate_import(text)
            case "assign":
                return self._eval_expr(text)
            case _:
                return self.evaluate(text)

    # -- Utility --------------------------------------------------------

    def _stringify(self, value: Any) -> str:
        """Convert any internal value to a final string."""
        if isinstance(value, _SectionRef):
            return self._select_one(value.name)
        if isinstance(value, _ListVal):
            return "".join(value.items)  # no separator — caller adds joinItems() if needed
        return str(value)

    @staticmethod
    def _find_top_level_equals(expr: str) -> int:
        """Find index of first ``=`` at depth 0 (not inside parens/strings)."""
        depth = 0
        in_str = False
        sc = None
        for i, ch in enumerate(expr):
            if in_str:
                if ch == sc:
                    in_str = False
                continue
            if ch in ('"', "'"):
                in_str = True
                sc = ch
                continue
            if ch in ("(", "["):
                depth += 1
            elif ch in (")", "]"):
                depth -= 1
            elif ch == "=" and depth == 0:
                return i
        return -1

    @staticmethod
    def _split_dot_chain(expr: str) -> list[str]:
        """Split ``name.selectMany(r).joinItems(" ")`` on top-level dots."""
        parts = []
        current = []
        depth = 0
        in_string = False
        string_char = None

        for ch in expr:
            if in_string:
                current.append(ch)
                if ch == string_char:
                    in_string = False
                continue

            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                current.append(ch)
                continue

            if ch in ("(", "["):
                depth += 1
            elif ch in (")", "]"):
                depth -= 1

            if ch == "." and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(ch)

        if current:
            parts.append("".join(current))
        return parts


# -- Core engine ------------------------------------------------------------


class PerchanceEngine:
    """Evaluate perchance generators to produce text output.

    Usage::

        engine = PerchanceEngine(seed=42)
        result = engine.evaluate("name-generator")
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self.random = random.Random(seed)
        self._cache: dict[str, dict] = {}
        self._import_depth = 0

    MAX_IMPORT_DEPTH: int = 5

    def evaluate(self, gen_id: str) -> str:
        """Run a generator and return text output."""
        if self._import_depth >= self.MAX_IMPORT_DEPTH:
            return ""
        try:
            data = self._fetch(gen_id)
        except Exception:
            return ""
        sections, root_assignments = _parse_model(data["modelText"])
        return self._evaluate_with_scope(sections, root_assignments)

    def _evaluate_with_scope(
        self,
        sections: dict[str, list[Item]],
        root_assignments: list[Item],
    ) -> str:
        """Evaluate sections with root-level assignments pre-loaded."""
        eval_scope = PerchanceEval(sections, self)

        log.debug("_evaluate_with_scope: %d sections, %d root assigns",
                  len(sections), len(root_assignments))
        for name, items in sections.items():
            log.debug("  section %r: %d items (sample: %r)",
                      name, len(items),
                      items[0]["text"][:80] if items else "(empty)")

        # Process root-level variable assignments first
        for item in root_assignments:
            eval_scope._eval_to_text(item)

        # Evaluate the output section
        if "output" not in sections:
            log.debug("  no 'output' section — returning empty")
            return ""

        output_text = eval_scope.evaluate("[output]")
        result = eval_scope.evaluate(output_text).strip()
        log.debug("  output: %r", result[:200])
        return result

    def evaluate_import(self, import_expr: str) -> str:
        """Evaluate a ``{import:name}`` expression."""
        if self._import_depth >= self.MAX_IMPORT_DEPTH:
            return ""

        gen_name = import_expr.strip("{}").replace("import:", "", 1)
        self._import_depth += 1
        try:
            result = self.evaluate(gen_name)
        except Exception:
            result = ""
        finally:
            self._import_depth -= 1
        return result

    def evaluate_raw(
        self,
        data: dict,
        seed: Optional[int] = None,
        prompt: str = "",
        section_overrides: Optional[dict[str, str]] = None,
    ) -> str:
        """Evaluate a pre-fetched generator data dict.

        Parameters
        ----------
        data:
            Raw generator data (from ``fetch_data``).
        seed:
            Custom random seed for reproducibility.
        prompt:
            Shortcut to override the ``input`` section.
        section_overrides:
            Map of section name → override value for any section.
        """
        old_seed = self.random
        if seed is not None:
            self.random = random.Random(seed)
            log.debug("evaluate_raw: seed=%s", seed)

        try:
            sections, root_assignments = _parse_model(data.get("modelText", ""))
            overrides = dict(section_overrides or {})
            if prompt:
                overrides["input"] = prompt
            if overrides:
                log.debug("evaluate_raw: overrides=%s", overrides)
            for name, value in overrides.items():
                sections[name] = [{"text": str(value), "weight": 1, "kind": "text"}]
            return self._evaluate_with_scope(sections, root_assignments)
        finally:
            if seed is not None:
                self.random = old_seed

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Search for generators matching *query* on perchance.org.

        Returns a list of raw result dicts (see
        ``GeneratorSearchResult.from_api`` for parsing).
        """
        resp = requests.get(
            "https://perchance.org/api/getGeneratorList",
            params={"q": query, "limit": limit},
            impersonate="chrome120",
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "success":
            return []
        return data.get("generators", [])

    def fetch_data(self, gen_id: str) -> dict:
        """Fetch raw generator data (public for pre-fetching)."""
        return self._fetch(gen_id)

    def _fetch(self, gen_id: str) -> dict:
        if gen_id not in self._cache:
            self._cache[gen_id] = _fetch_generator_data(gen_id)
        return self._cache[gen_id]


# -- Module-level helpers ---------------------------------------------------


def _weighted_choice(items: list[Item], rng: random.Random) -> Item:
    """Pick an item respecting proportional weights."""
    total = sum(it["weight"] for it in items)
    if total <= 0:
        return items[0]
    r = rng.random() * total
    for it in items:
        r -= it["weight"]
        if r <= 0:
            log.debug("  _weighted_choice: picked %r (w=%s)", it["text"], it["weight"])
            return it
    return items[-1]


def _strip_html(text: str) -> str:
    """Remove HTML tags, keeping text content."""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text
