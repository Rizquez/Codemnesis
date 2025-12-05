# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import sys, traceback, logging
from typing import TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.analyzers import *
from src.generators import *
from src.utils.scan import scanner
from helpers.trace import error_trace
from settings.constants import ALGORITHM

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
        3. Generates a README file with the consolidated documentation.
        4. Generates a visual dependency graph between modules.
    """
    logger.info(f"Scanning repository: {settings.repository}")
    files = list(scanner(settings.repository, settings.included, settings.excluded))
    logger.info(f"Number of {settings.framework} files found: {len(files)}")
    
    method = globals().get(f'analyze_{settings.framework}')

    modules = []
    for file in files:
        try:
            modules.append(method(file))
        except Exception:
            _, error, line_error = sys.exc_info()
            tb = traceback.extract_tb(line_error)
            error_trace(tb, logger, error)

    logger.info(f"Generating README ...")
    txt = render_readme(modules, settings.repository)
    target = write_readme(txt, settings.output)
    logger.info(f"README generated: {target}")

    """ if settings.graph:
        logger.info("Generating dependency graph ...")
        path = generate_graph(modules, settings.output, settings.repository)
        logger.info(f"Dependency graph generated: {path}") """

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE