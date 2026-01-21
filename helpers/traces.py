# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['error_trace']

def error_trace(tb: List[Tuple[str, int, str, str]], logger: 'Logger', error: Exception) -> None:
    """
    It records an error in the logger with filtered trace information.

    The function processes the error trace and removes entries that come from external libraries, 
    which are located in `Lib\\site-packages`. This preserves a more relevant traceback focused on 
    the application's own code.

    **Notes:**
        - This logic assumes a Windows environment because it searches for the path `Lib\\site-packages`.

    Args:
        tb (List[Tuple[str, int, str, str]]): 
            Traces obtained with `traceback.extract_tb`.
        logger (Logger): 
            Logger instance where the error will be recorded.
        error (Exception): 
            Captured exception object.
    """
    filtered = [
        (filename, line, funcname, text) 
        for filename, line, funcname, text in tb 
        if r'Lib\site-packages' not in filename
    ]

    if not filtered:
        logger.error(f"{error} - No relevant traceback found")
        return
    
    # The last call in the traceback of the project itself usually 
    # indicates the point where the internal logic actually failed
    filename, line, funcname, text = filtered[-1]

    logger.error(f"{error} occurred while processing {text} in function {funcname} (file: {filename}, line: {line})")

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE