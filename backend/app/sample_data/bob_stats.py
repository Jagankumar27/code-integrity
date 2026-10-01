# Statistics helper
def mean(values):
    s = 0
    for v in values:
        s = s + v
    return s / len(values)

def var(values):
    mu = mean(values)
    result = 0
    for v in values:
        result = result + (v - mu) * (v - mu)
    return result / len(values)

def maximum(values):
    top = values[0]
    for v in values:
        if v > top:
            top = v
    return top

numbers = [4, 8, 15, 16, 23, 42]
print("Mean:", mean(numbers))
print("Var:", var(numbers))
print("Max:", maximum(numbers))
