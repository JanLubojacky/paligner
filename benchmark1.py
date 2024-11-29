import pendulum
import random
import nw
import paligner
import caligner
import cythonaligner
from typing import Callable, Tuple
from statistics import mean, stdev


def generate_random_sequence(min_len: int = 20, max_len: int = 100) -> str:
    """Generate a random DNA sequence of length between min_len and max_len."""
    length = random.randint(min_len, max_len)
    return "".join(random.choices("ACGT", k=length))


def benchmark_implementation(
    func: Callable[[str, str], str],
    seq_a: str,
    seq_b: str,
    n_repetitions: int = 5,
    batch_size: int = 1000,
) -> Tuple[float, float]:
    """
    Benchmark a single implementation of Needleman-Wunsch algorithm.

    Args:
        func: The implementation to benchmark
        seq_a: First sequence
        seq_b: Second sequence
        n_repetitions: Number of times to repeat the batch of calls
        batch_size: Number of calls to make in each batch

    Returns:
        Tuple of (mean time, standard deviation)
    """
    times = []

    for _ in range(n_repetitions):
        # Time batch_size calls as a single operation
        start = pendulum.now()
        for _ in range(batch_size):
            func(seq_a, seq_b)
        end = pendulum.now()

        # Record the average time per call in this batch
        batch_time = (end - start).total_seconds() / batch_size
        times.append(batch_time)

    return mean(times), stdev(times)


def main():
    # Configuration
    n_experiments = 5  # Number of different sequence pairs to test
    batch_size = 1000  # Number of calls per timing measurement
    random.seed(42)

    # Dictionary mapping implementation names to their functions
    implementations = {
        "Rust": paligner.needleman_wunsch,
        "C": caligner.needleman_wunsch,
        "Cython": cythonaligner.needleman_wunsch,
        "Python": nw.needleman_wunsch,
        "Python w/Numba": nw.needleman_wunsch_fast,
    }

    # Warmup for Numba
    warmup_a = generate_random_sequence()
    warmup_b = generate_random_sequence()
    _ = nw.needleman_wunsch_fast(warmup_a, warmup_b)

    # Run benchmarks
    for exp in range(n_experiments):
        # Generate new random sequences for each experiment
        seq_a = generate_random_sequence()
        seq_b = generate_random_sequence()
        print(
            f"\nExperiment {exp+1} with sequences of length {len(seq_a)} and {len(seq_b)}"
        )

        # Benchmark each implementation
        for name, func in implementations.items():
            mean_time, std_time = benchmark_implementation(
                func, seq_a, seq_b, n_repetitions=5, batch_size=batch_size
            )
            print(f"{name:15} : {mean_time:.6f} ± {std_time:.6f} s per call")


if __name__ == "__main__":
    main()
