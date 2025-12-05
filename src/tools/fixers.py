# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import Optional, List
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['fix_bullets', 'fix_asterisk']

def fix_bullets(txt: Optional[str]) -> Optional[str]:
    """
    Normalizes bullets in multiline text.

    This method detects lines that begin with `-` or `*` and unifies them, 
    converting them into standard hyphenated bullets (`-`).

    Args:
        txt(str | None):
            Original text to process. Can contain one or more lines.

    Returns:
        (str | None):
            The text with normalized bullets, or the original value if `txt` is None.
    """
    if not txt:
        return txt

    lines = txt.splitlines()
    fixed: List[str] = []

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith('- ') or stripped.startswith('* '):
            fixed.append(f'- {stripped[2:].strip()}')
        else:
            fixed.append(line)

    return '\n'.join(fixed)

def fix_asterisk(txt: Optional[str]) -> Optional[str]:
    """
    Removes all asterisks from the text.

    Args:
        txt(str | None):
            Original text that may contain asterisks.

    Returns:
        (str | None):
            Text without asterisks, or the original value if `txt` is None.
    """
    if not txt:
        return txt
    
    return txt.replace('*', '')

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE