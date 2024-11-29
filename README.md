# Alignment in low level modules for python
- Background
  - This is an exploratory work for implementing faster pairwise alignment algorithms for python in low level modules that are able to run orders of magnitude faster
  - It is also an oppturnity for me to learn about this kind of development

# Overview of low level modules
Afaik there are several ways to write low level modules for python
- C modules and then compile them as python extensions
- Cython extensions (Cython is a python/C hybrid language that compiles to C)
- Rust via PyO3 bindings

## TODOs
- [x] Initial benchmarking of part of the nw algorithm using different languages as modules for python
- This pkg should implement
  - [ ] needleman-wunsch
  - [ ] needleman-wunsch-gotoh (used in pepsar)
  - [ ] smith-waterman
- Look into Hirschberg and Myers Miller alignments?
- There is only one implementation of the gotoh algorithm on github that is written in rust but it is not a package
- This looks interesting https://github.com/RagnarGrootKoerkamp/astar-pairwise-aligner
 - exact pairwise aligner in rust using a*, with linear-like runtime wrt to sequence lenght 0.0
- [ ] Hyperfine for benchmarking

## Comparisions
| Sequence Lengths | Implementation | Time (microseconds) | Speedup vs Python |
|-----------------|----------------|---------------------|-------------------|
| 22, 20          | Python         | 268.21             | 1x (baseline)    |
|                 | Numba          | 31.53              | 8.5x             |
|                 | Rust           | 2.48               | 108x             |
|                 | Cython         | 1.70               | 158x             |
|                 | C              | 1.51               | 178x             |
| 27, 27          | Python         | 436.45             | 1x (baseline)    |
|                 | Numba          | 40.36              | 10.8x            |
|                 | Rust           | 3.43               | 127x             |
|                 | Cython         | 1.93               | 226x             |
|                 | C              | 1.86               | 235x             |
| 44, 45          | Python         | 1,184.26           | 1x (baseline)    |
|                 | Numba          | 77.78              | 15.2x            |
|                 | Rust           | 7.61               | 156x             |
|                 | Cython         | 3.52               | 336x             |
|                 | C              | 3.38               | 350x             |

## Compare Rust and C without python

