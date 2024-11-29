# File: caligner.pyx
import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free
from libc.string cimport strlen

def needleman_wunsch(str a, str b, int match_score=1, int mismatch_score=-1):
    # Get byte strings from Python strings
    cdef bytes a_bytes = a.encode('utf8')
    cdef bytes b_bytes = b.encode('utf8')
    
    # Get C char pointers from byte strings
    cdef const char* a_chars = a_bytes
    cdef const char* b_chars = b_bytes
    
    # Declare C variables for better performance
    cdef size_t rows = strlen(a_chars) + 1
    cdef size_t cols = strlen(b_chars) + 1
    cdef size_t i, j
    
    # Allocate matrix memory in C
    cdef int* matrix = <int*>malloc(rows * cols * sizeof(int))
    if not matrix:
        raise MemoryError("Failed to allocate matrix")
    
    # Initialize first row and column
    for i in range(cols):
        matrix[i] = i * mismatch_score
    for i in range(rows):
        matrix[i * cols] = i * mismatch_score
    
    # Fill the matrix using C-level operations
    cdef int left, up, diag, max_val
    for i in range(1, rows):
        for j in range(1, cols):
            left = matrix[(i - 1) * cols + j] + mismatch_score
            up = matrix[i * cols + (j - 1)] + mismatch_score
            diag = matrix[(i - 1) * cols + (j - 1)] + (
                match_score if a_chars[i - 1] == b_chars[j - 1] else mismatch_score
            )
            
            # Find maximum value
            max_val = left
            if up > max_val:
                max_val = up
            if diag > max_val:
                max_val = diag
                
            matrix[i * cols + j] = max_val
    
    # Free the matrix memory
    free(matrix)
