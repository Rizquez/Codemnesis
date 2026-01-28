# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import List, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from common.constants import PROJECT_ROOT
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

class Trace(NamedTuple):
    filename: str
    line: int
    function: str
    text: str

def error_trace(traces: List[Trace], logger: Logger, error: Exception) -> None:
    """
    It records an error in the logger, filtering only the traces that belong to the project's internal code.

    Based on the traceback information, entries whose path is not under the project root are discarded. This way, 
    the resulting error message focuses on the exact point where the application's own logic failed, ignoring calls 
    from external libraries or the system.

    Args:
        traces (List[Trace]):
            List of traces obtained using `traceback.extract_tb`.
        logger (Logger):
            Instance of the logger where the error will be recorded.
        error (Exception):
            Captured exception that caused the failure.
    """
    root = _normalize(PROJECT_ROOT)

    internal = [
        trace for trace in traces
        if _normalize(trace[0]).startswith(root)
    ]

    if not internal:
        logger.error(f"{error} - No relevant internal traces were found")
        return
    
    # The last call in the traceback of the project itself usually 
    # indicates the point where the internal logic actually failed
    filename, line, funcname, text = internal[-1]

    about = f'while processing {text}' if text else ''
    logger.error(f"{error} occurred {about} in function {funcname} (file: {filename}, line: {line})")

def _normalize(path: str) -> str:
    """
    Normalize a file path.

    Args:
        path (str):
            Path of the file to be normalized.

    Returns:
        str:
            Normalized path in string format.
    """
    return str(Path(path).resolve()).lower()

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE