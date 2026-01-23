# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Optional
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def format_docstring(doc: str, *, cleaned: Optional[List[str]]) -> str:
    """
    Applies the full format to the received text (docstring) by cleanup steps.

    This method acts as a central entry point for normalizing the presentation 
    of docstrings before adding them to the README or other generated output.

    Args:
        doc (str):
            Original text of the docstring to be formatted.
        cleaned (List[str], optional): 
            List of tokens to be removed using replace.

    Returns:
        str:
            Text resulting after applying the format.

    Raises:
        TypeError:
            If `cleaned` is provided but is not a list.
    """
    if cleaned:
        if not isinstance(cleaned, list):
            raise TypeError('The `cleaned` parameter must be a list of strings')
        
        return _clean(doc, cleaned)

    return doc

def _clean(doc: str, cleaned: List[str]) -> str:
    """
    Removes unwanted formatting characters from docstring text.

    Args:
        doc (str):
            Text or docstring to be cleaned.
        cleaned (List[str]): 
            List of tokens to be removed using replace.

    Returns:
        str:
            Text without special characters or formatting symbols.
    """
    lines = doc.strip().splitlines()
    
    out: List[str] = []
    for line in lines:
        for item in cleaned:
            line = line.replace(item, '')
        
        out.append(line)
    
    return '\n'.join(out)

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE