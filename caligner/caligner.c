#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>

static PyObject *needleman_wunsch(PyObject *self, PyObject *args) {
  const char *a;
  const char *b;
  int match_score = 1;
  int mismatch_score = -1;

  if (!PyArg_ParseTuple(args, "ss|ii", &a, &b, &match_score, &mismatch_score)) {
    return NULL;
  }

  size_t rows = strlen(a) + 1;
  size_t cols = strlen(b) + 1;

  int *matrix = (int *)malloc(rows * cols * sizeof(int));
  if (!matrix) {
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate matrix");
    return NULL;
  }

  for (size_t i = 0; i < cols; i++) {
    matrix[i] = i * mismatch_score;
  }
  for (size_t i = 0; i < rows; i++) {
    matrix[i * cols] = i * mismatch_score;
  }

  for (size_t i = 1; i < rows; i++) {
    for (size_t j = 1; j < cols; j++) {
      int left = matrix[(i - 1) * cols + j] + mismatch_score;
      int up = matrix[i * cols + (j - 1)] + mismatch_score;
      int diag = matrix[(i - 1) * cols + (j - 1)] +
                 (a[i - 1] == b[j - 1] ? match_score : mismatch_score);

      int max = left;
      if (up > max)
        max = up;
      if (diag > max)
        max = diag;

      matrix[i * cols + j] = max;
    }
  }

  free(matrix);
  Py_RETURN_NONE;
}

// Method definition
static PyMethodDef CalignerMethods[] = {
    {"needleman_wunsch", needleman_wunsch, METH_VARARGS,
     "Compute Needleman-Wunsch alignment."},
    {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition struct
static struct PyModuleDef calignermodule = {PyModuleDef_HEAD_INIT,
                                            "caligner", // name of module
                                            NULL,       // module documentation
                                            -1, // size of per-interpreter state
                                            CalignerMethods};

// Module initialization function
PyMODINIT_FUNC PyInit_caligner(void) {
  return PyModule_Create(&calignermodule);
}
