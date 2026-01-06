def bin_packing_FFD(items, n, C):
    items.sort(reverse=True, key=lambda x: x[0])
    bins = []
    empty_space = []

    for i in range(n):
        value, index = items[i]
        placed = False

        for j in range(len(bins)):
            if empty_space[j] >= value:
                empty_space[j] -= value
                bins[j].append(index)
                placed = True
                break

        if not placed:
            bins.append([index])
            empty_space.append(C - value)

    return bins


def main():
    N, C = map(int, input().split())
    items = []

    for i in range(N):
        v = int(input())
        items.append((v, i + 1))

    bins = bin_packing_FFD(items, N, C)

    print(len(bins))
    for bin_items in bins:
        bin_items.sort()
        print(*bin_items)
