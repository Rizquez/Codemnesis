# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import sys, traceback, logging
from typing import TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from helpers.trace import error_trace
from settings.constants import ALGORITHM
from src.analyzers.python import analyze_file
from src.generators.readme import ReadmeHanler
from src.scanner.repository import scanner_repository

if TYPE_CHECKING:
    from settings.algorithm import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

def manage_implement(settings: 'Settings') -> None:
    """
    Executes the main flow of automatic documentation generation for the project.

    **This function coordinates all stages of the AutoDocMind process:**
        1. Scans the specified repository for files in the supported language.
        2. Analyzes each file found to extract its structure (classes, functions, and docstrings).
        3. Generates a `README` file with the consolidated documentation.
    """
    logger.info(f"Scanning repository: {settings.repository}")
    files = list(scanner_repository(settings.repository, settings.included, settings.excluded))
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

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE