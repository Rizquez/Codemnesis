# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.maps import dependencies_map
from common.constants import ALGORITHM_VERSION
from src.utils.metrics import repository_metrics
from src.renderers.builders.analysis import (
    summary, global_stats, complexity_notes, documentation_coverage, 
    hotspots_modules, best_documented_modules, worst_documented_modules, 
    internal_dependencies, technical_risks, risk_impact, recommendations
)

if TYPE_CHECKING:
    from src.models import ModuleInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

# TODO: Reportlab works, but the report format needs improvement

__all__ = ['render_report']

PDF_FILE = 'Report.pdf'

def render_report(modules: List[ModuleInfo], output: str, repository: str, framework: str) -> str:
    """
    
    """
    repository_name = Path(repository).resolve().name

    dep_map = dependencies_map(modules, repository, framework)
    statistics = repository_metrics(modules, repository)

    hotspots = hotspots_modules(statistics.sloc, statistics.module_stats)
    dependencies = internal_dependencies(dep_map, repository)
    doc_coverage = documentation_coverage(
        statistics.class_percent, 
        statistics.method_percent, 
        statistics.attribute_percent
    )

    context = {
        'repository_name': f'{repository_name}.',
        'analysis_date': f'{datetime.now().strftime("%A, %B %d, %Y")}.',
        'summary': summary(
            statistics.sloc, framework, repository_name,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots
        ),
        'global_stats': global_stats(statistics.loc, statistics.sloc, framework, modules),
        'modules_overview': statistics.modules_overview,
        'hotspots': hotspots,
        'complexity_notes': complexity_notes(statistics.sloc, statistics.module_stats),
        'doc_coverage': doc_coverage,
        'best_documented_modules': best_documented_modules(statistics.module_stats),
        'worst_documented_modules': worst_documented_modules(statistics.module_stats),
        'dependencies': dependencies,
        'risks': technical_risks(
            statistics.sloc,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots, dependencies
        ),
        'risk_impact': risk_impact(
            statistics.sloc,
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            hotspots, dependencies
        ),
        'recommendations': recommendations(
            statistics.class_percent, statistics.method_percent, statistics.attribute_percent,
            statistics.module_stats, hotspots, dependencies
        ),
        'version': ALGORITHM_VERSION,
    }

    Path(output).mkdir(parents=True, exist_ok=True)
    pdf_path = os.path.join(output, PDF_FILE)

    _render_pdf(pdf_path, context)
    return pdf_path

def _render_pdf(pdf_path: str, context: Dict[str, object]) -> None:
    """
    
    """
    styles = getSampleStyleSheet()
    title = ParagraphStyle('Title', parent=styles['Title'], fontSize=20, spaceAfter=12)
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], spaceBefore=10, spaceAfter=6)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], spaceBefore=8, spaceAfter=4)
    body = styles['BodyText']

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )

    story = []

    # Cover / header
    story.append(Paragraph(f'Repository analyzed: {context["repository_name"]}', title))
    story.append(Paragraph(f'Analysis date: {context["analysis_date"]}', body))
    story.append(Spacer(1, 12))

    # Executive summary
    story.append(Paragraph('Executive summary', h1))
    summary = context['summary']

    story.append(Paragraph('Objective of the repository analyzed', h2))
    story.append(Paragraph(summary['repository_goal'], body))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Scope of the analysis', h2))
    story.append(Paragraph(summary['scope'], body))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Main conclusions', h2))
    key_points = [ListItem(Paragraph(p, body), leftIndent=12) for p in summary['key_points']]
    story.append(ListFlowable(key_points, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 12))

    # General repository profile
    story.append(Paragraph('General repository profile', h1))
    story.append(Paragraph('General data', h2))
    gs = context['global_stats']
    story.append(Paragraph(f'Main languages: {gs["languages"]}', body))
    story.append(Paragraph(f'Total number of files analyzed: {gs["n_files"]}', body))
    story.append(Paragraph(f'Total lines of code (LOC): {gs["total_loc"]}', body))
    story.append(Paragraph(f'Total effective lines of code (SLOC): {gs["total_sloc"]}', body))
    story.append(Spacer(1, 10))

    # Modules overview table
    story.append(Paragraph('Distribution by modules', h2))
    story.append(Paragraph('Summary of modules analyzed:', body))
    story.append(Spacer(1, 6))
    story.append(_modules_table(context['modules_overview']))
    story.append(Spacer(1, 12))

    # Hotspots
    story.append(Paragraph('Key modules and hotspots', h1))
    story.append(Paragraph('Larger modules', h2))
    story.append(Paragraph('List of modules that contain the most code:', body))
    story.append(Spacer(1, 6))
    story.append(_hotspots_table(context['hotspots']))
    story.append(Spacer(1, 10))

    # Complexity notes
    story.append(Paragraph('Structural complexity', h2))
    notes = context['complexity_notes']
    if notes:
        items = [ListItem(Paragraph(n, body), leftIndent=12) for n in notes]
        story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    else:
        story.append(Paragraph('No complexity notes available.', body))
    story.append(Spacer(1, 12))

    # Documentation coverage
    story.append(Paragraph('Documentation coverage', h1))
    story.append(Paragraph('Coverage summary', h2))
    dc = context['doc_coverage']
    story.append(Paragraph(f'Classes documented: {dc["class_percent"]}', body))
    story.append(Paragraph(f'Methods/Functions documented: {dc["method_percent"]}', body))
    story.append(Paragraph(f'Attributes documented: {dc["attribute_percent"]}', body))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Best-documented modules', h2))
    best = context['best_documented_modules']
    if best:
        items = [ListItem(Paragraph(f'{m["name"]} {m["text"]}', body), leftIndent=12) for m in best]
        story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    else:
        story.append(Paragraph('No modules with documentation stats.', body))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Modules with the least documentation', h2))
    worst = context['worst_documented_modules']
    if worst:
        items = [ListItem(Paragraph(f'{m["name"]} {m["text"]}', body), leftIndent=12) for m in worst]
        story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    else:
        story.append(Paragraph('No modules with documentation stats.', body))
    story.append(Spacer(1, 12))

    # Architecture and dependencies
    story.append(Paragraph('Architecture and dependencies', h1))
    story.append(Paragraph('Overview', h2))
    deps = context['dependencies']
    story.append(Paragraph(f'Independent modules: {deps["independent_modules"]}', body))
    story.append(Paragraph(f'Average dependencies per module: {deps["avg_dependencies"]}', body))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Core modules (most referenced)', h2))
    core = deps.get('core_modules', []) or []
    if core:
        # Si quieres “negrita” en el nombre del módulo, puedes formatearlo con <b>...</b> aquí.
        items = [ListItem(Paragraph(c, body), leftIndent=12) for c in core]
        story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    else:
        story.append(Paragraph('No core modules detected.', body))
    story.append(Spacer(1, 8))

    story.append(Paragraph('Comments on the dependencies diagram', h2))
    dep_summary = deps.get('summary', []) or []
    if isinstance(dep_summary, list) and dep_summary:
        items = [ListItem(Paragraph(s, body), leftIndent=12) for s in dep_summary]
        story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    else:
        story.append(Paragraph(str(dep_summary), body))
    story.append(Spacer(1, 12))

    # Risks and technical debt
    story.append(Paragraph('Risks and technical debt', h1))
    story.append(Paragraph('Identified risks', h2))
    risks = context['risks'] or []
    items = [ListItem(Paragraph(r, body), leftIndent=12) for r in risks]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 10))

    story.append(Paragraph('Potential impact', h2))
    ri = context['risk_impact']

    story.append(Paragraph('Maintainability', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in ri['maintainability']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Onboarding', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in ri['onboarding']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Future evolution', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in ri['evolution']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 12))

    # Recommendations
    story.append(Paragraph('Recommendations', h1))
    rec = context['recommendations']

    story.append(Paragraph('Refactoring and structure', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in rec['refactor']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Documentation', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in rec['docs']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 6))

    story.append(Paragraph('Architecture', h2))
    items = [ListItem(Paragraph(x, body), leftIndent=12) for x in rec['architecture']]
    story.append(ListFlowable(items, bulletType='bullet', leftIndent=18))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f'Report generated by AutoDocMind – v.{context["version"]}', body))

    doc.build(story)

def _modules_table(modules_overview: List[Dict[str, object]]) -> Table:
    """
    
    """
    headers = ['Module', 'LOC', 'SLOC', 'Classes', 'Methods', 'Functions', 'Attributes']
    data = [headers]
    for m in modules_overview:
        data.append([
            str(m.get('name', '')),
            str(m.get('loc', '')),
            str(m.get('sloc', '')),
            str(m.get('n_classes', '')),
            str(m.get('n_methods', '')),
            str(m.get('n_functions', '')),
            str(m.get('n_attributes', '')),
        ])

    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return tbl


def _hotspots_table(hotspots: List[Dict[str, object]]) -> Table:
    """
    
    """
    headers = ['Module', 'SLOC', '\u0025 of total', 'Comment']
    data = [headers]
    for h in hotspots:
        data.append([
            str(h.get('name', '')),
            str(h.get('sloc', '')),
            str(h.get('percent', '')),
            str(h.get('comment', '')),
        ])

    tbl = Table(data, repeatRows=1, colWidths=[140, 60, 70, 240])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return tbl

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE