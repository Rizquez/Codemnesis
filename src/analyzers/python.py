# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
import ast, logging, inspect, re
from typing import List, Tuple, Optional
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models import *
from src.utils.metrics import module_metrics
from configuration.constants import ALGORITHM
from src.tools.fixers import fix_asterisk, fix_bullets
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['analyze_python']

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

RETURNS = ('Returns:', 'Return:')
SECTIONS = ('Args:', 'Arguments:', 'Parameters:')
RAISES = ('Raises:', 'Raise:', 'Exceptions:', 'Exception:')

def analyze_python(path: Path) -> ModuleInfo:
    """
    Analyzes a Python file and extracts structural information about its modules, classes, and functions.

    The analysis uses the standard `ast` (Abstract Syntax Tree) module to inspect the source code without 
    executing it. The docstrings, names, and definition lines of each relevant entity are collected, omitting 
    non-representative nodes (such as imports or single expressions).

    **Process details:**
        - Reads the file with UTF-8 encoding (ignoring errors).
        - Generates the syntax tree with `ast.parse()`.
        - Extracts:
            * Module docstring.
            * Top-level functions (`ast.FunctionDef`).
            * Classes (`ast.ClassDef`) and their internal methods.
        - Logs a warning (`logger.warning`) for each unexpected node, showing type and summary.

    Args:
        path (Path):
            Path of the Python file to be analyzed.

    Returns:
        ModuleInfo:
            Object describing the structural content of the module, including its classes, functions, and main 
            docstring.
    """
    src = path.read_text(encoding='utf-8', errors='ignore')
    tree = ast.parse(src)
    doc = ast.get_docstring(tree)

    funcs: List[FunctionInfo] = []
    classes: List[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            funcs.append(
                FunctionInfo(
                    name=node.name,
                    lineno=node.lineno,
                    doc=_normalize_document(ast.get_docstring(node)),
                    decorators=_collect_decorators(node, src)
                )
            )
        elif isinstance(node, ast.ClassDef):
            cls = ClassInfo(
                name=node.name,
                lineno=node.lineno,
                doc=_normalize_document(ast.get_docstring(node)),
                decorators=_collect_decorators(node, src)
            )

            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    cls.methods.append(FunctionInfo(
                        name=sub.name,
                        lineno=sub.lineno,
                        doc=_normalize_document(ast.get_docstring(sub)),
                        decorators=_collect_decorators(sub, src)
                    ))

                elif isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if isinstance(target, ast.Name):
                            cls.attributes.append(
                                AttributeInfo(
                                    name=target.id,
                                    lineno=sub.lineno,
                                    doc=None,
                                )
                            )
                elif isinstance(sub, ast.AnnAssign):
                    if isinstance(sub.target, ast.Name):
                        cls.attributes.append(
                            AttributeInfo(
                                name=sub.target.id,
                                lineno=sub.lineno,
                                doc=None,
                            )
                        )
                else:
                    pass

            classes.append(cls)
        else:
            node_type = type(node).__name__
            lineno = getattr(node, 'lineno', '?')

            # Short text representing the node
            # Limit length so as not to clutter the log
            try:
                summary = ast.dump(node, annotate_fields=True, include_attributes=False)
                summary = (summary[:120] + '...') if len(summary) > 120 else summary
            except Exception:
                summary = str(node)

            logger.warning(f"Unexpected node in {path.name} (line {lineno}): type={node_type} → {summary}")

    return ModuleInfo(
        path=str(path),
        doc=doc,
        functions=funcs,
        classes=classes,
        imports=_collect_imports(tree),
        metrics=module_metrics(src, classes, funcs)
    )

def _normalize_document(doc: Optional[str]) -> Optional[str]:
    """
    Normalizes and formats a docstring to produce consistent Markdown output.

    This function processes Python docstrings and transforms them into a standard format, 
    suitable for inclusion in a README file. 
    
    **It automatically recognizes typical documentation sections such as:**
        - Args / Arguments / Parameters
        - Returns / Return
        - Raises

    **And apply a uniform format using:**
        - "*Args:*", "*Returns:*" and "*Raises:*"
        - Bullets with `- name: description`
        - Clean up asterisks and normalize bullets using `fix_bullets` and `fix_asterisk`.

    **Additionally:**
        - Supports multiline descriptions.
        - Preserves indentation to identify blocks belonging to each section.
        - Removes unnecessary blank lines.
        - Unifies any inconsistent formatting from the original docstring.

    Args:
        doc (str | None):
            The original docstring extracted using `ast.get_docstring()`. 
            It can contain line breaks, indentation, long descriptions, 
            and different styles.

    Returns:
        (str | None):
            The fully normalized docstring, ready to be rendered in Markdown, 
            or `None` if the original docstring was empty.
    """
    if not doc:
        return doc

    txt = inspect.cleandoc(doc)
    lines = txt.splitlines()

    out: List[str] = []
    idx = 0
    n_lines = len(lines)

    headers_map = {
        **{s: '*Args:*'    for s in SECTIONS},
        **{s: '*Returns:*' for s in RETURNS},
        **{s: '*Raises:*'  for s in RAISES},
    }

    def _format_block_text(start: int) -> Tuple[int, List[str]]:
        """
        Processes an indented block belonging to a section (Args, Returns, Raises).

        This internal function analyzes all lines belonging to a section block, 
        detecting parameter or element names and their descriptions.

        **Features:**
            - Identifies lines with the pattern `name: description`.
            - Concatenates multiline descriptions while maintaining context.
            - Ignores leading blank lines.
            - Respects indentation to determine when the section ends.
            - Returns the updated index and a list of all formatted items.

        Args:
            start(int):
                Start index from which to begin processing the indented block.

        Returns:
            (int, List[str]):
                - New index after the analyzed block.
                - List of elements formatted as `- name: description`.
        """
        items: List[str] = []
        idx_local = start

        while idx_local < n_lines and (
            lines[idx_local].startswith('    ')
            or lines[idx_local].startswith('\t')
            or not lines[idx_local].strip()
        ):
            cursor = lines[idx_local]

            if not cursor.strip():
                idx_local += 1
                continue

            indent = len(cursor) - len(cursor.lstrip())
            match_cursor = re.match(r'\s*([^:]+):\s*(.*)', cursor)

            if match_cursor:
                name = match_cursor.group(1).strip()
                desc = match_cursor.group(2).strip()

                jdx = idx_local + 1
                extra: List[str] = []
                while jdx < n_lines:
                    nxt = lines[jdx]

                    if not nxt.strip():
                        jdx += 1
                        continue

                    nxt_indent = len(nxt) - len(nxt.lstrip())
                    if nxt_indent <= indent:
                        break

                    extra.append(nxt.strip())
                    jdx += 1

                if extra:
                    desc = (desc + ' ' + ' '.join(extra)).strip()

                items.append(f"- {name}: {desc.replace('- ', '')}")
                idx_local = jdx
            else:
                items.append(f"- {cursor.strip().replace('- ', '')}")
                idx_local += 1

        return idx_local, items

    while idx < n_lines:
        line = lines[idx]
        stripped = line.strip()

        if stripped in headers_map:
            out.append(headers_map[stripped])
            idx += 1

            idx, items = _format_block_text(idx)
            out.extend(items)
            out.append('')

            continue

        line_fixed = fix_bullets(line)
        line_fixed = fix_asterisk(line_fixed)

        out.append(line_fixed)

        idx += 1

    return '\n'.join(out)

def _collect_decorators(node: ast.AST, src: str) -> List[str]:
    """
    Extracts the decorators applied to a function or class in Python code.

    This function parses the AST node (`ast.AST`) corresponding to a function 
    definition (`ast.FunctionDef`) or class definition (`ast.ClassDef`) and obtains 
    the textual representation of each decorator as it appears in the source file.

    Args:
        node (ast.AST):
            Node of the syntax tree that may contain decorators.
        src (str):
            Full content of the source file where the node is located.
            Used to extract exact segments of the original text.

    Returns:
        List[str]:
            List with all the decorators found, each represented as a string without the `@` prefix.
            The order is preserved as it appears in the code.
    """
    decorators: List[str] = []

    for deco in getattr(node, 'decorator_list', []):
        text = ast.get_source_segment(src, deco)

        if text is None:
            try:
                text = ast.unparse(deco) 
            except Exception:
                text = repr(deco)

        decorators.append(text.lstrip('@').strip())

    return decorators

def _collect_imports(tree: ast.AST) -> List[str]:
    """
    Extracts all imports present in a Python module from its AST.

    Args:
        tree (ast.AST):
            The syntax tree of the file obtained using `ast.parse()`.

    Returns:
        List[str]:
            A single, ordered list containing all imported modules within the file.
    """
    imports: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                if module:
                    imports.append(f'{module}.{alias.name}')
                else:
                    imports.append(alias.name)
        else:
            pass

    return sorted(set(imports))

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE