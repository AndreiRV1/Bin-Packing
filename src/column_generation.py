import random
import time
import  pyomo.environ as pyo

# Restricted Master Problem (RMP) using Pyomo
def bin_packing_rmp(iter_num, weights, patterns, lp_relax=False):

    #Initiate model
    model = pyo.ConcreteModel(name=f"BinPacking_RMP_{iter_num}")
    
    # Create indices
    n_items = len(weights)
    items = range(1, n_items + 1)
    patterns_idx = list(patterns.keys())

    # Index sets in model
    model.Items = pyo.RangeSet(1, n_items)
    model.Patterns = pyo.RangeSet(1, len(patterns_idx)) 

    # Decision variables: z_j
    if lp_relax:
        # For LP relaxation
        model.z = pyo.Var(model.Patterns, domain=pyo.NonNegativeReals)
    else:
        # For MILP 
        model.z = pyo.Var(model.Patterns, domain=pyo.Binary)

    # Objective: minimize number of bins
    model.obj = pyo.Objective(rule=sum(model.z[j] for j in model.Patterns), sense=pyo.minimize)

    # Coverage constraints: each item exactly once
    def cover_rule(m, i):
        # patterns that contain item i
        js = [j for j in patterns_idx if i in patterns[j]]
        return sum(m.z[j] for j in js) == 1
    model.cover = pyo.Constraint(model.Items, rule=cover_rule)

    if lp_relax:
        # Importing duals from solver
        model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

    #Specify the solver to use and solve the model
    solver = pyo.SolverFactory("cbc")
    solver.solve(model)
    
    # Get objective value
    obj = pyo.value(model.obj)

    # Extract selected patterns (required for integer solve)
    selected_patterns = []
    for j in model.Patterns:
        zj = pyo.value(model.z[j])
        if zj is not None and zj >= 0.1:
            selected_patterns.append(patterns[j])

    # Duals only meaningful for LP relaxation
    if lp_relax:
        duals = [model.dual[model.cover[i]] for i in model.Items]
    else:
        duals = [0.0 for _ in model.Items]

    return obj, duals, selected_patterns

#Knapsack subproblem via Dynamic Programming
def knapsack_dp(weights, values, capacity):
    N = len(weights)
    # dp[i][c] = best value using items 1..i with capacity c
    dp = [[0] * (capacity + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        w_i = weights[i - 1]
        v_i = values[i - 1]
        prev = dp[i - 1]
        cur = dp[i]
        for c in range(1, capacity + 1):
            #Can insert item i only when its weight is less than current capacity
            if w_i <= c:
                without_i = prev[c]
                with_i = v_i + prev[c - w_i]
                #compare the cost of adding additional item vs not adding item
                cur[c] = with_i if with_i > without_i else without_i
            else:
                cur[c] = prev[c]

    # Traceback to retrieve chosen items
    selected_pattern = []
    c = capacity
    for i in range(N, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            selected_pattern.append(i)  # items numbered 1..N
            c -= weights[i - 1]
    selected_pattern.reverse()

    return selected_pattern, dp[-1][-1]

# Column Generation Loop
def column_generation_bin_packing(weights, capacity, num_iters):

    # Initial patterns: each item alone in its own bin
    patterns = {j: [j] for j in range(1, len(weights) + 1)}
    
    final_lp_obj = None

    for n in range(num_iters):

        #print(f"Num available patterns at iteration {n}: {len(patterns)}")

        # 1) Solve RMP in LP relaxation
        obj, duals, _ = bin_packing_rmp(
            iter_num=n,
            weights=weights,
            patterns=patterns,
            lp_relax=True
        )

        # 2) Solve knapsack subproblem to find new pattern
        selected_pattern, max_value = knapsack_dp(
            weights=weights,
            values=duals,
            capacity=capacity
        )

        reduced_cost = 1 - max_value

        # 3) Stopping condition: no pattern with negative reduced cost
        if reduced_cost >= -1e-8:
            break

        # 4) Add new pattern if it's not already in the pool
        if selected_pattern not in patterns.values():
            new_idx = len(patterns) + 1
            patterns[new_idx] = selected_pattern
        
        # Save objective of LP
        final_lp_obj = obj

    #Finally, solve the integer version using all generated patterns
    final_obj, _, selected_patterns = bin_packing_rmp(
        iter_num=len(weights),
        weights=weights,
        patterns=patterns,
        lp_relax=False
    )

    return patterns,selected_patterns, final_lp_obj,final_obj

if __name__ == "__main__":
    # Example: random items (you can replace with larger instances)
    items = 20
    capacity = 30
    print(f"\n===== Running instance with {items} items, {capacity} capacity =====")
    weights = [random.randint(2, 10) for _ in range(items)]
    print("Weights:", weights)
    t1 = time.perf_counter()
    num_gen_patterns, selected_patterns, lp_obj, obj = column_generation_bin_packing(
    weights, capacity, num_iters=50)
    t2 = time.perf_counter()
    print(f"\nFinal number of bins: {obj}, , lp objective: {lp_obj}")
    print(f"Total generated Patterns: {num_gen_patterns}" )
    print(f"Selected patterns (items per bin): {selected_patterns}")
    print("Runtime:", t2 - t1)