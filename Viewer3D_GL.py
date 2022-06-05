#from socket import *

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton,QSlider, QLineEdit, QOpenGLWidget,QTextEdit,
    QInputDialog, QApplication,QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint,QPointF, QSize,
        Qt, QTime, QTimer)
import OpenGL.GL as gl
from matplotlib.backend_bases import MouseEvent

from polygon import Mesh3D, Point3D,PrimitiveType

class Paint_in_GL(object):
    glList = None
    matrs:"list[list[list[float]]]" = None
    red = 0.
    green = 0.
    blue = 0.
    size = 1.
    alpha = 1
    norm:"list[Point3D]" = None
    obj_type:PrimitiveType
    points:"list[Point3D]"
    p2 = []
    p3 = []
    mesh_obj: Mesh3D = None
    def __init__(self, _red,  _green,  _blue,_size,_type:PrimitiveType,  _mesh_obj:Mesh3D):
        self.red = _red
        self.green = _green
        self.blue = _blue
        self.size = _size
        self.obj_type = _type
        self.mesh_obj = _mesh_obj

    def setTrasform(self,matr:"list[list[float]]"):
        trans_mesh = self.mesh_obj.setTransform(matr)
        return trans_mesh

    #сохранить stl
    def save(self,name:str):
        if(len(self.points)==0 or len(self.norm)==0 or self.obj_type != PrimitiveType.triangles):
            return
        text = "solid\n"
        n_i = 0
        print(len(self.points))       
        for i in range(int (len(self.points)/3)):
            #print(i)
            text+="facet normal "+str(self.norm[n_i].x)+" "+str(self.norm[n_i].y)+" "+str(self.norm[n_i].z)+"\n "
            text+="outer loop\n"
            text+="vertex "+str(self.points[i*3].x)+" "+str(self.points[i*3].y)+" "+str(self.points[i*3].z)+"\n "
            text+="vertex "+str(self.points[i*3+1].x)+" "+str(self.points[i*3+1].y)+" "+str(self.points[i*3+1].z)+"\n "
            text+="vertex "+str(self.points[i*3+2].x)+" "+str(self.points[i*3+2].y)+" "+str(self.points[i*3+2].z)+"\n "
            text+="endloop\n"
            text+="endfacet \n"            
            n_i+=1
        text += "endsolid\n"
        f = open(name+'.stl', 'w')
        f.write(text)
        f.close()
        
class GLWidget(QOpenGLWidget):
    paint_objs:"list[Paint_in_GL]"  = []
    cont_select:bool = False
    rot:bool = True
    trans:bool = True
    cont:"list[Point3D]" = None
    render_count = 0
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        format = self.format()
        format.setSamples(8)
        
        self.setFormat(format)
        self.object = 0
        self.xRot = 2200
        self.yRot = 0
        self.zRot = 1200
        self.off_x=0.0
        self.off_y=0.0
        self.lastPos = QPoint()
        self.zoom=1
        self.trolltechGreen = QColor.fromCmykF(1.0, 0.5, 0.5, 0.0)
        self.trolltechGreen1 = QColor.fromCmykF(1.0, 0.7, 0.7, 0.0)
        self.trolltechRed = QColor.fromCmykF(0.0, 1.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.0, 0.0, 0.0, 0.0)
        self.l2=[]
        self.w = 1000
        self.h = 1000

    def setXY(self):
        self.xRot = 0#2200
        self.yRot = 0
        self.zRot = 0#1200
        self.off_x=0.0
        self.off_y=0.0
        self.zoom=100
    def initializeGL(self):
        self.setClearColor(self.trolltechPurple)
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_MULTISAMPLE)    
        

        #gl.glEnable(gl.GL_CULL_FACE) 
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        lightPower = 1000.
        lightZeroPosition = [0.,0.,100.,1.]
        lightZeroColor = [lightPower,lightPower,lightPower,1.0] 
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightZeroPosition)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, lightZeroColor)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.05)
        
        #gl.glDisable(gl.GL_LIGHTING)
        #gl.glDisable(gl.GL_LIGHT0)
        self.resizeGL(self.w,self.h)
        self.getOpenglInfo()
       
    def initPaint_in_GL(self,  paint_gls: Paint_in_GL):

        
        mesh_obj = paint_gls.mesh_obj
        if(paint_gls.matrs!=None):
            ind_m = self.render_count % len(paint_gls.matrs)
            mesh_obj = paint_gls.setTrasform(paint_gls.matrs[ind_m])
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)  
        v = paint_gls
        gl.glLineWidth(v.size)
        gl.glPointSize(10*v.size)
        color = QColor.fromCmykF(v.red, v.green, v.blue, 0.0)
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_DIFFUSE, (v.red, v.green, v.blue))
        self.setColor(color)
        if v.obj_type == PrimitiveType.points:
            gl.glBegin(gl.GL_POINTS)
            len_points = len(v.mesh_obj.polygons)
            for j in range(len_points):  
                p2 = v.mesh_obj.polygons[j].vert_arr[0] 
                gl.glVertex3d(p1.x,p1.y,p1.z)
                gl.glNormal3d(0.5, 0.5, 0.5)
            gl.glEnd()

        elif v.obj_type == PrimitiveType.lines:
            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glLineStipple(2,58360)
            gl.glBegin(gl.GL_LINES)
                
            len_points = len(v.mesh_obj.polygons)
            for j in range(len_points):
                
                p1 = v.mesh_obj.polygons[j].vert_arr[0]  
                p2 = v.mesh_obj.polygons[j].vert_arr[1] 
                color1 = QColor.fromCmykF(p2.r, p2.g, p2.b, 0.0)
                self.setColor(color1)
                if p2.extrude == False:
                    color1 = QColor.fromCmykF(1., 0., 0., 0.0)
                    self.setColor(color1)
                    #gl.glEnable(gl.GL_LINE_STIPPLE)                           
                    
                    #gl.glDisable(gl.GL_LINE_STIPPLE) 
                gl.glVertex3d(p1.x,p1.y,p1.z)
                gl.glVertex3d(p2.x,p2.y,p2.z)
                gl.glNormal3d(0.5, 0.5, 0.5)
            gl.glEnd()
        
        elif v.obj_type == PrimitiveType.triangles:
            gl.glEnable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_LIGHT0)
            gl.glBegin(gl.GL_TRIANGLES)
            
            len_points = len(mesh_obj.polygons)
            for j in range(len_points):   
                p1 = mesh_obj.polygons[j].vert_arr[0]  
                p2 = mesh_obj.polygons[j].vert_arr[1] 
                p3 = mesh_obj.polygons[j].vert_arr[2]   
                n = mesh_obj.polygons[j].n
                if(n !=None):        
                    gl.glNormal3d(n.x, n.y, n.z)
                gl.glVertex3d(p1.x,p1.y,p1.z)
                gl.glVertex3d(p2.x,p2.y,p2.z)
                gl.glVertex3d(p3.x,p3.y,p3.z)
            
            gl.glEnd()
            gl.glDisable(gl.GL_LIGHTING)
            gl.glDisable(gl.GL_LIGHT0)  

        gl.glEndList()

        return genList
            
    def GL_paint(self,  paint_gls: "list[Paint_in_GL]"):
        for i in range(len(paint_gls)):
            if paint_gls[i].glList==None:
                paint_gls[i].glList = self.initPaint_in_GL(paint_gls[i])
            gl.glCallList(paint_gls[i].glList)


    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        
        
        gl.glTranslated(self.off_x, self.off_y,-10.)
        gl.glRotated(self.xRot, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot, 0.0, 0.0, 1.0)
        gl.glScalef(self.zoom,self.zoom,self.zoom)
        self.render_count+=1

        self.GL_paint(self.paint_objs)

        self.update()
    def extract_coords_from_stl(self,stl_file):
        result = []
        coords = []

        for l in open(stl_file):
            l = l.split()
            if l[0] == 'facet':
                result.append(list(map(float, l[-3:])))
            elif l[0] == 'vertex':
                vert = list(map(float, l[-3:]))
                result[-1] += vert
                coords.append(Point3D(vert[0],vert[1],vert[2]))
        return coords
    def getOpenglInfo(self):
        
        #print() 
        print(gl.glGetString(gl.GL_RENDERER))


    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(1200, 800)

    def compNorm(self, p1:Point3D,p2:Point3D,p3:Point3D):
        u = Point3D(p3.x-p1.x,p3.y-p1.y,p3.z-p1.z)
        v = Point3D(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
        #print("u: "+str(u.x)+" "+str(u.y)+" "+str(u.z)+" ")
        #print("v: "+str(v.x)+" "+str(v.y)+" "+str(v.z)+" ")
        Norm = Point3D(
            u.y * v.z - u.z * v.y,
            u.z * v.x - u.x * v.z,
            u.x * v.y - u.y * v.x)
        #print("Norm.x: "+str(Norm.x))
        Norm.normalyse()
        #print("norm: "+str(Norm.x)+" "+str(Norm.y)+" "+str(Norm.z)+" ")
        return Norm

    def gridToTriangleMesh(self,points2d:"list[list[Point3D]]"):
        points1d:list[Point3D] = []
        
        for i in range(len(points2d)-1):
            for j in range(len(points2d[0])-1):

                points1d.append( points2d[i][j+1])
                points1d.append(points2d[i][j])
                points1d.append(points2d[i+1][j])

                points1d.append(points2d[i+1][j])
                points1d.append(points2d[i+1][j+1])
                points1d.append(points2d[i][j+1])

        return points1d

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)
        scale = 1.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-width/ scale , width/ scale , -height/ scale , height/ scale , -20000., 50000.0)
        
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def wheelEvent(self, event):
        wheelcounter = event.angleDelta()
        if wheelcounter.y() < 0 :
            if self.zoom<0.02:
                pass
            else:
                self.zoom*=0.7
        elif wheelcounter.y() > 0:
            self.zoom/=0.7
        print(self.zoom)
        self.update()
    
    def mousePressEvent(self, event:QMouseEvent):
        self.lastPos = event.pos()
        if self.cont_select:
            pf = self.toSurfCoord(self.lastPos)
            self.cont.append(Point3D(pf.x(),pf.y(),0))

    def mouseMoveEvent(self, event:QMouseEvent):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if (event.buttons() & Qt.LeftButton) and self.rot:
            self.xRot += dy
            self.zRot += dx
        if (event.buttons() & Qt.RightButton) and self.trans:
            self.off_x+=2*dx
            self.off_y-=2*dy

        self.lastPos = event.pos()
        self.update()

    def toSurfCoord(self,p_widg:QPoint):
        scale = 2/(self.zoom)
        #print(str(p_widg.x())+" "+str(p_widg.y()))
        #print(str((p_widg.x()-self.w/2)*scale)+" "+str((p_widg.y()-self.h/2)*scale))
        x = (p_widg.x()-self.w/2)*scale
        y = -(p_widg.y()-self.h/2)*scale
        return QPointF(x,y)

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


