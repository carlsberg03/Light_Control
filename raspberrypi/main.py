import threading 
import socket
import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import smbus
from flask import Flask, render_template
global set_color
global set_intensity
global set_group
global rainbow_enable
global auto_color
global auto_intensity
global auto_enable
global target_color
global target_intensity
global real_temp
global real_humi
global real_intensity
global enable
global people
global loss
global client_flag

# global variables
set_color = ['0', '0', '0', '0']
set_intensity = ['0', '0', '0', '0']
set_group = ['1', '2', '3', '4']
rainbow_enable = False
auto_color = False
auto_intensity = False
auto_enable = False
target_color = 5
target_intensity = 5

real_temp = 0
real_humi = 0
real_intensity = 0
enable = [1, 1, 1, 1]
people = [0, 0, 0, 0]
loss = 0
client_flag=0  

#init
app = Flask(__name__)
dhtDevice = adafruit_dht.DHT11(board.D16)
__DEV_ADDR=0x23
__CMD_PWR_OFF=0x00
__CMD_PWR_ON=0x01
__CMD_RESET=0x07
__CMD_CHRES=0x10
__CMD_CHRES2=0x11
__CMD_CLHRES=0x13
__CMD_THRES=0x20
__CMD_THRES2=0x21
__CMD_TLRES=0x23
__CMD_SEN100H=0x42
__CMD_SEN100L=0x65
__CMD_SEN50H=0x44
__CMD_SEN50L=0x6A
__CMD_SEN200H=0x41
__CMD_SEN200L=0x73

bus = smbus.SMBus(1)
bus.write_byte(__DEV_ADDR,__CMD_PWR_ON)
bus.write_byte(__DEV_ADDR,__CMD_RESET)
bus.write_byte(__DEV_ADDR,__CMD_SEN100H)
bus.write_byte(__DEV_ADDR,__CMD_SEN100L)
bus.write_byte(__DEV_ADDR,__CMD_PWR_OFF)

'''
获取数据
'''
def initi():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5,GPIO.IN)
        GPIO.setup(6,GPIO.IN)
        GPIO.setup(13,GPIO.IN)
        GPIO.setup(26,GPIO.IN)
        GPIO.setup(7,GPIO.OUT)

def dec1():
        global real_intensity
        bus.write_byte(__DEV_ADDR,__CMD_PWR_ON)
        bus.write_byte(__DEV_ADDR,__CMD_THRES2)
        time.sleep(0.2)
        res=bus.read_word_data(__DEV_ADDR,0)
        res=((res>>8)&0xff)|(res<<8)&0xff00
        percent = int((100.0/65535.0)*res)
        real_intensity = res
        print(str(real_intensity)+'lux')

def dec3():
        a=[]
        time.sleep(1)
        if GPIO.input(5)== True :
                a.append(1)
        else :
                a.append(0)
        if GPIO.input(6)== True :
                a.append(1)
        else :
                a.append(0)
        if GPIO.input(13)== True :
                a.append(1)
        else :
                a.append(0)
        if GPIO.input(26)== True :
                a.append(1)
        else :
                a.append(0)
        return a

def get_data():
    global real_temp
    global real_humi
    global real_intensity
    global people
    while True:
        try:
                temperature_c = dhtDevice.temperature
                temperature_f = temperature_c *(9/5)+32
                humidity = dhtDevice.humidity
                real_temp = temperature_c
                real_humi = humidity
                print("temperature: {:.1f} C humidity :{}%".format(temperature_c,humidity))

        except RuntimeError as error:
                print(error.args[0])
                time.sleep(2)
                continue
        except Exception as error:
                dhtDevice.exit()
                raise error
        dec1()
        initi()
        people=dec3()
        print(people)
        time.sleep(0.5)


'''
设定LED参数
'''

def setcolor():
    global set_color
    global rainbow_enable
    global auto_color
    global target_color
    global real_temp
    while True:
        if rainbow_enable:
            for i in range(4):
                set_color[i] = str(int(set_color[i])+1) if int(set_color[i])<9 else str(0)
                time.sleep(1)
        elif auto_color:
            for i in range(4):
                set_color[i] = str(9-(int(real_temp[i]/4) if int(real_temp[i]/4)<=9 else 0))
        else:
            for i in range(4):
                set_color[i] = str(target_color)
        time.sleep(1)

def setlight():
    global set_intensity
    global auto_intensity
    global target_intensity
    global real_intensity
    global enable
    global people
    global auto_enable
    global loss
    while True:
        if auto_enable:
            if(auto_intensity):
                for i in range(4):
                    if people[i]==1:
                        if((target_intensity-real_intensity)<=-50):loss = -1
                        if((target_intensity-real_intensity)>=50):loss = 1
                        if(-50<=(target_intensity-real_intensity)<=50):loss = 0
                        
                        set_intensity[i] = str(int(9) if int(set_intensity[i]) + loss>=9 else 0 if int(set_intensity[i]) + loss<0 else int(set_intensity[i]) + loss)
                    else:
                        set_intensity[i] = str(0)
            else:
                for i in range(4):
                    if people[i]==1:
                        set_intensity[i] = str(int(target_intensity/20))
                    else:
                        set_intensity[i] = str(0)
        else:
            if(auto_intensity):
                for i in range(4):
                    if enable[i]==1:
                        if((target_intensity-real_intensity)<=-50):loss = -1
                        if((target_intensity-real_intensity)>=50):loss = 1
                        if(-50<=(target_intensity-real_intensity)<=50):loss = 0
                        
                        set_intensity[i] = str(int(9) if int(set_intensity[i]) + loss>=9 else 0 if int(set_intensity[i]) + loss<0 else int(set_intensity[i]) + loss)
                    else:
                        set_intensity[i] = str(0)
            else:
                for i in range(4):
                    if enable[i]==1:
                        set_intensity[i] = str(int(target_intensity))
                    else:
                        set_intensity[i] = str(0)
        time.sleep(1)


'''
TCP发送数据
'''

def send(socket_tcp_server):   
    global set_color
    global set_intensity 
    global set_group 
    global client_flag  #声明该变量可以在该方法使用
    new_client_socket, client_addr = socket_tcp_server.accept()  #当服务器得到客户端请求连接时，client_flag=1
    client_flag=1
    print("Connect Success",client_addr)
    while True:  
        # 发送数据
        for i in range(4):
            data=set_group[i]+' '+set_color[i]+' '+set_intensity[i]+'\n'
            new_client_socket.send(data.encode('utf-8'))
            time.sleep(0.1)
        time.sleep(1)

def TCPserver():
    global client_flag
    socket_tcp_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    socket_addr=("0.0.0.0",8888)
    socket_tcp_server.bind(socket_addr) #绑定端口
    socket_tcp_server.listen(128) 
    print("waiting for connection")
    client1_threading = threading.Thread(target=send, args=(socket_tcp_server,))
    client1_threading.start()
    while True:
        if  client_flag:   #当client_flag为1时，即服务器得到客户端请求连接时，开始一个新的线程
            client1_threading = threading.Thread(target=send,args=(socket_tcp_server,)) #新建一个线程 
            client1_threading.start()  #开启这个线程
            client_flag = 0    #标志为，目的使线程不会一直增多，只有当服务器得到客户端请求连接时，才开始一个新的线程


'''
WebPage
'''

@app.route('/')
def index():
    global target_intensity
    global rainbow_enable
    global auto_color
    global auto_intensity
    global auto_enable
    global target_color
    global real_temp
    global real_humi
    return render_template('index.html',
                           target_intensity=target_intensity,
                           rainbow_enable=rainbow_enable,
                           auto_color=auto_color,
                           auto_intensity=auto_intensity,
                           auto_enable=auto_enable,
                           target_color=target_color,
                           real_temp=real_temp,
                           real_humi=real_humi,
                           enable1=enable[0],
                           enable2=enable[1],
                           enable3=enable[2],
                           enable4=enable[3])


@app.route('/toggle_rainbow_enable')
def toggle_rainbow_enable():
    global rainbow_enable
    rainbow_enable = False if rainbow_enable else True
    return 'OK'


@app.route('/toggle_target_intensity/<int:target>')
def toggle_target_intensity(target):
    global target_intensity
    target_intensity = target
    print(enable)
    return 'OK'


@app.route('/toggle_auto_color')
def toggle_auto_color():
    global auto_color
    auto_color = False if auto_color else True
    return 'OK'


@app.route('/toggle_enable1')
def toggle_enable1():
    global enable
    enable[0] = 1 if enable[0] == 0 else 0
    return 'OK'

@app.route('/toggle_enable2')
def toggle_enable2():
    global enable
    enable[1] = 1 if enable[1] == 0 else 0
    return 'OK'

@app.route('/toggle_enable3')
def toggle_enable3():
    global enable
    enable[2] = 1 if enable[2] == 0 else 0
    return 'OK'

@app.route('/toggle_enable4')
def toggle_enable4():
    global enable
    enable[3] = 1 if enable[3] == 0 else 0
    return 'OK'


@app.route('/toggle_auto_intensity')
def toggle_auto_intensity():
    global auto_intensity
    global target_intensity
    auto_intensity = False if auto_intensity else True
    if auto_intensity:
        target_intensity=100
    else:
        target_intensity=5
    return 'OK'


@app.route('/toggle_auto_enable')
def toggle_auto_enable():
    global auto_enable
    auto_enable = False if auto_enable else True
    return 'OK'


@app.route('/toggle_target_color/<int:target>')
def toggle_target_color(target):
    global target_color
    target_color = target
    print(enable)
    return 'OK'

def webrun():
     app.run(host='0.0.0.0')

def run():
    TCPserver_threading = threading.Thread(target=TCPserver)
    setcolor_threading = threading.Thread(target=setcolor)
    setlight_threading = threading.Thread(target=setlight)
    get_data_threading = threading.Thread(target=get_data)
    webrun_threading = threading.Thread(target=webrun)
    setcolor_threading.start()
    setlight_threading.start()
    get_data_threading.start()
    TCPserver_threading.start()
    webrun_threading.start()


if __name__ =='__main__':
        run()

 
