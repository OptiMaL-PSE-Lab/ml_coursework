import numpy as np
import matplotlib.pyplot as plt


def sin_line(x, b, a, c):
    return b + (a * np.sin(c * x))


def add_start_and_end(x, y):
    s = y[0]
    e = y[-1]
    x = [x[0] - 0.5] + list(x)
    x = list(x) + [x[-1] + 0.6]
    y = [y[0]] + list(y) + [y[-1]]
    return x, y


def build_arrays(p1, p2):

    x = np.linspace(0, 4.4, 180)
    # p1 = 0.25 # 0.1 <-> 0.6
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

    y1 = sin_line(x, 0.5, p1, p2)
    y2 = sin_line(x, 0.0, 0.25, p2)

    x1, y1 = add_start_and_end(x, y1)
    x2, y2 = add_start_and_end(x, y2)

    plt.figure()
    plt.plot(x1, y1, c="k")
    plt.plot(x2, y2, c="k")
    plt.grid()
    plt.savefig("mesh.png")

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

    return l11, l12, l21, l22


def build_mesh(p1, p2):
    l11, l12, l21, l22 = build_arrays(p1, p2)
    f = open("mesh_construction/blockMeshDict_ref", "rb")

    lines = f.readlines()
    l = 0
    s = []
    s.append(str(lines[l]).split("""b'""")[-1].split("""\\n""")[0])
    while "polyLine" not in str(lines[l]):
        s.append(str(lines[l]).split("""b'""")[-1].split("""\\n""")[0])
        l += 1

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
    with open("mesh_construction/blockMeshDict", "w") as f:
        for item in s:
            f.write("%s\n" % item)
    return


build_mesh(0.25, 5)
