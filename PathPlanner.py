import numpy as np
import random
from Viewer3D_GL import Paint_in_GL, Point3D, PrimitiveType,GLWidget,QtWidgets
import sys

from polygon import Mesh3D, Polygon3D

def rotate_point(x: float, y: float, alfa: float):
    x_r = x * np.cos(alfa) - y * np.sin(alfa)
    y_r = x * np.sin(alfa) + y * np.cos(alfa)
    return x_r, y_r

def rotate_list_points(points: "list[Point3D]", alfa: float):
    rotated_points = []
    for i in range(len(points)):
        p_r_x, p_r_y = rotate_point(points[i].x, points[i].y, alfa)
        point_rot = Point3D(p_r_x, p_r_y, points[i].z)
        rotated_points.append(point_rot)
    return rotated_points                

def plane_equation (normal: Point3D, vector_x: Point3D, point: Point3D):
    x1 = normal.x + point.x
    y1 = normal.y+ point.y
    z1 = normal.z + point.z
    x2 = vector_x.x + point.x
    y2 = vector_x.y + point.y
    z2 = vector_x.z + point.z
    x3 = point.x
    y3 = point.y
    z3 = point.z
    znamenatel = x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1
    if znamenatel == 0:
        #print("znam==0")
        return Point3D(0,0,1)
    else:
        x = -(y1*z2-y2*z1-y1*z3+y3*z1+y2*z3-y3*z2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)

        y = (x1*z2-x2*z1-x1*z3+x3*z1+x2*z3-x3*z2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)

        z = -(x1*y2-x2*y1-x1*y3+x3*y1+x2*y3-x3*y2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)
        #print("znam==1")
        return Point3D(x,y,z)

def correct_normal(normal: Point3D, vector_x: Point3D, point: Point3D):
    n = plane_equation (normal, vector_x, point)
    A = n.x
    B = n.y
    C = n.z
    D = 1
    ax = vector_x.x#hhh
    ay = vector_x.y
    az = vector_x.z 
    
    by = -(A*az - C*ax - D*ax + D*az)/(A*ay-A*az-B*ax+B*az+C*ax-C*ay)
    bz = (D*ax-A*ay*by+B*ax*by)/(A*az-C*ax)
    bx = -(ay*by+az*bz)/ax

    return Point3D(bx, by, bz).normalyse()

def correct_normal_cross(normal: Point3D, vector_x: Point3D):
    y = (normal*vector_x).normalyse()
    n = (vector_x*y).normalyse()
    return n

def distance(p1: Point3D, p2: Point3D):
    dist3 = (p1.x-p2.x)**2+(p1.y-p2.y)**2+(p1.z-p2.z)**2
    return np.sqrt(dist3)

def area_around_point(mesh: Mesh3D, p: Point3D, r_area: float):
    polygons_array = []
    for i in range (len(mesh.polygons)):
        dist = distance(p, mesh.polygons[i].vert_arr[0])
        if dist < r_area:
            polygons_array.append(mesh.polygons[i]) 
    return polygons_array

def comp_normal_in_area(pol_list: "list[Polygon3D]"):
    if pol_list != None:
        if len(pol_list) != 0:
            sum_norm = Point3D(0, 0, 0)
            for i in range (len(pol_list)):
                sum_norm += pol_list[i].n
            return sum_norm.normalyse()
        else:
            return Point3D(0, 0, 1)
    else:
        return Point3D(0, 0, 1)

def createFrame(matrix,dim:float):
    p1 = Point3D(matrix[0][3],matrix[1][3],matrix[2][3])
    p2 = Point3D(dim*matrix[0][0],dim*matrix[0][1],dim*matrix[0][2])
    p3 = Point3D(dim*matrix[1][0],dim*matrix[1][1],dim*matrix[1][2])
    p4 = Point3D(dim*matrix[2][0],dim*matrix[2][1],dim*matrix[2][2])
    ps = []
    ps.append(p1) 
    ps.append(p1+p2)
    ps.append(p1) 
    ps.append(p1+p3)
    ps.append(p1) 
    ps.append(p1+p4) 
    return ps

def computeYvector(rx:Point3D,rz:Point3D):
    x = rz.y*rx.z-rz.z*rx.y
    y = rz.z*rx.x-rz.x*rx.z
    z = rz.x*rx.y-rz.y*rx.x
    return Point3D(x,y,z)

def computeXvector(p1:Point3D,p2:Point3D):
    pd = p2-p1
    pd = pd.normalyse()
    return pd

def computeXvectorRob(normal:Point3D):
    vector_x =  Point3D(-1,0,0)
    y = (normal*vector_x).normalyse()
    x = (y*normal).normalyse()

    return x



def matrix_of_rotation(traj:"list[Point3D]",normals:"list[Point3D]", mesh: Mesh3D):
    matr_arr = []
    for i in range(len(traj)):
        rx = computeXvectorRob(normals[i])
        rz = correct_normal_cross(normals[i], rx)
        ry = (rz*rx).normalyse()
        matr = [[rx.x,rx.y,rx.z,traj[i].x],[ry.x,ry.y,ry.z,traj[i].y],[rz.x,rz.y,rz.z,traj[i].z],[0,0,0,1]]
        matr_arr.append(matr)
    return matr_arr

def projection(mesh: Mesh3D, traj: Mesh3D, zet: float, r:float,g:float,b:float)->"tuple[list[Point3D],list[Point3D]]":
    traj_proj_arr_:list[Point3D] = []
    traj_proj_arr_n:list[Point3D] = []
    for i in range (len(traj.polygons)):
        p,n = point_on_triangle(mesh, traj.polygons[i])
        p.z+= zet
        p.r = r
        p.g = g
        p.b = b
        traj_proj_arr_.append(p)
        traj_proj_arr_n.append(n)
    return traj_proj_arr_,traj_proj_arr_n

def point_on_triangle(mesh: Mesh3D, polygon: Polygon3D)->"tuple[Point3D,Point3D]":
    p = polygon.vert_arr[0]
    for i in range (len(mesh.polygons)):
        detect = mesh.polygons[i].affilationPoint(p)
        if detect == True:
            return mesh.polygons[i].project_point(p), mesh.polygons[i].n
    

def GenerateContour(n: int,rad:float,delt:float)->"list[Point3D]":
    step = 2*np.pi/n
    a = 0
    contour = []
    for a in range (n):
        l = random.uniform(rad,rad+delt)
        x = l*np.cos(a*step)
        y = l*np.sin(a*step)
        contour.append(Point3D(x, y, 0))
    return contour

def divideTraj(s: "list[Point3D]", step: float)->"list[Point3D]":
    cont_traj = []
    for i in range(len(s)-1):
        cont_traj.append(s[i])
        dist2 = (s[i+1].x-s[i].x)**2+(s[i+1].y-s[i].y)**2+(s[i+1].z-s[i].z)**2
        dist = np.sqrt(dist2)
        
        if(2*dist>step):
            n = int(dist/step)
            for j in range(n):
                x = s[i].x +(step*j*(s[i+1].x - s[i].x))/dist
                y = s[i].y +(step*j*(s[i+1].y - s[i].y))/dist
                z = s[i].z +(step*j*(s[i+1].z - s[i].z))/dist
                cont_traj.append(Point3D(x,y,z))

    return cont_traj

def filterTraj(s: "list[Point3D]", filt: float)->"list[Point3D]":
    cont_traj = []
    for i in range(len(s)-1):
        dist2 = (s[i+1].x-s[i].x)**2+(s[i+1].y-s[i].y)**2+(s[i+1].z-s[i].z)**2
        dist = np.sqrt(dist2)      
        if(dist>filt):
            cont_traj.append(s[i])
    return cont_traj

def FindPoints_for_line(contour: "list[Point3D]", y: float):
    p1: Point3D
    p2: Point3D
    ps: list[Point3D]
    ps = []
    for i in range(0, len(contour)):
        if((y >= contour[i].y and y <contour[i-1].y or (y >= contour[i-1].y and y <contour[i].y))):
            ps.append(contour[i-1] ) 
            ps.append(contour[i] ) 
    #print(len(ps))
    if(len(ps)>3):
        
        if(ps[0].x<ps[2].x):
            return ps
        else:
            ps2: list[Point3D]
            ps2 = []
            ps2.append(ps[2])
            ps2.append(ps[3])
            ps2.append(ps[0])
            ps2.append(ps[1])
            return ps2
    else:
        return []


def FindCross_for_line(p: "list[Point3D]" ,y: float):

    x = p[0].x+(p[1].x-p[0].x)*(y-p[0].y)/(p[1].y-p[0].y)
    p1 = Point3D(x,y,0)

    x = p[2].x+(p[3].x-p[2].x)*(y-p[2].y)/(p[3].y-p[2].y)
    p2 = Point3D(x,y,0)
    return p1,p2
            


def GeneratePositionTrajectory_angle(contour: "list[Point3D]", step: float, alfa: float):
    contour_rotate = rotate_list_points(contour, alfa)
    traj = GeneratePositionTrajectory(contour_rotate, step)
    traJ_rotate = rotate_list_points(traj, -alfa)
    return traJ_rotate

def GeneratePositionTrajectory(contour: "list[Point3D]", step: float):
    # нахождение нижней точки
    y_min:float = 10000.
    i_min = 0.
    y_max:float = -10000.
    i_max = 0.
    for i in range(len(contour)):
        if(contour[i].y < y_min):
            y_min = contour[i].y
            i_min = i
        if(contour[i].y>y_max):
            y_max = contour[i].y
            i_max = i
    p_min = contour[i_min]
    p_max = contour[i_max]
    traj = []
    #добавление линии
    y = p_min.y
    flagRL = 0
    while y<p_max.y:
        ps = FindPoints_for_line(contour,y)
        if(len(ps)==4) and flagRL == 0:
            p1,p2 = FindCross_for_line(ps,y)
            traj.append(p2)
            traj.append(p1)
            flagRL =1
        elif(len(ps)==4) and flagRL == 1:
            p1,p2 = FindCross_for_line(ps,y)
            traj.append(p1)
            traj.append(p2)
            flagRL =0
    
        y+=step

    #for i in range(len(traj)):
        #print(str(traj[i].x)+" "+str(traj[i].y)+" "+str(traj[i].z)+" ")
    #добавление точки слева
    return traj

   
def pass_array(array, x_w, y_w):
    row_len = len(array)
    col_len = len(array[0])
    mov_aver_array = empty_ar(row_len, col_len)
    
    for i in range (0,row_len-x_w+1):
        for j in range (0,col_len-y_w+1):
            mov_aver_array[i][j] = eval_aver_array(take_small_window(array, x_w, y_w, i, j))
    return mov_aver_array       


def take_small_window(ar, x_w, y_w, x_st, y_st):
    tiny_arr = empty_ar(x_w, y_w)
    for i in range(0,x_w):
        for j in range(0,y_w):
            tiny_arr[i][j] = ar[i+x_st][j+y_st]
    return tiny_arr
#_________________________________________________________________
# ищет количество столбцов и строк двухмерного массива
def size_of_2dim_array(array):
    return len(array), len(array[0])

def cut_array(array, offset):
    row_len, col_len  = size_of_2dim_array(array) # ищет количество столбцов и строк двухмерного массива
    cutted_array = empty_ar(row_len - 2*offset, col_len - 2*offset) # создаем пустой вырезанный массив
    cutted_row, cutted_col = size_of_2dim_array(cutted_array)
    for i in range (0, cutted_row):
        for j in range(0, cutted_col):
            cutted_array[i][j] = array[i+offset][j+offset]
    return cutted_array 

#нужна для прохождения массива без краёв, которые неизвестны (центр ядра)    
#на вход - массив, размеры окна, возвращает - сглаженный массив
def pass_array_center(array, x_window, y_window):
    row_len, col_len  = size_of_2dim_array(array) #вычисляем размер входного массива
    offset_window_x = int((x_window - 1)/2) # расстояние от центра до края массива (ещё одна характеристика размеров окна)
    offset_window_y = int((y_window - 1)/2)
    mov_aver_array = empty_ar(row_len, col_len) # создаём пустой массив под средние
   
   #заполнение пустого массива средними:
   # начало и конец массива средних относительно несглаженного массива (отнимаем от количества строк и столбцов оффсеты)
   
    for i in range (offset_window_x,row_len-offset_window_x):
        for j in range (offset_window_y,col_len-offset_window_y):
            window = take_small_window_center(array, x_window, y_window, i, j)
            mov_aver_array[i][j] = eval_aver_array(window)
        print("i: "+str(i))
    
    return mov_aver_array      

# взять подмассив с размерами окна и центром в точке x_start, y_start из большого массива
def take_small_window_center(ar, x_window, y_window, x_start, y_start):
    offset_window_x = int((x_window - 1)/2) # расстояние от центра до края массива (ещё одна характеристика размеров окна)
    offset_window_y = int((y_window - 1)/2)
    tiny_arr = empty_ar(x_window, y_window)
    for i in range(0,x_window):
        for j in range(0,y_window):
            tiny_arr[i][j] = ar[i+x_start-offset_window_x][j+y_start-offset_window_y]
    return tiny_arr

# находим среднее арифметическое значений окна
def eval_aver_array(array):
    sum = 0
    for i in range(len(array)):
        for j in range(len(array[i])):
            sum = sum+array[i][j]
    size = len(array)*len(array[0])
    return float(sum)/float(size)

# создание пустого массива
def empty_ar(rows, columns):

    b = columns*[0.]
    ar = rows *[0.]
    for i in range(len(ar)):
        ar[i] = np.array(b)
    return np.array(ar)

# массив заполненный значениями k
def empty_ar_k(rows, columns, k):
    b = columns*[k]
    ar = rows *[k]
    for i in range(len(ar)):
        ar[i] = np.array(b)
    return np.array(ar)

#____________________________________________-



# принимает на вход размер ядра свёртки, возвращает массив координат сгенерированной зашумлённой повверхности, 
def surface(kernelSize:int = 3): 
    # function for Z values
    def f(x, y):
        noise = random.uniform(-5,5)
        noise = 0
        vyr =10+0.3*( 0.2*(((x**2)/20) - ((y**2)/4))+0.5*x+noise)
        #vyr  = 10.+0*x+0*y
        return vyr

    # x and y values
    #создаём "случайную" поверхность"
    x = np.linspace(-30, 30,20) # нижний предел, верхний предел, кол-во - с одинаковым шагом
    y = np.linspace(-30, 30, 20)

    X, Y = np.meshgrid(x, y)
  
    Z = f(X, Y)
    for i in range(len(X)):
        for j in range(len(X[0])):
            Z[i][j] = f(X[i][j], Y[i][j])

   # оффсет это отступ от краёв изначального массива 
   # для получения результирующего (после применения функции скользящего среднего) массива
    offset = int((kernelSize - 1)/2) 
    ar = pass_array_center(Z, kernelSize,kernelSize)
    X_cutted = cut_array(X, offset) # удаление невычисленных значений для соблюдения размеров массивов для построения пов-ти
    Y_cutted = cut_array(Y, offset)
    ar_cutted = cut_array(ar, offset)
    #Z_cutted = cut_array(Z, offset)
    #print("z0:" + str(Z[0][0]))
    #print("ar_cutted0:" + str(ar_cutted[0][0]))
    #сгенерированная сетка, сглаженная сетка
    return [X,Y,Z],[X_cutted,Y_cutted,ar_cutted]

def arrayViewer(X,Y,Z):
    koords = []
    for i in range(len(X)):
        for j in range(len(X[0])):
            koords.append([X[i][j],Y[i][j],Z[i][j],1])
    return koords

def arrayViewer_GL(X,Y,Z):
    koords:list[Point3D] = []
    for i in range(len(X)):
        for j in range(len(X[0])):
            koords.append(Point3D(X[i][j],Y[i][j],Z[i][j]))
    return koords

def arrayViewer_GL_2d(X,Y,Z,off_y:float = 0.)->"list[list[Point3D]]":
    koords:list[list[Point3D]] = []
    print("Z0:" + str(Z[0][0]))
    for i in range(len(X)):
        sub_koords: list[Point3D] = []
        for j in range(len(X[0])):
            sub_koords.append(Point3D(X[i][j],Y[i][j]+off_y,Z[i][j]))
        koords.append(sub_koords)
    return koords

def draw_frame(matr: "list[Point3D]", windowGL: GLWidget):
    points = createFrame(matr, 1)
    frame1 = Mesh3D( points[0:2] ,PrimitiveType.lines)
    frame2 = Mesh3D( points[2:4],PrimitiveType.lines)
    frame3 = Mesh3D( points[4:6] ,PrimitiveType.lines)

    windowGL.paint_objs.append(Paint_in_GL(0,1,1.0,4,PrimitiveType.lines,frame1))
    windowGL.paint_objs.append(Paint_in_GL(1.0,0,1.0,4,PrimitiveType.lines,frame2))
    windowGL.paint_objs.append(Paint_in_GL(1.0,1,0,4,PrimitiveType.lines,frame3))

def angles_of_extruder(list_of_matr: "list[list[list[float]]]"):
    list_of_angles = []
    for i in range (len(list_of_matr)):
        b = np.arcsin (list_of_matr[i][2][0])
        c = -np.arcsin((list_of_matr[i][2][1])/np.cos(b))
        a = np.arcsin((list_of_matr[i][1][0])/np.cos(b))
        list_of_angles.append([list_of_matr[i][0][3],list_of_matr[i][1][3], list_of_matr[i][2][3], a, b, c])
    return list_of_angles

def push_string(value_of_matr: "list[list[float]]"):
    full_str = ""
    for i in range (len(value_of_matr)):  
        for j in range (len(value_of_matr[i])):
            full_str += str(value_of_matr[i][j]) + " "
        full_str += "\n"
    return full_str

def ToStringList(cont:"list[Point3D]"):
        text = "___________\n"
        for i in range(len(cont)):
            text+=cont[i].ToString()+" \n"
        return text

def Generate_one_layer_traj (contour: "list[Point3D]", step: float, alfa: float, surface: Mesh3D, div_step: float, zet: float, trans: float, r:float,g:float,b:float):
    
    traj = GeneratePositionTrajectory_angle(contour, step, alfa)
    div_tr = divideTraj(traj, div_step)
    fil_tr = divideTraj(div_tr, div_step/2)

    mesh3d_1 = Mesh3D(fil_tr,PrimitiveType.lines)
    
    proj_traj,normal_arr = projection(surface,  mesh3d_1, zet,r,g,b)
    proj_traj[0].z += trans
    proj_traj[-1].z += trans
    proj_traj[0].extrude = False
    proj_traj[1].extrude = False
    proj_traj[-1].extrude = False

    matrs =  matrix_of_rotation(proj_traj,normal_arr, surface)
    return  proj_traj,normal_arr, matrs

def filResTraj(filt:float,proj_traj: "list[Point3D]",normal_arr,matrs):
    proj_traj_f = []
    normal_arr_f = []
    matrs_f = []
    proj_traj_f.append(proj_traj[0])
    normal_arr_f.append(normal_arr[0])
    matrs_f.append(matrs[0])
    for i in range(1,len(proj_traj)):
        dist = distance( proj_traj_f[-1],proj_traj[i])
        if dist>filt:
            proj_traj_f.append(proj_traj[i])
            normal_arr_f.append(normal_arr[i])
            matrs_f.append(matrs[i])

    return proj_traj_f,normal_arr_f, matrs_f
        


def Generate_multiLayer (contour: "list[Point3D]", step: float, alfa: float, surface: Mesh3D, div_step: float, zet: float, amount: int, trans: float):
    colors = [[0.,0.5,0.5],[1.,0.5,0.5],[0.,1.0,0.5],[0.,0.5,1.0],[0.,0.5,0.5],[0.,0.5,0.5],[0.,0.5,0.5],[0.,0.5,0.5]]
    proj_traj:"list[Point3D]" = []
    normal_arr = []
    matrs = []
    
    for i in range (amount):
        alfa2 = alfa
        if i % 2 == 0:
            alfa2 += np.pi/2
        p, n, m = Generate_one_layer_traj (contour, step, alfa2, surface, div_step, zet*(i+1), trans,colors[i][0],colors[i][1],colors[i][2])
        proj_traj += p
        normal_arr += n
        matrs += m
        
    return filResTraj(step/2,proj_traj,normal_arr, matrs)

def saveTrajTxt(traj:"list[Point3D]",list_of_matr: "list[list[list[float]]]",name:str):
    f1=open(name+'.txt','w')
    i1=0
    v = 20
    for i in range(len(traj)):
        x = traj[i].x
        y = traj[i].y
        z = traj[i].z
        b = np.arcsin (list_of_matr[i][2][0])
        a = 0
        c = 0
        if np.cos(b)!=0:
            c = -np.arcsin((list_of_matr[i][2][1])/np.cos(b))
            a = np.arcsin((list_of_matr[i][1][0])/np.cos(b))

        e = 0
        if  traj[i].extrude:
            e = 1

        f1.write('  X '+str(round(x,4))+', Y '+str(round(y,4))+', Z '+str(round(z,4))+
                    ',  A '+str(round(a,4))+', B '+str(round(b,4))+', C '+str(round(c,4))+
                    ', V '+str(round(v,4))+', D '+str(round(e,4))+'  \n')

    f1.write('q\n')
    f1.close()

def initWind(window:GLWidget):
    # позволяет оконному приложени работать (почитать про это)
    #koords = arrayViewer_GL(x,y,z)   
    #window.paint_objs.append(Paint_in_GL(0,1,0,2,1,koords,PrimitiveType.lines))

    #orig,smooth1 = surface(3)
    orig,smooth2 = surface()
    #из трёх отдельных двухмерных массив создаём общий двухмерный масиив точек
    koords3 = arrayViewer_GL_2d(smooth2[0],smooth2[1],smooth2[2], 0)
    koordsorig = arrayViewer_GL_2d(orig[0],orig[1],orig[2], 30)
    
    #создание объектов из массива координат (расчет нормалей и создание треугольников)
    mesh3=  window.gridToTriangleMesh(koords3)
    mesh3d_surface = Mesh3D(mesh3,PrimitiveType.triangles)
    meshorig=  window.gridToTriangleMesh(koordsorig)
   

    cont = GenerateContour(20,5,3) 
    proj_traj,normal_arr, matrs = Generate_multiLayer(cont, 1., np.pi/2, mesh3d_surface, 1.3, 0.1, 2, 5)
    saveTrajTxt(proj_traj,matrs,"traj_test2")


  
    mesh3d_traj = Mesh3D(proj_traj,PrimitiveType.lines)
    window.paint_objs.append(Paint_in_GL(0.5,1,0.5,5,PrimitiveType.lines,mesh3d_traj))

    extruder_m = window.extract_coords_from_stl("extruder.stl")
    extruder_mesh = Mesh3D( extruder_m,PrimitiveType.triangles)
    #extruder_mesh.scaleMesh(0.01)
    extruder_mesh.invertMormals()
    extruder_mesh.setTransform(matrs[0])
    window.paint_objs.append(Paint_in_GL(0.5,0.5,0,1,PrimitiveType.triangles,mesh3d_surface))
    
    #glObjExtr = Paint_in_GL(0.2,0.2,0.2,1,PrimitiveType.triangles,extruder_mesh)
    #glObjExtr.matrs = matrs
    #window.paint_objs.append(glObjExtr)
    #window.paint_objs.append(Paint_in_GL(0.5,0.,0.5,1,PrimitiveType.triangles,mesh3d_orig))

    



