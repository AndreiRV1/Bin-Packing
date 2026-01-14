import random
import time
import numpy as np
from collections import defaultdict

def ffd_initial_patterns(weights, capacity):
    """Fast FFD for initial patterns."""
    sorted_items = sorted(enumerate(weights, 1), key=lambda x: x[1], reverse=True)
    bins = []
    bin_caps = []
    
    for idx, weight in sorted_items:
        for i, remaining in enumerate(bin_caps):
            if remaining >= weight:
                bins[i].append(idx)
                bin_caps[i] -= weight
                break
        else:
            bins.append([idx])
            bin_caps.append(capacity - weight)
    
    return bins

def solve_pricing_dp(weights, duals, capacity):
    """
    Optimized DP knapsack for pricing problem.
    Returns pattern and reduced cost.
    """
    n = len(weights)
    
    # Use numpy for faster operations
    dp = np.zeros(capacity + 1, dtype=np.float64)
    parent = np.full((capacity + 1, 2), -1, dtype=np.int32)
    
    for i in range(n):
        w = weights[i]
        v = duals[i]
        
        # Process in reverse to avoid using same item twice
        for c in range(capacity, w - 1, -1):
            new_val = dp[c - w] + v
            if new_val > dp[c] + 1e-10:
                dp[c] = new_val
                parent[c] = [i, c - w]
    
    # Backtrack to find pattern
    pattern = []
    c = capacity
    while c >= 0 and parent[c, 0] >= 0:
        item_idx = parent[c, 0]
        pattern.append(item_idx + 1)  # 1-indexed
        c = parent[c, 1]
    
    pattern.sort()
    reduced_cost = 1.0 - dp[capacity]
    
    return pattern, reduced_cost

def solve_rmp_lp(n_items, patterns, item_coverage):
    """
    Fast RMP solver using direct numpy operations.
    Builds and solves the LP without Pyomo overhead.
    """
    try:
        from scipy.optimize import linprog
        
        n_patterns = len(patterns)
        
        # Objective: minimize sum of pattern usage
        c = np.ones(n_patterns)
        
        # Coverage constraints: each item must be covered at least once
        # A_ub @ x >= b_ub  =>  -A_ub @ x <= -b_ub
        A_ub = np.zeros((n_items, n_patterns))
        for j, pattern in enumerate(patterns):
            for item in pattern:
                A_ub[item - 1, j] = -1
        
        b_ub = -np.ones(n_items)
        
        # Solve LP
        bounds = [(0, None) for _ in range(n_patterns)]
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if not result.success:
            return None, None
        
        # Extract duals (shadow prices)
        duals = -result.ineqlin.marginals
        
        return result.fun, duals
        
    except ImportError:
        # Fallback to simple greedy if scipy not available
        return None, None

def solve_rmp_ip(n_items, patterns):
    """
    Solve RMP as integer program using branch and bound with strong branching.
    """
    try:
        from scipy.optimize import milp, LinearConstraint, Bounds
        
        n_patterns = len(patterns)
        
        # Objective
        c = np.ones(n_patterns)
        
        # Coverage constraints
        A = np.zeros((n_items, n_patterns))
        for j, pattern in enumerate(patterns):
            for item in pattern:
                A[item - 1, j] = 1
        
        constraints = LinearConstraint(A, lb=1, ub=np.inf)
        
        # Integer bounds
        integrality = np.ones(n_patterns, dtype=int)
        bounds = Bounds(lb=0, ub=np.inf)
        
        result = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
        
        if result.success:
            # Extract selected patterns
            selected = []
            for j, val in enumerate(result.x):
                if val > 0.5:
                    selected.append(patterns[j])
            return len(selected), selected
        
        return None, None
        
    except ImportError:
        # Fallback: greedy set cover
        return greedy_set_cover(n_items, patterns)

def greedy_set_cover(n_items, patterns):
    """Greedy set cover for IP fallback."""
    uncovered = set(range(1, n_items + 1))
    selected = []
    
    while uncovered:
        # Find pattern covering most uncovered items
        best_pattern = None
        best_coverage = 0
        
        for pattern in patterns:
            coverage = len([i for i in pattern if i in uncovered])
            if coverage > best_coverage:
                best_coverage = coverage
                best_pattern = pattern
        
        if best_pattern is None:
            break
            
        selected.append(best_pattern)
        for item in best_pattern:
            uncovered.discard(item)
    
    return len(selected), selected

def column_generation_bin_packing(weights, capacity, num_iters, time_limit=30.0):
    """
    State-of-the-art Column Generation for Bin Packing.
    
    Returns: (all_patterns, selected_patterns, lp_bound, ip_solution)
    """
    n_items = len(weights)
    start_time = time.perf_counter()
    
    # Phase 1: Initialize with FFD patterns
    ffd_bins = ffd_initial_patterns(weights, capacity)
    patterns = [sorted(b) for b in ffd_bins]
    
    # Track seen patterns for deduplication
    seen = {tuple(p) for p in patterns}
    
    # Build item coverage map
    item_coverage = defaultdict(list)
    for j, pattern in enumerate(patterns):
        for item in pattern:
            item_coverage[item].append(j)
    
    best_lp_obj = float('inf')
    stall_count = 0
    max_stalls = 20
    
    # Phase 2: Column Generation Loop
    for iteration in range(num_iters):
        if time.perf_counter() - start_time > time_limit:
            break
        
        # Solve RMP LP relaxation
        lp_obj, duals = solve_rmp_lp(n_items, patterns, item_coverage)
        
        if lp_obj is None:
            break
        
        # Check for improvement
        if lp_obj < best_lp_obj - 1e-6:
            best_lp_obj = lp_obj
            stall_count = 0
        else:
            stall_count += 1
        
        if stall_count >= max_stalls:
            break
        
        # Solve pricing problem
        new_pattern, reduced_cost = solve_pricing_dp(weights, duals, capacity)
        
        # Check termination
        if reduced_cost >= -1e-8:
            break
        
        # Add new pattern if unique
        pattern_tuple = tuple(new_pattern)
        if pattern_tuple not in seen and new_pattern:
            patterns.append(new_pattern)
            seen.add(pattern_tuple)
            
            # Update coverage map
            for item in new_pattern:
                item_coverage[item].append(len(patterns) - 1)
    
    # Phase 3: Solve IP
    ip_obj, selected_patterns = solve_rmp_ip(n_items, patterns)
    
    if ip_obj is None:
        ip_obj = len(ffd_bins)
        selected_patterns = ffd_bins
    
    return patterns, selected_patterns, best_lp_obj, ip_obj

if __name__ == "__main__":
    # Test with 2500 elements
    items_count = 2500
    bin_capacity = 100
    weights = [random.randint(10, 45) for _ in range(items_count)]
    
    print(f"--- Running optimized Column Generation for {items_count} items ---")
    start = time.perf_counter()
    all_pats, chosen_pats, lp_val, int_val = column_generation_bin_packing(weights, bin_capacity, 200)
    end = time.perf_counter()
    
    # Calculate FFD separately for comparison
    ffd_result = len(ffd_initial_patterns(weights, bin_capacity))
    
    print(f"FFD Baseline: {ffd_result} bins")
    print(f"CG LP Bound:  {lp_val:.4f}")
    print(f"CG Final Bins: {int_val} bins")
    print(f"Improvement:   {ffd_result - int_val} bins")
    print(f"Runtime:       {end - start:.4f}s")