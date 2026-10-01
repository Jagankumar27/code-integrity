def average(nums):
    total = 0
    for n in nums:
        total = total + n
    return total / len(nums)

def variance(nums):
    m = average(nums)
    acc = 0
    for n in nums:
        acc = acc + (n - m) * (n - m)
    return acc / len(nums)

def largest(nums):
    best = nums[0]
    for n in nums:
        if n > best:
            best = n
    return best

data = [4, 8, 15, 16, 23, 42]
print("Average:", average(data))
print("Variance:", variance(data))
print("Largest:", largest(data))
