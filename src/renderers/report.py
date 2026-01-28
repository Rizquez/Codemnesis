# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import List, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from src.utils.metrics import repository_metrics
from src.renderers.builders.document import Document
from src.renderers.builders.insights import (
    general_summary, global_stats, complexity_notes, documentation_coverage, 
    hotspots_modules, best_documented_modules, worst_documented_modules, 
    internal_dependencies, technical_risks, risk_impact, recommendations
)

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['render_report']

PDF_FILE = 'Analysis-Report.pdf'

def render_report(modules: List[ModuleInfo], output: str, repository: str, framework: str) -> Path:
    """
    Generates a PDF report of technical analysis for a repository.

    This function orchestrates the calculation of metrics and the composition of the final document 
    using the `Document` class. Based on information from modules and the repository, it calculates 
    global statistics, documentation coverage, hotspots, and internal dependencies, and builds a report 
    with predefined sections.

    Args:
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.
        output (str):
            Path of the directory where the file will be stored.
        repository (str):
            Base path of the repository or project to be analyzed.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.

    Returns:
        Path:
            Absolute path to the generated PDF file.
    """
    out = Path(output) / PDF_FILE
    repository_name = Path(repository).resolve().name

    statistics = repository_metrics(modules, repository)
    doc_coverage = documentation_coverage(
        statistics.class_percent, 
        statistics.method_percent, 
        statistics.attribute_percent
    )

    hotspots = hotspots_modules(statistics.sloc, statistics.module_stats)

    dep_map = dependencies_map(modules, repository, framework)
    dependencies = internal_dependencies(dep_map, repository)

    doc = Document(str(out))
    doc.front_page(
        repository_name,
        datetime.now().strftime('%A, %B %d, %Y')
    )
    doc.summary_page(
        general_summary(
            statistics.sloc, framework, repository_name,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots
        )
    )
    doc.general_repository_profile(
        global_stats(
            statistics.loc, 
            statistics.sloc, 
            framework, 
            modules
        ),
        statistics.modules_overview
    )
    doc.key_modules_hotspots(
        hotspots,
        complexity_notes(
            statistics.sloc, 
            statistics.module_stats
        )
    )
    doc.documentation_coverage(
        doc_coverage,
        best_documented_modules(statistics.module_stats),
        worst_documented_modules(statistics.module_stats)
    )
    doc.architecture_dependencies(dependencies)
    doc.risk_technical_debt(
        technical_risks(
            statistics.sloc,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots, dependencies
        ),
        risk_impact(
            statistics.sloc,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            hotspots, dependencies
        )
    )
    doc.final_recommendations(
        recommendations(
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots, dependencies
        )
    )

    doc.build()
    return out

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE