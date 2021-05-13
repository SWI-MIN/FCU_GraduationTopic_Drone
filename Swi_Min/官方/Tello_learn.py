import threading   # 多執行緒
import socket
import sys
import time


# 這段應該是要接收本地端的資料用的(電腦阿手機之類的)
host = ''
port = 9000
locaddr = (host,port) 


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# socket.socket([family], [type] , [proto] )
    # family: 串接的類型可分為 IPv4本機、IPv4網路、IPv6網路。
    # type: 串接可分為TCP/UDP。
    # protocol: 串接協定(通常預設為0)。

# family  :  socket.AF_INET	於伺服器與伺服器之間進行串接
# type  :  socket.SOCK_DGRAM 使用UDP()的方式通用的免連線訊息交換通道	



tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)
# socket變數名稱.bind(host, port)   用於伺服器端需監聽的IP位址和Port。
    # host : IP位址
    # prot : port號


# 這裡是用於無人機回傳資料到電腦端
def recv():
    count = 0
    while True: 
        try:
            data, server = sock.recvfrom(1518)
            # data,addr = socket變數名稱.recvfrom(bufsize)
                # 可用於接收資料，並會回傳(data,addr)接收到的資料和IP位址資訊。
                # bufsize : 為宣告接收最多字數值
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


print ('\r\n\r\nTello Python3 Demo.\r\n')
print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')
print ('end -- quit demo.\r\n')


#recvThread create
recvThread = threading.Thread(target=recv)  # target是該run()方法要調用的可調用對象。所以我猜是指上面那個函數
recvThread.start()

while True: 

    try:
        msg = input("");

        if not msg:
            break  

        if 'end' in msg:
            print ('...')
            sock.close()   # 關閉socket連接
            break

        # Send data
        # 這裡應該是將電腦端的資料傳輸到無人機上
        msg = msg.encode(encoding="utf-8") 
        sent = sock.sendto(msg, tello_address)
        # socket變數名稱.sendto(data,(addr, port))
        # 可用於傳送資料過去給串接對象，回傳值為要送出的字數。
            # data : 欲傳送之資料字串
            # addr : 欲傳送之IP位址
            # port : 欲傳送之Port號
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()  
        break




# threading — Thread-based parallelism : 
# https://docs.python.org/3/library/threading.html
# Python_Socket小實作 : 
# https://ithelp.ithome.com.tw/articles/10205819





# 指令
# command 進入SDK命令模式
# takeoff 起飛
# land 降落
# streamon / streamoff  開 / 關 視頻流
# emergency  停止電機轉動
# -------------------------------------------------
# up x      向上飛x
# down x    向下
# left      左
# right     右
# forward   前
# back      後
# x = 20 ~ 500
# 
# cw x       順時針轉
# ccw x      逆時針轉
# x = 1 ~ 360
# 
# 
# 
# 
# 
# 
# 
