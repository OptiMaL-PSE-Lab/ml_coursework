import numpy as np
from datetime import datetime
from scipy.special import factorial
import matplotlib.pyplot as plt
import os
from os import path
import sys
sys.path.insert(1, os.path.join(sys.path[0], ".."))
from mesh_construction.construct_mesh import build_mesh
from scipy.signal import find_peaks
from PyFoam.Basics.DataStructures import Vector
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Execution.AnalyzedRunner import AnalyzedRunner
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.LogAnalysis.SimpleLineAnalyzer import GeneralSimpleLineAnalyzer
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer





def calc_etheta(N, theta, off, up):
    theta = theta - off
    z = factorial(N - 1)
    xy = (N * ((N * theta) ** (N - 1))) * (np.exp(-N * theta))
    etheta_calc = xy / z
    return etheta_calc * up


def loss(X, theta, etheta):
    N, off, up = X
    error_sq = 0
    et = []
    for i in range(len(etheta)):
        et.append(calc_etheta(N, theta[i], off, up))

    # for i in range(len(theta)):
    #     if theta[i] > 2:
    #         error_sq += 0
    #     else:
    #         error_sq += (calc_etheta(N, theta[i], off, up) - etheta[i]) ** 2
    error_sq += (max(etheta)-max(et))**2
    return error_sq


class CompactAnalyzer(BoundingLogAnalyzer):
    def __init__(self):
        BoundingLogAnalyzer.__init__(self)
        self.addAnalyzer(
            "concentration",
            GeneralSimpleLineAnalyzer(
                r"averageConcentration", r"^[ ]*areaAverage\(outlet\) of s = (.+)$"
            ),
        )


def vel_calc(re):
    return (re * 9.9 * 10**-4) / (990 * 0.005)

def val_to_rtd(time,value,path):

    value = np.array(value)
    time = np.array(time)

    plt.figure()
    peaks, _ = find_peaks(value, prominence=0.0001)
    times_peaks = time[peaks]
    values_peaks = value[peaks]
    plt.plot(time, value, c="k", lw=1, alpha=0.1)
    plt.plot(times_peaks, values_peaks, c="r", lw=1,label='CFD')


    plt.grid()
    plt.xlabel("time")
    plt.ylabel("concentration")
    plt.legend()
    plt.savefig(path+"/preprocessed_plot.png")

    # difference between time values
    dt = np.diff(times_peaks)[0]

    # getting lists of interest (theta, e_theta)
    et = values_peaks / (sum(values_peaks * dt))
    tau = (sum(times_peaks * values_peaks * dt)) / sum(values_peaks * dt)
    etheta = tau * et
    theta = times_peaks / tau
    return theta,etheta

def calculate_N(value, time,path):
    # obtaining a smooth curve by taking peaks
    
    theta,etheta = val_to_rtd(time,value,path)

    # fitting value of N
    s = 1000
    x0_list = np.array(
        [
            np.logspace(np.log(1), np.log(50), s),
            np.random.uniform(-0.001, 0.001, s),
            np.random.uniform(1, 1.0001, s),
        ]
    ).T

    best = np.Inf
    for x0 in x0_list:
        l = loss(x0, theta, etheta)
        if l < best:
            best = l
            X = x0

    N, off, up = X

    plt.figure()
    plt.scatter(theta, etheta, c="k", alpha=0.4,label="CFD")
    etheta_calc = []
    for t in theta:
        etheta_calc.append(calc_etheta(N, t, off, up))
    plt.plot(theta, etheta_calc, c="k",ls='dashed', label="Dimensionless")
    plt.grid()
    plt.legend()
    plt.savefig(path+"/dimensionless_conversion.png")
    return N




def parse_conditions(case, a, f, vel):
    velBC = ParsedParameterFile(path.join(case, "0", "U"))
    velBC["boundaryField"]["inlet"]["variables"][1] = '"amp= %.5f;"' % a
    velBC["boundaryField"]["inlet"]["variables"][0] = '"freq= %.5f;"' % f
    velBC["boundaryField"]["inlet"]["variables"][2] = '"vel= %.5f;"' % vel
    velBC["boundaryField"]["inlet"]["value"].setUniform(Vector(vel, 0, 0))
    velBC.writeFile()
    decomposer = UtilityRunner(
        argv=["decomposePar", "-case", case],
        logname="decomposePar",
    )
    decomposer.start()
    return


def run_cfd(case):

    run_command = f"pimpleFoam"

    run = AnalyzedRunner(
        CompactAnalyzer(),
        argv=[run_command, "-case", case],
        logname="Solution",
    )
    # running CFD
    run.start()

    # post processing concentrations

    with open(case+'/postProcessing/patchAverage_massfraction/0/s') as f:
        res = f.readlines()

    t = []
    c = []
    for l in res[1:]:
        t.append(float(l[:13].split(' ')[-1]))
        c.append(float(l[-13:].split(' ')[-1]))

    time = np.asarray(t)
    value = np.asarray(c)

    return time, value


def eval_cfd(a, f, p1, p2, p3):
    identifier = identifier = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    print('Starting to mesh '+identifier)
    newcase = "outputs/" + identifier
    build_mesh(p1,p2,p3,path=newcase)
    vel = vel_calc(50)
    parse_conditions(newcase, a, f, vel)
    time, value = run_cfd(newcase)
    N = calculate_N(value, time,newcase)
    return N



