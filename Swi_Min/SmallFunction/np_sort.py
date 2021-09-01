import numpy as np 

# arr = np.array([[5, 2, 3],
#                 [5, 2, 2],
#                 [5, 2, 1],
#                 [5, 1, 3]])
# print('%=============原始資料(4行3列)=================')
# print(arr)

# arrSortedIndex = np.lexsort((arr[:, 2], arr[:, 1], arr[:, 0]))
# print('%======按照x優先，y次級，z最後規則排序後=======')
# print(arr[arrSortedIndex , :])

# arrSortedIndex = arr[np.lexsort((arr[:, 2], arr[:, 1], arr[:, 0]))]
# print('%======按照x優先，y次級，z最後規則排序後=======')
# print(arrSortedIndex)

sort_id = np.zeros((5, 5), dtype=np.float_)
a = \
[[ 72.0 , 91.20128083 , 0.0 , 0.0 , 0.0 ],
 [ 99.0 , 105.9999999 , 0.0 , 0.0 , 0.0 ],
 [ 50.0 , 105.9999999 , 0.0 , 0.0 , 0.0 ],
 [  2.0 , 95.81260758 , 0.0 , 0.0 , 0.0 ],
 [ 22.0 , 100.3634205 , 0.0 , 0.0 , 0.0 ]]
sort_id = np.array(a)
# print(sort_id)

# arrSort = sort_id[np.lexsort((sort_id[:, 0], sort_id[:, 1]))]
# print('%======按照y優先、x次之 小到大 排序=======')
# print(arrSort)

idlist = sort_id[0:,0:1]
idlist = idlist.astype("int")
print(idlist)
used_id = [72, 99, 50, 22, 2]
if 72 in idlist:
    print("72")


'''
NO SORT :  
[[ 72.         100.17388047   0.           0.           0.        ]
 [ 99.         111.85447684   0.           0.           0.        ]
 [  2.          97.86586284   0.           0.           0.        ]
 [ 22.         100.03979346   0.           0.           0.        ]
 [ 50.         102.90511624   0.           0.           0.        ]]
SORT :  
[[  2.          97.86586284   0.           0.           0.        ]
 [ 22.         100.03979346   0.           0.           0.        ]
 [ 72.         100.17388047   0.           0.           0.        ]
 [ 50.         102.90511624   0.           0.           0.        ]
 [ 99.         111.85447684   0.           0.           0.        ]]
 '''