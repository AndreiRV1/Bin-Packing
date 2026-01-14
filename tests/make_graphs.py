import time
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import sys



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.brute_force import bin_packing_BF
from src.first_fit_descending import bin_packing_FFD
from src.modified_ffd import mffd_algorithm
from src.column_generation import column_generation_bin_packing



def generate_test(n, C, dist):
    if dist == 0: return [random.randint(1, C) for _ in range(n)]
    elif dist == 1: return [random.randint(1, C // 4) for _ in range(n)]
    elif dist == 2: return [random.randint(C // 2, C) for _ in range(n)]
    elif dist == 3: return [random.randint(C // 3, 2 * C // 3) for _ in range(n)]
    elif dist == 4:
        num_types = 5
        distinct_types = [random.randint(C//4, C//2) for _ in range(num_types)]
        return [random.choice(distinct_types) for _ in range(n)]

def get_distribution_string(dist):
    return ["Uniform", "Small", "Large", "Half", "Duplicates"][dist]


def solve_FFD(items, C):
    formatted_items = [(v, i + 1) for i, v in enumerate(items)]
    bins = bin_packing_FFD(formatted_items, len(items), C)
    return len(bins)

def solve_MFFD(items, C):
    bins = mffd_algorithm(items, C)
    return len(bins)

def solve_CG(items, C):
    _, _, _, obj = column_generation_bin_packing(items, C, 150)
    return obj


def plot_all_results(scalability_data, unique_type_data):
    print("\n--- Generare Grafice Finalez ---")
    dist_names = ["Uniform", "Small", "Large", "Half", "Duplicates"]
    n_values = sorted(list(set(d['n'] for d in scalability_data)))
    colors = {'ffd': '#3498db', 'mffd': '#e67e22', 'cg': '#2ecc71'}

    # 1. SCALABILITATE TIMP
    plt.figure(figsize=(10, 6))
    for algo in ['ffd', 'mffd', 'cg']:
        times = [np.mean([d[f't_{algo}'] for d in scalability_data if d['n'] == n]) for n in n_values]
        plt.plot(n_values, times, marker='o', label=algo.upper(), linewidth=2)
    plt.yscale('log')
    plt.title('Scalabilitate: Timp de Execuție vs. N', fontsize=14)
    plt.xlabel('Număr de obiecte (n)')
    plt.ylabel('Timp mediu (ms) - Scară Logaritmică')
    plt.grid(True, which="both", ls="-", alpha=0.3); plt.legend()
    plt.savefig('1_scalabilitate_timp.png', dpi=300); plt.close()

    # 2. BINS PER DISTRIBUTIE
    for dist in dist_names:
        plt.figure(figsize=(10, 6))
        x = np.arange(len(n_values))
        width = 0.25
        for i, algo in enumerate(['ffd', 'mffd', 'cg']):
            vals = [np.mean([d[algo] for d in scalability_data if d['dist'] == dist and d['n'] == n]) for n in n_values]
            plt.bar(x + (i-1)*width, vals, width, label=algo.upper(), color=colors[algo])
        plt.title(f'Eficiență Distribuție: {dist}', fontsize=14); plt.xticks(x, n_values)
        plt.ylabel('Număr Bins'); plt.legend(); plt.grid(axis='y', alpha=0.3)
        plt.savefig(f'2_distributie_{dist.lower()}.png', dpi=300); plt.close()

    # 3. IMPACT UNIQUE TYPES (RUNTIME)
    plt.figure(figsize=(10, 6))
    ks = [d['k'] for d in unique_type_data]
    for algo in ['ffd', 'mffd', 'cg']:
        plt.plot(ks, [d[f't_{algo}'] for d in unique_type_data], marker='o', label=algo.upper())
    plt.yscale('log'); plt.title('Impact Diversitate Obiecte (Unique Types)', fontsize=14)
    plt.xlabel('Tipuri unice'); plt.ylabel('Timp (ms)'); plt.legend(); plt.grid(True, alpha=0.3)
    plt.savefig('3_runtime_vs_unique_types.png', dpi=300); plt.close()

    # 4. ANALIZA IROSIRE (WASTE %)
    plt.figure(figsize=(10, 6))
    for algo in ['ffd', 'mffd', 'cg']:
        waste = []
        for n in n_values:
            subset = [d for d in scalability_data if d['n'] == n]
            avg_waste = np.mean([1 - (d['sum_items'] / (d[algo] * d['C'])) for d in subset])
            waste.append(avg_waste * 100)
        plt.plot(n_values, waste, marker='o', label=algo.upper(), linewidth=2)
    plt.title('Eficiență Economică: Spațiu Neutilizat (%)', fontsize=14)
    plt.xlabel('Număr de obiecte (n)'); plt.ylabel('Waste (%)'); plt.legend(); plt.grid(True, alpha=0.3)
    plt.savefig('4_waste_analysis.png', dpi=300); plt.close()

    # 5. OPTIMALITY GAP (%)
    plt.figure(figsize=(10, 6))
    for algo in ['ffd', 'mffd', 'cg']:
        gap = []
        for n in n_values:
            subset = [d for d in scalability_data if d['n'] == n]
            avg_gap = np.mean([(d[algo] - d['lower_bound']) / d['lower_bound'] for d in subset])
            gap.append(avg_gap * 100)
        plt.plot(n_values, gap, marker='s', label=algo.upper(), linewidth=2)
    plt.title('Optimality Gap: Distanța față de Bound-ul Inferior (%)', fontsize=14)
    plt.xlabel('Număr de obiecte (n)'); plt.ylabel('Gap (%)'); plt.legend(); plt.grid(True, alpha=0.3)
    plt.savefig('5_optimality_gap.png', dpi=300); plt.close()


def run_benchmarks():
    different_n = [50, 100, 250, 500]
    different_C = [100, 500]
    distributions = [0, 1, 2, 3, 4]
    results_scalability = []

    print(f"{'n':<5} {'C':<5} {'Dist':<10} | {'FFD':<5} {'T_FFD':<8} | {'CG':<5} {'T_CG':<8}")
    print("-" * 65)

    for n in different_n:
        for C in different_C:
            for dist in distributions:
                random.seed(42)
                items = generate_test(n, C, dist)
                sum_items = sum(items)
                lower_bound = math.ceil(sum_items / C)

                t0 = time.time(); ffd = solve_FFD(items, C); t_ffd = (time.time() - t0) * 1000
                t0 = time.time(); mffd = solve_MFFD(items, C); t_mffd = (time.time() - t0) * 1000
                t0 = time.time(); cg = solve_CG(items, C); t_cg = (time.time() - t0) * 1000

                dist_str = get_distribution_string(dist)
                results_scalability.append({
                    'n': n, 'C': C, 'dist': dist_str, 'sum_items': sum_items, 'lower_bound': lower_bound,
                    'ffd': ffd, 't_ffd': t_ffd, 'mffd': mffd, 't_mffd': t_mffd, 'cg': cg, 't_cg': t_cg
                })
                print(f"{n:<5} {C:<5} {dist_str:<10} | {ffd:<5} {t_ffd:<8.2f} | {cg:<5} {t_cg:<8.2f}")

    results_unique = []
    for k in [2, 10, 20, 50, 100]:
        unique_sizes = [random.randint(10, 50) for _ in range(k)]
        items = [random.choice(unique_sizes) for _ in range(300)]
        t0 = time.time(); solve_FFD(items, 100); t_ffd = (time.time() - t0) * 1000
        t0 = time.time(); solve_MFFD(items, 100); t_mffd = (time.time() - t0) * 1000
        t0 = time.time(); solve_CG(items, 100); t_cg = (time.time() - t0) * 1000
        results_unique.append({'k': k, 't_ffd': t_ffd, 't_mffd': t_mffd, 't_cg': t_cg})

    plot_all_results(results_scalability, results_unique)

if __name__ == "__main__":
    run_benchmarks()