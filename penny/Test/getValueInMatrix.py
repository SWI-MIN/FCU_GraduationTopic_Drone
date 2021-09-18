import numpy as np 

# sort_id是二維陣列
# 把 main marker 的方位傳給

sort_id = np.zeros((4, 5), dtype=np.float_)

sort_id[0] = [2,1,3,1,0]
sort_id[1] = [3,1,1,0,0]
sort_id[2] = [1,1,0,1,0]
sort_id[3] = [4,0,1,1,0]

main_marker = 1

n = np.where(sort_id[:,0] == main_marker)

print(sort_id)

print(n)
m = [0,0,0,0,0]
m = sort_id[n][0]
print(m)

