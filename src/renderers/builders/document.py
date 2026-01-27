# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Union, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, Spacer, Table, TableStyle, 
    ListFlowable, ListItem, PageBreak
)
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from common.constants import ALGORITHM_VERSION
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

PAGE_MARGIN = 36

FONT_STYLE = 'Helvetica'
FONT_STYLE_BOLD = 'Helvetica-Bold'

BULLET_TYPE = 'bullet'
LEFT_INDENT = 12 * mm
BULLET_DEDENT = 6 * mm

# Color palette extracted from → https://www.bairesdev.com/tools/ai-colors
PRIMARY_200 = colors.HexColor('#b6ccd8')
ACCENT_100 = colors.HexColor('#71c4ef')
ACCENT_200 = colors.HexColor('#00668c')
TEXT_200 = colors.HexColor('#313d44')
BG_100 = colors.HexColor('#fffefb')
BG_200 = colors.HexColor('#f5f4f1')

cover = ParagraphStyle(
    'TitleCover',
    fontName=FONT_STYLE_BOLD,
    fontSize=24,
    alignment=TA_CENTER,
    textColor=TEXT_200,
    spaceAfter=25
)

footer = ParagraphStyle(
    'Footer',
    fontName=FONT_STYLE,
    fontSize=11,
    alignment=TA_CENTER,
    textColor=TEXT_200,
    spaceBefore=10
)

title1 = ParagraphStyle(
    'Title1',
    fontName=FONT_STYLE_BOLD,
    fontSize=20,
    alignment=TA_JUSTIFY,
    textColor=TEXT_200,
    spaceBefore=20, 
    spaceAfter=18
)

title2 = ParagraphStyle(
    'Title2',
    fontName=FONT_STYLE_BOLD,
    fontSize=16,
    alignment=TA_JUSTIFY,
    textColor=TEXT_200,
    spaceBefore=20, 
    spaceAfter=14
)

title3 = ParagraphStyle(
    'Title3',
    fontName=FONT_STYLE_BOLD,
    fontSize=14,
    alignment=TA_JUSTIFY,
    textColor=TEXT_200,
    spaceBefore=18, 
    spaceAfter=10
)

paragraph = ParagraphStyle(
    'Paragraph',
    fontName=FONT_STYLE,
    fontSize=11,
    alignment=TA_JUSTIFY,
    textColor=TEXT_200,
    spaceBefore=10
)

vignette = ParagraphStyle(
    'Vignette',
    fontName=FONT_STYLE,
    fontSize=11,
    alignment=TA_JUSTIFY,
    textColor=TEXT_200,
    spaceBefore=6
)

table_style = TableStyle([ 
    # Header
    ('FONTNAME', (0, 0), (-1, 0), FONT_STYLE_BOLD),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('TEXTCOLOR', (0, 0), (-1, 0), BG_100),
    ('BACKGROUND', (0, 0), (-1, 0), ACCENT_200),
    ('LINEBELOW', (0, 0), (-1, 0), 1, ACCENT_100),

    # Body
    ('FONTNAME', (0, 1), (-1, -1), FONT_STYLE),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('TEXTCOLOR', (0, 1), (-1, -1), TEXT_200),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),

    # Grid / Borders
    ('GRID', (0, 0), (-1, -1), 0.25, PRIMARY_200),
    ('BOX', (0, 0), (-1, -1), 0.6, PRIMARY_200),

    # Zebra rows
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BG_200, BG_100]),

    # Padding
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
])

class Document:
    """
    Section-based PDF report builder.

    The class encapsulates a `SimpleDocTemplate` and an internal list of *flowables* 
    that are added using high-level methods.
    """

    def __init__(self, filename: str) -> None:
        self.__story = []
        self.__doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=PAGE_MARGIN,
            rightMargin=PAGE_MARGIN,
            topMargin=PAGE_MARGIN,
            bottomMargin=PAGE_MARGIN
        )

    def __add_vignettes(
        self, 
        items: List[str], 
        *, 
        simple: bool = True, 
        first_key: Optional[str] = None, 
        second_key: Optional[str] = None
    ) -> None:
        """
        Adds a bulleted list to the document history.

        Args:
            items (List[str]): 
                Items to include as bullets (strings or dictionaries).
            simple (bool, optional): 
                If `True`, use the item as is. If `False`, compose the text with keys.
            first_key (str, optional): 
                Key of the first text fragment (required if `simple=False`).
            second_key (str, optional):
                Key of the second text fragment (required if `simple=False`).
        """
        if simple:
            elements = [ListItem(Paragraph(item, vignette)) for item in items]
        else:
            elements = [ListItem(Paragraph(f'{item[first_key]} {item[second_key]}', vignette)) for item in items]

        self.__story.append(ListFlowable(
            elements,
            bulletType=BULLET_TYPE,
            leftIndent=LEFT_INDENT,
            bulletDedent=BULLET_DEDENT
        ))
    
    def build(self) -> None:
        """
        Build the final PDF from the accumulated story.
        """
        self.__doc.build(self.__story)

    def front_page(self, repository_name: str, analysis_date: str) -> None:
        """
        Add a standard cover page to the document.

        **The cover page includes:**
            - Main title of the report.
            - Name of the repository analyzed.
            - Date of analysis and version of the generator.
            - Page break at the end.

        Args:
            repository_name (str): 
                Name of the analyzed repository.
            analysis_date (str): 
                Date of the analysis (formatted as a string).
        """
        self.__story.append(Spacer(1, 20))
        self.__story.append(Paragraph('TECHNICAL REPOSITORY', cover))
        self.__story.append(Paragraph('ANALYSIS REPORT', cover))

        self.__story.append(Spacer(1, 240))
        self.__story.append(Paragraph('Repository analyzed:', cover))
        self.__story.append(Paragraph(repository_name, cover))
        self.__story.append(Spacer(1, 300))

        self.__story.append(Paragraph(analysis_date, footer))
        self.__story.append(Paragraph(f'Report generated by Codemnesis - v.{ALGORITHM_VERSION}', footer))

        self.__story.append(PageBreak())

    def summary_page(self, summary: Dict[str, Union[str, List[str]]]) -> None:
        """
        Add an executive summary page.

        Args:
            summary (Dict[str, Union[str, List[str]]]): 
                Dictionary with the summary content.
        """
        self.__story.append(Paragraph('Executive summary', title1))

        self.__story.append(Paragraph('Objective of the repository analyzed', title2))
        self.__story.append(Paragraph(summary['repository_goal'], paragraph))

        self.__story.append(Paragraph('Scope of the analysis', title2))
        self.__story.append(Paragraph(summary['scope'], paragraph))

        self.__story.append(Paragraph('Main conclusions', title2))
        self.__add_vignettes(summary['key_points'])

        self.__story.append(PageBreak())

    def general_repository_profile(
        self, 
        global_stats: Dict[str, Union[str, int]], 
        modules_overview: List[Dict[str, object]]
    ) -> None:
        """
        Add the general profile section of the repository.

        Args:
            global_stats (Dict[str, Union[str, int]]): 
                Aggregate metrics for the repository.
            modules_overview (List[Dict[str, object]]): 
                List of dictionaries with metrics per module.
        """
        self.__story.append(Paragraph('General repository profile', title1))

        self.__story.append(Paragraph('General data', title2))
        self.__story.append(Paragraph(f'Main languages: {global_stats["languages"]}', paragraph))
        self.__story.append(Paragraph(f'Total number of files analyzed: {global_stats["n_files"]}', paragraph))
        self.__story.append(Paragraph(f'Total lines of code (LOC): {global_stats["total_loc"]}', paragraph))
        self.__story.append(Paragraph(f'Total effective lines of code (SLOC): {global_stats["total_sloc"]}', paragraph))

        self.__story.append(Paragraph('Distribution by modules', title2))
        self.__story.append(Paragraph('Summary of modules analyzed:', paragraph))
        self.__story.append(Spacer(1, 10))
        self.__story.append(self.__modules_table(modules_overview))

        self.__story.append(PageBreak())

    def key_modules_hotspots(self, hotspots: List[Dict[str, object]], complexity_notes: List[str]) -> None:
        """
        Add the key modules and hotspots section.

        Args:
            hotspots (List[Dict[str, object]]): 
                List of dictionaries with data on noteworthy modules.
            complexity_notes (List[str]): 
                Comments or findings on code complexity.
        """
        self.__story.append(Paragraph('Key modules and hotspots', title1))

        self.__story.append(Paragraph('Larger modules', title2))
        self.__story.append(Paragraph('List of modules that contain the most code:', paragraph))
        self.__story.append(Spacer(1, 10))
        self.__story.append(self.__hotspots_table(hotspots))

        self.__story.append(Paragraph('Structural complexity', title2))
        self.__add_vignettes(complexity_notes)

        self.__story.append(PageBreak())        

    def documentation_coverage(
        self, 
        doc_coverage: Dict[str, str], 
        best_modules: List[Dict], 
        worst_modules: List[Dict]
    ) -> None:
        """
        Add the documentation coverage section.

        Args:
            doc_coverage (Dict[str, str]): 
                Dictionary with coverage percentages.
            best_modules (List[Dict]): 
                List of modules with the best documentation.
            worst_modules (List[Dict]): 
                List of modules with the worst documentation.
        """
        self.__story.append(Paragraph('Documentation coverage', title1))

        self.__story.append(Paragraph('Coverage summary', title2))
        self.__story.append(Paragraph(f'Classes documented: {doc_coverage["class_percent"]}', paragraph))
        self.__story.append(Paragraph(f'Methods/Functions documented: {doc_coverage["method_percent"]}', paragraph))
        self.__story.append(Paragraph(f'Attributes documented: {doc_coverage["attribute_percent"]}', paragraph))

        self.__story.append(Paragraph('Modules with the best documentation', title2))
        self.__story.append(self.__add_vignettes(best_modules, simple=False, first_key='name', second_key='text'))

        self.__story.append(Paragraph('Modules with the least documentation', title2))
        self.__story.append(self.__add_vignettes(worst_modules, simple=False, first_key='name', second_key='text'))

        self.__story.append(PageBreak())

    def architecture_dependencies(self, dependencies: Dict[str, Union[int, float, List[str], str]]) -> None:
        """
        Add the architecture and dependencies section.

        Args:
            dependencies (Dict[str, Union[int, float, List[str], str]]): 
                Dictionary with metrics and listings related to dependencies.
        """
        self.__story.append(Paragraph('Architecture and dependencies', title1))

        self.__story.append(Paragraph('Overview', title2))
        self.__story.append(Paragraph(f'Independent modules: {dependencies["independent_modules"]}', paragraph))
        self.__story.append(Paragraph(f'Average dependencies per module: {dependencies["avg_dependencies"]}', paragraph))

        self.__story.append(Paragraph('Core modules (most referenced)', title2))
        self.__story.append(self.__add_vignettes(dependencies['core_modules']))

        self.__story.append(Paragraph('Comments on the dependencies diagram', title2))
        self.__story.append(self.__add_vignettes(dependencies['summary']))

        self.__story.append(PageBreak())

    def risk_technical_debt(self, technical_risks: List[str], risk_impact: Dict[str, List[str]]) -> None:
        """
        Add the risks and technical debt section.

        Args:
            technical_risks (List[str]): 
                Identified risks.
            risk_impact (Dict[str, List[str]]): 
                Dictionary with lists by category.
        """
        self.__story.append(Paragraph('Risks and technical debt', title1))

        self.__story.append(Paragraph('Identified risks', title2))
        self.__story.append(self.__add_vignettes(technical_risks))

        self.__story.append(Paragraph('Potential impact', title2))

        self.__story.append(Paragraph('Maintainability', title3))
        self.__story.append(self.__add_vignettes(risk_impact['maintainability']))

        self.__story.append(Paragraph('Onboarding', title3))
        self.__story.append(self.__add_vignettes(risk_impact['onboarding']))

        self.__story.append(Paragraph('Future evolution', title3))
        self.__story.append(self.__add_vignettes(risk_impact['evolution']))

        self.__story.append(PageBreak())

    def final_recommendations(self, recommendation: Dict[str, List[str]]) -> None:
        """
        Add the final section of recommendations.

        Args:
            recommendation (Dict[str, List[str]]):
                Dictionary with lists of recommendations by category.
        """
        self.__story.append(Paragraph('Recommendations', title1))

        self.__story.append(Paragraph('Refactoring and structure', title2))
        self.__story.append(self.__add_vignettes(recommendation['refactor']))

        self.__story.append(Paragraph('Documentation', title2))
        self.__story.append(self.__add_vignettes(recommendation['docs']))

        self.__story.append(Paragraph('IdentifiArchitectureed', title2))
        self.__story.append(self.__add_vignettes(recommendation['architecture']))

    @staticmethod
    def __modules_table(modules_overview: List[Dict[str, object]]) -> Table:
        """
        Build the distribution table by modules.

        Args:
            modules_overview (List[Dict[str, object]]): 
                List of dictionaries with metrics per module.

        Returns:
            Table:
                A ReportLab `Table` with style applied and header repeated on each page.
        """
        headers = ['Module name', 'LOC', 'SLOC', 'N. Classes', 'N. Methods', 'N. Functions', 'N. Attributes']
        data = [headers]
        for module in modules_overview:
            data.append([
                str(module.get('name', '')),
                str(module.get('loc', '')),
                str(module.get('sloc', '')),
                str(module.get('n_classes', '')),
                str(module.get('n_methods', '')),
                str(module.get('n_functions', '')),
                str(module.get('n_attributes', ''))
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(table_style)
        return table
    
    @staticmethod
    def __hotspots_table(hotspots: List[Dict[str, object]]) -> Table:
        """
        Build the hotspots table (featured modules).

        Args:
            hotspots (List[Dict[str, object]]): 
                List of dictionaries with data on noteworthy modules.

        Returns:
            Table:
                A ReportLab `Table` with style applied and header repeated on each page.
        """
        headers = ['Module name', 'SLOC', '\u0025 of total', 'Comment']
        data = [headers]
        for hotspot in hotspots:
            data.append([
                str(hotspot.get('name', '')),
                str(hotspot.get('sloc', '')),
                str(hotspot.get('percent', '')),
                str(hotspot.get('comment', '')),
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(table_style)
        return table

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE