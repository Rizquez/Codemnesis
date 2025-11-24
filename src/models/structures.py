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

__all__ = ['FunctionInfo', 'ClassInfo', 'AttributeInfo', 'ModuleInfo']

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

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE