import random
import time

def first_fit_descending(items, capacity, existing_bins=None):
    """Standard FFD algorithm to pack items into bins."""
    if existing_bins is None:
        bins = []
    else:
        bins = existing_bins
        
    items.sort(reverse=True)
    
    for item in items:
        placed = False
        for i in range(len(bins)):
            if sum(bins[i]) + item <= capacity:
                bins[i].append(item)
                placed = True
                break
        if not placed:
            bins.append([item])
    return bins

def mffd_algorithm(items, capacity):
    A = sorted([w for w in items if capacity/2 < w <= capacity], reverse=True)
    B = sorted([w for w in items if capacity/3 < w <= capacity/2], reverse=True)
    C_group = sorted([w for w in items if 0 < w <= capacity/3], reverse=True)
    
    bins = [[item] for item in A]
    
    remaining_B = B[:]
    remaining_C = C_group[:]
    
    for b_idx in range(len(bins)):
        bin_content = bins[b_idx]
        current_load = sum(bin_content)
        space_left = capacity - current_load
        
        added_from_B = False
        for i, item_b in enumerate(remaining_B):
            if item_b <= space_left:
                bin_content.append(remaining_B.pop(i))
                added_from_B = True
                break
        
        if not added_from_B and len(remaining_C) >= 1:
            smallest_two_sum = sum(remaining_C[-2:]) if len(remaining_C) >= 2 else remaining_C[-1]
            if smallest_two_sum <= space_left:
                pass
            else:
                bin_content.append(remaining_C.pop(-1))
                new_space = capacity - sum(bin_content)
                for i, item_c in enumerate(remaining_C):
                    if item_c <= new_space:
                        bin_content.append(remaining_C.pop(i))
                        break

    all_remaining = sorted(remaining_B + remaining_C, reverse=True)
    
    for b_idx in range(len(bins)):
        i = 0
        while i < len(all_remaining):
            if sum(bins[b_idx]) + all_remaining[i] <= capacity:
                bins[b_idx].append(all_remaining.pop(i))
            else:
                i += 1
    final_bins = first_fit_descending(all_remaining, capacity, existing_bins=bins)
    return final_bins

if __name__ == "__main__":
    items_count = 2500
    bin_capacity = 100
    weights = [random.randint(10, 45) for _ in range(items_count)]
    
    start = time.perf_counter()
    result = mffd_algorithm(weights, bin_capacity)
    end = time.perf_counter()
    
    
    print(f"Total bins used: {len(result)}")
    print(f"Runtime:       {end - start:.4f}s")
    

        