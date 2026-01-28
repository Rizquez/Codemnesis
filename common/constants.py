# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from pathlib import Path
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
"""
Absolute path to the root of the project.
"""

ALGORITHM = 'ALGORITHM'
"""
Handler for the `.log` file for storing the execution trace.
"""

ALGORITHM_VERSION = '0.18.4'
"""
Current version of the algorithm.
"""

NO_MODULE = 'This module does not contain documentation on classes or functions.'
"""
Message to print when a module has no documentation.
"""

NO_CLASS = 'This class does not contain documentation or it has not been possible to extract it.'
"""
Message to print when a class has no documentation.
"""

NO_ATTRIBUTE = 'This attribute does not contain documentation or it has not been possible to extract it.'
"""
Message to print when a attribute has no documentation.
"""

NO_METHOD = 'This method does not contain documentation or it has not been possible to extract it.'
"""
Message to print when a method has no documentation.
"""

NO_FUNCTION = 'This function does not contain documentation or it has not been possible to extract it.'
"""
Message to print when a function has no documentation.
"""

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE