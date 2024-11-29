import pendulum
import random
import nw
import raligner
import caligner
import cythonaligner
from typing import Callable, List, Tuple
from statistics import mean, stdev


def generate_random_sequences(
    n_sequences: int, min_len: int = 20, max_len: int = 100
) -> List[Tuple[str, str]]:
    """
    Generate pairs of random DNA sequences for benchmarking.
    Returns a list of tuples, where each tuple contains two sequences to align.
    """
    sequence_pairs = []
    for _ in range(n_sequences):
        seq_a = "".join(random.choices("ACGT", k=random.randint(min_len, max_len)))
        seq_b = "".join(random.choices("ACGT", k=random.randint(min_len, max_len)))
        sequence_pairs.append((seq_a, seq_b))
    return sequence_pairs


def benchmark_implementation(
    func: Callable[[str, str], str],
    sequence_pairs: List[Tuple[str, str]],
    n_experiments: int = 5,
) -> Tuple[float, float]:
    """
    Benchmark an implementation by running all alignments in batch.

    Args:
        func: The alignment implementation to benchmark
        sequence_pairs: List of sequence pairs to align
        n_experiments: Number of times to repeat the entire batch

    Returns:
        Tuple of (mean time in seconds, standard deviation)
    """
    # Store the total time for each complete experiment
    experiment_times = []

    for _ in range(n_experiments):
        # Time how long it takes to process all sequences
        start = pendulum.now()

        # Process all sequences in this experiment
        for seq_a, seq_b in sequence_pairs:
            func(seq_a, seq_b)

        end = pendulum.now()
        total_time = (end - start).total_seconds()
        experiment_times.append(total_time)

    return mean(experiment_times), stdev(experiment_times)


def main():
    # Configuration
    batch_size = 100  # Number of alignments per experiment
    n_experiments = 10  # Number of times to repeat the batch
    random.seed(42)

    # Dictionary of implementations to test
    implementations = {
        "C": caligner.needleman_wunsch,
        "Cython": cythonaligner.needleman_wunsch,
        "Rust": raligner.needleman_wunsch,
        "Python w/Numba": nw.needleman_wunsch_fast,
        "Python": nw.needleman_wunsch,
    }

    # Warmup for Numba
    warmup_a, warmup_b = "ACGT", "ACGT"
    _ = nw.needleman_wunsch_fast(warmup_a, warmup_b)

    # Generate all sequence pairs once
    print(f"Generating {batch_size} random sequence pairs...")
    sequence_pairs = generate_random_sequences(batch_size, min_len=10, max_len=100)

    # Calculate average sequence lengths for reporting
    avg_len_a = mean(len(seq_a) for seq_a, _ in sequence_pairs)
    avg_len_b = mean(len(seq_b) for _, seq_b in sequence_pairs)
    print(f"Average sequence lengths: {avg_len_a:.1f} and {avg_len_b:.1f}\n")

    # Benchmark each implementation
    print(f"Running {n_experiments} experiments of {batch_size} alignments each\n")
    for name, func in implementations.items():
        mean_time, std_time = benchmark_implementation(
            func, sequence_pairs, n_experiments
        )
        # Calculate and display various metrics
        total_time = f"{mean_time:.3e} ± {std_time:.3e}"
        per_alignment = (
            f"{(mean_time/batch_size)*1000:.3e} ± {(std_time/batch_size)*1000:.3e}"
        )
        alignments_per_sec = f"{batch_size/mean_time:.1f} ± {(batch_size/mean_time)*(std_time/mean_time):.1f}"

        print(f"{name:15} results:")
        print(f"  Total batch time (s)     : {total_time}")
        print(f"  Time per alignment (ms)   : {per_alignment}")
        print(f"  Alignments per second     : {alignments_per_sec}")
        print()


if __name__ == "__main__":
    main()
