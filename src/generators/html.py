# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import html
from pathlib import Path
from typing import List, TYPE_CHECKING, Union
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from src.utils.strings import DocStrings
from settings.constants import ALGORITHM_VERSION

if TYPE_CHECKING:
    from src.models.structures import ModuleInfo, FunctionInfo
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['HtmlGenerator']

INDEX_FILE = 'index.html'

TEMPLATE_FILE = Path('public/templates/base.html')
STYLE_FILE = Path('public/styles/main.css')

class HtmlGenerator:
    """
    Utility for creating and maintaining project documentation in README format.

    This class concentrates the **presentation** (HTML format) and **output** (writing to disk) operations based 
    on the structured results produced by the code analyzer (`ModuleInfo`). It does not perform static analysis: 
    it only transforms already processed data into a readable document.
    """

    @classmethod
    def render(cls, modules: List['ModuleInfo'], directory: str, *, cleaned: List[str] = ['*', '`']) -> str:
        """
        Assemble the final HTML document using the base template.

        **Replace the following markers in the template:**
            - {{SIDEBAR}}: List with links to each module.
            - {{SECTIONS}}: Blocks with details of each module.
                - {{REPO}}: Path of the analyzed repository (escaped).
                - {{VERSION}}: Version of the algorithm.

        Args:
            modules (List[ModuleInfo]):
                Collection of analyzed modules with their structure.
            directory (str):
                Root path of the repository; used to calculate visible relative paths.
            cleaned (List[str]):
                List of tokens to be removed from the html.

        Returns:
            str:
                HTML ready to be written to disk.
        """
        root = Path(directory).resolve()

        sidebar: List[str] = []
        for module in sorted(modules, key=lambda module: module.path):
            path = Path(module.path).resolve()

            id_module = cls.__escape(path.as_posix())
            label = cls.__escape(path.relative_to(root).as_posix())

            sidebar.append(f'<li><a href="#{id_module}">{label}</a></li>')

        sections: List[str] = []
        for module in sorted(modules, key=lambda module: module.path):
            path = Path(module.path).resolve()

            id_module = cls.__escape(path.as_posix())
            label = cls.__escape(path.relative_to(root).as_posix())

            parts = [f'<section id="{id_module}" data-module="{label.lower()}">']
            parts.append(f'<h2>Module: {label}</h2>')

            if not module.classes and not module.functions:
                parts.append('<p class=italics>This module does not contain documentation on classes or functions.</p>')
            else:
                if module.classes:
                    parts.append('<h3>Classes</h3>')
                    for clss in module.classes:
                        id_clss = f'{id_module}::class::{cls.__escape(clss.name)}'
                        parts.append(
                            f"""
                                <details id="{id_clss}">
                                    <summary>{cls.__escape(clss.name)}</summary>
                                    <div class="card function">
                                        {DocStrings.to_html(clss.doc, cleaned=cleaned) if clss.doc else '<br/>'}
                                        {cls.__render_methods(clss.methods, cleaned)}
                                    </div>
                                </details>
                            """
                        )

                if module.functions:
                    parts.append('<h3>Functions</h3>')
                    for func in module.functions:
                        fid = f'{id_module}::func::{cls.__escape(func.name)}'
                        parts.append(
                            f"""
                                <details id="{fid}">
                                    <summary>{cls.__escape(func.name)} (Declared in line: {func.lineno})</summary>
                                    <div class="card function">
                                        {DocStrings.to_html(func.doc, cleaned=cleaned) if func.doc else '<br/>'}
                                    </div>
                                </details>
                            """
                        )

            parts.append('</section>')
            sections.append("\n".join(parts))

        template = TEMPLATE_FILE.read_text(encoding='utf-8')
        css = STYLE_FILE.read_text(encoding='utf-8')

        template = template.replace('</head>', f'<style>\n{css}\n</style>\n</head>')
        
        return (
            template
            .replace('{{SIDEBAR}}', ''.join(sidebar))
            .replace('{{SECTIONS}}', ''.join(sections))
            .replace('{{REPO}}', html.escape(root.name))
            .replace('{{VERSION}}', ALGORITHM_VERSION)
        )

    @classmethod
    def __render_methods(cls, methods: List['FunctionInfo'], cleaned: List[str]) -> str:
        """
        Builds the HTML block for the methods of a class.

        Args:
            methods (List[FunctionInfo]):
                List of methods belonging to a class.
            cleaned (List[str]):
                List of tokens to be removed from the html.

        Returns:
            str:
                HTML with each method (name, line, and docstring if it exists). 
                Returns an empty string if there are no methods.
        """
        if not methods:
            return ''
        
        out = []
        for method in methods:
            out.append(
                f"""
                    <div class="card method">
                        <span class="italics">{html.escape(method.name)} (Declared in line: {method.lineno})</span>
                        {DocStrings.to_html(method.doc, cleaned=cleaned) if method.doc else '<br/>'}
                    </div>
                """
            )

        return '\n'.join(out)

    @staticmethod
    def __escape(section: Union[str, None]) -> str:
        """
        Escapes text for safe use in HTML.

        Args:
            section (str | None):
                Text to escape.

        Returns:
            str:
                Text escaped with HTML entities, if None, returns an empty string.
        """
        return html.escape(section) if section else '<br/>'

    @staticmethod
    def write(text: str, output: str) -> Path:
        """
        Writes the generated HTML to the `index.html` 
        file in the output directory.

        Args:
            text (str):
                HTML content to persist.
            output (str):
                Output directory path.

        Returns:
            Path:
                Full path of the written file.
        """
        out = Path(output)
        out.mkdir(parents=True, exist_ok=True)

        target = out / INDEX_FILE

        target.write_text(text, encoding='utf-8')

        return target

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE