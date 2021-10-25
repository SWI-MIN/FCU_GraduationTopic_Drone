import numpy as np 
import csv

class MarkerDefine():
    def __init__(self):
        with open('MarkerAction/marker_conf.csv', 'rt', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            self.marker_nav = list(reader)

    def changeMarker(self, ID):
        selected = 'Origin'
        for i in self.marker_nav:
            if i[0] == str(ID):
                selected = i[1]
                break

        print(selected + " marker")

        switcher={                              # vx, vy, vz, yaw
                'Origin':                np.array([[0., 0., 0, 0.]]),            
                'Rotate right corner': np.array([[0., 0., 0, 10.]]),          
                'Rotate left corner':  np.array([[0., 0., 0, -10.]]),               
                'Up':                    np.array([[0., 0., 20, 0.]]),           
                'Down':                  np.array([[0., 0., -20, 0.]]),
                'Land':                  np.array([[0., 0., 0, -1.]])   
             }
        return switcher.get(selected, "Invalid marker type")