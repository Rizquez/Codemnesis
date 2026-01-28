# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Union, Set, TYPE_CHECKING
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.tools.nums import percentage, average

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def general_summary(
    sloc: int, 
    framework: str,
    repository_name: str,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]]
) -> Dict[str, Union[str, List[str]]]:
    """
    Generates the executive summary block of the report.

    Based on the repository's global metrics (SLOC and documentation coverage) and signals such as 
    the presence of *hotspots*, it builds a dictionary ready to be injected into the DOCX template.

    **Notes:**
        - Average coverage is calculated as the average of classes, methods, and attributes.
        - The thresholds used are heuristic for classifying coverage as high/moderate/low.

    Args:
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        repository_name (str):
            Name of the repository/project.
        class_percent (Union[float, int]):
            Percentage of documented classes out of the total.
        method_percent (Union[float, int]):
            Percentage of documented methods out of the total.
        attribute_percent (Union[float, int]):
            Percentage of documented attributes out of the total.
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        hotspots (List[Dict[str, Union[str, int]]]):
            List of modules considered *hotspots* (by size, complexity, or low documentation).

    Returns:
        Dict:
            Dictionary with keys expected by the template.
    """
    key_points = []
    key_points.append(
        f'The repository contains {len(module_stats)} modules with a total of {sloc} source lines of code.'
    )

    doc_average = average([class_percent, method_percent, attribute_percent])
    if doc_average >= 75:
        key_points.append('The overall documentation coverage is high across the codebase.')
    elif doc_average >= 50:
        key_points.append('The documentation coverage is moderate and could be improved in some areas.')
    else:
        key_points.append('The documentation coverage is low, which may affect maintainability.')

    if hotspots:
        key_points.append(
            f'{len(hotspots)} modules concentrate a significant '
            'portion of the logic and may require special attention.'
        )
    else:
        key_points.append('No significant concentration of complexity was detected across the modules.')

    return {
        'repository_goal': (
            f'This repository implements a {framework.capitalize()}-based codebase '
            f'designed to provide structured functionality within the {repository_name} project.'
        ),
        'scope': (
            'The analysis covers all detected source modules, focusing on structure, '
            'documentation coverage, and complexity distribution.'
        ),
        'key_points': key_points
    }

def global_stats(loc: int, sloc: int, framework: str, modules: List[ModuleInfo]) -> Dict[str, Union[str, int]]:
    """
    Build basic global statistics for the report.

    Generate a dictionary with high-level information: main language/framework, number of files analyzed, 
    and LOC/SLOC totals. The returned format is designed to be inserted directly into the DOCX template.

    Args:
        loc (int):
            Total number of lines in the file, including comments, blank lines, and code.
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        framework (str):
            Name of the framework used, which must have a compatible mapping method.
        modules (List[ModuleInfo]):
            List of `ModuleInfo` objects representing the analyzed modules in the repository.

    Returns:
        Dict:
            Dictionary with keys expected by the template.
    """
    return {
        'languages': f'{framework.capitalize()}.',
        'n_files': f'{len(modules)}.',
        'total_loc': f'{loc}.',
        'total_sloc': f'{sloc}.'
    }

def hotspots_modules(sloc: int, module_stats: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
    """
    Identify hotspot modules based on size, approximate complexity, and documentation.

    A hotspot is a module that is a candidate for priority review for one or more reasons:
        - It contributes a significant percentage of the total SLOC (>= 10% or >= 20%).
        - It has many methods (>= 15), which may indicate high complexity.
        - It has low documentation coverage (<= 50%) considering items (classes+methods+attributes).

    **Notes:**
        - If `sloc` is 0, percentages cannot be calculated and an empty list is returned.
        - Thresholds are heuristic and can be adjusted according to the context of the project.

    Args:
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.

    Returns:
        List:
            List of candidates ranked from most to least relevant.
    """
    if not sloc:
        return []
    
    candidates = []
    for stats in module_stats:
        if not stats['sloc']:
            continue
        
        comment = []

        sloc_percentage = percentage(stats['sloc'], sloc)
        if sloc_percentage >= 20:
            comment.append("Very large module (\u2265 20\u0025 of total SLOC).")
        elif sloc_percentage >= 10:
            comment.append("Relevant module by size (\u2265 10\u0025 of total SLOC).")
        else:
            pass # Size is only considered relevant above 10% of the total SLOC

        if stats['n_methods'] >= 15:
            comment.append("Many methods (potentially high complexity).")

        doc_percentage = percentage(stats['documented_items'], stats['total_items']) if stats['total_items'] else 0
        if stats['total_items'] and doc_percentage <= 50:
            comment.append("Low documentation coverage (\u2264 50\u0025).")

        if not comment:
            continue

        candidates.append({
            'name': stats['name'],
            'sloc': stats['sloc'],
            'percent': f'{sloc_percentage}\u0025',
            'num_percent': sloc_percentage,
            'comment': '\n'.join(comment)
        })

    return sorted(
        candidates, 
        key=lambda candidate: (candidate['num_percent'], candidate['sloc']),
        reverse=True
    )

def complexity_notes(sloc: int, module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 10) -> List[str]:
    """
    Generates interpretive notes on complexity based on simple metrics.

    Produces natural language phrases that help contextualize the analysis:
        - Average size per module (SLOC).
        - Average number of methods per module.
        - Detection of very large modules by absolute size (heuristic).
        - Concentration of SLOC in the top 20% of modules.
        - Modules with many methods (possible God modules/objects).

    **Notes:**
        - Default thresholds used:
            - `LARGE_SLOC = 1000` for large module.
            - `MANY_METHODS = 30` for many methods.
        - If there is no `sloc` or `module_stats` is empty, an empty list is returned.

    Args:
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        limit (int, optional):
            Maximum number of grades returned.

    Returns:
        List:
            List of notes (phrases) with complexity observations, truncated to `limit`.
    """
    if not sloc or not module_stats:
        return []
    
    notes = []

    num_modules = len(module_stats)
    total_methods = sum(int(module['n_methods']) for module in module_stats)

    sloc_average = average(sloc, divider=num_modules, round_off=True) if num_modules else 0
    methods_average = average(total_methods, divider=num_modules, round_off=True, decimals=1) if num_modules else 0
    notes.append(
        f'The project contains {num_modules} modules with an average size of '
        f'{sloc_average} SLOC and about {methods_average} methods per module.'
    )

    # Identify very large modules by absolute size
    LARGE_SLOC = 1000  # heuristic threshold
    large_modules = [module for module in module_stats if int(module['sloc']) >= LARGE_SLOC]

    if large_modules:
        names = ', '.join(module['name'] for module in large_modules[:limit])

        if len(large_modules) == 1:
            notes.append(
                f'One module exceeds {LARGE_SLOC} SLOC ({names}), '
                'which may indicate high structural complexity.'
            )
        else:
            notes.append(
                f'{len(large_modules)} modules exceed {LARGE_SLOC} SLOC '
                f'({names}), concentrating a significant amount of logic.'
            )

    # Concentration in the code base: the top 20% of modules by SLOC
    sorted_by_sloc = sorted(
        module_stats,
        key=lambda module: int(module['sloc']),
        reverse=True
    )

    top_count = max(1, int(num_modules * 0.2))
    top_modules = sorted_by_sloc[:top_count]
    sloc_top = sum(int(module['sloc']) for module in top_modules)
    sloc_top_percent = percentage(sloc_top, sloc)
    if sloc_top_percent >= 50:
        names = ', '.join(module['name'] for module in top_modules[:limit])
        notes.append(
            f'A small group of modules ({top_count} modules: {names}) '
            f'contains about {sloc_top_percent}\u0025 of the total SLOC.'
        )

    # Modules with many methods (possible God objects)
    MANY_METHODS = 30  # heuristic threshold
    heavy_method_modules = [module for module in module_stats if int(module['n_methods']) >= MANY_METHODS]
    if heavy_method_modules:
        names = ', '.join(m['name'] for m in heavy_method_modules[:limit])
        notes.append(
            f'Some modules declare a large number of methods ({MANY_METHODS} or more), '
            f'which may complicate maintenance ({names}).'
        )

    return notes[:limit]

def documentation_coverage(
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int]
) -> Dict[str, str]:
    """
    Format the documentation coverage for the report.

    Convert the numerical percentages of documentation (classes/methods/attributes) into strings with 
    the percent symbol and period, as is usually required by a DOCX template.

    Args:
        class_percent (Union[float, int]):
            Percentage of documented classes out of the total.
        method_percent (Union[float, int]):
            Percentage of documented methods out of the total.
        attribute_percent (Union[float, int]):
            Percentage of documented attributes out of the total.

    Returns:
        Dict:
            Dictionary with keys expected by the template.
    """
    return {
        'class_percent': f'{class_percent}\u0025.',
        'method_percent': f'{method_percent}\u0025.',
        'attribute_percent': f'{attribute_percent}\u0025.'
    }

def best_documented_modules(module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 5) -> List[Dict]:
    """
    Select the modules with the best documentation coverage.

    Calculate, for each module, the percentage of documented items: `documented_items / total_items * 100`, 
    and return the best ones sorted from highest to lowest.

    **Notes:**
        - Modules with `total_items == 0` are omitted to avoid invalid divisions.

    Args:
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        limit (int, optional):
            Maximum number of modules to be returned.

    Returns:
        List:
            List of items (dictionaries) sorted by descending percentage, truncated to `limit`.
    """
    candidates = []

    for stats in module_stats:
        total_items = stats['total_items']
        if not total_items:
            continue
        
        doc_percentage = percentage(stats['documented_items'], total_items)

        candidates.append({
            'name': f'{stats["name"]}:',
            'text':f'{doc_percentage}\u0025 of this module is documented.',
            'percent': doc_percentage
        })

    return sorted(
        candidates,
        key=lambda candidate: candidate['percent'],
        reverse=True
    )[:limit]

def worst_documented_modules(module_stats: List[Dict[str, Union[str, int]]], *, limit: int = 5) -> List[Dict]:
    """
    Select the modules with the worst documentation coverage.

    Same as `_best_documented_modules`, but sorted from lowest to highest percentage to identify modules that 
    require priority attention in terms of documentation.

    **Notes:**
        - Modules with `total_items == 0` are omitted.

    Args:
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        limit (int, optional):
            Maximum number of modules to be returned.

    Returns:
        List:
            List of items (dictionaries) sorted by ascending percentage, truncated to `limit`.
    """
    candidates = []

    for stats in module_stats:
        total_items = stats['total_items']
        if not total_items:
            continue

        doc_percentage = percentage(stats['documented_items'], total_items)

        candidates.append({
            'name': f'{stats["name"]}:',
            'text':f'{doc_percentage}\u0025 of this module is documented.',
            'percent': doc_percentage
        })

    return sorted(
        candidates,
        key=lambda candidate: candidate['percent']
    )[:limit]

def internal_dependencies(
    dep_map: Dict[str, Set[str]], 
    repository: str, 
    *, 
    limit: int = 5, 
    factor: int = 2
) -> Dict[str, Union[int, float, List[str], str]]:
    """
    Analyzes the graph of internal dependencies between modules and generates a summary.

    Based on a dependency map (`dep_map`), it calculates:
        - Out-degree: number of modules that each module imports (outgoing dependencies).
        - In-degree: number of modules that import each module (incoming dependencies).
        - Independent modules: no incoming or outgoing dependencies.
        - Average dependencies per module (average of outgoing edges).
        - Core modules: modules with the highest in-degree (most referenced by other modules).

    **Notes:**
        - If `dep_map` is empty, return default values and a summary message.
        - If a destination appears that does not exist as a key (rare case), it is added to maintain consistency.
        - Dense interconnectivity is estimated by counting modules with >= 5 outgoing dependencies.

    Args:
        dep_map(Dict[str, Set[str]]): 
            Dictionary where each key is a module and its value is a set of modules on which 
            it depends.
        repository (str):
            Base path of the repository or project to be analyzed.
        limit (int, optional):
            Maximum number of modules to be returned.
        factor (int, optional):
            Number of decimal places to use when rounding the average number of dependencies when it is not an integer.

    Returns:
        Dict:
            Dictionary with keys expected by the template.
    """
    if not dep_map:
        return {
            'independent_modules': 0,
            'avg_dependencies': 0,
            'core_modules': [],
            'summary': 'No dependencies were detected, or the dependency map could not be constructed.'
        }
    
    summary_parts = []
    modules = list(dep_map.keys())

    # out-degree: how many modules each module imports
    out_degree = {module: len(dep_map.get(module, set())) for module in modules}

    # in-degree: how many modules matter to each module
    in_degree = {module: 0 for module in modules}
    for targets in dep_map.values():
        for dest in targets:
            if dest in in_degree:
                in_degree[dest] += 1
            else: # If a destination appears that is not listed as a key (a rare case), it will be added
                in_degree[dest] = 1
                out_degree.setdefault(dest, 0)
                dep_map.setdefault(dest, set())

    all_modules = sorted(set(list(out_degree.keys()) + list(in_degree.keys())))

    num_modules = len(all_modules)
    total_edges = sum(out_degree.get(module, 0) for module in all_modules)
    summary_parts.append(
        f'{num_modules} modules were analyzed and {total_edges} '
        'dependency relationships (internal imports) were detected.'
    )

    dependencies_average = average(total_edges, divider=num_modules, round_off=True, decimals=factor)
    summary_parts.append(f'The average number of dependencies per module is {dependencies_average}.')

    # Independent modules:
    #   These modules do not import other modules (out = 0)
    #   No one imports these modules (in = 0)
    independent = [
        module for module in all_modules
        if out_degree.get(module, 0) == 0 and in_degree.get(module, 0) == 0
    ]

    if independent:
        summary_parts.append(
            f'{len(independent)} independent modules (with no incoming or outgoing dependencies) were found.'
        )
    else:
        summary_parts.append('No completely independent modules were found.')

    # Core modules (most referenced): highest in-degree (NOT in+out)
    most_referenced = sorted(
        all_modules,
        key=lambda module: in_degree.get(module, 0),
        reverse=True
    )[:limit]

    core_modules = []
    for module in most_referenced:
        indeg = in_degree.get(module, 0)
        if indeg <= 0:
            continue

        # % of files referencing this module (approx)
        # Excluding self-reference potential
        reference_percetage = percentage(indeg, max(1, num_modules - 1))

        name = Path(module).resolve().relative_to(Path(repository).resolve()).name
        core_modules.append(f'{name}: referenced by \u007e{reference_percetage}\u0025 of the files in the repository.')

    if core_modules:
        summary_parts.append(
            f'The repository contains a total of {len(core_modules)} modules that we consider '
            'to be the most central (with the greatest connectivity).'
        )
    else:
        summary_parts.append(
            'No clear core modules were identified (very low or non-existent dependencies).'
        )

    dense = sum(1 for module in all_modules if out_degree.get(module, 0) >= 5)
    if dense >= max(1, int(0.2 * num_modules)):
        summary_parts.append(
            'The structure has moderate/high interconnectivity: several modules have quite a few dependencies.'
        )
    else:
        summary_parts.append('The structure appears relatively modular: most modules have few dependencies.')

    return {
        'independent_modules': len(independent),
        'avg_dependencies': dependencies_average,
        'core_modules': core_modules,
        'summary': summary_parts
    }

def technical_risks(
    sloc: int,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]],
    *,
    limit: int = 8
) -> List[str]:
    """
    Generates a list of main technical risks based on heuristic signals.

    Assesses typical risks of maintainability and evolution:
        1) Low or moderate documentation coverage.
        2) Concentration of SLOC in a few modules (top 20%).
        3) Existence of very large modules (>= 1500 SLOC).
        4) Modules with many methods (>= 40) as an indicator of complexity.
        5) Presence of hotspots (critical modules due to size/complexity/doc).
        6) Dependencies concentrated in core modules (cascading impact).

    **Notes:**
        - If there is no `module_stats`, return a message indicating that risks could not be calculated.
        - The thresholds (35/55, 60% concentration, 1500 SLOC, 40 methods) are heuristic.

    Args:
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        class_percent (Union[float, int]):
            Percentage of documented classes out of the total.
        method_percent (Union[float, int]):
            Percentage of documented methods out of the total.
        attribute_percent (Union[float, int]):
            Percentage of documented attributes out of the total.
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        hotspots (List[Dict[str, Union[str, int]]]):
            List of detected hotspots.
        dependencies (Dict[str, Union[int, float, List[str], str]]):
            Dependency summary (includes `core_modules`).
        limit (int, optional):
            Maximum number of modules to be returned.
    
    Returns:
        List:
            List of phrases describing main risks, truncated to `limit`.
    """
    if not module_stats:
        return ['Risks could not be calculated because no module statistics are available.']

    risks: List[str] = []

    # Risk 1: Insufficient documentation
    doc_average = average([class_percent, method_percent, attribute_percent])
    if doc_average < 35:
        risks.append(
            'Low documentation coverage: increases the risk of difficult maintenance and errors when modifying the code.'
        )
    elif doc_average < 55:
        risks.append('Moderate documentation coverage: some parts may be difficult to understand without context.')
    else:
        pass # If the average coverage is >= 55%, it is not considered a risk
    
    # Risk 2: Code concentration (SLOC)
    if sloc:
        top_count = max(1, int(len(module_stats) * 0.2))

        sorted_by_sloc = sorted(module_stats, key=lambda module: int(module.get('sloc', 0)), reverse=True)

        top_modules = sorted_by_sloc[:top_count]
        top_sloc = sum(int(module.get('sloc', 0)) for module in top_modules)

        top_percentage = percentage(top_sloc, sloc)
        if top_percentage >= 60:
            risks.append(f'High concentration of logic: {top_percentage}\u0025 of SLOC is in {top_count} modules.')

    # Risk 3: very large modules
    large = [module for module in module_stats if int(module.get('sloc', 0)) >= 1500]
    if large:
        risks.append(f'There are very large modules (\u2265 1500 SLOC) that may require refactoring.')

    # Risk 4: Too many methods in one module
    heavy_methods = [module for module in module_stats if int(module.get('n_methods', 0)) >= 40]
    if heavy_methods:
        risks.append(
            'Potentially high complexity: some modules have many methods (\u2265 40), '
            'which makes testing and changes difficult.'
        )

    # Risk 5: Hotspots detected
    if hotspots:
        risks.append(f'Hotspots (modules critical due to size/complexity/documentation) were detected.')

    # Risk 6: Central dependency
    if dependencies and isinstance(dependencies.get('core_modules', None), list):
        core = dependencies.get('core_modules', [])
        if core:
            risks.append(
                f'Concentrated dependencies: there are very central modules whose modification can impact many parts.'
            )

    return risks[:limit]

def risk_impact(
    sloc: int,
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]]
) -> Dict[str, List[str]]:
    """
    Interpret the impact of risks in three dimensions: maintainability, onboarding, and evolution.

    Produces explanations in natural language that help understand how they affect:
        - Documentation coverage (average).
        - Number of hotspots.
        - Total code size (SLOC).
        - Average dependency level and core size (core modules).

    **Notes:**
        - The documentation thresholds and size thresholds are heuristic for classifying impact.
        
    Args:
        sloc (int):
            Number of meaningful lines in the file, excluding comments and blank lines.
        class_percent (Union[float, int]):
            Percentage of documented classes out of the total.
        method_percent (Union[float, int]):
            Percentage of documented methods out of the total.
        attribute_percent (Union[float, int]):
            Percentage of documented attributes out of the total.
        hotspots (List[Dict[str, Union[str, int]]]):
            List of detected hotspots.
        dependencies (Dict[str, Union[int, float, List[str], str]]):
            Dependency summary (includes `core_modules`).

    Returns:
        Dict:
            Dictionary with three lists of phrases.
    """
    num_core = 0
    dependencies_average = 0
    
    # Maintainability
    maintainability = []

    doc_average = average([class_percent, method_percent, attribute_percent])
    if doc_average < 40:
        maintainability.append(
            'The lack of documentation increases maintenance costs '
            'and the risk of errors when modifying existing code.'
        )
    elif doc_average < 60:
        maintainability.append(
            'Documentation is uneven: some parts will be easy to maintain, '
            'while others will require more time to understand.'
        )
    else:
        maintainability.append(
            'Documentation coverage is reasonable and helps maintain the code with less friction.'
        )

    num_hotspots = len(hotspots) if hotspots else 0
    if num_hotspots >= 3:
        maintainability.append(
            'The existence of several hotspots suggests areas with '
            'high logical load where changes may be more delicate.'
        )
    elif num_hotspots == 0:
        maintainability.append(
            'No clear hotspots are detected, which usually indicates a more uniform distribution of logic.'
        )
    else:
        maintainability.append(
            'There are some isolated hotspots that should be monitored to prevent them from becoming bottlenecks.'
        )

    if sloc >= 20000:
        maintainability.append(
            'The total size of the code (high SLOC) implies more '
            'maintenance surface area and a greater need for consistency.'
        )
    elif sloc >= 5000:
        maintainability.append(
            'The code size is medium: maintenance is manageable, but complexity should be monitored.'
        )
    else:
        maintainability.append(
            'The code size is small: maintenance should be relatively easy if the structure is consistent.'
        )

    # Onboarding
    onboarding = []

    if doc_average < 40:
        onboarding.append(
            'Poor documentation hinders the onboarding of new developers and increases reliance on tacit knowledge.'
        )
    elif doc_average < 60:
        onboarding.append(
            'Onboarding will be reasonable, but some areas will require support or knowledge transfer sessions.'
        )
    else:
        onboarding.append(
            'Documentation facilitates onboarding and reduces the time needed to understand the system.'
        )

    if dependencies:
        dependencies_average = float(dependencies.get('avg_dependencies', 0) or 0)
        core = dependencies.get('core_modules', [])
        num_core = len(core) if isinstance(core, list) else 0
        
        if num_core >= 3:
            onboarding.append(
                'The presence of several core modules suggests that '
                'onboarding should start with those key components.'
            )
        elif num_core == 0:
            onboarding.append(
                'There are no clearly central modules, which may allow for incremental learning by area.'
            )
        else:
            onboarding.append(
                'There is a small set of core modules that serve as an entry point for understanding the system.'
            )

        if dependencies_average >= 5:
            onboarding.append(
                'The level of dependencies is relatively high, which may increase the learning curve.'
            )
        elif dependencies_average >= 2:
            onboarding.append(
                'Dependencies are moderate; the learning curve depends on how the domains are separated.'
            )
        else:
            onboarding.append('Dependencies are low, which favors understanding by isolated modules.')
    
    # Evolution (future changes)
    evolution = []

    if dependencies and num_core >= 3:
        evolution.append(
            'Changes to core modules can have a cascading impact, '
            'so it is advisable to reinforce tests and review changes.'
        )
    elif dependencies and num_core > 0:
        evolution.append(
            'There is a small core whose evolution must be managed carefully to avoid collateral effects.'
        )
    else:
        evolution.append(
            'The dependency structure does not show a dominant core, which may facilitate localized changes.'
        )

    if num_hotspots >= 3:
        evolution.append(
            'Hotspots can become friction points for evolution; it is advisable to plan gradual refactors.'
        )
    elif num_hotspots > 0:
        evolution.append(
            'Monitoring specific hotspots will help prevent too much logic from being concentrated in a few modules.'
        )
    else:
        evolution.append(
            'No notable hotspots are observed, suggesting potentially more stable evolution by area.'
        )

    if doc_average < 40:
        evolution.append(
            'Improving documentation will accelerate future evolutions and reduce risk when introducing changes.'
        )
    elif doc_average < 60:
        evolution.append(
            'Strengthening documentation in critical modules will reduce the cost of evolution in the medium term.'
        )
    else:
        evolution.append(
            'Current documentation helps introduce changes with greater security and predictability.'
        )

    return {
        'maintainability': maintainability,
        'onboarding': onboarding,
        'evolution': evolution
    }
    
def recommendations(
    class_percent: Union[float, int], 
    method_percent: Union[float, int], 
    attribute_percent: Union[float, int],
    module_stats: List[Dict[str, Union[str, int]]],
    hotspots: List[Dict[str, Union[str, int]]],
    dependencies: Dict[str, Union[int, float, List[str], str]],
    *,
    limit: int = 6
) -> Dict[str, List[str]]:
    """
    Generates actionable recommendations for refactoring, documentation, and architecture.

    Produces three lists of recommendations:
        - `refactor`: actions to reduce complexity and size (hotspots, very large modules, many methods).
        - `docs`: actions to improve coverage and consistency of docstrings.
        - `architecture`: actions to reduce coupling, improve layers, and manage core modules.

    **Notes:**
        - If there is no `module_stats`, a recommendation is returned indicating that there is insufficient data.
        - Heuristic thresholds used:
            - Large module: >= 1500 SLOC.
            - Many methods: >= 40.
            - High dependencies: `avg_dependencies` >= 5 (moderate from 2).

    Args:
        class_percent (Union[float, int]):
            Percentage of documented classes out of the total.
        method_percent (Union[float, int]):
            Percentage of documented methods out of the total.
        attribute_percent (Union[float, int]):
            Percentage of documented attributes out of the total.
        module_stats (List[Dict[str, Union[str, int]]]):
            List with detailed statistics by module.
        hotspots (List[Dict[str, Union[str, int]]]):
            List of detected hotspots.
        dependencies (Dict[str, Union[int, float, List[str], str]]):
            Dependency summary (includes `core_modules`).

    Returns:
        Dict:
            Dictionary with lists of recommendations.
    """
    recommendations = {
        'refactor': [],
        'docs': [],
        'architecture': [],
    }

    if not module_stats:
        recommendations['architecture'].append('There are not enough module statistics to generate recommendations.')
        return recommendations
    
    # Refactor
    if hotspots:
        names = ', '.join(str(hot.get('name', '')) for hot in hotspots[:limit] if hot.get('name'))
        if names:
            recommendations['refactor'].append(
                f'Prioritize refactoring in hotspots to reduce complexity and isolate responsibilities ({names}).'
            )
        else:
            recommendations['refactor'].append(
                'Prioritize refactoring in hotspots to reduce complexity and isolate responsibilities.'
            )

    # Top modules by SLOC (for more specific suggestions)
    sorted_by_sloc = sorted(module_stats, key=lambda module: int(module.get('sloc', 0)), reverse=True)
    
    big = [module for module in sorted_by_sloc if int(module.get('sloc', 0)) >= 1500]
    if big:
        names = ', '.join(str(module.get('name', '')) for module in big[:limit] if module.get('name'))
        recommendations['refactor'].append(
            f'Split very large modules (\u2265 1500 SLOC) into smaller, testable components. ({names}).'
        )

    heavy_methods = [module for module in sorted_by_sloc if int(module.get('n_methods', 0)) >= 40]
    if heavy_methods:
        names = ', '.join(str(module.get('name', '')) for module in heavy_methods[:limit] if module.get('name'))
        recommendations['refactor'].append(
            'Reduce modules with too many methods (\u2265 40): '
            f'extract services/helpers and simplify logic ({names}).'
        )

    if not recommendations['refactor']:
        recommendations['refactor'].append(
            'No clear signs of urgent refactoring were detected; maintain periodic review of complexity.'
        )

    # Documentation
    doc_average = average([class_percent, method_percent, attribute_percent])
    if doc_average < 35:
        recommendations['docs'].append(
            'Increase base documentation: add docstrings/summaries to main classes and methods.'
        )
        recommendations['docs'].append(
            'Document critical modules (hotspots and cores modules) in particular before adding new features.'
        )
    elif doc_average < 60:
        recommendations['docs'].append(
            'Reinforce documentation in areas with low coverage to reduce maintenance time.'
        )
        recommendations['docs'].append(
            'Ensure consistency of format in docstrings (Args/Returns/Raises) to facilitate automatic reading.'
        )
    else:
        recommendations['docs'].append(
            'Maintain the current level of documentation and require minimum docstrings for relevant changes.'
        )

    # If there are hotspots, specific documentation is suggested there
    if hotspots:
        names = ', '.join(str(hot.get('name', '')) for hot in hotspots[:limit] if hot.get('name'))
        if names:
            recommendations['docs'].append(
                f'Add usage examples and design notes in hotspots to facilitate future modifications. ({names}).'
            )

    # Architecture
    cores = dependencies.get('core_modules', []) if isinstance(dependencies, dict) else []
    cores = cores if isinstance(cores, list) else []
    if cores:
        recommendations['architecture'].append(
            'Clearly define responsibilities and contracts in core modules to minimize cascading impact.'
        )

    dependencies_average = float(dependencies.get('avg_dependencies', 0) or 0) if isinstance(dependencies, dict) else 0
    if dependencies_average >= 5:
        recommendations['architecture'].append(
            'Reduce coupling between modules: review imports, introduce layers or interfaces where it makes sense.'
        )
        recommendations['architecture'].append(
            'Avoid circular dependencies and reinforce boundaries between domains '
            '(for example: separate IO layer, domain, and utilities).'
        )
    elif dependencies_average >= 2:
        recommendations['architecture'].append(
            'Review dependencies between modules to maintain clear domain separation and avoid progressive coupling.'
        )
    else:
        recommendations['architecture'].append(
            'The dependency structure appears to be modular; maintain '
            'import discipline so that it does not deteriorate over time.'
        )

    independent = int(dependencies.get('independent_modules', 0) or 0) if isinstance(dependencies, dict) else 0
    if independent >= 5:
        recommendations['architecture'].append(
            'Review independent modules: confirm whether they are intended as utilities, tests, or orphaned code.'
        )

    recommendations['refactor'] = recommendations['refactor'][:limit]
    recommendations['docs'] = recommendations['docs'][:limit]
    recommendations['architecture'] = recommendations['architecture'][:limit]
    
    return recommendations

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE