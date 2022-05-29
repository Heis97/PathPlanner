
import math
import enum


class PrimitiveType(enum.Enum):
    points = 1
    lines = 2
    triangles = 3

class Point3D(object):
    x:float = 0
    y:float = 0
    z:float = 0
    extrude:bool
    r:float = 0
    g:float = 0
    b:float = 0
    def __init__(self,_x:float,_y:float,_z:float,_extrude:bool = True,_r:float = 0.0,_g:float = 1.,_b:float =1.):
        self.x = _x
        self.y = _y
        self.z = _z
        self.r = _r
        self.g = _g
        self.b = _b
        self.extrude = _extrude

    def normalyse(self):
        mod = abs(self.x*self.x)+abs(self.y*self.y)+abs(self.z*self.z)
        norm = math.sqrt(mod)
        if norm!=0:
            self.x /=norm
            self.y /=norm
            self.z /=norm
        return Point3D(self.x,self.y,self.z,self.extrude)
    def ToString(self):
        return str(self.x)+" "+str(self.y)+" "+str(self.z)+" "+self.extrude

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point3D(x,y,z,self.extrude)

    def __sub__(self, other):
        x =  self.x- other.x
        y = self.y - other.y
        z = self.z - other.z
        #self.x-=other.x
        #self.y-=other.y
        #self.z-=other.z
        return Point3D(x,y,z,self.extrude)

    def Clone(self):
        return Point3D(self.x,self.y,self.z,self.extrude,self.r,self.g,self.b)

    def __mul__(self, other):
        if(type(other)==Point3D):
            return Point3D(self.y*other.z-self.z*other.y, self.z*other.x-self.x*other.z,self.x*other.y-self.y*other.x,self.extrude)
        else:
            return Point3D(self.x*other,self.y*other,self.z*other,self.extrude)
    def matrMul(self,matr:"list[list[float]]"):

        x = matr[0][0]*self.x + matr[0][1]*self.y + matr[0][2]*self.z+matr[0][3]
        y = matr[1][0]*self.x + matr[1][1]*self.y + matr[1][2]*self.z+matr[1][3]
        z = matr[2][0]*self.x + matr[2][1]*self.y + matr[2][2]*self.z+matr[2][3]
        return Point3D(x,y,z,self.extrude)
    

class Polygon3D(object):
    vert_arr:"list[Point3D] "
    n:Point3D
    def __init__(self,_vert_arr:"list[Point3D]"=None):
        if(_vert_arr!=None):
            self.n = None
            self.vert_arr = _vert_arr
            if (len(_vert_arr) > 2):
                self.n = self.compNorm(_vert_arr[0],_vert_arr[1],_vert_arr[2])

    def compNorm(self, p3:Point3D,p2:Point3D,p1:Point3D):
        v = p3-p1
        u = p2-p1
        v = v.normalyse()
        u = u.normalyse()
        '''Norm = Point3D(
            u.y * v.z - u.z * v.y,
            u.z * v.x - u.x * v.z,
            u.x * v.y - u.y * v.x)'''
        Norm = u*v
        Norm.normalyse()
        return Point3D(Norm.x,Norm.y,Norm.z)
    
    def matrMul(self,matr:"list[list[float]]"):
        for i in range(len(self.vert_arr)):
            self.vert_arr[i] = self.vert_arr[i].matrMul(matr)
        return self
    
    def affilationPoint(self, p: Point3D):
        if (len(self.vert_arr)<3):
            return False
        a = self.vert_arr [0].Clone()
        b = self.vert_arr [1].Clone()
        c = self.vert_arr [2].Clone()
        p = p.Clone()
        p = p - a
        b = b - a
        c = c - a

        m =  (p.x*b.y - b.x*p.y)/(c.x*b.y - b.x*c.y)
        if(m >=0 and m <=1):
            l = (p.x - m*c.x)/b.x
            if (l >=0 and m+l <=1):
                return True
        return False

    def project_point(self,p: Point3D):
        p1 = self.vert_arr [0]
        d = -(self.n.x*p1.x + self.n.y*p1.y + self.n.z*p1.z)
        z = (-d - self.n.x*p.x- self.n.y*p.y)/self.n.z
        return Point3D(p.x, p.y, z)

    def __mul__(self, other):
        if(type(other)==float):
            for i in range(len(self.vert_arr)):
                self.vert_arr[i]*=other
            return self
    def Clone(self):
        vert = []
        norm = self.n.Clone()
        for i in range(len(self.vert_arr)):
            vert.append(self.vert_arr[i].Clone())
        copy = Polygon3D()
        copy.vert_arr = vert
        copy.n = norm
        return copy
    def matrMul(self,matr:"list[list[float]]"):
        copy = self.Clone()
        for i in range(len(self.vert_arr)):
             copy.vert_arr[i] = self.vert_arr[i].matrMul(matr)
        return  copy
    

class Mesh3D(object):
    polygons:"list[Polygon3D]" = []

    def __init__(self,_points:"list[Point3D]"=None, prim_type: PrimitiveType=None):
        self.polygons = []
        if _points!=None:
            if (prim_type == PrimitiveType.points ):
                
                for i in range (len(_points)):
                    vert_array = []
                    vert_array.append(_points[i])
                    self.polygons.append(Polygon3D(vert_array))

            elif (prim_type == PrimitiveType.lines):
                for i in range (len(_points)-1):
                    vert_array = []
                    vert_array.append(_points[i])
                    vert_array.append(_points[i+1])
                    self.polygons.append(Polygon3D(vert_array)) 

            elif (prim_type == PrimitiveType.triangles):
                for i in range (int(len(_points)/3)):
                    vert_array = []
                    vert_array.append(_points[3*i])
                    vert_array.append(_points[3*i+1])
                    vert_array.append(_points[3*i+2])
                    self.polygons.append(Polygon3D(vert_array))
    
    def scaleMesh(self,sc:float):
        for i in range(len(self.polygons)):
            self.polygons[i]*=sc
        return self
    def invertMormals(self):
        for i in range(len(self.polygons)):
            self.polygons[i].n*=-1
        return self
    def Clone(self):
        polygons = []
        for i in range(len(self.polygons)):
            polygons.append(self.polygons[i])
        copy = Mesh3D()
        copy.polygons = polygons
        return copy
    def setTransform(self,matr:"list[list[float]]"):
        copy = self.Clone()
        for i in range(len(copy.polygons)):
            copy.polygons[i] = self.polygons[i].matrMul(matr)
        return copy

        

        
       