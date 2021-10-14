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

# a = set(np.random.randint(10, size=5))
# print(a)
# # b = set(np.random.randint(50, size = 10))
# # print(b)
# # a = [1, 2, 3, 4, 5, 1, 2]
# # a = set(a)
# b = [3, 4, 5]
# b = set(b)
# c = b & (a ^ b)
# print(c)
# print(len(c))

# if len(c) != 0:
#     print("have something")
# else:
#     print("沒咚咚")

# sort_id = [4, 6, 5]
# new_id = [5, 6]
# for i in range(3):
#     if sort_id[i] in new_id:
#         next_id = sort_id[i]
#         break
# print(next_id)
main_marker = 1
sort = np.array([[2. ,  158.59586556],[1. , 165.28353247]])
main_dist = np.where(sort[:,0] == main_marker)
sort[main_dist]
print(str(int(sort[main_dist][0][0])), sort[main_dist][0][1])
