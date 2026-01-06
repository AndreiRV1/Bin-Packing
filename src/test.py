import math
import random
import time
from brute_force import bin_packing_BF
from first_fit_descending import bin_packing_FFD


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
    for num_bins in range(1, n + 1):
        bins = [0] * num_bins
        assignment = [-1] * n
        if bin_packing_BF(items, bins, num_bins, C, 0, assignment):
            return num_bins
    return n


def solve_FFD(items, n, C):
    bins = bin_packing_FFD([(v, i + 1) for i, v in enumerate(items)], n, C)
    return len(bins)


def get_distribution_string(dist):
    if dist == 0:
        return "Uniform"
    elif dist == 1:
        return "Small"
    elif dist == 2:
        return "Large"
    elif dist == 3:
        return "Half"


def run_small_tests():
    # Test configurations
    different_n = [4, 8, 12]
    different_C = [20, 50, 100, 1000, 10000]
    distributions = [0, 1, 2, 3]
    num_instances = 1

    print("n\tC\tDistribution\tBF\tTime_BF(ms)\tFFD\tTime_FFD(ms)\tFFD_Optimality")

    total_time_start = time.time()
    total_ffd_optimality = 0
    for n in different_n:
        for C in different_C:
            for distribution in distributions:
                for test_id in range(num_instances):
                    random.seed(1 + test_id)
                    items = generate_test(n, C, distribution)

                    # Brute Force
                    start_bf = time.time()
                    bf_solution = solve_brute_force(items, C)
                    end_bf = time.time()
                    time_bf = (end_bf - start_bf) * 1000

                    # First Fit Descending
                    start_ffd = time.time()
                    ffd_solution = solve_FFD(items, n, C)
                    end_ffd = time.time()
                    time_ffd = (end_ffd - start_ffd) * 1000

                    ffd_optimality = ffd_solution / bf_solution
                    total_ffd_optimality += ffd_optimality
                    print(
                        f"{n:<8}"
                        f"{C:<8}"
                        f"{get_distribution_string(distribution):<16}"
                        f"{bf_solution:<8}"
                        f"{time_bf:<16.0f}"
                        f"{ffd_solution:<8}"
                        f"{time_ffd:<16.0f}"
                        f"{ffd_optimality:<5.2f}"
                    )

    total_time = time.time() - total_time_start
    total_ffd_optimality /= (
        len(different_n) * len(different_C) * len(distributions) * num_instances
    )
    print(total_time)
    print(total_ffd_optimality)


def run_large_tests():
    # Test configurations
    different_n = [100, 500, 1000]
    different_C = [20, 50, 100, 1000, 10000]
    distributions = [0, 1, 2, 3]
    num_instances = 1

    print("n\tC\tDistribution\tFFD\tTime_FFD(ms)\tTheoretical_min")

    total_time_start = time.time()
    for n in different_n:
        for C in different_C:
            for distribution in distributions:
                for test_id in range(num_instances):
                    random.seed(1 + test_id)
                    items = generate_test(n, C, distribution)

                    # First Fit Descending
                    start_ffd = time.time()
                    ffd_solution = solve_FFD(items, n, C)
                    end_ffd = time.time()
                    time_ffd = (end_ffd - start_ffd) * 1000

                    print(
                        f"{n:<8}"
                        f"{C:<8}"
                        f"{get_distribution_string(distribution):<16}"
                        f"{ffd_solution:<8}"
                        f"{time_ffd:<16.0f}"
                        f"{math.floor(sum(items) / C)}"
                    )

    total_time = time.time() - total_time_start
    print(total_time)


if __name__ == "__main__":
    run_large_tests()
