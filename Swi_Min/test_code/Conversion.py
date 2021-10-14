import numpy as np
import math
# from scipy.spatial.transform import Rotation

# 檢查矩陣是否是有效的旋轉矩陣
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6

# 計算旋轉矩陣到歐拉角
def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])

# def rotationVectorToEulerAngles(rvec):
#     r = Rotation.from_rotvec(rvec)
#     return r.as_euler('xyz')

# 計算合適的Speed倍率
def speed_test(tvecs_X,tvecs_Y,tvecs_Z,euler_Y):
    speed_adjust = [0, 0, 0, 0]
    speed_adjust[0] = abs(tvecs_X) / 3          # speed_max = 15
    speed_adjust[1] = abs(tvecs_Y) / 3          # speed_max = 25
    speed_adjust[2] = abs(tvecs_Z-100) / 10     # speed_max = 50
    speed_adjust[3] = abs(euler_Y) / 5          # speed_max = 20

    if(speed_adjust[0] >= 3):
        speed_adjust[0] = 3

    if(speed_adjust[1] >= 5):
        speed_adjust[1] = 5

    if(speed_adjust[2] >= 10):
        speed_adjust[2] = 10

    if(speed_adjust[3] >= 4):
        speed_adjust[3] = 4

    for i in range(4):
        if(speed_adjust[i] < 1):
            speed_adjust[i] = 1

    return np.array(speed_adjust)

a = speed_test(108, 51, 205, 27)
print(a)