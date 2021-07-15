import cv2 
import numpy as np 
import glob

#圖片放在此之資料夾


#找棋盤格角點
#設置尋找亞像素角點的參數，採用的停止準則是最大循環次數30和最大誤差容限0.001
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30 , 0.001 ) #閾值
#棋盤格模板規格
w = 9    # 10 - 1
h = 6    # 7 - 1 
#世界坐標系中的棋盤格點,例如(0,0,0), (1,0,0), (2,0,0 ) ....,(8,5,0)，去掉Z坐標，記為二維矩陣
objp = np.zeros((w*h, 3 ), np.float32) 
objp[:,: 2 ] = np .mgrid[ 0 :w, 0 :h].T.reshape( -1 , 2 ) 
objp = objp* 18.1   # 18.1 mm

#儲存棋盤格角點的世界坐標和圖像坐標對
objpoints = [] #在世界坐標系中的三維點
imgpoints = [] #在圖像平面的二維點
#加載pic文件夾下所有的jpg圖像
images = glob.glob( './*.jpg' )   #拍攝的十幾張棋盤圖片所在目錄

i= 0 
for fname in images:

    img = cv2.imread(fname) #獲取畫面中心點#獲取圖像的長寬    
    h1, w1 = img.shape[ 0 ], img.shape[ 1 ]     
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)     
    u, v = img.shape[: 2 ] #找到棋盤格角點    
    ret, corners = cv2.findChessboardCorners(gray, (w,h), None ) #如果找到足夠點對，將其存儲起來

    if ret == True :         
        print( "i:" , i)         
        i = i+ 1 #在原角點的基礎上尋找亞像素角點        
        cv2.cornerSubPix(gray,corners,( 11 , 11 ),( -1 , -1 ),criteria)
    
        #追加進入世界三維點和平面二維點中
        objpoints.append(objp) 
        imgpoints.append(corners) #將角點在圖像上顯示        
        cv2.drawChessboardCorners(img, (w,h), corners, ret)         
        cv2. namedWindow( 'findCorners' , cv2.WINDOW_NORMAL)         
        cv2.resizeWindow( 'findCorners' , 640 , 480 )         
        cv2.imshow( 'findCorners' ,img)         
        cv2.waitKey( 200 ) 
        cv2.destroyAllWindows() #%%標定
        print( '正在計算' ) #標定
        ret, mtx, dist, rvecs, tvecs = \     
        cv2.calibrateCamera(objpoints, imgpoints, gray.shape[:: -1], None , None )


print( "ret:" ,ret ) 
print( "mtx:\n" ,mtx)       #內參數矩陣
print( "dist畸變值:\n" ,dist )    #畸變係數distortion cofficients = (k_1,k_2,p_1, p_2,k_3)
print( "rvecs旋轉（向量）外參:\n" ,rvecs)    #旋轉向量#外參數
print( "tvecs平移（向量）外參:\n" ,tvecs )   #平移向量#外參數
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0 , (u, v)) 
print( 'newcameramtx外參' ,newcameramtx) 

#打開攝像機
camera=cv2.VideoCapture( 0 ) 
while  True : 
    (grabbed,frame)=camera.read()
    h1, w1 = frame.shape[: 2 ] 
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0 , (u, v)) #糾正畸變    
    dst1 = cv2.undistort(frame, mtx, dist, None , newcameramtx) #dst2 = cv2.undistort(frame, mtx, dist, None, newcameramtx)     
    mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist, None ,newcameramtx,(w1,h1), 5 )     
    dst2=cv2 .remap(frame,mapx,mapy,cv2.INTER_LINEAR) #裁剪圖像，輸出糾正畸變以後的圖片    
    x, y, w1, h1 = roi     
    dst1 = dst1[y:y + h1, x:x + w1]

    #cv2.imshow('frame',dst2) #cv2.imshow('dst1',dst1)     
    cv2.imshow( 'dst2' , dst2) 
    if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ):   #按q保存一張圖片        
        cv2.imwrite( "../u4/frame.jpg" , dst1) 
    break
    

    
        

camera.release() 
cv2.destroyAllWindows()