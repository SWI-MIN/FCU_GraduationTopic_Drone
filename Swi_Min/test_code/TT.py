import math 

# x = 50
# y = 50

# opposite_angle = round(math.degrees(math.asin(x/(x**2+y**2)**0.5)),2)

# z = x/(x**2+y**2)**0.5
# print(z)
# a = math.asin(z)
# print(a)
# print(round(math.degrees(a),2))


import numpy as np

a = set(np.random.randint(10, size=5))
print(a)
# b = set(np.random.randint(50, size = 10))
# print(b)
# a = [1, 2, 3, 4, 5, 1, 2]
# a = set(a)
b = [5]
b = set(b)
c = b & (a ^ b)
print(c)
print(len(c))

if len(c) != 0:
    print("have something")
else:
    print("沒咚咚")
