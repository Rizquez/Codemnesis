# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from typing import List, Optional
import logging, re, xml.etree.ElementTree as ET
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models import *
from src.utils.metrics import module_metrics
from configuration.constants import ALGORITHM
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['analyze_csharp']

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

# Regular expression to detect classes, interfaces, records and structs
CLASS_RE = re.compile(
    r'^\s*(?:public|internal|protected|private)?\s*'
    r'(?:abstract|sealed|static|partial)?\s*'
    r'(class|record|struct|interface)\s+([A-Za-z_][A-Za-z0-9_]*)\b',
    re.MULTILINE
)

# Regular expression to detect methods within the body of a class
METHOD_RE = re.compile(
    r'^\s*(?:public|private|protected|internal)\s*'
    r'(?:static\s+|virtual\s+|override\s+|async\s+|sealed\s+|partial\s+)*'
    r'[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*{?',
    re.MULTILINE
)

# Regular expression to detect fields/properties in a class
ATTRIBUTE_RE = re.compile(
    r'^\s*(?:public|private|protected|internal)\s*'
    r'(?:static\s+|readonly\s+|const\s+)?'
    r'[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*'
    r'(?:{[^}]*}|=>|=|;)',
    re.MULTILINE
)

# Regular expression to detect using
USING_RE = re.compile(r'^\s*using\s+([A-Za-z0-9_.]+)\s*;', re.MULTILINE)

def analyze_csharp(path: Path) -> ModuleInfo:
    """
    Analyzes a C# file and extracts structural information about its classes and methods.

    **What this parser extracts:**
        - Classes, records, structs, and interfaces.
        - Methods within each class.
        - Associated XML documentation (`/// <summary>`, `<param>`, `<returns>`, `<exception>`).

    **What it does NOT extract:**
        - Top-level functions (C# does not usually have them).
        - Attributes, properties, delegates (these can be added later if needed).

    **How it works:**
        1. Reads the file as text.
        2. Detects classes using regular expressions.
        3. Delimits the `{ ... }` block of each class by counting curly brackets.
        4. Within the block, detects methods with another regular expression.
        5. Before each class/method, collect upstream XML documentation (`///` lines).
        6. Convert the XML to readable, structured text.

    Args:
        path (Path):
            Path of the C# file to be analyzed.

    Returns:
        ModuleInfo:
            Object with all the structural and documentary information of the C# file.
    """
    src = path.read_text(encoding='utf-8', errors='ignore')
    lines = src.splitlines()

    classes: List[ClassInfo] = []

    for cls_match in CLASS_RE.finditer(src):
        kind = cls_match.group(1)
        cls_name = cls_match.group(2)
        
        cls_start = cls_match.start()
        cls_lineno = src.count("\n", 0, cls_start) + 1

        cls_doc = _collect_xml_doc(lines, cls_lineno - 1)
        cls_decorators = _collect_decorators(lines, cls_lineno - 1)

        cls_info = ClassInfo(
            name=cls_name, 
            lineno=cls_lineno, 
            doc=cls_doc, 
            decorators=cls_decorators
        )

        # Within the approximate block of that class, search for methods
        # Find the closest opening key and count keys to narrow down the block
        idx_brace = src.find('{', cls_match.end())
        if idx_brace == -1:
            logger.warning(f"Could not find '{{' for {kind} {cls_name} in {path.name} (Line {cls_lineno})")
            classes.append(cls_info)
            continue

        # Count keys to delimit the block
        depth = 0
        idx = idx_brace
        idx_end = len(src)

        while idx < len(src):
            if src[idx] == '{':
                depth += 1
            elif src[idx] == '}':
                depth -= 1

                if depth == 0:
                    idx_end = idx
                    break
            else:
                pass
            
            idx += 1

        # Regular expression to detect constructor methods
        CTOR_RE = re.compile(
            rf'^\s*(?:public|private|protected|internal)\s*'
            rf'(?:static\s+)?'
            rf'{re.escape(cls_name)}\s*\([^)]*\)\s*{{?',
            re.MULTILINE
        )

        class_block = src[idx_brace:idx_end]

        for ctor in CTOR_RE.finditer(class_block):
            ctor_abs_start = idx_brace + ctor.start()
            ctor_lineno = src.count('\n', 0, ctor_abs_start) + 1
            ctor_doc = _collect_xml_doc(lines, ctor_lineno - 1)

            cls_info.methods.append(
                FunctionInfo(
                    name=cls_name, 
                    lineno=ctor_lineno, 
                    doc=ctor_doc
                )
            )

        for method in METHOD_RE.finditer(class_block):
            method_name = method.group(1)
            method_abs_start = idx_brace + method.start()
            method_lineno = src.count('\n', 0, method_abs_start) + 1
            method_doc = _collect_xml_doc(lines, method_lineno - 1)
            method_decorators = _collect_decorators(lines, method_lineno - 1)

            cls_info.methods.append(
                FunctionInfo(
                    name=method_name,
                    lineno=method_lineno,
                    doc=method_doc,
                    decorators=method_decorators
                )
            )

        for attr in ATTRIBUTE_RE.finditer(class_block):
            attr_name = attr.group(1)
            attr_abs_start = idx_brace + attr.start()
            attr_lineno = src.count('\n', 0, attr_abs_start) + 1
            attr_doc = _collect_xml_doc(lines, attr_lineno - 1)

            cls_info.attributes.append(
                AttributeInfo(
                    name=attr_name, 
                    lineno=attr_lineno, 
                    doc=attr_doc
                )
            )

        classes.append(cls_info)

    return ModuleInfo(
        path=str(path),
        doc=None,           # C# does not have module docstrings
        functions=[],       # In C#, there are no typical top-level functions, it is left empty
        classes=classes,
        imports=_collect_usings(src),
        metrics=module_metrics(src, classes, [])
    )

def _collect_xml_doc(lines: List[str], start_idx: int) -> Optional[str]:
    """
    Extracts, interprets, and converts XML documentation preceding a class or method.

    This type of documentation consists of lines beginning with `///`.

    The algorithm ascends from `start_idx`, collecting all immediately preceding documentation,
    sorting it, and then parsing it as valid XML.

    **The function:**
        - Detects `<summary>`
        - Detects `<param name="x">`
        - Detects `<returns>`
        - Detects `<exception cref="X">`
        - Converts `<see cref="X"/>` nodes to plain text (X)
        - Generates a structured block of readable text

    If the block is not valid XML or does not contain relevant tags, it is returned as is.

    Args:
        lines (List[str]):
            List of lines from the source file.

        start_idx (int):
            Index where the class or method appears, used to search documentation upwards.

    Returns:
        Optional[str]:
            Processed and cleaned text from the documentation, or None if there is no associated documentation.
    """
    idx = start_idx - 1
    buf: List[str] = []

    # We move upward collecting lines ///
    while idx >= 0:
        txt = lines[idx].rstrip()

        # XML format
        if txt.strip().startswith('///'):
            buf.append(txt.strip().lstrip('/').strip())
            idx -= 1
            continue

        # Empty lines
        if txt.strip() == '':
            idx -= 1
            continue

        # C# attributes
        if txt.strip().startswith('[') and txt.strip().endswith(']'):
            idx -= 1
            continue

        break

    if not buf:
        return None

    buf.reverse()
    raw = '\n'.join(buf)

    # If it does not appear to be documentation XML, we return it as is
    if not any(tag in raw for tag in ('<summary', '<param', '<returns', '<exception')):
        return raw

    # We wrap it in a root so that it is valid XML
    xml_source = '<root>\n' + raw + '\n</root>'

    try:
        root = ET.fromstring(xml_source)
    except Exception:
        return raw # If parsing fails, we return the raw text

    parts: List[str] = []

    # SUMMARY
    summary = root.find('summary')
    if summary is not None:
        txts = _xml_node_to_text(summary).strip()

        if txts:
            parts.append(txts)
            parts.append('')

    # PARAMS
    params = root.findall('param')
    if params:
        parts.append('*Params:*')

        for param in params:
            name = param.attrib.get('name', '').strip()
            textp = _xml_node_to_text(param).strip()

            if name:
                parts.append(f'- {name}: {textp}')
            else:
                parts.append(f'- {textp}')

        parts.append('')

    # RETURNS
    returns = root.find('returns')
    if returns is not None:
        txtr = _xml_node_to_text(returns).strip()

        if txtr:
            txtr = txtr.replace('- ', '')
            parts.append('*Returns:*')
            parts.append(f'- {txtr}')
            parts.append('')

    # EXCEPTIONS
    exceptions = root.findall('exception')
    if exceptions:
        parts.append('*Exceptions:*')

        for exception in exceptions:
            cref = exception.attrib.get('cref', '').strip().lstrip('T:') # Usually comes as T:Name
            texte = _xml_node_to_text(exception).strip()

            if cref:
                parts.append(f'- {cref}: {texte}')
            else:
                parts.append(f'- {texte}')

        parts.append('')

    # Cleaning: remove any excess blank lines at the end
    while parts and parts[-1] == '':
        parts.pop()

    return '\n'.join(parts)

def _xml_node_to_text(node: ET.Element) -> str:
    """
    Converts an XML documentation node into plain text.

    **Key features:**
        - Removes noise and unnecessary spaces.
        - Interprets `<see cref="X"/>` nodes, returning only "X".
        - Processes nested nodes while maintaining the natural order of the text.
        - Respects the content before, between, and after child nodes.

    Args:
        node (ET.Element):
            XML node to be transformed.

    Returns:
        str:
            Clean, readable text corresponding to the node's content.
    """
    parts: List[str] = []

    if node.text and node.text.strip():
        parts.append(node.text.strip())

    for child in node:
        if child.tag == 'see':
            cref = child.attrib.get('cref', '').strip()
            
            # Sometimes it comes as T:Namespace.Type
            if ':' in cref:
                cref = cref.split(':', 1)[-1]

            if cref:
                parts.append(cref)

        elif child.tag == 'paramref':
            name = child.attrib.get('name', '').strip()
            
            if name:
                parts.append(name)
        else:
            text_child = _xml_node_to_text(child)
            
            if text_child:
                parts.append(text_child)

        if child.tail and child.tail.strip():
            parts.append(child.tail.strip())

    return ' '.join(parts)

def _collect_decorators(lines: List[str], start_idx: int) -> List[str]:
    """
    Extracts C#-style decorators (attributes) applied to a class, method, constructor or field.

    The algorithm ascends from `start_idx`, collecting all immediately preceding documentation,
    sorting it, and then parsing it as valid XML.

    Args:
        lines (List[str]):
            The file content split into lines.
        start_idx (int):
            The 1-based index of the declaration line.

    Returns:
        List[str]:
            List with all decorators found.
    """
    attrs: List[str] = []
    idx = start_idx - 1

    while idx >= 0:
        txt = lines[idx].rstrip()

        if txt.strip().startswith('[') and txt.strip().endswith(']'):
            attrs.append(txt.strip())
            idx -= 1
            continue

        if txt.strip().startswith('///'):
            idx -= 1
            continue

        break

    attrs.reverse()

    return attrs

def _collect_usings(src: str) -> List[str]:
    """
    Extracts all `using` statements present in a C# file.

    This function analyzes the entire contents of the source file (`src`) 
    and uses the regular expression `USING_RE` to locate all statements of 
    the type: `using System.Text`.

    Args:
        src(str):
            Complete contents of the C# file in text format.

    Returns:
        List[str]:
            Ordered list, without duplicates, of all namespaces imported using `using` statements.
    """
    return sorted({using.group(1) for using in USING_RE.finditer(src)})

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE