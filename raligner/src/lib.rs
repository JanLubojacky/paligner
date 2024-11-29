//use pyo3::prelude::*;
//use std::vec::Vec;
//
//#[derive(Debug)]
//struct Matrix {
//    rows: usize,
//    cols: usize,
//    data: Vec<i32>,
//}
//
//impl Matrix {
//    fn new(rows: usize, cols: usize) -> Self {
//        Self {
//            rows,
//            cols,
//            data: vec![0; rows * cols],
//        }
//    }
//
//    #[inline]
//    fn index(&self, row: usize, col: usize) -> usize {
//        row * self.cols + col
//    }
//
//    fn get(&self, row: usize, col: usize) -> &i32 {
//        &self.data[self.index(row, col)]
//    }
//
//    fn set(&mut self, row: usize, col: usize, value: i32) {
//        let idx = self.index(row, col);
//        self.data[idx] = value;
//    }
//
//    fn print(&self) {
//        // First find the maximum width needed for any number
//        let mut max_width = 0;
//        for row in 0..self.rows {
//            for col in 0..self.cols {
//                let num_width = self.get(row, col).to_string().len();
//                max_width = max_width.max(num_width);
//            }
//        }
//
//        // Print dimensions as header
//        println!("Matrix {}×{}", self.rows, self.cols);
//
//        // Print the matrix with aligned numbers
//        for row in 0..self.rows {
//            for col in 0..self.cols {
//                let num = self.get(row, col).to_string();
//                if col + 1 == self.cols {
//                    println!("{:>width$}", num, width = max_width);
//                } else {
//                    print!("{:>width$} ", num, width = max_width);
//                }
//            }
//        }
//    }
//}
//
//fn initialize_matrix(matrix: &mut Matrix, mismatch_score: i32) {
//    for i in 0..matrix.rows {
//        matrix.set(i, 0, i as i32 * mismatch_score);
//    }
//    for i in 0..matrix.cols {
//        matrix.set(0, i, i as i32 * mismatch_score);
//    }
//}
//
//#[pyfunction]
//#[pyo3(signature = (a, b, match_score=None, missmatch_score=None))]
//fn needleman_wunsch(
//    a: &str,
//    b: &str,
//    match_score: Option<i32>,
//    missmatch_score: Option<i32>,
//) -> PyResult<String> {
//    // there is only a small difference between as_bytes() and
//    // collecting into a vector of chars
//    //let a = a.chars().collect::<Vec<char>>();
//    //let b = b.chars().collect::<Vec<char>>();
//    let a = a.as_bytes();
//    let b = b.as_bytes();
//
//    let match_score = match_score.unwrap_or(1);
//    let missmatch_score = missmatch_score.unwrap_or(-1);
//
//    let mut matrix: Matrix = Matrix::new(a.len() + 1, b.len() + 1);
//
//    initialize_matrix(&mut matrix, missmatch_score);
//
//    for i in 1..=a.len() {
//        for j in 1..=b.len() {
//            let left = matrix.get(i - 1, j) + missmatch_score;
//            let up = matrix.get(i, j - 1) + missmatch_score;
//            let diag = matrix.get(i - 1, j - 1)
//                + (if a[i - 1] == b[j - 1] {
//                    match_score
//                } else {
//                    missmatch_score
//                });
//
//            matrix.set(i, j, left.max(up).max(diag));
//        }
//    }
//
//    Ok("".to_string())
//}
//
///// A Python module implemented in Rust.
//#[pymodule]
//fn raligner(m: &Bound<'_, PyModule>) -> PyResult<()> {
//    m.add_function(wrap_pyfunction!(needleman_wunsch, m)?)?;
//    Ok(())
//}

use pyo3::prelude::*;
use std::alloc::{alloc, dealloc, Layout};

/// A matrix struct that safely encapsulates raw memory operations.
/// It maintains the performance of direct memory access while providing
/// a safe interface for the rest of the code to use.
struct Matrix {
    ptr: *mut i32,
    rows: usize,
    cols: usize,
    layout: Layout,
}

impl Matrix {
    /// Creates a new matrix with the specified dimensions.
    /// Returns None if the allocation size would overflow or if allocation fails.
    fn new(rows: usize, cols: usize) -> Option<Self> {
        // Check for potential overflow in size calculation
        let size = rows.checked_mul(cols)?;
        let layout = Layout::array::<i32>(size).ok()?;

        // Allocate memory and create matrix if successful
        let ptr = unsafe { alloc(layout) as *mut i32 };
        if ptr.is_null() {
            None
        } else {
            Some(Self {
                ptr,
                rows,
                cols,
                layout,
            })
        }
    }

    /// Gets a value from the matrix at the specified position.
    /// The bounds checking is done through debug assertions in debug builds only.
    #[inline(always)]
    fn get(&self, row: usize, col: usize) -> i32 {
        debug_assert!(row < self.rows && col < self.cols, "Index out of bounds");
        unsafe { *self.ptr.add(row * self.cols + col) }
    }

    /// Sets a value in the matrix at the specified position.
    #[inline(always)]
    fn set(&mut self, row: usize, col: usize, value: i32) {
        debug_assert!(row < self.rows && col < self.cols, "Index out of bounds");
        unsafe {
            *self.ptr.add(row * self.cols + col) = value;
        }
    }

    /// Initializes the matrix with gap penalties along the first row and column.
    fn init(&mut self, mismatch_score: i32) {
        for i in 0..self.cols {
            self.set(0, i, (i as i32) * mismatch_score);
        }
        for i in 0..self.rows {
            self.set(i, 0, (i as i32) * mismatch_score);
        }
    }
}

impl Drop for Matrix {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.ptr as *mut u8, self.layout);
        }
    }
}

#[pyfunction]
#[pyo3(signature = (a, b, match_score=None, mismatch_score=None))]
fn needleman_wunsch(
    a: &str,
    b: &str,
    match_score: Option<i32>,
    mismatch_score: Option<i32>,
) -> PyResult<()> {
    let match_score = match_score.unwrap_or(1);
    let mismatch_score = mismatch_score.unwrap_or(-1);

    // This assumes ASCII characters only and is slightly faster
    let a = a.as_bytes();
    let b = b.as_bytes();

    // collect into a vector of chars
    //let a = a.chars().collect::<Vec<char>>();
    //let b = b.chars().collect::<Vec<char>>();

    let mut matrix = Matrix::new(a.len() + 1, b.len() + 1)
        .ok_or_else(|| pyo3::exceptions::PyMemoryError::new_err("Failed to allocate matrix"))?;

    matrix.init(mismatch_score);

    // fill matrix
    for i in 1..matrix.rows {
        for j in 1..matrix.cols {
            let left = matrix.get(i - 1, j) + mismatch_score;
            let up = matrix.get(i, j - 1) + mismatch_score;
            let diag = matrix.get(i - 1, j - 1)
                + if a[i - 1] == b[j - 1] {
                    match_score
                } else {
                    mismatch_score
                };

            let max = left.max(up).max(diag);

            matrix.set(i, j, max);
        }
    }

    Ok(())
}

#[pymodule]
fn raligner(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(needleman_wunsch, m)?)?;
    Ok(())
}
