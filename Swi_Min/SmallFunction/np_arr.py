import numpy as np

# 簡易測試用的
# a = np.zeros((5, 4), dtype = np.int_)

# b = np.ones((1, 4), dtype = np.int_)
# c = [[1, 2, 3, 4]]
# d = [1, 2, 3, 4]

# print(a)
# print(np.delete(a, 0, axis = 0))
# print(np.append(a, b, axis = 0))
# print(np.append(a, c, axis = 0))
# print(np.insert(a,5,d,0))

class act_record():
    ''' 一組 行(column)*列(row) 的動作紀錄
        replace_act : 只會保留 col * row 大小的紀錄表，col 超過會刪除先進來的動作
                ---------------------    
            --> | 1 | 2 | 3 | 4 | 5 | -->
                ---------------------    
                ---------------------
          6 --> | 1 | 2 | 3 | 4 | 5 | -->
                ---------------------
                ---------------------
            --> | 6 | 1 | 2 | 3 | 4 | --> 5
                ---------------------
        get_value : 從前面向後取得值，取得後會移除該值
    '''
    def __init__(self, col, row) -> None:
        self.col = col
        self.row = row
        self.act_list = np.zeros((0, row), dtype = np.int_)

    def replace_act(self, act): # 更新 act_list
        self.act_list = np.insert(self.act_list, self.act_list.shape[0], act, axis = 0)
        if self.act_list.shape[0] > self.col:
            self.act_list = np.delete(self.act_list, 0, axis = 0)

    def get_value(self):
        value = self.act_list[self.act_list.shape[0]-1]
        self.act_list = np.delete(self.act_list, self.act_list.shape[0]-1, axis = 0)
        return value

# 測試 act_record 用的
# action = act_record(5, 4)

# action.replace_act([1,1,1,1])
# action.replace_act([2,2,2,2])
# action.replace_act([3,3,3,3])
# action.replace_act([4,4,4,4])
# action.replace_act([5,5,5,5])
# action.replace_act([6,6,6,6])

# print(action.act_list)

# value = action.get_value()
# print(value)
# print(action.act_list)


li = np.array([0, 1, 2, 3])
li = np.array([0, 0, 0, 0])

if np.all(li == 0):
    print("li 沒值", li)
else:
    print("li 有值", li)

    