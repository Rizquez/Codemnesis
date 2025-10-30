# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
import sys, traceback, logging, os
from typing import TYPE_CHECKING, Set, Optional, Iterator
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from helpers.trace import error_trace
from settings.constants import ALGORITHM
from src.analyzers.python import analyze_file
from src.generators.readme import ReadmeHanler

if TYPE_CHECKING:
    from settings.algorithm import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['execute']

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

def execute(settings: 'Settings') -> None:
    """
    Executes the main flow of automatic documentation generation for the project.

    **This function coordinates all stages of the AutoDocMind process:**
        1. Scans the specified repository for files in the supported language.
        2. Analyzes each file found to extract its structure (classes, functions, and docstrings).
        3. Generates a `README` file with the consolidated documentation.
    """
    logger.info(f"Scanning repository: {settings.repository}")
    files = list(_scanner(settings.repository, settings.included, settings.excluded))
    logger.info(f"Number of .py files found: {len(files)}")

    modules = []
    for file in files:
        try:
            modules.append(analyze_file(file))
        except Exception:
            _, error, line_error = sys.exc_info()
            tb = traceback.extract_tb(line_error)
            error_trace(tb, logger, error)

    logger.info("Generating README ...")
    txt = ReadmeHanler.render(modules, settings.repository)
    target = ReadmeHanler.write(txt, settings.output)
    logger.info(f"Ready: {target}")

def _scanner(directory: str, included: Set[str], excluded: Optional[Set[str]] = None) -> Iterator[Path]:
    """
    Recursively traverse a directory and generate the paths of files that match the specified extensions, 
    excluding unwanted folders.

    Args:
        directory (str):
            Base path of the repository or project to be analyzed.
        included (Set[str]):
            Set of file extensions to include in the scan.
        excluded (Set[str], optional):
            Set of directory names to ignore during the search.

    Yields:
        Path:
            Absolute path of each file that meets the defined criteria.
    """
    root = Path(directory).resolve()

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in excluded]

        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix in included:
                yield path

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE