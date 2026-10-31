"""Translation of the Studio's own pages (plan M4.1).

    python tools/yuem/i18n.py scan              # UI texts not yet translatable, per file
    python tools/yuem/i18n.py wrap [paths...]   # make them translatable in place
    python tools/yuem/i18n.py catalog           # lupdate -> .ts, fill from zh_CN.json, lrelease -> .qm
    python tools/yuem/i18n.py check             # gate: nothing untranslatable, every entry translated

``wrap`` turns a literal handed to a Qt text call (``setText``,
``setToolTip``, ``QLabel(...)``, ``addItem``, message boxes, ...) into
``QCoreApplication.translate("PHGX", <the literal as written>)`` - its source
kept, line breaks and comments included - and an f-string into
``QCoreApplication.translate("PHGX", "<template>").format(...)``. That is the
form ``pyside6-lupdate`` extracts. The translations live in
``PyHydroGeophysX/qt_apps/translations/zh_CN.json`` (source -> Chinese), from
which ``catalog`` fills ``phgx_zh_CN.ts`` and compiles ``phgx_zh_CN.qm``.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import tokenize
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _repo import ROOT

CONTEXT = "PHGX"
UI_ROOT = ROOT / "PyHydroGeophysX" / "qt_apps"
TRANSLATIONS = UI_ROOT / "translations"
TS_FILE = TRANSLATIONS / "phgx_zh_CN.ts"
QM_FILE = TRANSLATIONS / "phgx_zh_CN.qm"
JSON_FILE = TRANSLATIONS / "zh_CN.json"
#: Files of qt_apps that hold no user interface text.
SKIP_FILES = frozenset({"adtlert_probe.py", "em_probe.py", "selftest.py", "one_click_runner.py"})

#: Call name -> positions of its arguments that are user-visible text.
TEXT_ARGS: dict[str, tuple[int, ...]] = {
    "setText": (0,),
    "setToolTip": (0,),
    "setWindowTitle": (0,),
    "setPlaceholderText": (0,),
    "setTitle": (0,),
    "setStatusTip": (0,),
    "setWhatsThis": (0,),
    "showMessage": (0,),
    "setLabelText": (0,),
    "setPrefix": (0,),
    "setSuffix": (0,),
    "setSpecialValueText": (0,),
    "addTab": (1,),
    "insertTab": (2,),
    "setTabText": (1,),
    "setTabToolTip": (1,),
    "addAction": (0, 1),
    "addMenu": (0, 1),
    "addRow": (0,),
    "addButton": (0,),
    "set_xlabel": (0,),
    "set_ylabel": (0,),
    "set_title": (0,),
    "suptitle": (0,),
    "setLabel": (1,),
    # The Studio's own helpers that put their text on screen.
    "_add_action": (1,),
    "_hint": (0,),
    "_button": (0, 3),
    "_primary": (0,),
    "select_directory": (1,),
    "fold": (0,),
    "message": (0,),
    "start_card": (0, 1, 4),
    "QLabel": (0,),
    "QPushButton": (0, 1),
    "QCheckBox": (0,),
    "QRadioButton": (0,),
    "QGroupBox": (0,),
    "QToolButton": (),
    "QMenu": (0,),
    "QAction": (0, 1),
    "information": (1, 2),
    "warning": (1, 2),
    "critical": (1, 2),
    "question": (1, 2),
    "about": (1, 2),
    "getOpenFileName": (1,),
    "getSaveFileName": (1,),
    "getExistingDirectory": (1,),
    "getOpenFileNames": (1,),
    "getText": (1, 2),
    "getItem": (1, 2),
    "getInt": (1, 2),
    "getDouble": (1, 2),
}
#: Calls whose list argument holds one text per item.
LIST_ARGS: dict[str, int] = {
    "setHeaderLabels": 0,
    "setHorizontalHeaderLabels": 0,
    "setVerticalHeaderLabels": 0,
    "start_card": 2,
}
#: Combo and list entries are translated only with a data argument: without
#: one the code reads the text back as the value (``currentText()``).
DATA_ARGS: dict[str, tuple[int, int]] = {"addItem": (0, 1), "insertItem": (1, 2)}
#: Calls whose every positional string argument is shown (``flow_layout.group``).
ALL_ARGS = frozenset({"group"})
#: Calls that look entries up by their text: kept as written, never translated.
LOOKUP_CALLS = frozenset({"setCurrentText", "findText", "findItems", "addItems"})
#: Calls whose variable arguments are not wrapped: there they are mostly actions,
#: menus or buttons, which ``qt_apps.i18n.tr`` would pass through unchanged.
NO_DYNAMIC = frozenset({"addAction", "addMenu", "addButton"})
#: Helpers that translate their own text (``main_window._make_dock`` keeps the
#: English title as the dock's object name); their literals go into the catalog.
INNER_TRANSLATED: dict[str, tuple[int, ...]] = {"_make_dock": (0,)}
#: Sources whose named placeholders hold only an English plural "s"; the
#: Chinese may leave those out (``str.format`` ignores unused arguments).
PLURAL_SUFFIXES: dict[str, tuple[str, ...]] = {
    "● {0} unsaved run{1}": ("{1}",),
    "<b>{0}</b><br>{1} survey{2} · {3:,} cells · {4} layer{5}": ("{2}", "{5}"),
    "{0} step{1} applied in {2:.2f} s.": ("{1}",),
    "{0:g} Hz ({1} run{2})": ("{2}",),
}
#: Marks a line whose texts stay as written (a language's own name, say).
AS_WRITTEN = "i18n: as written"
_WORDS = re.compile(r"[A-Za-z]{2,}")
_PLACEHOLDER = re.compile(r"\{\d+(?:![rsa])?(?::[^{}]*)?\}")


@dataclass(frozen=True)
class Site:
    line: int
    kind: str  # "literal" | "fstring"
    text: str


@dataclass(frozen=True)
class _Edit:
    start: int
    end: int
    text: str


def is_text(value: str) -> bool:
    """True for words a person reads; False for symbols, units, numbers and format specs."""
    return bool(_WORDS.search(value)) and not value.strip().startswith(("%", "*."))


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return func.id if isinstance(func, ast.Name) else ""


#: Static calls that are UI only on these classes (``logger.warning`` is not).
RECEIVERS: dict[str, frozenset[str]] = {
    **dict.fromkeys(("information", "warning", "critical", "question", "about"), frozenset({"QMessageBox"})),
    **dict.fromkeys(("getText", "getItem", "getInt", "getDouble"), frozenset({"QInputDialog"})),
    **dict.fromkeys(
        ("getOpenFileName", "getSaveFileName", "getExistingDirectory", "getOpenFileNames"),
        frozenset({"QFileDialog"}),
    ),
}
#: Getters of text already on screen: never translated again.
SHOWN_TEXT = frozenset(
    {"text", "toolTip", "title", "windowTitle", "currentText", "placeholderText", "tabText"}
)


def _positions(node: ast.Call) -> list[tuple[ast.expr, bool]]:
    """Text arguments of a UI call, each with whether a variable there may be wrapped."""
    name = _call_name(node)
    if name in RECEIVERS:
        func = node.func
        receiver = (
            func.value.id if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) else ""
        )
        if receiver not in RECEIVERS[name]:
            return []
    found: list[tuple[ast.expr, bool]] = []
    dynamic = name not in NO_DYNAMIC
    for position in TEXT_ARGS.get(name, ()):
        if position < len(node.args):
            found.append((node.args[position], dynamic))
    if name in DATA_ARGS:
        text_at, data_at = DATA_ARGS[name]
        if len(node.args) > data_at:
            found.append((node.args[text_at], True))
    if name in ALL_ARGS:
        found += [(arg, False) for arg in node.args]
    if name in LIST_ARGS and LIST_ARGS[name] < len(node.args):
        target = node.args[LIST_ARGS[name]]
        if isinstance(target, (ast.List, ast.Tuple)):
            found += [(element, False) for element in target.elts]
    return found


def _branches(expr: ast.expr) -> list[ast.expr]:
    """The expressions a text argument can take: both sides of ``a if c else b``."""
    if isinstance(expr, ast.IfExp):
        return _branches(expr.body) + _branches(expr.orelse)
    return [expr]


def _is_translated(node: ast.AST) -> bool:
    """``QCoreApplication.translate(...)``, ``....format(...)`` of one, or ``i18n.tr(...)``."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "translate":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "format":
        return _is_translated(func.value)
    return (isinstance(func, ast.Attribute) and func.attr == "tr") or (
        isinstance(func, ast.Name) and func.id == "tr"
    )


def _text_nodes(tree: ast.AST, *, dynamic: bool = False) -> list[tuple[ast.expr, str]]:
    """Text arguments of UI calls not yet translated: ``(node, "literal" | "fstring" | "dynamic")``."""
    found: list[tuple[ast.expr, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for argument, may_wrap in _positions(node):
            for candidate in _branches(argument):
                if isinstance(candidate, ast.Constant) and isinstance(candidate.value, str):
                    if is_text(candidate.value):
                        found.append((candidate, "literal"))
                elif isinstance(candidate, ast.JoinedStr):
                    if is_text(_template(candidate)[0] or ""):
                        found.append((candidate, "fstring"))
                elif (
                    dynamic
                    and may_wrap
                    and not (isinstance(candidate, ast.Name) and candidate.id in ("self", "parent"))
                    and isinstance(candidate, (ast.Name, ast.Attribute, ast.Subscript, ast.Call))
                    and not _is_translated(candidate)
                    and not (
                        isinstance(candidate, ast.Call)
                        and isinstance(candidate.func, ast.Attribute)
                        and candidate.func.attr in SHOWN_TEXT
                    )
                ):
                    found.append((candidate, "dynamic"))
    return found


def _template(node: ast.JoinedStr) -> tuple[str | None, list[ast.expr]]:
    """``("Loaded {0} files", [n])`` for ``f"Loaded {n} files"``; ``(None, [])`` when not expressible."""
    parts: list[str] = []
    values: list[ast.expr] = []
    for piece in node.values:
        if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
            parts.append(piece.value.replace("{", "{{").replace("}", "}}"))
        elif isinstance(piece, ast.FormattedValue):
            spec = ""
            spec_node = piece.format_spec
            if spec_node is not None:
                if not isinstance(spec_node, ast.JoinedStr):
                    return None, []
                constants = [p for p in spec_node.values if isinstance(p, ast.Constant)]
                if len(constants) != len(spec_node.values):
                    return None, []
                spec = ":" + "".join(str(p.value) for p in constants)
            conversion = {-1: "", 115: "!s", 114: "!r", 97: "!a"}[piece.conversion]
            parts.append("{" + str(len(values)) + conversion + spec + "}")
            values.append(piece.value)
        else:
            return None, []
    return "".join(parts), values


def _literal(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
    return f'"{escaped}"'


def _offsets(source: bytes) -> list[int]:
    starts = [0]
    for line in source.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))
    return starts


def _has_comment(segment: str) -> bool:
    """True when an expression's source (implicitly concatenated strings) holds a comment."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(f"({segment})").readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return True
    return any(token.type == tokenize.COMMENT for token in tokens)


def _as_written(source: str) -> set[int]:
    return {number for number, line in enumerate(source.splitlines(), start=1) if AS_WRITTEN in line}


def scan(path: Path, *, dynamic: bool = False) -> list[Site]:
    source = path.read_text(encoding="utf-8")
    sites = []
    kept = _as_written(source)
    for node, kind in _text_nodes(ast.parse(source), dynamic=dynamic):
        if node.lineno in kept:
            continue
        if isinstance(node, ast.JoinedStr):
            template, _ = _template(node)
            sites.append(Site(node.lineno, kind, template or ast.get_source_segment(source, node) or ""))
        elif isinstance(node, ast.Constant):
            sites.append(Site(node.lineno, kind, str(node.value)))
        else:
            sites.append(Site(node.lineno, kind, ast.get_source_segment(source, node) or ""))
    return sites


def wrap(path: Path) -> int:
    """Make every UI text in ``path`` translatable; returns how many were changed.

    Also undoes a translation where it does not belong: a combo entry without
    data, or a text an entry is looked up by.
    """
    source = path.read_text(encoding="utf-8")
    raw = source.encode("utf-8")
    starts = _offsets(raw)
    tree = ast.parse(source)
    edits: list[_Edit] = []
    uses_tr = False

    def span(node: ast.expr) -> tuple[int, int]:
        assert node.end_lineno is not None and node.end_col_offset is not None
        return starts[node.lineno - 1] + node.col_offset, starts[node.end_lineno - 1] + node.end_col_offset

    kept = _as_written(source)
    for node, kind in _text_nodes(tree, dynamic=True):
        if node.lineno in kept:
            continue
        start, end = span(node)
        original = raw[start:end].decode("utf-8")
        if kind == "literal":
            replacement = f'QCoreApplication.translate("{CONTEXT}", {original})'
        elif kind == "dynamic":
            replacement = f"i18n.tr({original})"
            uses_tr = True
        else:
            assert isinstance(node, ast.JoinedStr)
            template, values = _template(node)
            if template is None or _has_comment(original):
                continue
            arguments = ", ".join(ast.get_source_segment(source, v) or "" for v in values)
            replacement = f'QCoreApplication.translate("{CONTEXT}", {_literal(template)})'
            if values:
                replacement += f".format({arguments})"
        edits.append(_Edit(start, end, replacement))
    for node, inner in _misplaced(tree):
        start, end = span(node)
        inner_start, inner_end = span(inner)
        edits.append(_Edit(start, end, raw[inner_start:inner_end].decode("utf-8")))
    # An edit around another (a variable wrapped around a call whose literal is
    # wrapped too) is dropped: the inner one is the translation that matters.
    edits = [e for e in edits if not any(o is not e and e.start <= o.start and o.end <= e.end for o in edits)]
    if not edits:
        return 0
    for edit in sorted(edits, key=lambda e: e.start, reverse=True):
        raw = raw[: edit.start] + edit.text.encode("utf-8") + raw[edit.end :]
    text = raw.decode("utf-8")
    if "QCoreApplication.translate(" in text:
        text = _ensure_import(text)
    if uses_tr:
        text = _ensure_i18n_import(text)
    ast.parse(text)
    path.write_text(text, encoding="utf-8")
    return len(edits)


def _misplaced(tree: ast.AST) -> list[tuple[ast.expr, ast.expr]]:
    """Translations of combo entries without data and of lookup texts: (the call, its literal)."""
    found: list[tuple[ast.expr, ast.expr]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        arguments: list[ast.expr] = []
        if name in LOOKUP_CALLS and node.args:
            first = node.args[0]
            arguments = list(first.elts) if isinstance(first, (ast.List, ast.Tuple)) else [first]
        elif name in DATA_ARGS and len(node.args) <= DATA_ARGS[name][1]:
            text_at = DATA_ARGS[name][0]
            arguments = [node.args[text_at]] if len(node.args) > text_at else []
        elif name in DATA_ARGS:
            # The data argument is a value the code reads back, never shown.
            arguments = [node.args[DATA_ARGS[name][1]]]
        func = node.func
        receiver = (
            func.value.id if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) else ""
        )
        if name in RECEIVERS and receiver not in RECEIVERS[name]:
            # ``logger.warning(...)`` and the like: logs stay in English.
            for argument in node.args:
                if isinstance(argument, ast.Call) and isinstance(argument.func, ast.Attribute):
                    if argument.func.attr == "tr" and len(argument.args) == 1:
                        found.append((argument, argument.args[0]))
                    elif (
                        argument.func.attr == "translate"
                        and len(argument.args) == 2
                        and isinstance(argument.args[1], ast.Constant)
                    ):
                        found.append((argument, argument.args[1]))
        if (
            name == "tr"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Attribute)
            and node.args[0].func.attr in SHOWN_TEXT
        ):
            found.append((node, node.args[0]))
        if name in NO_DYNAMIC:
            for argument in node.args:
                if (
                    isinstance(argument, ast.Call)
                    and isinstance(argument.func, ast.Attribute)
                    and argument.func.attr == "tr"
                    and len(argument.args) == 1
                    and not isinstance(argument.args[0], (ast.Constant, ast.JoinedStr))
                ):
                    found.append((argument, argument.args[0]))
        for argument in arguments:
            if (
                isinstance(argument, ast.Call)
                and isinstance(argument.func, ast.Attribute)
                and argument.func.attr == "translate"
                and len(argument.args) == 2
                and isinstance(argument.args[1], ast.Constant)
            ):
                found.append((argument, argument.args[1]))
    return found


def _ensure_i18n_import(text: str) -> str:
    """Make ``i18n`` importable from PyHydroGeophysX.qt_apps, on an existing import line when possible."""
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "PyHydroGeophysX.qt_apps" and node.level == 0:
            if any(alias.name == "i18n" for alias in node.names):
                return text
            lines = text.splitlines(keepends=True)
            row = node.lineno - 1
            marker = "import "
            index = lines[row].find(marker, lines[row].find("PyHydroGeophysX.qt_apps"))
            if index >= 0 and not lines[row].rstrip().endswith("("):
                lines[row] = lines[row][: index + len(marker)] + "i18n, " + lines[row][index + len(marker) :]
                return "".join(lines)
    lines = text.splitlines(keepends=True)
    anchor = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            anchor = node.end_lineno or node.lineno
    lines.insert(anchor, "from PyHydroGeophysX.qt_apps import i18n\n")
    return "".join(lines)


def _ensure_import(text: str) -> str:
    """Add QCoreApplication to the file's PySide6.QtCore import, on an existing line when there is one."""
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "PySide6.QtCore":
            if any(alias.name == "QCoreApplication" for alias in node.names):
                return text
            lines = text.splitlines(keepends=True)
            first = node.names[0]
            row = first.lineno - 1 if hasattr(first, "lineno") else node.lineno - 1
            line = lines[row]
            name = first.name if first.asname is None else f"{first.name} as {first.asname}"
            index = line.find(name, (first.col_offset if hasattr(first, "col_offset") else 0))
            if index < 0:
                index = line.find(name)
            lines[row] = line[:index] + "QCoreApplication, " + line[index:]
            return "".join(lines)
    lines = text.splitlines(keepends=True)
    anchor = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            anchor = node.end_lineno or node.lineno
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                continue
            break
    lines.insert(anchor, "from PySide6.QtCore import QCoreApplication\n")
    return "".join(lines)


def _builds_widgets(text: str) -> bool:
    """Imports Qt, or the translation of a page split into parts (``modules/ert/``)."""
    return "PySide6" in text or "QCoreApplication" in text


def ui_files() -> list[Path]:
    """Files of qt_apps that build widgets; Qt-free ones (records, stores, bridges) are left in English."""
    return sorted(
        p
        for p in UI_ROOT.rglob("*.py")
        if p.name not in SKIP_FILES and p.name != "i18n.py" and _builds_widgets(p.read_text(encoding="utf-8"))
    )


# -- catalog --------------------------------------------------------------------------
def _tool(name: str) -> str:
    import PySide6

    return str(Path(PySide6.__file__).resolve().parent / name)


_IDENTIFIER = re.compile(r"[\w.\-/:+*#%]+")
_TITLE_WORDS = re.compile(r"[A-Z][a-z]+(?: [A-Za-z]+)*")


def table_texts(path: Path) -> list[str]:
    """Texts in label tables (tuples and lists of literals) and in helpers that translate their own.

    Shown through variables, so ``wrap`` cannot see them; ``qt_apps.i18n.tr``
    looks them up at run time. Identifiers, icon names, paths and lower-case
    keys are left out.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    texts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Tuple, ast.List)):
            for element in node.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    value = element.value
                    readable = " " in value.strip() and not _IDENTIFIER.fullmatch(value)
                    if is_text(value) and (readable or _TITLE_WORDS.fullmatch(value)):
                        texts.append(value)
        elif isinstance(node, (ast.Return, ast.Assign, ast.AnnAssign)) and isinstance(
            node.value, ast.Constant
        ):
            # Messages kept in constants or returned by helpers, shown through tr().
            message = node.value.value
            if (
                isinstance(message, str)
                and is_text(message)
                and " " in message.strip()
                and not _IDENTIFIER.fullmatch(message)
            ):
                texts.append(message)
        elif isinstance(node, ast.Call) and _call_name(node) in INNER_TRANSLATED:
            for position in INNER_TRANSLATED[_call_name(node)]:
                if position < len(node.args):
                    argument = node.args[position]
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                        texts.append(argument.value)
    return texts


def extra_sources() -> list[str]:
    """Texts shown through variables: navigation, page titles, label tables."""
    sys.path.insert(0, str(ROOT))
    from PyHydroGeophysX.qt_apps.modules import MODULE_SPECS
    from PyHydroGeophysX.qt_apps.widgets.project_tree import TREE_STRUCTURE

    texts: list[str] = [str(spec[2]) for spec in MODULE_SPECS.values() if len(spec) > 2]
    for group, children in TREE_STRUCTURE:
        texts.append(str(group))
        texts += [str(label) for label, _key in children]
    for path in ui_files():
        texts += table_texts(path)
    return [t for t in dict.fromkeys(texts) if is_text(t)]


def catalog() -> int:
    TRANSLATIONS.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            _tool("lupdate"),
            *[str(p) for p in ui_files()],
            "-no-obsolete",
            "-locations",
            "none",
            "-ts",
            str(TS_FILE),
        ],
        check=True,
        capture_output=True,
    )
    translations = json.loads(JSON_FILE.read_text(encoding="utf-8")) if JSON_FILE.exists() else {}
    tree = ET.parse(TS_FILE)
    root = tree.getroot()
    root.set("language", "zh_CN")
    context = next((c for c in root.iter("context") if c.findtext("name") == CONTEXT), None)
    if context is None:
        context = ET.SubElement(root, "context")
        ET.SubElement(context, "name").text = CONTEXT
    present = {m.findtext("source") for m in context.iter("message")}
    for text in extra_sources():
        if text not in present:
            message = ET.SubElement(context, "message")
            ET.SubElement(message, "source").text = text
            ET.SubElement(message, "translation", type="unfinished")
    missing = 0
    for message in root.iter("message"):
        source = message.findtext("source") or ""
        translation = message.find("translation")
        if translation is None:
            translation = ET.SubElement(message, "translation")
        value = translations.get(source)
        if value:
            translation.text = value
            translation.attrib.pop("type", None)
        else:
            translation.text = ""
            translation.set("type", "unfinished")
            missing += 1
    ET.indent(tree)
    tree.write(TS_FILE, encoding="utf-8", xml_declaration=True)
    subprocess.run([_tool("lrelease"), str(TS_FILE), "-qm", str(QM_FILE)], check=True, capture_output=True)
    return missing


def ts_entries() -> dict[str, str]:
    root = ET.parse(TS_FILE).getroot()
    return {m.findtext("source") or "": m.findtext("translation") or "" for m in root.iter("message")}


def check() -> list[str]:
    problems = []
    for path in ui_files():
        for site in scan(path, dynamic=True):
            problems.append(
                f"{path.relative_to(ROOT)}:{site.line}: untranslatable {site.kind}: {site.text[:60]!r}"
            )
    if not TS_FILE.exists() or not QM_FILE.exists():
        return [*problems, f"{TS_FILE.relative_to(ROOT)} or its .qm is missing; run: i18n.py catalog"]
    for source, translation in ts_entries().items():
        if not translation:
            problems.append(f"no translation: {source[:70]!r}")
        elif sorted(
            p for p in _PLACEHOLDER.findall(source) if p not in PLURAL_SUFFIXES.get(source, ())
        ) != sorted(p for p in _PLACEHOLDER.findall(translation) if p not in PLURAL_SUFFIXES.get(source, ())):
            problems.append(f"placeholders differ: {source[:50]!r} -> {translation[:50]!r}")
    if QM_FILE.stat().st_mtime + 1 < TS_FILE.stat().st_mtime:
        problems.append("the .qm is older than the .ts; run: i18n.py catalog")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan")
    wrap_cmd = sub.add_parser("wrap")
    wrap_cmd.add_argument("paths", nargs="*", type=Path)
    sub.add_parser("catalog")
    sub.add_parser("check")
    args = parser.parse_args(argv)
    if args.command == "scan":
        total = 0
        for path in ui_files():
            sites = scan(path, dynamic=True)
            if sites:
                total += len(sites)
                print(f"{len(sites):5d}  {path.relative_to(ROOT)}")
        print(f"{total} untranslatable UI texts")
        return 0
    if args.command == "wrap":
        changed = sum(wrap(p.resolve()) for p in (args.paths or ui_files()))
        print(f"{changed} UI texts made translatable")
        return 0
    if args.command == "catalog":
        missing = catalog()
        print(f"{TS_FILE.relative_to(ROOT)}: {len(ts_entries())} entries, {missing} without a translation")
        return 0
    problems = check()
    for problem in problems[:50]:
        print(problem)
    if len(problems) > 50:
        print(f"... and {len(problems) - 50} more")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
