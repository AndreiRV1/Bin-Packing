def bin_packing_BF(items, bins, num_bins, C, i, assignment):
    remaining_items = sum(items[i:])
    remaining_space = num_bins * C - sum(bins)
    if remaining_items > remaining_space:
        return False

    if i == len(items):
        return True  # toate elementele au fost plasate

    used_empty = False

    for b in range(num_bins):
        if bins[b] == 0:
            if used_empty:
                continue
            used_empty = True

        if bins[b] + items[i] <= C:
            bins[b] += items[i]
            assignment[i] = b
            if bin_packing_BF(items, bins, num_bins, C, i + 1, assignment):
                return True
            bins[b] -= items[i]  # backtrack
            assignment[i] = -1
    return False


def main():
    # citire date
    n = int(input())
    C = int(input())
    items = [int(input()) for _ in range(n)]

    for num_bins in range(1, n + 1):
        bins = [0] * num_bins
        assignment = [-1] * n  # assignment[i] = bin-ul in care se afla items[i]
        if bin_packing_BF(items, bins, num_bins, C, 0, assignment):
            print(num_bins)
            # construim lista de indicii pentru fiecare bin
            bins_items = [[] for _ in range(num_bins)]
            for idx, b in enumerate(assignment):
                bins_items[b].append(idx + 1)  # indicii 1-based
            for b in bins_items:
                print(" ".join(map(str, sorted(b))))
            break


if __name__ == "__main__":
    main()
