def sum_as_string(a: int, b: int) -> str:
    """
    Accepts two integers and returns their sum as a string

    Args:
        a (int): The first integer
        b (int): The second integer
    Returns:
        str: The sum of the two integers

    >>> paligner.sum_as_string(1, 2)
    '3'
    >>> paligner.sum_as_string(3, 4)
    '7'
    """

def needleman_wunsch(
    a: str, b: str, match_score: int | None, mismatch_score: int | None
) -> str:
    """
    Accepts two strings and returns their Needleman-Wunsch alignment
    """
