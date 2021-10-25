import numpy as np

class ActRecord():
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