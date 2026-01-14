import math
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
# 4 - duplicates
def generate_test(n, C, dist):
    if dist == 0:
        return [random.randint(1, C) for _ in range(n)]
    elif dist == 1:
        return [random.randint(1, C // 4) for _ in range(n)]
    elif dist == 2:
        return [random.randint(C // 2, C) for _ in range(n)]
    elif dist == 3:
        return [random.randint(C // 3, 2 * C // 3) for _ in range(n)]
    elif dist == 4:
        num_types = random.randint(5,10)
        distinct_types = [random.randint(C//4, C//2) for _ in range(num_types)]
        return [random.choice(distinct_types) for _ in range(n)]


def solve_FFD(items, C):
    bins = bin_packing_FFD([(v, i + 1) for i, v in enumerate(items)], len(items), C)
    return len(bins)


def solve_MFFD(items, C):
    bins = mffd_algorithm(items, C)
    return len(bins)


def solve_column_generation(items, C):
    _, _, _, obj = column_generation_bin_packing(items, C, 150)
    return obj


def get_distribution_string(dist):
    return ["Uniform", "Small", "Large", "Half", "Duplicates"][dist]


def run_large_tests():
    # Test configurations
    different_n = [100, 250]
    different_C = [20, 50, 100, 1000, 10000]
    distributions = [0, 1, 2, 3, 4]
    num_instances = 1

    print(
        "n\tC\tDistribution\t" "FFD\tT_FFD(ms)\t" "MFFD\tT_MFFD(ms)\t" "CG\tT_CG(ms)\t"
    )

    total_time_FFD = 0.0
    total_time_MFFD = 0.0
    total_time_CG = 0.0

    best_FFD = 0
    best_MFFD = 0
    best_CG = 0

    num_tests = 0

    for n in different_n:
        for C in different_C:
            for dist in distributions:
                for test_id in range(num_instances):
                    random.seed(23 + test_id)
                    items = generate_test(n, C, dist)

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

                    if cg <= ffd and cg <= mffd:
                        best_CG += 1
                    elif ffd <= mffd:
                        best_FFD += 1
                    else:
                        best_MFFD += 1

                    num_tests += 1

                    print(
                        f"{n:<8}"
                        f"{C:<8}"
                        f"{get_distribution_string(dist):<16}"
                        f"{ffd:<8.0f}{t_ffd:<16.0f}"
                        f"{mffd:<8.0f}{t_mffd:<16.0f}"
                        f"{cg:<8.0f}{t_cg:<16.0f}"
                    )

    print("\n===== Summary =====")
    print(f"Total tests run: {num_tests}")
    print(f"Total time FFD: {total_time_FFD:.0f} ms")
    print(f"Total time MFFD: {total_time_MFFD:.0f} ms")
    print(f"Total time CG: {total_time_CG:.0f} ms")
    print(f"Best FFD: {best_FFD:.0f}")
    print(f"Best MFFD: {best_MFFD:.0f}")
    print(f"Best CG: {best_CG:.0f}")


if __name__ == "__main__":
    run_large_tests()
