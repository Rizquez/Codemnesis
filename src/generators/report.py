# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from docxtpl import DocxTemplate
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['generate_report']

FILE = 'Report.docx'

def generate_report(template: str, output: str) -> str:
    """
    
    """
    docx = DocxTemplate(template)

    context = {
        'repository_name': '',
        'analysis_date': '',
        'summary': {
            'repository_goal': '',
            'scope': '',
            'key_points': [
                '',
                '',
                '',
                # ...
            ],
        },
        'global_stats': {
            'languages': '',
            'n_files': 0,
            'total_loc': 0,
            'total_sloc': 0,
        },
        'modules_overview': [
            {
                'path': '',
                'loc': 0,
                'sloc': 0,
                'n_classes': 0,
                'n_methods': 0,
                'n_functions': 0,
            },
            # ...
        ],
        'hotspots': [
            {
                'module': '',
                'sloc': 0,
                'percent_of_total': '0%',
                'comment': '',
            },
            # ...
        ],
        'complexity_notes': [
            '',
            '',
            # ...
        ],
        'doc_coverage': {
            'class_percent': 0,
            'method_percent': 0,
            'attribute_percent': 0,
        },
        'best_documented_modules': [
            {
                'name': '', 
                'percent': 0
            },
            # ...
        ],
        'worst_documented_modules': [
            {
                'name': '', 
                'percent': 0
            },
            # ...
        ],
        'dependencies': {
            'independent_modules': 0,
            'avg_dependencies': 0,
            'core_modules': [
                '', 
                '',
                # ...
            ],
            'summary': '',
        },
        'risks': [
            '',
            '',
            # ...
        ],
        'risk_impact': {
            'maintainability': '',
            'onboarding': '',
            'evolution': '',
            # ...
        },
        'recommendations': {
            'refactor': [
                '',
                # ...
            ],
            'docs': [
                '',
                # ...
            ],
            'architecture': [
                '',
                # ...
            ],
        }
    }

    docx.render(context)

    path = os.path.join(output, FILE)

    docx.save(path)

    return path

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE