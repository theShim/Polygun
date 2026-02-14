

import random

count = 10
a = [random.randint(0, 100) for i in range(count)]
print(a)

for j in range(0, count, 3):
    if rem := (count - j) >= 3:
        print(a[j:j+3])
    else:
        print(a[j:])