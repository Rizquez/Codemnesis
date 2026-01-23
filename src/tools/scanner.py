# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Set, Iterator
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def scanner(repository: str, included: Set[str], excluded: Set[str]) -> Iterator[Path]:
    """
    Recursively traverse a directory and generate the paths of files that match 
    the specified extensions, excluding unwanted folders.

    Args:
        repository (str):
            Base path of the repository or project to be analyzed.
        included (Set[str]):
            Set of file extensions to include in the scan.
        excluded (Set[str]):
            Set of directory names to ignore during the search.

    Yields:
        Path:
            Absolute path of each file that meets the defined criteria.
    """
    root = Path(repository).resolve()

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in excluded]

        for filename in filenames:
            path = Path(dirpath) / filename
            
            if path.suffix in included:
                yield path

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE