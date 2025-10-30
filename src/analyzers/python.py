# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import ast, logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from settings.constants import ALGORITHM
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

@dataclass
class FunctionInfo:
    """
    Represents the basic information of a function found within a module or class.

    Attributes:
        name (str):
            Name of the function.
        lineno (int):
            Line number where it is defined within the source file.
        doc (str, optional):
            Docstring associated with the function, if it exists; otherwise, None.
    """
    name: str
    lineno: int
    doc: Optional[str]

@dataclass
class ClassInfo:
    """
    Contains the structural information of a class detected during module analysis.

    Attributes:
        name (str):
            Class name.
        lineno (int):
            Line number of the class definition in the file.
        doc (str, optional):
            Docstring associated with the class, if any.
        methods (List[FunctionInfo]):
            List of methods defined within the class, represented by `FunctionInfo` objects.
    """
    name: str
    lineno: int
    doc: Optional[str]
    methods: List[FunctionInfo] = field(default_factory=list)

@dataclass
class ModuleInfo:
    """
    Represents the analyzed structure of a source code file or module.

    Attributes:
        path (str):
            Full path to the file that was analyzed.
        doc (str, optional):
            Docstring of the module, if defined at the beginning of the file.
        functions (List[FunctionInfo]):
            List of functions defined at the module level.
        classes (List[ClassInfo]):
            List of classes found in the module, including their internal methods.
    """
    path: str
    doc: Optional[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]

def analyze_file(path: Path) -> ModuleInfo:
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
                    doc=ast.get_docstring(node)
                )
            )
        elif isinstance(node, ast.ClassDef):
            cls = ClassInfo(
                name=node.name,
                lineno=node.lineno,
                doc=ast.get_docstring(node)
            )

            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    cls.methods.append(FunctionInfo(
                        name=sub.name,
                        lineno=sub.lineno,
                        doc=ast.get_docstring(sub)
                    ))

            classes.append(cls)
        else:
            node_type = type(node).__name__
            lineno = getattr(node, "lineno", "?")

            # Short text representing the node
            # Limit length so as not to clutter the log
            try:
                summary = ast.dump(node, annotate_fields=True, include_attributes=False)
                summary = (summary[:120] + "...") if len(summary) > 120 else summary
            except Exception:
                summary = str(node)

            logger.warning(f"Unexpected node in {path.name} (line {lineno}): type={node_type} → {summary}")

    return ModuleInfo(
        path=str(path),
        doc=doc,
        functions=funcs,
        classes=classes
    )

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE