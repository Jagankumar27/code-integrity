def sieve(limit):
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    p = 2
    while p * p <= limit:
        if flags[p]:
            for k in range(p * p, limit + 1, p):
                flags[k] = False
        p += 1
    return [i for i, f in enumerate(flags) if f]

if __name__ == "__main__":
    print(sieve(50))
