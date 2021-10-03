import numpy as np
import math
import cv2

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

R_flip  = np.zeros((3,3), dtype=np.float32)
R_flip[0,0] =  1.0
R_flip[1,1] = -1.0
R_flip[2,2] = -1.0

# rvec = (-2.68856942, 0.14331998, -1.29753909)
# R_ct    = np.matrix(cv2.Rodrigues(rvec)[0])
R_ct = np.matrix([[ 0.6206654, -0.0196688,  0.7838289],
                  [-0.1518742, -0.9837682,  0.0955738],
                  [ 0.7692261, -0.1783628, -0.6135780 ]])

R_tc    = R_ct.T

# 橫滾標記(X)、俯仰標記(Y)、偏航標記 繞(Z)軸旋轉的角度
# roll_marker1, pitch_marker1, yaw_marker1 = rotationMatrixToEulerAngles(R_tc)
# roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(R_flip*R_tc)
# print(R_flip)
# print(R_tc)
# print(roll_marker1, pitch_marker1, yaw_marker1)
# print(R_flip*R_tc)
# print(roll_marker, pitch_marker, yaw_marker)

roll_marker1, pitch_marker1, yaw_marker1 = rotationMatrixToEulerAngles(R_tc)
roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(R_flip*R_tc)
print(math.degrees(roll_marker1), math.degrees(pitch_marker1), math.degrees(yaw_marker1))
print(math.degrees(roll_marker), math.degrees(pitch_marker), math.degrees(yaw_marker))