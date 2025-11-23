# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
from typing import List, Optional
import logging, re, xml.etree.ElementTree as ET
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.models.structures import *
from settings.constants import ALGORITHM
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
    r'(?:{[^}]*}|=|;)',
    re.MULTILINE
)

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

    # Search classes/records/structs/interfaces
    for cls_match in CLASS_RE.finditer(src):
        kind = cls_match.group(1)
        cls_name = cls_match.group(2)
        
        # Calculate line (1-based)
        cls_start = cls_match.start()
        cls_lineno = src.count("\n", 0, cls_start) + 1

        cls_doc = _collect_xml_doc(lines, cls_lineno - 1)
        cls_info = ClassInfo(name=f"{cls_name}", lineno=cls_lineno, doc=cls_doc)

        # Within the approximate block of that class, search for methods (simple heuristic)
        # Find the closest opening key and count keys to narrow down the block
        open_brace_idx = src.find('{', cls_match.end())
        if open_brace_idx == -1:
            logger.warning(f"Could not find '{{' for {kind} {cls_name} in {path.name} (Line {cls_lineno})")
            classes.append(cls_info)
            continue

        # Count keys to delimit the block
        depth = 0
        idx = open_brace_idx
        end_idx = len(src)

        while idx < len(src):
            if src[idx] == '{':
                depth += 1
            elif src[idx] == '}':
                depth -= 1

                if depth == 0:
                    end_idx = idx
                    break
            idx += 1

        class_block = src[open_brace_idx:end_idx]

        for method in METHOD_RE.finditer(class_block):
            method_name = method.group(1)
            method_abs_start = open_brace_idx + method.start()
            method_lineno = src.count('\n', 0, method_abs_start) + 1
            method_doc = _collect_xml_doc(lines, method_lineno - 1)

            cls_info.methods.append(FunctionInfo(name=method_name, lineno=method_lineno, doc=method_doc))

        for attr in ATTRIBUTE_RE.finditer(class_block):
            attr_name = attr.group(1)
            attr_abs_start = open_brace_idx + attr.start()
            attr_lineno = src.count('\n', 0, attr_abs_start) + 1
            attr_doc = _collect_xml_doc(lines, attr_lineno - 1)

            cls_info.attributes.append(AttributeInfo(name=attr_name, lineno=attr_lineno, doc=attr_doc))

        classes.append(cls_info)

    return ModuleInfo(
        path=str(path),
        doc=None,           # C# does not have module docstrings
        functions=[],       # In C#, there are no typical top-level functions, it is left empty
        classes=classes
    )

def _collect_xml_doc(lines: List[str], start_idx: int) -> Optional[str]:
    """
    Extracts, interprets, and converts XML documentation preceding a class or method.

    This type of documentation consists of lines beginning with `///`.

    The algorithm ascends from `start_idx`, collecting all immediately preceding documentation,
    sorting it, and then parsing it as valid XML.

    **The function:**
        - Detects <summary>
        - Detects <param name="x">
        - Detects <returns>
        - Detects <exception cref="X">
        - Converts <see cref="X"/> nodes to plain text (X)
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
    i = start_idx - 1
    buf: List[str] = []

    # We move upward collecting lines ///
    while i >= 0:
        s = lines[i].rstrip()

        # XML format
        if s.strip().startswith('///'):
            buf.append(s.strip().lstrip('/').strip())
            i -= 1
            continue

        # Empty lines
        if s.strip() == '':
            i -= 1
            continue

        # C# attributes
        if s.strip().startswith('[') and s.strip().endswith(']'):
            i -= 1
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
    summary_el = root.find('summary')
    if summary_el is not None:
        summary_text = _xml_node_to_text(summary_el).strip()

        if summary_text:
            parts.append(summary_text)
            parts.append('')

    # PARAMS
    params = root.findall('param')
    if params:
        parts.append('*Params:*')

        for p in params:
            name = p.attrib.get('name', '').strip()
            text = _xml_node_to_text(p).strip()

            if name:
                parts.append(f'- {name}: {text}')
            else:
                parts.append(f'- {text}')

        parts.append('')

    # RETURNS
    returns_el = root.find('returns')
    if returns_el is not None:
        returns_text = _xml_node_to_text(returns_el).strip()

        if returns_text:
            returns_text = returns_text.replace('- ', '')
            parts.append('*Returns:*')
            parts.append(f'- {returns_text}')
            parts.append('')

    # EXCEPTIONS
    exceptions = root.findall('exception')
    if exceptions:
        parts.append('*Exceptions:*')

        for ex in exceptions:
            cref = ex.attrib.get('cref', '').strip().lstrip('T:') # Usually comes as T:Name
            text = _xml_node_to_text(ex).strip()

            if cref:
                parts.append(f'- {cref}: {text}')
            else:
                parts.append(f'- {text}')

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

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE