# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import Union, List, Optional
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

def percentage(part: int, total: int, *, decimals: int = 2) -> Union[float, int]:
    """
    Calculate the percentage that `part` represents of `total`.

    Args:
        part (int):
            The part value to compare against the total.
        total (int):
            The total or whole used as the denominator.
        decimals (int, optional):
            The number of decimal places to which the result 
            will be rounded (if applicable).

    Returns:
        (float | int):
            The percentage value.
    """
    if total == 0:
        return total
    
    num = round((part / total) * 100, decimals)
    return int(num) if num.is_integer() else num
    
def average(
    items: Union[List[Union[int, float]], float, int], 
    *, 
    divider: Optional[int] = None, 
    round_off: bool = False, 
    decimals: int = 2
) -> Union[int, float]:
    """
    Calculates the arithmetic mean of one or more numerical values, 
    with explicit control of the divisor and rounding.

    **The average can be calculated:**
        - Using the number of elements.
        - Using an explicitly provided external divisor.

    Args:
        items (Union[List[Union[int, float]], float, int]):
            Numeric values to average.
        divider (int, optional):
            Divisor to use instead of `len(items)`.
        round_off (bool, optional):
            Indicates whether the result should be rounded.
        decimals (int, optional):
            Number of decimal places to retain when `round_off=True`.

    Returns:
        (int | float):
            Calculated average value.

    Raises:
        ValueError:
            - If `items` is an empty list.
            - If the effective divisor is 0.
            - If `round_off=True` and `decimals < 0`.
    """
    if isinstance(items, (int, float)):
        values: List[Union[int, float]] = [items]
    else:
        values = items

    if not values:
        raise ValueError('You cannot calculate the average of an empty list')

    if divider is not None and divider <= 0:
        raise ValueError('The divisor must be an integer greater than 0')

    effective = divider if divider is not None else len(values)
    avg = sum(values) / effective

    if round_off:
        if decimals < 0:
            raise ValueError('The number of decimal places cannot be negative')
        
        avg = round(avg, decimals)

    return int(avg) if float(avg).is_integer() else avg

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE