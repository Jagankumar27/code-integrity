def average(nums):
    return sum(nums) / len(nums)

def largest(nums):
    return max(nums)

def spread(nums):
    lo, hi = min(nums), max(nums)
    return hi - lo

scores = [70, 82, 91, 64, 58]
avg = average(scores)
print("Average:", avg)
if avg > 60:
    print("Class passed")
else:
    print("Class needs review")
print("Best:", largest(scores), "Spread:", spread(scores))
