
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
#import BayOpt
import threading
from time import sleep

import numpy as np
import scipy.stats
from matplotlib import pyplot as plt
import GPy
import GPyOpt
from random import randint, choice
from PyQt5.QtCore import QThread

import bayesianUI


class ProcessingThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        
    def __del__(self):
        self.wait()

    def f_u(self, x):
        global radio_val, process, iteration, radiobuttonHidden
        
        print("Iteration: "+str(iteration))
        # plt.figure(1)
        print(x)
        # im = x.reshape(1, 1, 3).repeat(3, axis=0).repeat(3, axis=1)
        # plt.imshow(im)
        # plt.show(block=False)
        #while True:
        #     res = input('Grade? (1 to 5) ')
        #     if res in ['1', '2', '3', '4', '5']:
        #         res = int(res)
        #         # plt.close(1)
        #         return res
        
        while True:
            sleep(1)
            if radio_val in [1, 2, 3, 4, 5]:
                print("Optimizing with RANK: "+str(radio_val))
                val = radio_val
                radio_val = -1
                iteration += 1
                radiobuttonHidden.setChecked(True)
                return val

    def run_bo(self, max_iter):
        bounds = [{'name': 'R', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'G', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'B', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'color_hue', 'type': 'continuous', 'domain': (0, 2*np.pi)},
                  {'name': 'brush_radius', 'type': 'continuous', 'domain': (0.1, 100)},
                  {'name': 'blur_radius', 'type': 'continuous', 'domain': (0.1, 100)},
                  {'name': 'point_bool', 'type': 'categorical', 'domain': (0, 1)},
                  {'name': 'tune_balance', 'type': 'continuous', 'domain': (0, 100)},
                  {'name': 'shadow_hue', 'type': 'continuous', 'domain': (0, 360)},
                  {'name': 'highlight_hue', 'type': 'continuous', 'domain': (0, 360)},
                  {'name': 'shadow_sat', 'type': 'continuous', 'domain': (0, 100)},
                  {'name': 'highlight_sat', 'type': 'continuous', 'domain': (0, 100)},
                  {'name': 'distort_horiz', 'type': 'continuous', 'domain': (0, 20)},
                  {'name': 'distort_vert', 'type': 'continuous', 'domain': (0, 20)}
                  ]
        myBopt = GPyOpt.methods.BayesianOptimization(
            f=self.f_u, domain=bounds,
            acquisition_type='EI',
            exact_feval=False,
            eps=1e-6,
            normalize_Y=False,
            initial_design_numdata=2,
            maximize=True)
        myBopt.run_optimization(max_iter=max_iter - 2)

        return myBopt


    def run_random(max_iter):
        xs = np.zeros((max_iter, 14)) #don't hardcode this
        ys = np.zeros((max_iter,))

        for i in range(max_iter):
            xs[i, :] = np.hstack((np.random.rand(3), 2*np.pi*np.random.rand(1), (100-0.1)*np.random.rand(1),
                                       (100-0.1)*np.random.rand(1), np.array(np.random.randint(2)), 100*np.random.rand(1),
                                       360*np.random.rand(1), 360*np.random.rand(1), 100*np.random.rand(1),
                                       100*np.random.rand(1), 20*np.random.rand(1), 20*np.random.rand(1)))
            ys[i] = f_u(xs[i, :])

        return xs, ys


    def initBayOpt(self):
        n_iter = 4
        # run BO
        bo = self.run_bo(n_iter)
        # run random for comparison
        # ra = run_random(n_iter)

        print("1")
        bo_xs, bo_ys = bo.get_evaluations()
        # ra_xs, ra_ys = ra
        print("2")
        
        # one can investigate these to see how good colors were found and compare
        # to a ground truth color

        #plt.plot(-bo_ys, 'k-', label='BO')
        # plt.plot(ra_ys, 'r-', label='Random')
        #plt.xlabel('iterations')
        #plt.ylabel('grades')
        #plt.legend()
        #plt.show()

        # let's say ground truth color was red
        # x_gt = np.array([1.0, 0.0, 0.0])
        x_gt = np.array([1.0, 0.0, 0.0, np.pi, 50, 50, 0, 50, 180, 180, 180, 50, 10, 10]) # now hardcoded, later randomize


        # plt.plot(np.sqrt(np.sum((bo_xs - x_gt) ** 2, 1)), 'k-', label='BO')
        # plt.plot(np.sqrt(np.sum((ra_xs - x_gt) ** 2, 1)), 'r-', label='Random')
        # plt.xlabel('iterations')
        # plt.ylabel('distance from ground truth')
        # plt.legend()
        # plt.show()
    def run(self):
        self.initBayOpt()