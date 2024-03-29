from ntpath import join
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import shutil 
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], ".."))

def sin_line(x, b, a, c,off):
    return b + (a * np.sin(c * (x-off)))



def smooth(x,y,n_add):
    k = 5
    x_p = [x[n_add-k],x[n_add],x[n_add+k]]
    y_mid_new = (((y[n_add-k] + y[n_add+k])/2) + y[n_add])/2
    y_p = [y[n_add-k],y_mid_new,y[n_add+k]]
    
    x_new = np.linspace(x[n_add-k],x[n_add+k],2*k)
    y_new = interp1d(x_p,y_p,kind='quadratic')(x_new)

    x[n_add-k:n_add+k] = x_new
    y[n_add-k:n_add+k] = y_new
    return x,y

def build_arrays(p1, p2, p3):


    x = np.linspace(0, 3, 180)
    # p1 = 0.25 # 0.1 <-> 0.4
    # p2 = 5    # 3 <-> 6

    if p1 > 0.70:
        print("--- You have entered an invalid geometry ---")
        print("The value of p1 is too high (", p1, "> 0.70 )")
        return

    if p1 < 0.1:
        print("--- You have entered an invalid geometry ---")
        print("The value of p1 is too low (", p1, "< 0.1 )")
        return

    if p2 < 3:
        print("--- You have entered an invalid geometry ---")
        print("The value of p2 is too low (", p2, "< 3 )")
        return

    if p2 > 6:
        print("--- You have entered an invalid geometry ---")
        print("The value of p2 is too high (", p2, "> 6 )")
        return
    
    if p3 < 0:
        print("--- You have entered an invalid geometry ---")
        print("The value of p3 is too low (", p3, "< 0 )")
        return 

    if p3 > np.pi/2:
        print("--- You have entered an invalid geometry ---")
        print("The value of p3 is too high (", p3, "> pi/2 )")
        return 

    y1 = sin_line(x, 0.5, p1, p2,p3)
    y2 = sin_line(x, 0.0, 0.25, p2,p3)

    x1 = x 
    x2 = x
    n_add = 19
    add_start_x = list(np.linspace(x1[0]-0.5,x1[0],n_add,endpoint=False))
    add_end_x = list(np.flip(np.linspace(x1[-1]+0.5,x1[-1],n_add,endpoint=False)))


    y1 = np.append(np.append([y1[0] for i in range(n_add)],y1),[y1[-1] for i in range(n_add)])
    y2 = np.append(np.append([y2[0] for i in range(n_add)],y2),[y2[-1] for i in range(n_add)])

    x1 = np.append(np.append(add_start_x,x1),add_end_x)
    x2 = np.append(np.append(add_start_x,x2),add_end_x)



    x1,y1 = smooth(x1,y1,n_add)
    x2,y2 = smooth(x2,y2,n_add)
    x1,y1 = smooth(x1,y1,n_add+180)
    x2,y2 = smooth(x2,y2,n_add+180)



    l11 = [
        """(\t""" + str(x1[i]) + "\t" + str(y1[i]) + """\t0\t)"""
        for i in range(len(x1))
    ]
    l12 = [
        """(\t""" + str(x1[i]) + "\t" + str(y1[i]) + """\t0.1\t)"""
        for i in range(len(x1))
    ]

    l21 = [
        """(\t""" + str(x2[i]) + "\t" + str(y2[i]) + """\t0\t)"""
        for i in range(len(x2))
    ]
    l22 = [
        """(\t""" + str(x2[i]) + "\t" + str(y2[i]) + """\t0.1\t)"""
        for i in range(len(x2))
    ]

    return l11, l12, l21, l22,x1,y1,x2,y2


def build_mesh(p1, p2,p3,path):
    shutil.copytree("05-cavity-curve", path)
    l11, l12, l21, l22,x1,y1,x2,y2 = build_arrays(p1, p2,p3)

    plt.figure()
    plt.plot(x1, y1, c="k")
    plt.plot(x2, y2, c="k")
    plt.xlim(min(x1)-0.1,max(x2)+0.1)
    plt.ylim(-0.5-2,max(x2)-2)
    plt.grid()
    plt.savefig(path+"/reactor_geometry.png")

    with open(path+"/system/blockMeshDict", "rb") as f:
        lines = f.readlines()

    l = 0
    s = []
    s.append(str(lines[l]).split("""b'""")[-1].split("""\\n""")[0])
    while "polyLine" not in str(lines[l]):
        s.append(str(lines[l]).split("""b'""")[-1].split("""\\n""")[0])
        l += 1

    i = 0 
    c = 0 
    while i < len(s):
        if '$' in s[i] and c in [0,4,7,3]:
            s[i] = s[i].replace('$xmin',str(x2[0]))
            s[i] = s[i].replace('$xmax',str(x1[0]))
            s[i] = s[i].replace('$ymax',str(y1[0]))
            s[i] = s[i].replace('$ymin',str(y2[0]))
            c += 1
            i += 1
        elif '$' in s[i] and c in [2,6,5,1]:
            s[i] = s[i].replace('$xmin',str(x1[-1]))
            s[i] = s[i].replace('$xmax',str(x2[-1]))
            s[i] = s[i].replace('$ymax',str(y1[-1]))
            s[i] = s[i].replace('$ymin',str(y2[-1]))
            c += 1
            i += 1 
        else:
            i += 1


    nums = ["0 1", "4 5", "3 2", "7 6"]
    lines_add = [l21, l22, l11, l12]

    for i in range(len(nums)):
        new_poly = "	polyLine " + nums[i] + " (" + lines_add[i][0]
        s.append(new_poly)
        for j in range(1, len(lines_add[i])):
            s.append(lines_add[i][j])
        s.append(""")""")
    s.append(""");""")

    while "boundary" not in str(lines[l]):
        l += 1

    for i in range(l, len(lines)):
        s.append(str(lines[l]).split("""b'""")[-1].split("""\\n""")[0])
        l += 1


    with open(path+"/system/blockMeshDict", "w") as f:
        for item in s:
            f.write("%s\n" % item)
      
    os.system('blockMesh -case '+path)
    
    return


