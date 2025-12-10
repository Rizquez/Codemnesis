# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from argparse import Namespace
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['Settings']

FOLDER = 'AutoDocMind-Output'

EXTENSIONS = {
    'python': {'.py'},
    'csharp': {'.cs'}
}

EXCLUDED = {
    '.git', '.hg', '.svn', '.idea', '.vscode', '.ruff_cache', '.mypy_cache', '.pytest_cache', '.tox', '.eggs', 
    '__pycache__', 'build', 'dist', 'site-packages', 'node_modules', 'venv', '.venv', 'env', '.env', 'bin', 'obj',
    'Debug', 'Release', '.vs'
}

class Settings:
    """
    Class that builds and manages the specific configuration for executing the algorithm.

    **Purpose:**
        - Centralize the loading of input arguments.
        - Define and prepare the necessary paths for storing the output of the generated files.

    When this class is instantiated, the output paths and necessary resources are automatically generated.
    """

    def __init__(self, args: 'Namespace') -> None:
        self.__root = self.__root_path()

        self.__framework = args.framework.lower()
        self.__repository = args.repository
        self.__excluded = self.__set_excluded(args.excluded)
        self.__included = EXTENSIONS.get(self.__framework, set())
        
        self.__template = os.path.join(self.__root, 'templates', 'report.docx')

        if args.output:
            self.__output = os.path.join(args.output, FOLDER)
        else:
            self.__output = os.path.join(self.__root, FOLDER)

    @property
    def framework(self) -> str:
        return self.__framework
    
    @property
    def repository(self) -> str:
        return self.__repository

    @property
    def excluded(self) -> Set[str]:
        return self.__excluded
    
    @property
    def included(self) -> Set[str]:
        return self.__included
    
    @property
    def template(self) -> str:
        return self.__template
    
    @property
    def output(self) -> str:
        return self.__output
    
    @staticmethod
    def __root_path() -> str:
        """
        This static method determines the absolute path of the current file, 
        removes the last directory level, and returns the resulting path.

        Returns:
            str: 
                Absolute path of the project root directory.
        """
        return '\\'.join(item for item in os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])
    
    @staticmethod
    def __set_excluded(excluded: str) -> Set[str]:
        """
        Updates the set of directories or files excluded from analysis.

        Converts the received string into a set of values separated by commas, and adds them 
        to the global set `EXCLUDED`.

        Args:
            excluded (str):
                String with the names of directories or files to exclude, separated by commas.

        Returns:
            Set:
                Updated set of exclusions.
        """
        if excluded:
            return EXCLUDED.update(set(excluded.split(',')))

        return EXCLUDED

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE