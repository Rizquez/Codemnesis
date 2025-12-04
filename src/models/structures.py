# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Optional
from dataclasses import dataclass, field
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['FunctionInfo', 'ClassInfo', 'AttributeInfo', 'ModuleMetrics', 'ModuleInfo']

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
        decorators (List[str]):
            List of decorators found in the function.
    """
    name: str
    lineno: int
    doc: Optional[str]
    decorators: List[str] = field(default_factory=list)

@dataclass
class AttributeInfo:
    """
    Represents the basic information of an attribute found within a class.

    Attributes:
        name (str):
            Name of the attribute.
        lineno (int):
            Line number where it is defined within the source file.
        doc (str, optional):
            Docstring associated with the attribute, if it exists; otherwise, None.
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
        attributes (List[AttributeInfo]):
            List of attributes found in the module classes, represented by `AttributeInfo` objects.
        decorators (List[str]):
            List of decorators found in the class.
    """
    name: str
    lineno: int
    doc: Optional[str]
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[AttributeInfo] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)

@dataclass
class ModuleMetrics:
    """
    It contains basic metrics extracted from a source module.

    Attributes:
        loc (int):
            Total number of lines in the file (Lines of Code), 
            including comments, blank lines, and code.
        sloc (int):
            Number of "meaningful" lines in the file (Source Lines of Code), 
            excluding comments and blank lines.
        n_classes (int):
            Total number of classes detected in the module.
        n_functions (int):
            Number of functions defined at the module level (excluding methods within classes).
        n_methods (int):
            Total number of methods defined within all classes of the module.
    """
    loc: int
    sloc: int
    n_classes: int
    n_functions: int
    n_methods: int

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
        imports(List[str]):
            List of imports on the module.
        metrics (ModuleMetrics, optional):
            Metrics associated with the module.
    """
    path: str
    doc: Optional[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str] = field(default_factory=list)
    metrics: Optional[ModuleMetrics] = None

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE