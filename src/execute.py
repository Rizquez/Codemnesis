# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
import logging
import traceback
from typing import List, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.analyzers import *
from src.renderers import *
from src.tools.scanner import scanner
from helpers.traces import error_trace
from common.constants import ALGORITHM

if TYPE_CHECKING:
    from src.models import ModuleInfo
    from common.settings import Settings
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

logger = logging.getLogger(ALGORITHM)
"""
Instance of the logger used by the analysis module.
"""

def execute(settings: Settings) -> None:
    """
    Executes the main flow of automatic documentation generation for the project.

    **This function coordinates all stages of the Codemnesis process:**
        1. Scans the specified repository for files in the supported language.
        2. Analyzes each file found to extract its structure (classes, functions, and docstrings).
        3. Generates a README file with the consolidated documentation.
        4. Generates a visual dependency graph between modules.

    Args:
        settings (Settings):
            Object that contains the general settings for the execution of the algorithm.
    """
    logger.info(f"Scanning repository: {settings.repository}")
    files = list(scanner(settings.repository, settings.included, settings.excluded))
    logger.info(f"Number of {settings.framework} files found: {len(files)}")
    
    analyze_method = globals().get(f'analyze_{settings.framework}')

    modules: List[ModuleInfo] = []
    for file in files:
        try:
            modules.append(analyze_method(file))
        except Exception:
            _, error, line_error = sys.exc_info()
            tb = traceback.extract_tb(line_error)
            error_trace(tb, logger, error)

    logger.info(f"Generating README ...")
    readme_path = render_readme(modules, settings.repository, settings.output)
    logger.info(f"README generated: {readme_path}")

    logger.info("Generating dependency graph ...")
    graphic_path = render_graphic(modules, settings.output, settings.repository, settings.framework)
    logger.info(f"Dependency graph generated: {graphic_path}")

    logger.info("Generating report ...")
    report_path = render_report(modules, settings.output, settings.repository, settings.framework)
    logger.info(f"Report generated: {report_path}")

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE