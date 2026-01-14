import random
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.brute_force import bin_packing_BF
from src.first_fit_descending import bin_packing_FFD
from src.modified_ffd import mffd_algorithm
from src.column_generation import column_generation_bin_packing



# 0 - uniform
# 1 - small
# 2 - large
# 3 - half
def generate_test(n, C, dist):
    if dist == 0:
        return [random.randint(1, C) for _ in range(n)]
    elif dist == 1:
        return [random.randint(1, C // 4) for _ in range(n)]
    elif dist == 2:
        return [random.randint(C // 2, C) for _ in range(n)]
    elif dist == 3:
        return [random.randint(C // 3, 2 * C // 3) for _ in range(n)]


def solve_brute_force(items, C):
    n = len(items)
    items_sorted = sorted(items, reverse=True)
    for num_bins in range(1, n + 1):
        bins = [0] * num_bins
        assignment = [-1] * n
        if bin_packing_BF(items_sorted, bins, num_bins, C, 0, assignment):
            return num_bins
    return n


def solve_FFD(items, C):
    bins = bin_packing_FFD([(v, i + 1) for i, v in enumerate(items)], len(items), C)
    return len(bins)


def solve_MFFD(items, C):
    bins = mffd_algorithm(items, C)
    return len(bins)


def solve_column_generation(items, C):
    _, _, _, obj = column_generation_bin_packing(
        weights=items, capacity=C, num_iters=50
    )
    return obj


def get_distribution_string(dist):
    return ["Uniform", "Small", "Large", "Half"][dist]


def run_small_tests():
    # Test configurations
    different_n = [10, 15, 20, 25, 30]
    different_C = [20, 50, 100, 1000, 10000]
    distributions = [0, 1, 2, 3]
    num_instances = 1

    print(
        "n\tC\tDistribution\t"
        "BF\tT_BF(ms)\t"
        "FFD\tT_FFD(ms)\t"
        "MFFD\tT_MFFD(ms)\t"
        "CG\tT_CG(ms)\t"
        "FFD/OPT\t\tMFFD/OPT\tCG/OPT"
    )

    total_time_BF = 0.0
    total_time_FFD = 0.0
    total_time_MFFD = 0.0
    total_time_CG = 0.0

    total_ffd_ratio = 0.0
    total_mffd_ratio = 0.0
    total_cg_ratio = 0.0

    num_tests = 0

    for n in different_n:
        for C in different_C:
            for dist in distributions:
                for test_id in range(num_instances):
                    random.seed(23 + test_id)
                    items = generate_test(n, C, dist)

                    # Brute Force
                    t0 = time.time()
                    bf = solve_brute_force(items, C)
                    t1 = time.time()
                    t_bf = (t1 - t0) * 1000
                    total_time_BF += t_bf

                    # First Fit Descending
                    t0 = time.time()
                    ffd = solve_FFD(items, C)
                    t1 = time.time()
                    t_ffd = (t1 - t0) * 1000
                    total_time_FFD += t_ffd

                    # MFFD
                    t0 = time.time()
                    mffd = solve_MFFD(items, C)
                    t1 = time.time()
                    t_mffd = (t1 - t0) * 1000
                    total_time_MFFD += t_mffd

                    # Column Generation
                    t0 = time.time()
                    cg = solve_column_generation(items, C)
                    t1 = time.time()
                    t_cg = (t1 - t0) * 1000
                    total_time_CG += t_cg

                    # Corectness
                    ffd_ratio = ffd / bf
                    mffd_ratio = mffd / bf
                    cg_ratio = cg / bf

                    total_ffd_ratio += ffd_ratio
                    total_mffd_ratio += mffd_ratio
                    total_cg_ratio += cg_ratio

                    num_tests += 1

                    print(
                        f"{n:<8}"
                        f"{C:<8}"
                        f"{get_distribution_string(dist):<16}"
                        f"{bf:<8.0f}{t_bf:<16.0f}"
                        f"{ffd:<8.0f}{t_ffd:<16.0f}"
                        f"{mffd:<8.0f}{t_mffd:<16.0f}"
                        f"{cg:<8.0f}{t_cg:<16.0f}"
                        f"{ffd_ratio:<16.2f}{mffd_ratio:<16.2f}{cg_ratio:<16.2f}"
                    )

    print("\n===== Summary =====")
    print(f"Total tests run: {num_tests}")
    print(f"Total time BF: {total_time_BF:.0f} ms")
    print(f"Total time FFD: {total_time_FFD:.0f} ms")
    print(f"Total time MFFD: {total_time_MFFD:.0f} ms")
    print(f"Total time CG: {total_time_CG:.0f} ms")

    print(f"Average FFD correctness: {100 * total_ffd_ratio / num_tests:.2f} %")
    print(f"Average MFFD correctness: {100 * total_mffd_ratio / num_tests:.2f} %")
    print(f"Average CG correctness: {100 * total_cg_ratio / num_tests:.2f} %")


if __name__ == "__main__":
    run_small_tests()
