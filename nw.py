import numpy as np
from numba import jit

def needleman_wunsch(
    a: str, b: str, match_score: int = 1, mismatch_score: int = -1
) -> str:
    # Convert strings to list of chars
    a_chars = list(a)
    b_chars = list(b)
    # Create matrix with zeros
    rows = len(a_chars) + 1
    cols = len(b_chars) + 1
    matrix = np.zeros((rows, cols), dtype=np.int32)
    # Initialize first row and column
    matrix[0, :] = np.arange(cols) * mismatch_score
    matrix[:, 0] = np.arange(rows) * mismatch_score
    # Fill the matrix
    for i in range(1, rows):
        for j in range(1, cols):
            left = matrix[i - 1, j] + mismatch_score
            up = matrix[i, j - 1] + mismatch_score
            diag = matrix[i - 1, j - 1] + (
                match_score if a_chars[i - 1] == b_chars[j - 1] else mismatch_score
            )
            matrix[i, j] = max(left, up, diag)
    return ""


@jit(nopython=True)
def needleman_wunsch_fast(
    a_chars: str,
    b_chars: str,
    match_score: int = 1,
    mismatch_score: int = -1,
) -> str:
    rows = len(a_chars) + 1
    cols = len(b_chars) + 1
    matrix = np.zeros((rows, cols), dtype=np.int32)
    # Initialize
    for i in range(cols):
        matrix[0, i] = i * mismatch_score
    for i in range(rows):
        matrix[i, 0] = i * mismatch_score
    # Fill matrix
    for i in range(1, rows):
        for j in range(1, cols):
            left = matrix[i - 1, j] + mismatch_score
            up = matrix[i, j - 1] + mismatch_score
            diag = matrix[i - 1, j - 1] + (
                match_score if a_chars[i - 1] == b_chars[j - 1] else mismatch_score
            )
            matrix[i, j] = max(left, up, diag)
    return ""
