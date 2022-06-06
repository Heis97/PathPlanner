#from socket import *
from concurrent.futures import thread
import socket
import sys
import time
import serial
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton,QSlider, QLineEdit, QOpenGLWidget,QTextEdit,
    QInputDialog, QApplication,QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize,
        Qt, QTime, QTimer)
import OpenGL.GL as gl
HOST = '127.0.0.1'    # The remote host
PORT = 50019              # The same port as used by the server
s = None
ser=None
pi=3.141592653589793

def fil_med(spis,extr):
    spis.sort()
    ret=0
    for i in range(extr,len(spis)-extr):
        ret+=spis[i]
    ret=ret/(len(spis)-2*extr)
    return ret

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.i=0
    def run(self):
        while True:
            QtCore.QThread.msleep(100)
            self.i+=1
            self.mysignal.emit(str(self.i))
        

class ex11(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отправка на KUKA")
        self.comport=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6","COM7","COM8","COM9","COM10","COM11","COM12"]
        self.resize(1400, 800)        
        self.build()
        #self.send_2()
    def build(self):
        self.glWidget = GLWidget()
        mainLayout1 = QGridLayout()
        mainLayout1.addWidget(self.glWidget,0,0,1,1)
        self.setLayout(mainLayout1)

        
        
        self.but1 = QtWidgets.QPushButton('Отправить роботу', self)
        self.but1.setGeometry(QtCore.QRect(30, 20, 120, 40))
        self.but1.clicked.connect(self.open_simple)

        self.but2 = QtWidgets.QPushButton('test', self)
        self.but2.setGeometry(QtCore.QRect(30, 70, 120, 40))
        
        self.mythread = MyThread()
        self.but2.clicked.connect(self.tr_start)
        self.mythread.mysignal.connect(self.tr_change, QtCore.Qt.QueuedConnection)

        self.but3 = QtWidgets.QPushButton('test1', self)
        self.but3.setGeometry(QtCore.QRect(30, 120, 120, 40))
        self.but3.clicked.connect(self.send)
        
        self.but4 = QtWidgets.QPushButton('Подключиться', self)
        self.but4.setGeometry(QtCore.QRect(30, 170, 120, 40))
        self.but4.clicked.connect(self.op1)

        self.but5 = QtWidgets.QPushButton('close', self)
        self.but5.setGeometry(QtCore.QRect(30, 220, 120, 40))
        self.but5.clicked.connect(self.close)

        self.but6 = QtWidgets.QPushButton('sensor', self)
        self.but6.setGeometry(QtCore.QRect(30, 270, 120, 40))
        self.but6.clicked.connect(self.datch)

        self.but7 = QtWidgets.QPushButton('send_fish', self)
        self.but7.setGeometry(QtCore.QRect(830, 570, 120, 40))
        self.but7.clicked.connect(self.otpravit1)

        self.but7a = QtWidgets.QPushButton('send_tv', self)
        self.but7a.setGeometry(QtCore.QRect(690, 570, 120, 40))
        self.but7a.clicked.connect(self.otpravit_tv)

        self.but8 = QtWidgets.QPushButton('send_shvp', self)
        self.but8.setGeometry(QtCore.QRect(970, 570, 120, 40))
        self.but8.clicked.connect(self.otpravit2)

        self.but9 = QtWidgets.QPushButton('send_reg', self)
        self.but9.setGeometry(QtCore.QRect(1140, 570, 120, 40))
        self.but9.clicked.connect(self.otpravit3)

        self.but10 = QtWidgets.QPushButton('stop', self)
        self.but10.setGeometry(QtCore.QRect(830, 710, 120, 40))
        self.but10.clicked.connect(self.stop)

        self.lin1 = QtWidgets.QLineEdit(self)
        self.lin1.setGeometry(QtCore.QRect(830, 620, 120, 20))

        self.lin1a = QtWidgets.QLineEdit(self)
        self.lin1a.setGeometry(QtCore.QRect(690, 620, 120, 20))
        
        self.lin2 = QtWidgets.QLineEdit(self)
        self.lin2.setGeometry(QtCore.QRect(830, 650, 120, 20))

        self.lin2a = QtWidgets.QLineEdit(self)
        self.lin2a.setGeometry(QtCore.QRect(690, 650, 120, 20))

        self.lin3 = QtWidgets.QLineEdit(self)
        self.lin3.setGeometry(QtCore.QRect(830, 680, 120, 20))

        self.lin4 = QtWidgets.QLineEdit(self)
        self.lin4.setGeometry(QtCore.QRect(970, 620, 120, 20))#poz

        self.lin5 = QtWidgets.QLineEdit(self)
        self.lin5.setGeometry(QtCore.QRect(970, 680, 120, 20))#sens
        self.lin5.setText('650')

        self.lin5_1 = QtWidgets.QLineEdit(self)
        self.lin5_1.setGeometry(QtCore.QRect(970, 710, 120, 20))#vel
        self.lin5_1.setText('3')

        self.lin5_2 = QtWidgets.QLineEdit(self)
        self.lin5_2.setGeometry(QtCore.QRect(970, 740, 120, 20))#dsh
        self.lin5_2.setText('2')                                                                                                                                                                                                                                                                                                                                                                                                                                    

        self.lin6 = QtWidgets.QLineEdit(self)
        self.lin6.setGeometry(QtCore.QRect(1140, 620, 120, 20))#k_s
        self.lin6.setText('600')

        self.lin7 = QtWidgets.QLineEdit(self)
        self.lin7.setGeometry(QtCore.QRect(1140, 650, 120, 20))#k_p
        self.lin7.setText('30')

        self.lin8 = QtWidgets.QLineEdit(self)
        self.lin8.setGeometry(QtCore.QRect(1140, 680, 120, 20))#k_i
        self.lin8.setText('0')

        self.lin9 = QtWidgets.QLineEdit(self)
        self.lin9.setGeometry(QtCore.QRect(1140, 710, 120, 20))#comp
        self.lin9.setText('1')

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(QtCore.QRect(970, 650, 120, 18))
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.valueChanged[int].connect(self.z1)

                                       
        self.velocity=0
        self.label3 = QtWidgets.QLabel(self)
        self.label3.setGeometry(QtCore.QRect(200, 16, 236, 50))
        self.label3.setText('Убедитесь что сервер\n на роботе открыт')

        self.label4 = QtWidgets.QLabel(self)
        self.label4.setGeometry(QtCore.QRect(700, 16, 236, 50))
        self.label4.setText('Скорость')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(750, 16, 236, 50))
        self.label5.setText('Авто')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1100, 680, 60, 20))
        self.label5.setText('sens')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1100, 710, 60, 20))
        self.label5.setText('vel')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1100, 620, 60, 20))
        self.label5.setText('poz')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1270, 620, 60, 20))
        self.label5.setText('k_s')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1270, 650, 60, 20))
        self.label5.setText('k_p')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1270, 680, 60, 20))
        self.label5.setText('k_i')

        self.label5 = QtWidgets.QLabel(self)
        self.label5.setGeometry(QtCore.QRect(1270, 710, 60, 20))
        self.label5.setText('comp')
    def z1(self,value):
        try:
            self.otpravit(str(value),str(self.lin5_1.text()),'000','000','3')
        except BaseException:
            pass
    def tr_change(self, s):
        self.label5.setText(s)
    def tr_start(self):
        self.mythread.start()
    def otpravit1(self):
        try:
            self.otpravit(str(self.lin1.text()),str(self.lin2.text()),str(self.lin3.text()),'050','1')
        except BaseException:
            pass
    def otpravit_tv(self):
        vel = float(self.lin2a.text())
        s_c = (3.14159265*0.5*0.5)/4
        v_c = vel
        s_p = (3.14159265*9.6*9.6)/4
        v_p = (s_c*v_c)/s_p
        c = 0.003175
        n_timer = 2000
        vel_st  = (c*n_timer)/v_p

        print(vel_st)
        
        try:
            self.otpravit(str(self.lin1a.text()),str(int(vel_st)),str(self.lin3.text()),'050','1')
        except BaseException:
            pass

    
    def otpravit2(self):
        try:
            self.otpravit(str(self.lin4.text()),str(self.lin5_1.text()),str(self.lin5_2.text()),str(self.lin5.text()),'3')
        except BaseException:
            pass
    def otpravit3(self):
        try:
            self.otpravit(str(self.lin6.text()),str(self.lin7.text()),str(self.lin8.text()),str(self.lin9.text()),'4')
        except BaseException:
            pass
    def stop(self):
        try:
            self.otpravit('0','0','50','050','1')
        except BaseException:
            pass
    def otpravit(self,q0,q1,q2,q3,q4):
        q=[0,1,2,3,4]
        q[0]=q0
        q[1]=q1
        q[2]=q2
        q[3]=q3
        q[4]=q4
        i=0
        for i in range(4):
             i1=0
             if len(q[i])<4:
                 while len(q[i])< 3:
                    q[i]='0'+q[i]
                    i1=i1+1
                 i=i+1
        
        dat1 = str(q[0])+str(q[1])+str(q[2])+str(q[3])+str(q[4])
        control_sum=0
        for i in range(13):
            control_sum=control_sum+int(dat1[i])
        i=0
        control_sum=str(control_sum)
        while len(control_sum)< 3:
            control_sum='0'+control_sum
            i=i+1
        dat1 ='b'+dat1+control_sum+'0'
        print(dat1)
        for i in range(17):
            dat2=str(dat1[i])
            self.data = bytes(dat2, encoding='ascii')
            self.ser.write(self.data)   
        otv=0
        otv1=0
        con=0
        i1=0
        i=0
        while otv!=1:
            
            response = str(self.ser.readline())
            i+=1
            print(response)
            try:
                if len(response)>5:
                    con=100*int(response[2])+10*int(response[3])+int(response[4])
            except:pass
            if con == int(control_sum):
                otv=1
                print(response[7:12])
                print('ok')
            elif con == 999 or i>100:
                i=0
                for i in range(17):
                    dat2=str(dat1[i])
                    self.data = bytes(dat2, encoding='ascii')
                    self.ser.write(self.data)
        #for i in range(3):
            #response = str(self.ser.readline())
            #print(response)
    def send_1(self):
        f = open('traj_test_1.txt')
        print("open")
        f1=f.read()
        print("read")
        f1=f1.encode()
        print("encode")
        self.s.sendall(f1)
        print("sendall")
        f.close()
        print("close")
        #ud='q'
        #self.s.send(ud.encode('utf-8'))

    def open_simple(self):       
        host = '172.31.1.147'
        flag_con=0
        self.label3.setText('Поиск свободных портов...')
        i=10
        while flag_con==0 and i>1:            
            try:                
                time.sleep(.1)
                i-=1
                port=int('3000'+str(i))
                port=30005
                addr = (host,port)
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect(addr)
                flag_con=1
                self.label3.setText('Соединение установлено')
                
            except BaseException:
                pass
        if flag_con==0:
            self.label3.setText('Не удалось подключиться')
        if flag_con==1:
            time.sleep(0.2)
            self.points=[]
            try:
                self.send_1()
                self.s.close()
            except BaseException:
                self.label3.setText('Не удалось подключиться') 

    def open_1(self):       
        host = '172.31.1.147'
        flag_con=0
        self.label3.setText('Поиск свободных портов...')
        i=10
        while flag_con==0 and i>1:            
            try:                
                time.sleep(.1)
                i-=1
                port=int('3000'+str(i))
                port=30005
                addr = (host,port)
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect(addr)
                flag_con=1
                self.label3.setText('Соединение установлено')
                
            except BaseException:
                pass
        if flag_con==0:
            self.label3.setText('Не удалось подключиться')
        if flag_con==1:
            self.points=[]
            try:
                res_a=[]
                data = self.s.recv(1000)
                res=str(data.decode('utf-8'))
                res_a=res.split(',')
                self.points=res_a
                print(self.points)
                self.send_2()
                self.send_1()
            except BaseException:
                self.label3.setText('Не удалось подключиться')
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)  
        self.drawLines(qp)
        #qp.restore()
    def drawLines(self, qp):
        pen1 = QPen()
        qp.setPen(pen1)
        #qp.drawPolyline(self.ef_1)
        pen = QPen(Qt.blue, 1, Qt.SolidLine)
        qp.setPen(pen)
        #print(str(self.koord_2))
        Xmin=10000
        Ymin=10000
        Xmax=-10000
        Ymax=-10000
        Xq1=200
        Xq2=800
        Yq1=20
        Yq2=800
    def test(self):
        ud='j\n'
        self.s.send(ud.encode('utf-8'))
        while True:
            try:
                data = self.s.recv(100)
                res=str(data.decode('utf-8'))
                otv=res[0:7]                
                self.otpravit(otv[0],otv[1]+otv[2]+otv[3],otv[4]+otv[5]+otv[6],'050','1')
            except BaseException:
                pass
        self.s.close()        
    def datch(self):
        
        res=460
        sum1=460
        sum2=460
        k2=15
        dr2=10
        k=5
        dr=150
        ud='j\n'
        try:
            self.s.settimeout(0.001)
            self.s.send(ud.encode('utf-8'))
            fmass=[]
            fmass2=[]
            for i in range(k):
                fmass.append(res)
            for i in range(k2):
                fmass2.append(res)
        except BaseException:
            pass
        
        f1='fsdfsdf'
        i1=0
        while f1[2]!='q':
            i1+=1
            otv='000000000000000000'
            try:
                data = self.s.recv(1000)
                res=str(data.decode('utf-8'))
                print(str(res[13:]))
                otv=res[0:13]
                self.otpravit(otv[0]+otv[1]+otv[2],otv[3]+otv[4]+otv[5],otv[6]+otv[7]+otv[8],otv[9]+otv[10]+otv[11],otv[12])
            except BaseException as e:
                pass#print(e)
            f2=""
            '''try:
                f1=self.ser.readline()
                n=len(f1)
            except BaseException:
                f1='www'
                n=3
            if n>5:
                f1=str(f1)
                if f1[2]=='d':
                    try:
                        q=f1+'\n'
                        q=q.encode()
                        self.s.sendall(q)
                        #print('q'+str(q))
                    except BaseException:
                        pass'''
            f1=otv
        self.close_2()  
    def close_1(self):
        self.s.close()
    def close(self):
        try:
            self.ser.close()
            self.label3.setText('Сериал порт закрыт')
        except BaseException:
            pass
    def send(self,inp):        
        dat1 ='b'+inp+'0'
        #print(dat1)
        try:
            self.ser.write(bytes(dat1,encoding='ascii'))
        except BaseException:
            pass      
    def op1(self):
        i1=0
        while(i1<11):            
            baud = 2000000#115200
            try:
                self.ser = serial.Serial(self.comport[i1], baud, timeout=0)
                self.label3.setText('Сериал порт открыт')
            except BaseException:
                pass
            i1=i1+1
            
    def send_2(self):
        #f = open('TEST_COLLAGEN.txt')
        #f = open('Square.txt')
        self.points=['619.5516789079381', '-75.80697911235869', '106.59444416401084', 
        '609.856696853156', '-75.81670017995225', '107.87026909021267', 
        '601.6546609091087', '-75.7888384506065', '104.02339097727605', 
        
        '599.3894496554303', '-67.6787312638806', '102.67027154605285',
         '604.7884750032555', '-45.46371694349858', '107.22744822835563',
          '623.4692472978895', '-67.75860333501795', '105.14093695340571',
          
           '621.0489916895073', '-57.97572219332513', '105.42607853224104', 
           '610.1970987133091', '-57.98186061843465', '107.08935380881547',
            '602.5935798639625', '-57.97775641295552', '103.31046656992916',
            
             '609.6908397928476', '-52.21995716151367', '105.47661461444824', 
             '609.8022266093342', '-80.96707418455267', '108.0', '\r\n']
        f = open('Krug_pig.txt')
        
        px=[]
        py=[]
        pz=[]
        i=0
        while i<33:
            px.append(float(self.points[i]))
            py.append(float(self.points[i+1]))
            pz.append(float(self.points[i+2]))
            i+=3
        cenx=[self.points[10],self.points[1],self.points[4],self.points[7],self.points[9]]
        #ceny=[self.points[10],self.points[1],self.points[4],self.points[7],self.points[9]]
        file_str=f.readlines()
        i_f=0
        len_f=len(file_str)
        f1=open('output.txt','w')
        while i_f<len_f:
            i_s=0
            i_x=0
            l_s=file_str[i_f]
            
            l_s=file_str[i_f]
            l_s=l_s.replace('A1','X')
            l_s=l_s.replace('A2','Y')
            l_s=l_s.replace('A3','Z')
            l_s=l_s.replace('A4','A')
            l_s=l_s.replace('A5','B')
            l_s=l_s.replace('A6','C')
            #print(l_s)
            len_s=len(l_s)
            while i_s<len_s:
                symb=l_s[i_s]
                
                if symb=='X' or symb=='}' or symb=='{' :
                    f1.write('\n')
                f1.write(symb)
                i_s+=1
            if i_x>1:        
                pass
            i_f+=1
        
        f1.close()
        prog=[]
        f = open('output.txt')
        file_str=f.readlines()
        len_f=len(file_str)
        i_f=1
        prog_G_1=[]
        prog_X_1=[]
        prog_Y_1=[]
        prog_Z_1=[]
        prog_A_1=[]
        prog_B_1=[]
        prog_C_1=[]
        prog_V_1=[]
        prog_D_1=[]
        prog_F_1=[]
        prog_S_1=[]
        while i_f<len_f:
            prog_g_1=''
            prog_x_1=''
            prog_y_1=''
            prog_z_1=''
            prog_a_1=''
            prog_b_1=''
            prog_c_1=''
            prog_v_1=''
            prog_d_1=''
            prog_f_1=''
            prog_s_1=''
            prog_g=''
            prog_x=''
            prog_y=''
            prog_z=''
            prog_a=''
            prog_b=''
            prog_c=''
            prog_v=''
            prog_d=''
            prog_f=''
            prog_s=''
            #print('STROKA['+str(i_f)+']='+file_str[i_f])
            i_s=0
            len_s=len(file_str[i_f])
            while i_s<len_s:
                symb=file_str[i_f][i_s]
                #print(str(i_s)+'sym: '+symb) 
                if symb=='G':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or symb=='-' or symb=='9' or symb=='8' or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                                                
                        symb=file_str[i_f][i_s+i]
                        if symb!='G' and symb!='X' and symb!='Y' and symb!='Z' and symb!=' ' and symb!=',':
                            prog_g=prog_g+symb
                        i=i+1
                if symb=='V':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_v=prog_v+symb
                        i=i+1
                if symb=='D':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_d=prog_d+symb
                        i=i+1
                if symb=='F':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_f=prog_f+symb
                        i=i+1
                if symb=='S':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_s=prog_s+symb
                        i=i+1
                if symb=='X':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_x=prog_x+symb
                        i=i+1           
                if symb=='Y':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if symb!='G' and symb!='X' and symb!='Z' and symb!=',':
                            prog_y=prog_y+symb
                        i=i+1      
                if symb=='Z':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if symb!='G' and symb!='X' and symb!='Y' and symb!=',':
                            prog_z=prog_z+symb
                        i=i+1
                if symb=='A':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_a=prog_a+symb
                        i=i+1
                if symb=='B':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_b=prog_b+symb
                        i=i+1
                if symb=='C':
                    i=1
                    symb=file_str[i_f][i_s+i]
                    while symb==' ' or  symb=='-' or symb=='9'or symb=='8'or symb=='7'or symb=='6'or symb=='5'or symb=='4'or symb=='3'or symb=='2'or symb=='1'or symb=='0'or symb=='.':                        
                        symb=file_str[i_f][i_s+i]
                        if  symb!='G' and symb!='Y' and symb!='Z' and symb!=',':
                            prog_c=prog_c+symb                        
                        i=i+1
                i_s=i_s+1
            k1=1
            Xc=0
            Yc=0
            Zc=0
            Vc=0
            if prog_g!='':
                prog_g_1=int(prog_g)
            if prog_x!='':
                if prog_x[0]==' ':
                    prog_x=prog_x[1:]
                if prog_x[0]=='-':
                    prog_x=prog_x[1:]
                    prog_x_1=round(Xc-k1*float(prog_x),3)
                else:
                    prog_x_1=round(Xc+k1*float(prog_x),3)
            if prog_d!='':
                if prog_d[0]==' ':
                    prog_d=prog_d[1:]
                if prog_d[0]=='-':
                    prog_d=prog_d[1:]
                    prog_d_1=round(-k1*float(prog_d),3)
                else:
                    prog_d_1=round(+k1*float(prog_d),3)
            if prog_f!='':
                if prog_f[0]==' ':
                    prog_f=prog_f[1:]
                if prog_d[0]=='-':
                    prog_f=prog_f[1:]
                    prog_f_1=round(-k1*float(prog_f),0)
                else:
                    prog_f_1=round(+k1*float(prog_f),0)
            if prog_s!='':
                if prog_s[0]==' ':
                    prog_s=prog_s[1:]
                if prog_s[0]=='-':
                    prog_s=prog_s[1:]
                    prog_s_1=round(-k1*float(prog_s),3)
                else:
                    prog_s_1=round(+k1*float(prog_s),3)
            if prog_v!='':
                if prog_v[0]==' ':
                    prog_v=prog_v[1:]
                if prog_v[0]=='-':
                    prog_v=prog_v[1:]
                    prog_v_1=round(Vc-k1*float(prog_v),3)
                else:
                    prog_v_1=round(Vc+k1*float(prog_v),3)
            if prog_y!='':
                if prog_y[0]==' ':
                    prog_y=prog_y[1:]
                if prog_y[0]=='-':
                    prog_y=prog_y[1:]
                    prog_y_1=round(Yc-k1*float(prog_y),3)
                else:
                    prog_y_1=round(Yc+k1*float(prog_y),3)
            if prog_z!='':
                if prog_z[0]==' ':
                    prog_z=prog_z[1:]
                if prog_z[0]=='-':
                    prog_z=prog_z[1:]
                    prog_z_1=round(Zc-float(prog_z),3)
                else:
                    prog_z_1=round(Zc+float(prog_z),3)
            if prog_a!='':
                if prog_a[0]==' ':
                    prog_a=prog_a[1:]
                if prog_a[0]=='-':
                    prog_a=prog_a[1:]
                    prog_a_1=round(-float(prog_a),3)
                else:
                    prog_a_1=round(float(prog_a),3)
            if prog_b!='':
                if prog_b[0]==' ':
                    prog_b=prog_b[1:]
                if prog_b[0]=='-':
                    prog_b=prog_b[1:]
                    prog_b_1=round(-float(prog_b),3)
                else:
                    prog_b_1=round(float(prog_b),3)
            if prog_c!='':
                if prog_c[0]==' ':
                    prog_b=prog_c[1:]
                if prog_c[0]=='-':
                    prog_c=prog_c[1:]
                    prog_c_1=round(-float(prog_c),3)
                else:
                    prog_c_1=round(float(prog_c),3)
            prog_G_1.append(prog_g_1)
            prog_X_1.append(prog_x_1)
            prog_Y_1.append(prog_y_1)
            prog_Z_1.append(prog_z_1)
            prog_A_1.append(prog_a_1)
            prog_B_1.append(prog_b_1)
            prog_C_1.append(prog_c_1)
            prog_V_1.append(prog_v_1)
            prog_D_1.append(prog_d_1)
            prog_F_1.append(prog_f_1)
            prog_S_1.append(prog_s_1)
            i_f=i_f+1
        prog_G_2=[]
        prog_X_2=[]
        prog_Y_2=[]
        prog_Z_2=[]
        prog_A_2=[]
        prog_B_2=[]
        prog_C_2=[]
        prog_V_2=[]
        prog_D_2=[]
        prog_F_2=[]
        prog_S_2=[]
        prog_r_2=[]
        prog_fi_2=[]
        max_rass=0

        for i in range(len(prog_X_1)):
            if type(prog_X_1[i]) and type(prog_Y_1[i]) is not str:
                
                prog_G_2.append(prog_G_1[i])
                prog_X_2.append(prog_X_1[i])
                prog_Y_2.append(prog_Y_1[i])
                prog_Z_2.append(prog_Z_1[i])
                prog_A_2.append(prog_A_1[i])
                prog_B_2.append(prog_B_1[i])
                prog_C_2.append(prog_C_1[i])
                prog_V_2.append(prog_V_1[i])
                prog_D_2.append(prog_D_1[i])
                prog_F_2.append(prog_F_1[i])
                prog_S_2.append(prog_S_1[i])
                x=prog_X_1[i]
                y=prog_Y_1[i]
                r=(x**2+y**2)**0.5
                if x==0:
                    x=0.000001
                fi=math.atan(y/x)
                prog_r_2.append(r)
                prog_fi_2.append(fi)

        for i in range(10,len(prog_X_2)-10):     
            x0=prog_X_2[i]
            y0=prog_Y_2[i]
            x1=prog_X_2[i+1]
            y1=prog_Y_2[i+1]
            dx=abs(x1-x0)
            dy=abs(y1-y0)
            rass=((x0-x1)**2+(y0-y1)**2)**0.5
            if dx>dy:
                if rass>max_rass:
                    max_rass=rass
                    max_i=i

        x0=prog_X_2[max_i]
        y0=prog_Y_2[max_i]
        x1=prog_X_2[max_i+1]
        y1=prog_Y_2[max_i+1]
        dx=x1-x0
        dy=y1-y0
        if dx==0:
            dx=0.000001
        off_fi=abs(math.atan(dy/dx))
        for i in range(len(prog_X_2)):
            r=prog_r_2[i]
            fi=prog_fi_2[i]+off_fi
            x=r*math.cos(fi)
            y=r*math.sin(fi)
            prog_X_2[i]=x
            prog_Y_2[i]=y

        pro_X_2=prog_X_2
        pro_Y_2=prog_Y_2
        del pro_X_2[0]
        del pro_Y_2[0]
        del pro_X_2[-1]
        del pro_Y_2[-1]
        P4x=min(pro_X_2)+(max(pro_X_2)-min(pro_X_2))/2
        P4y=max(pro_Y_2)
        offX=px[9]-P4x
        offY=py[9]-P4y
        ekv_X=[]
        ekv_Y=[]
        for i in range(len(prog_X_2)):
            prog_X_2[i]=prog_X_2[i]+offX
            prog_Y_2[i]=prog_Y_2[i]+offY
        PTP=[prog_X_2[0],prog_Y_2[0],prog_Z_2[0],prog_A_2[0],prog_B_2[0],prog_C_2[0]]
        Xn=[prog_X_2[0],prog_X_2[1]]
        Yn=[prog_Y_2[0],prog_Y_2[1]]
    #------------------------
        Xmin=10000
        Ymin=10000
        Zmin=10000
        Xmax=-10000
        Ymax=-10000
        Zmax=-10000
        
        for i in range(1,int(len(prog_X_2))-1):
            
            if prog_X_2[i]>Xmax:
                Xmax=prog_X_2[i]
            if prog_X_2[i]<Xmin:
                Xmin=prog_X_2[i]
            if prog_Y_2[i]>Ymax:
                Ymax=prog_Y_2[i]
            if prog_Y_2[i]<Ymin:
                Ymin=prog_Y_2[i]
            if prog_Z_2[i]>Zmax:
                Zmax=prog_Z_2[i]
            if prog_Z_2[i]<Zmin:
                Zmin=prog_Z_2[i]
        Yq1=-0.5
        Yq2=0.5
        Xq1=-0.5
        Xq2=0.5  
        kx=abs(Yq1-Yq2)/abs(Ymax-Ymin)
        ky=abs(Xq1-Xq2)/abs(Xmax-Xmin)
        if kx<ky:
            k=kx
            Yq1=-0.5
            Yq2=0.5        
            Xq1=-k*(Xmax-Xmin)/2
            Xq2=-Xq1
        else:
            k=ky
            Xq1=-0.5
            Xq2=0.5        
            Yq1=-k*(Ymax-Ymin)/2
            Yq2=-Xq1
        
        Zq1=0
        Zq2=1
        loordm = []
        offX=Xmin*k-Xq1
        offY=Ymin*k-Yq1
        offZ=Zmin*k-Zq1
        for i in range(int(len(prog_X_2)-1)):
            x1=prog_X_2[i]
            y1=prog_Y_2[i]
            z1=prog_Z_2[i]
            #loordm.append([x1*k-offX,y1*k-offY,z1*k-offZ,1])
        
        #loordm.append([prog_X_2[len(prog_X_2)-2]*k+600,prog_Y_2[len(prog_X_2)-2]*k,prog_Z_2[len(prog_X_2)-2]*k-offZ,1])
            
#------------------------
        step=1.7
        self.test=[]
        
        mas=[]
        for i in range(2,len(prog_X_2)-1):
            x0=prog_X_2[i-2]
            y0=prog_Y_2[i-2]
            x1=prog_X_2[i-1]
            y1=prog_Y_2[i-1]
            x2=prog_X_2[i]
            y2=prog_Y_2[i]
            x3=prog_X_2[i+1]
            y3=prog_Y_2[i+1]
            a=y2-y3
            if a==0:
                a=0.000001
            b=x3-x2
            if b==0:
                b=0.000001  
            c=x2*y3-x3*y2
            rasst=abs(a*x1+b*y1+c)/((a*a+b*b)**0.5)
            if rasst<step+0.01 and rasst>step-0.01:
                dx=x2-x1
                dy=y2-y1
                dx1=x1-x0
                dy1=y1-y0
                dx2=x3-x2
                dy2=y3-y2
                if (abs(dy2)<step-0.01 or abs(dy1)<step-0.01):
                    sry=(y1+y2)/2
                    srx=(x1+x2)/2
                    if sry<py[9] and sry>py[10]:
                        mas.append(i-1)
                        mas.append(i)
                        if sry>=py[10] and sry<py[0]:
                            mx1=px[2]
                            mx2=px[10]
                            mx3=px[0]
                            my1=py[2]
                            my2=py[10]
                            my3=py[0]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            qD=(4*x_okr*x_okr-4*(x_okr*x_okr+sry*sry-2*y_okr*sry+y_okr*y_okr-r_okr*r_okr))**0.5;
                            if srx>px[10]:
                                xsry1=(2*x_okr+qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                                
                            else:
                                xsry1=(2*x_okr-qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                            ekv_X.append(xsry1)
                            ekv_Y.append(sry)
                            
                        elif sry<py[4] and sry>=py[0]:
                            if srx>px[7]:
                                mx1=px[0]
                                mx2=px[5]
                                mx3=px[6]
                                my1=py[0]
                                my2=py[5]
                                my3=py[6]
                            else:
                                mx1=px[8]
                                mx2=px[2]
                                mx3=px[3]
                                my1=py[8]
                                my2=py[2]
                                my3=py[3]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            qD=(4*x_okr*x_okr-4*(x_okr*x_okr+sry*sry-2*y_okr*sry+y_okr*y_okr-r_okr*r_okr))**0.5;
                            if srx>px[7]:
                                xsry1=(2*x_okr+qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                                
                            else:
                                xsry1=(2*x_okr-qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                            ekv_X.append(xsry1)
                            ekv_Y.append(sry)
                        elif sry<py[7] and sry>=py[4]:
                            if srx>px[7]:
                                mx1=px[0]
                                mx2=px[5]
                                mx3=px[6]
                                my1=py[0]
                                my2=py[5]
                                my3=py[6]
                            else:
                                mx1=px[8]
                                mx2=px[2]
                                mx3=px[3]
                                my1=py[8]
                                my2=py[2]
                                my3=py[3]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            qD=(4*x_okr*x_okr-4*(x_okr*x_okr+sry*sry-2*y_okr*sry+y_okr*y_okr-r_okr*r_okr))**0.5;
                            if srx>px[7]:
                                xsry1=(2*x_okr+qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                                
                            else:
                                xsry1=(2*x_okr-qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                            ekv_X.append(xsry1)
                            ekv_Y.append(sry)
                        elif sry<py[9] and sry>=py[7]:
                            mx1=px[8]
                            mx2=px[9]
                            mx3=px[6]
                            my1=py[8]
                            my2=py[9]
                            my3=py[6]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            qD=(4*x_okr*x_okr-4*(x_okr*x_okr+sry*sry-2*y_okr*sry+y_okr*y_okr-r_okr*r_okr))**0.5
                            if srx>px[7]:
                                xsry1=(2*x_okr+qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                                
                            else:
                                xsry1=(2*x_okr-qD)*0.5
                                prog_X_2[i-1]=xsry1
                                prog_X_2[i]=xsry1
                            ekv_X.append(xsry1)
                            ekv_Y.append(sry)
                elif (abs(dx2)<step-0.1 or abs(dx1)<step-0.1):
                    sry=(y1+y2)/2
                    srx=(x1+x2)/2
                    if srx<=px[5] and srx>=px[3]:
                        mas.append(i-1)
                        mas.append(i)
                        if srx<=px[2] and srx>=px[3]:
                            mx1=px[2]
                            mx2=px[3]
                            mx3=px[8]
                            my1=py[2]
                            my2=py[3]
                            my3=py[8]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            
                            qD=(4*y_okr*y_okr-4*(y_okr*y_okr+srx*srx-2*x_okr*srx+x_okr*x_okr-r_okr*r_okr))**0.5;
                            if sry>py[4]:
                                xsry1=(2*y_okr+qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                                
                            else:
                                xsry1=(2*y_okr-qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                            ekv_X.append(srx)
                            ekv_Y.append(xsry1)
                        elif srx<=px[4] and srx>px[2]:
                            if sry>py[4]:
                                mx1=px[8]
                                mx2=px[9]
                                mx3=px[6]
                                my1=py[8]
                                my2=py[9]
                                my3=py[6]
                            else:
                                mx1=px[10]
                                mx2=px[2]
                                mx3=px[0]
                                my1=py[10]
                                my2=py[2]
                                my3=py[0]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            
                            qD=(4*y_okr*y_okr-4*(y_okr*y_okr+srx*srx-2*x_okr*srx+x_okr*x_okr-r_okr*r_okr))**0.5;
                            if sry>py[4]:
                                xsry1=(2*y_okr+qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                                
                            else:
                                xsry1=(2*y_okr-qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                            ekv_X.append(srx)
                            ekv_Y.append(xsry1)
                        elif srx<=px[0] and srx>px[4]:
                            if sry>py[4]:
                                mx1=px[8]
                                mx2=px[9]
                                mx3=px[6]
                                my1=py[8]
                                my2=py[9]
                                my3=py[6]
                            else:
                                mx1=px[10]
                                mx2=px[0]
                                mx3=px[2]
                                my1=py[10]
                                my2=py[0]
                                my3=py[2]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            
                            qD=(4*y_okr*y_okr-4*(y_okr*y_okr+srx*srx-2*x_okr*srx+x_okr*x_okr-r_okr*r_okr))**0.5;
                            if sry>py[4]:
                                xsry1=(2*y_okr+qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                                
                            else:
                                xsry1=(2*y_okr-qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                            ekv_X.append(srx)
                            ekv_Y.append(xsry1)
                        elif srx<=px[5] and srx>px[0]:
                            mx1=px[0]
                            mx2=px[5]
                            mx3=px[6]
                            my1=py[0]
                            my2=py[5]
                            my3=py[6]
                            x_okr=((2*my3-2*my2)*(my2*my2-my1*my1+mx2*mx2-mx1*mx1)-(2*my2-2*my1)*(my3*my3-my2*my2+mx3*mx3-mx2*mx2))/((2*my2-2*my1)*(2*mx2-2*mx3)-(2*my3-2*my2)*(2*mx1-2*mx2))
                            y_okr=(my2*my2-my1*my1+mx2*mx2-mx1*mx1+2*mx1*x_okr-2*mx2*x_okr)/(2*my2-2*my1)
                            r_okr=((my1-y_okr)**2+(mx1-x_okr)**2)**0.5
                            
                            qD=(4*y_okr*y_okr-4*(y_okr*y_okr+srx*srx-2*x_okr*srx+x_okr*x_okr-r_okr*r_okr))**0.5;
                            
                            if sry>py[4]:
                                xsry1=(2*y_okr+qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                                
                            else:
                                xsry1=(2*y_okr-qD)*0.5
                                prog_Y_2[i-1]=xsry1
                                prog_Y_2[i]=xsry1
                            ekv_X.append(srx)
                            ekv_Y.append(xsry1)
        obr=2.3
        print(str(mas))        
        hj1=prog_X_2
        hj2=prog_Y_2
        hj3=prog_Z_2
        hj4=prog_A_2
        hj5=prog_B_2
        hj6=prog_C_2
        hj7=prog_V_2
        hj8=prog_D_2
        hj9=prog_F_2
        hj10=prog_S_2
        prog_X_2=[]
        prog_Y_2=[]
        prog_Z_2=[]
        prog_A_2=[]
        prog_B_2=[]
        prog_C_2=[]
        prog_V_2=[]
        prog_D_2=[]
        prog_F_2=[]
        prog_S_2=[]
        for i in mas:
            prog_X_2.append(hj1[i])
            prog_Y_2.append(hj2[i])
            prog_Z_2.append(hj3[i])
            prog_A_2.append(hj4[i])
            prog_B_2.append(hj5[i])
            prog_C_2.append(hj6[i])
            prog_V_2.append(hj7[i])
            prog_D_2.append(hj8[i])
            prog_F_2.append(hj9[i])
            prog_S_2.append(hj10[i])
        hj1=prog_X_2
        hj2=prog_Y_2
        hj3=prog_Z_2
        hj4=prog_A_2
        hj5=prog_B_2
        hj6=prog_C_2
        hj7=prog_V_2
        hj8=prog_D_2
        hj9=prog_F_2
        hj10=prog_S_2
        prog_X_2=[hj1[0]]
        prog_Y_2=[hj2[0]]
        prog_Z_2=[hj3[0]]
        prog_A_2=[hj4[0]]
        prog_B_2=[hj5[0]]
        prog_C_2=[hj6[0]]
        prog_V_2=[hj7[0]]
        prog_D_2=[hj8[0]]
        prog_F_2=[hj9[0]]
        prog_S_2=[hj10[0]]
        prev_p=1
        cur_p=0
        
        for i in range(len(hj1)):
            if i<len(hj1)-1:
                if abs(hj2[i]-hj2[i+1])>0.001:
                    usl= abs((hj1[i]-hj1[i+1])/(hj2[i]-hj2[i+1]))
                    rasst=((hj1[i]-hj1[i+1])**2+(hj2[i]-hj2[i+1])**2)**0.5
                else:
                    usl=1000
            else:
                usl=1000
            if usl<50 and usl>0.05 and rasst>2:
                cur_p=0
                hj3[i]=hj3[i]+3
                               
            else:
                cur_p=1
            if cur_p==0 and prev_p==0:
                sad=3
            else:
                prog_X_2.append(hj1[i])
                prog_Y_2.append(hj2[i])
                prog_Z_2.append(hj3[i])
                prog_A_2.append(hj4[i])
                prog_B_2.append(hj5[i])
                prog_C_2.append(hj6[i])
                prog_V_2.append(hj7[i])
                prog_D_2.append(hj8[i])
                prog_F_2.append(hj9[i])
                prog_S_2.append(hj10[i])

            prev_p=cur_p
        
        Xn=[prog_X_2[1]]
        
        Yn=[prog_Y_2[1]]
        Zn=[prog_Z_2[1]]
        An=[prog_A_2[1]]
        Bn=[prog_B_2[1]]
        Cn=[prog_C_2[1]]
        Vn=[prog_V_2[1]]
        Dn=[prog_D_2[1]]
        Fn=[prog_F_2[1]]
        Sn=[prog_S_2[1]]
        
         #------------------------
        Xmin=10000
        Ymin=10000
        Zmin=10000
        Xmax=-10000
        Ymax=-10000
        Zmax=-10000
        
        for i in range(1,int(len(prog_X_2))-1):
            
            if prog_X_2[i]>Xmax:
                Xmax=prog_X_2[i]
            if prog_X_2[i]<Xmin:
                Xmin=prog_X_2[i]
            if prog_Y_2[i]>Ymax:
                Ymax=prog_Y_2[i]
            if prog_Y_2[i]<Ymin:
                Ymin=prog_Y_2[i]
            if prog_Z_2[i]>Zmax:
                Zmax=prog_Z_2[i]
            if prog_Z_2[i]<Zmin:
                Zmin=prog_Z_2[i]
        Yq1=-0.5
        Yq2=0.5
        Xq1=-0.5
        Xq2=0.5  
        kx=abs(Yq1-Yq2)/abs(Ymax-Ymin)
        ky=abs(Xq1-Xq2)/abs(Xmax-Xmin)
        if kx<ky:
            k=kx
            Yq1=-0.5
            Yq2=0.5        
            Xq1=-k*(Xmax-Xmin)/2
            Xq2=-Xq1
        else:
            k=ky
            Xq1=-0.5
            Xq2=0.5        
            Yq1=-k*(Ymax-Ymin)/2
            Yq2=-Xq1
        
        Zq1=0
        Zq2=1
        loordm = []
        offX=Xmin*k-Xq1
        offY=Ymin*k-Yq1
        offZ=Zmin*k-Zq1
        for i in range(int(len(prog_X_2)-1)):
            x1=prog_X_2[i]
            y1=prog_Y_2[i]
            z1=prog_Z_2[i]
            loordm.append([x1*k-offX,y1*k-offY,z1*k-offZ,1])
        
        loordm.append([prog_X_2[len(prog_X_2)-2]*k+600,prog_Y_2[len(prog_X_2)-2]*k,prog_Z_2[len(prog_X_2)-2]*k-offZ,1])
            
#------------------------
        for i in range(2,len(prog_X_2)-1):
            if type(prog_Y_2[i])==complex:
                prog_Y_2[i]=(prog_Y_2[i]).real
            if type(prog_Z_2[i])==complex:
                prog_Z_2[i]=(prog_Z_2[i]).real
            x1=prog_X_2[i-1]
            y1=prog_Y_2[i-1]
            x2=prog_X_2[i]
            y2=prog_Y_2[i]
            a1=prog_A_2[i-1]
            a2=prog_A_2[i]
            rasst=((x1-x2)**2+(y1-y2)**2)**0.5
            if rasst>obr*2.1:
                x_3=[]
                y_3=[]
                a_3=[]
                x4=x2-obr*(x2-x1)/rasst
                y4=y2-obr*(y2-y1)/rasst
                x3=x1+obr*(x2-x1)/rasst
                y3=y1+obr*(y2-y1)/rasst
                rasst=((x3-x4)**2+(y3-y4)**2)**0.5
                while rasst>obr*2:
                    x1=x1+obr*(x4-x1)/rasst
                    y1=y1+obr*(y4-y1)/rasst
                    a1=a1+obr*(a2-a1)/rasst
                    x_3.append(x1)
                    y_3.append(y1)
                    a_3.append(a1)
                    rasst=((x1-x4)**2+(y1-y4)**2)**0.5
                    
                Xn.append(prog_X_2[i-1])
                Xn.append(x3)
                for i1 in range(len(x_3)):
                    Xn.append(x_3[i1])
                Xn.append(x4)
                Xn.append(prog_X_2[i])
                
                Yn.append(prog_Y_2[i-1])  
                Yn.append(y3)
                for i1 in range(len(x_3)):
                    Yn.append(y_3[i1])
                Yn.append(y4)  
                Yn.append(prog_Y_2[i])
                
                Zn.append(prog_Z_2[i-1])
                Zn.append(prog_Z_2[i-1])
                for i1 in range(len(x_3)):
                    Zn.append(prog_Z_2[i-1])
                Zn.append(prog_Z_2[i-1])
                Zn.append(prog_Z_2[i])
                
                An.append(prog_A_2[i-1])
                An.append(prog_A_2[i-1])
                for i1 in range(len(x_3)):
                    An.append(a_3[i1])
                An.append(prog_A_2[i])
                An.append(prog_A_2[i])
                Bn.append(prog_B_2[i-1])
                Bn.append(prog_B_2[i-1])
                for i1 in range(len(x_3)):
                    Bn.append(prog_B_2[i-1])
                Bn.append(prog_B_2[i])
                Bn.append(prog_B_2[i])
                Cn.append(prog_C_2[i-1])
                Cn.append(prog_C_2[i-1])
                for i1 in range(len(x_3)):
                    Cn.append(prog_C_2[i-1])
                Cn.append(prog_C_2[i])
                Cn.append(prog_C_2[i])
                Vn.append(prog_V_2[i-1])
                Vn.append(prog_V_2[i-1])
                for i1 in range(len(x_3)):
                    Vn.append(prog_V_2[i-1])
                Vn.append(prog_V_2[i])
                Vn.append(prog_V_2[i])
                Dn.append(prog_D_2[i-1])
                Dn.append(prog_D_2[i-1])
                for i1 in range(len(x_3)):
                    Dn.append(prog_D_2[i-1])
                Dn.append(prog_D_2[i])
                Dn.append(prog_D_2[i])
                Fn.append(prog_F_2[i-1])
                Fn.append(prog_F_2[i-1])
                for i1 in range(len(x_3)):
                    Fn.append(prog_F_2[i-1])
                Fn.append(prog_F_2[i])
                Fn.append(prog_F_2[i])
                Sn.append(prog_S_2[i-1])
                Sn.append(prog_S_2[i-1])
                for i1 in range(len(x_3)):
                    Sn.append(prog_S_2[i-1])
                Sn.append(prog_S_2[i])
                Sn.append(prog_S_2[i])
                
                
        prog_X_2=Xn
        prog_Y_2=Yn
        prog_Z_2=Zn
        prog_A_2=An
        prog_B_2=Bn
        prog_C_2=Cn
        prog_V_2=Vn
        prog_D_2=Dn
        prog_F_2=Fn
        prog_S_2=Sn
        rasst_min=0
        rasst_MIN=0.45
        koord=[[600,0,150,0,0.0,90.0,0.0]]
         
        for i in range(1,len(prog_X_2)):
            rasst=((koord[-1][0]-prog_X_2[i])**2+(koord[-1][1]-prog_Y_2[i])**2+(koord[-1][2]-prog_Z_2[i])**2)**0.5
            if rasst>rasst_MIN:
                koord.append([prog_X_2[i],prog_Y_2[i],prog_Z_2[i],prog_A_2[i],prog_B_2[i],prog_C_2[i],prog_V_2[i],prog_D_2[i],prog_F_2[i],prog_S_2[i]])
        #loordm=[]
        P4x=0
        P4y=0
        inX=[]
        inY=[]
        inZ=[]
        inA=[]
        inB=[]
        inC=[]
        inV=[]
        inD=[]
        inF=[]
        inS=[]
        _inZ=[]
        for i in range(2,len(koord)):
            inX.append(round(koord[i][0],4))
            inY.append(round(koord[i][1],4))
            inZ.append(round(koord[i][2],4))
            inA.append(round(koord[i][3],4))
            inB.append(round(koord[i][4],4))
            inC.append(round(koord[i][5],4))
            inV.append(round(koord[i][6],4))
            inD.append(round(koord[i][7],4))
            inF.append(round(koord[i][8],4))
            inS.append(round(koord[i][9],4))
        for i in range(len(inZ)):
            _inZ.append(inZ[i])
        y_okr=[0,0,0,0,0]
        py=[0]+py
        y_okr[0] = py[11];
        y_okr[1] = py[2];
        y_okr[2] = py[5];
        y_okr[3] = py[8];
        y_okr[4] = py[10];
        pX=[0]+px
        pY=py
        pZ=[0]+pz
        ip=0
        x_okr=[0,0,0,0,0]
        z_okr=[0,0,0,0,0]
        r_okr=[0,0,0,0,0]
        for id1 in range(1,4):
            x_okr[id1] =((2*pZ[ip+3]-2*pZ[ip+2])*(pZ[ip+2]*pZ[ip+2]-pZ[ip+1]*pZ[ip+1]+pX[ip + 2]*pX[ip+2]-pX[ip + 1]*pX[ip + 1])
            -(2*pZ[ip+2]-2*pZ[ip+1])*(pZ[ip+3]*pZ[ip+3]-pZ[ip+2]*pZ[ip+2]
            +pX[ip+3]*pX[ip+3]-pX[ip+2]*pX[ip+2]))/((2*pZ[ip+2]-2*pZ[ip+1])*(2*pX[ip+2]-2*pX[ip+3])-(2*pZ[ip+3]-2*pZ[ip+2])*(2*pX[ip+1]-2*pX[ip + 2]))
            z_okr[id1] = (pZ[ip + 2] * pZ[ip + 2] - pZ[ip + 1] * pZ[ip + 1]
                            + pX[ip + 2] * pX[ip + 2] - pX[ip + 1] * pX[ip + 1] + 2
                            * pX[ip + 1] * x_okr[id1] - 2 * pX[ip + 2] * x_okr[id1])/ (2 * pZ[ip + 2] - 2 * pZ[ip + 1])
            r_okr[id1] = ((pZ[ip + 1] - z_okr[id1])
                            * (pZ[ip + 1] - z_okr[id1]) + (pX[ip + 1] - x_okr[id1])
                            * (pX[ip + 1] - x_okr[id1]))**0.5
            ip += 3
        _delz=0
        for i in range(len(inX)):
            if i>0:
                _delz=_delz+_inZ[i]-_inZ[i-1]
            else:
                _delz=0
            if _delz>2:
                inD[i]=0
            kon=0
            _ymin = y_okr[3]
            _ymax = y_okr[4]
            ip = 4;
            while ((inY[i] < y_okr[ip - 1] and inY[i] < y_okr[ip]) or (inY[i] > y_okr[ip - 1] and inY[i] > y_okr[ip])) and kon == 0:
                if inY[i] > y_okr[ip - 1] and inY[i] > y_okr[ip] and kon == 0:
                    ip+=1
                    if ip == 5:
                        ip = 4
                        kon = 1

                if inY[i] < y_okr[ip - 1] and inY[i] < y_okr[ip] and kon == 0:
                    ip-=1
                    if ip == 0:
                        ip = 1
                        kon = 1
            _ymin = y_okr[ip - 1]
            _ymax = y_okr[ip]
            if ip==1:                
                delz = abs(pZ[11] - pZ[2])
                dely = abs(pY[11] - pY[2])
                _zmax = z_okr[1]
                _xmax = x_okr[1]
                _rmax = r_okr[1]
                _r_okr = _rmax
                _z_okr = _zmax
                _x_okr = _xmax
                D = 4* _z_okr* _z_okr- 4* (_z_okr * _z_okr + inX[i] * inX[i]- 2 * _x_okr * inX[i] + _x_okr* _x_okr - _r_okr * _r_okr)
                sqD = D**0.5
                if pZ[11] < pZ[2]:
                    inZ[i] = (2 * _z_okr + sqD) * 0.5- (delz * (pY[2] - inY[i])) / dely+ delz+_delz
                else:
                    inZ[i] = (2 * _z_okr + sqD) * 0.5+ (delz * (pY[2] - inY[i])) / dely+_delz
            elif ip==4:
                _zmin = z_okr[3]
                _xmin = x_okr[3]
                _rmin = r_okr[3]
                delz = abs(pZ[10] - pZ[8])
                dely = abs(pY[10] - pY[8])
                _r_okr = _rmin
                _z_okr = _zmin
                _x_okr = _xmin
                D = 4* _z_okr* _z_okr- 4* (_z_okr * _z_okr + inX[i] * inX[i]- 2 * _x_okr * inX[i] + _x_okr* _x_okr - _r_okr * _r_okr)
                sqD = D**0.5
                if pZ[10] < pZ[8]:
                        inZ[i] = (2 * _z_okr + sqD) * 0.5+ (delz * (pY[10] - inY[i])) / dely- delz+_delz
                else:
                        inZ[i] = (2 * _z_okr + sqD) * 0.5 - (delz * (pY[10] - inY[i])) / dely+ delz+_delz
            else:
                _zmax = z_okr[ip]
                _xmax = x_okr[ip]
                _rmax = r_okr[ip]
                _zmin = z_okr[ip - 1]
                _xmin = x_okr[ip - 1]
                _rmin = r_okr[ip - 1]
                _inek = (inY[i] - _ymin) / (_ymax - _ymin)
                _r_okr = _rmin + (_rmax - _rmin) * _inek
                _z_okr = _zmin + (_zmax - _zmin) * _inek
                _x_okr = _xmin + (_xmax - _xmin) * _inek
                D = 4* _z_okr* _z_okr- 4* (_z_okr * _z_okr + inX[i] * inX[i]- 2 * _x_okr * inX[i] + _x_okr* _x_okr - _r_okr * _r_okr)
                sqD = D**0.5
                inZ[i] = (2 * _z_okr + sqD) * 0.5+_delz
            
            inB[i]=0.3*math.atan(((-_x_okr+inX[i])*1)/(abs(_z_okr-inZ[i])))
            inC[i]=pi-abs(pZ[10]-pZ[11])/abs(pY[10]-pY[11])
                         
        
#----------------------------------------------
        Xmin=10000
        Ymin=10000
        Zmin=10000
        Xmax=-10000
        Ymax=-10000
        Zmax=-10000
        for i in range(1,int(len(inX))-1):
            if type(inZ[i])==complex:
                    inZ[i]=(inZ[i]).real
            if inX[i]>Xmax:
                Xmax=inX[i]
            if inX[i]<Xmin:
                Xmin=inX[i]
            if inY[i]>Ymax:
                Ymax=inY[i]
            if inY[i]<Ymin:
                Ymin=inY[i]
            if inZ[i]>Zmax:
                Zmax=inZ[i]
            if inZ[i]<Zmin:
                Zmin=inZ[i]
        Yq1=-0.5
        Yq2=0.5
        Xq1=-0.5
        Xq2=0.5  
        kx=abs(Yq1-Yq2)/abs(Ymax-Ymin)
        ky=abs(Xq1-Xq2)/abs(Xmax-Xmin)
        if kx<ky:
            k=kx
            Yq1=-0.5
            Yq2=0.5        
            Xq1=-k*(Xmax-Xmin)/2
            Xq2=-Xq1
        else:
            k=ky
            Xq1=-0.5
            Xq2=0.5        
            Yq1=-k*(Ymax-Ymin)/2
            Yq2=-Xq1
        
        Zq1=0
        Zq2=1
        offX=Xmin*k-Xq1
        offY=Ymin*k-Yq1
        offZ=Zmin*k-Zq1
        
        f1=open('output.txt','w')
        i1=0
        for i in range(len(inX)):
            i1+=1
            inV[i]=22
            
            if i>1 and i<len(inX)-2:
                x1=inX[i]
                y1=inY[i]
                x2=inX[i+1]
                y2=inY[i+1]
                rasst=((x2-x1)**2+(y2-y1)**2)**0.5
                if rasst<1.702 and rasst>1.698:
                    inD[i]=0.0
                if inZ[i]-inZ[i+1]<-4.9:
                    inD[i]=0.0
                    inV[i]=2
                if inZ[i+1]-inZ[i]<-4.9:
                    inD[i]=0.0
                    inV[i]=2
                    
            f1.write('  X '+str(round(inX[i],4))+', Y '+str(round(inY[i],4))+', Z '+str(round(inZ[i],4))+
                     ',  A '+str(round(inA[i],4))+', B '+str(round(inB[i],4))+', C '+str(round(inC[i],4))+
                     ', V '+str(round(inV[i],4))+', D '+str(round(inD[i],4))+', F '+str(round(inF[i]*0.23,4))+', S '+str(round(inS[i],4))+',                 \n')

        f1.write(' L'+str(i1)+',     \n')
        f1.write('q\n')
        f1.close()
        for i in range(int(len(inX)-1)):
            x1=inX[i]
            y1=inY[i]
            z1=inZ[i]
            #loordm.append([x1*k-offX,y1*k-offY,z1*k-offZ,inD[i]])
        #self.glWidget.koordList(loordm)
        #--------DEB-----------------------
        '''f = open('12.txt')
        file_str=f.readlines()
        len_f=len(file_str)
        kord=[]
        kord1=[0,0,0]
        for i in range(1,len_f):
            if len(file_str[i])>3:
                kord=file_str[i].split(' ')
                kord1.append(float(kord[1]))

        f = open('16.txt')
        file_str=f.readlines()
        len_f=len(file_str)
        kord=[]
        kord2=[]
        kord1=[[0],[0],[0],[0],[0]]
        for i in range(5,len_f):
            if len(file_str[i])>3:
                kord=file_str[i].split(' ')
                kord2=[]
                for i in range(len(kord)-1):
                    kord2.append(int(kord[i]))
                kord1.append(kord2)
        
        for i in range(5,len(inX)-3):
            x1=inX[i-4]
            y1=inY[i-4]
            x2=inX[i-3]
            y2=inY[i-3]
            rasst=((x1-x2)**2+(y1-y2)**2)**0.5
            obr=rasst/len(kord1[i])
            for i1 in range(len(kord1[i])):
                x1=x1+obr*(x2-x1)/rasst
                y1=y1+obr*(y2-y1)/rasst
                
                z1=kord1[i][i1]
                loordm.append([x1*k-offX,y1*k-offY,z1*k-offZ,inD[i],z1])
        d1=40
        
        for i in range(9,len(loordm)):
            d=loordm[i][4]
            #d1=d1+0.1*(d-d1)
            sp=[]
            sp.append(loordm[i-8][4])
            sp.append(loordm[i-7][4])
            sp.append(loordm[i-6][4])
            sp.append(loordm[i-5][4])
            sp.append(loordm[i-4][4])
            sp.append(loordm[i-3][4])
            sp.append(loordm[i-2][4])
            sp.append(loordm[i-1][4])
            sp.append(loordm[i][4])
            d1=fil_med(sp,2)
            #loordm[i][2]=d1*k-offZ'''
                
            
        self.glWidget.koordList(loordm)
class GLWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        
        self.object = 0
        self.xRot = 2200
        self.yRot = 0
        self.zRot = 1200
        self.offx=0.0
        self.offy=0.0
        self.lastPos = QPoint()
        self.zoom=0.6
        self.trolltechGreen = QColor.fromCmykF(1.0, 0.5, 0.5, 0.0)
        self.trolltechGreen1 = QColor.fromCmykF(1.0, 0.7, 0.7, 0.0)
        self.trolltechRed = QColor.fromCmykF(0.0, 1.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.0, 0.0, 0.0, 0.0)
        self.l2=[]
    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):
        #print(self.getOpenglInfo())

        self.setClearColor(self.trolltechPurple)
        #self.object = self.makeObject()
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        self.resizeGL(400,400)
    def koordList(self,l1):
        self.l2=l1
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0,0.0,-10.0)
        gl.glScalef(self.zoom,self.zoom,1)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glLineWidth(1.0)
        gl.glBegin(gl.GL_LINES)
        self.setColor(self.trolltechGreen)
        for i in range(1,len(self.l2)):
            if self.l2[i-1][3]==1:
                self.setColor(self.trolltechGreen)
            else:
                self.setColor(self.trolltechRed)
            gl.glVertex3d(self.l2[i-1][0]+self.offx, self.l2[i-1][1]+self.offy, self.l2[i-1][2])
            gl.glVertex3d(self.l2[i][0]+self.offx, self.l2[i][1]+self.offy, self.l2[i][2])
        gl.glEnd()
        gl.glEndList()
        gl.glCallList(genList)

        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glPointSize(1.8)
        gl.glBegin(gl.GL_POINTS)
        self.setColor(self.trolltechGreen1)
        
        for i in range(1,len(self.l2)):
            gl.glVertex3d(self.l2[i-1][0]+self.offx, self.l2[i-1][1]+self.offy, self.l2[i-1][2])
            gl.glVertex3d(self.l2[i][0]+self.offx, self.l2[i][1]+self.offy, self.l2[i][2])
        gl.glEnd()
        gl.glEndList()
        gl.glCallList(genList)
        self.update()

        

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
    def wheelEvent(self, event):
        wheelcounter = event.angleDelta()
        if wheelcounter.y() / 120 == -1:
            if self.zoom<0.2:
                self.zoom==self.zoom
            else:
                self.zoom*=0.7
        elif wheelcounter.y() / 120 == 1:
            self.zoom*=1.3
        self.update()
    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            #self.setYRotation(self.yRot + 8 * dx)
            self.setZRotation(self.zRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.offx+=dx/360#зависит от угла и масштаба ещё
            self.offy+=dy/360

        self.lastPos = event.pos()
        self.update()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.setColor(self.trolltechGreen)

        gl.glVertex3d(x1, y1, -0.5)
        gl.glVertex3d(x2, y2, -0.5)
        gl.glVertex3d(x3, y3, -0.5)
        gl.glVertex3d(x4, y4, -0.5)

        gl.glVertex3d(x4, y4, +0.05)
        gl.glVertex3d(x3, y3, +0.05)
        gl.glVertex3d(x2, y2, +0.05)
        gl.glVertex3d(x1, y1, +0.05)


    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())  
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ex11()
    window.show()
    sys.exit(app.exec_())
