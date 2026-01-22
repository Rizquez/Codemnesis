# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import Union, List
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def percentage(part: int, total: int, *, factor: int = 2) -> Union[float, int]:
    """
    Calculate the percentage that `part` represents of `total`.

    Args:
        part (int):
            The part value to compare against the total.
        total (int):
            The total or whole used as the denominator.
        factor (int, optional):
            The number of decimal places to which the result 
            will be rounded (if applicable).

    Returns:
        (float | int):
            The percentage value.
    """
    if total == 0:
        return total
    
    num = round((part / total) * 100, factor)
    return int(num) if num.is_integer() else num
    
def average(elements: List[Union[int, float]]) -> Union[int, float]:
    """
    Calculate the average of a list of numerical values.

    Args:
        elements (List[Union[int, float]]):
            List of numerical values to be averaged.

    Returns:
        (int | float):
            The calculated average.
    """
    num = sum(elements) / len(elements)
    return int(num) if num.is_integer() else num

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE