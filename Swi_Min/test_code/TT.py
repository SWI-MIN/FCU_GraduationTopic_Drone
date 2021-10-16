import numpy as np

# a = [0., 0., 0, 10.]
# a = np.array(a)
# b = np.where(a != 0)[0][0]
# c = b

# print(c)

# print(a[c])


main_marker = 1
sort = np.array([[2. ,  158.59586556],[1. , 165.28353247]])
main_dist = np.where(sort[:,0] == main_marker)
# print(main_dist)
print(sort[main_dist])
print(str(int(sort[main_dist][0][0])), sort[main_dist][0][1])