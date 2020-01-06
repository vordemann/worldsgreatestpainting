
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
#import bayesianUI

#images
pixmap_prev_label = False
pixmap_current_label = False
        
        
IMAGE_WIDTH = 500
res = 0
radio_val = -1
iteration = 1
radiobuttonHidden = False

process = False
path_to_raw_image = "" #location of image to be processed
processingThread = False

from PyQt5.QtCore import QThread

#PictureRequest imports
from hashlib import sha1
import hmac
import xmltodict
import urllib
import numpy as np
import time
#PictureRequest gloabals
LINE_END = '\n'
pictureRequestThread = False
cold_start = False
import PictureRequest


class PictureRequestThread(QThread):
    def __init__(self, arr, picUrl):
        QThread.__init__(self)
        self.arr = arr
        self.picUrl = picUrl
        
    def __del__(self):
        self.wait()

    def run(self):
        global radiobuttonHidden, pixmap_current_label, pixmap_prev_label
        #print("sending image",self.picUrl, self.arr)
        pixmap_current = QPixmap('current.jpg')
        pixmap_current = pixmap_current.scaledToWidth(IMAGE_WIDTH)
        pixmap_prev_label.setPixmap(pixmap_current)
        
        pixmap_current = QPixmap('loading.jpg')
        pixmap_current = pixmap_current.scaledToWidth(IMAGE_WIDTH)
        pixmap_current_label.setPixmap(pixmap_current)

        PictureRequest.sendImage(self.picUrl, self.arr)
        
        pixmap_current = QPixmap('current.jpg')
        pixmap_current = pixmap_current.scaledToWidth(IMAGE_WIDTH)
        pixmap_current_label.setPixmap(pixmap_current)
        sleep(1);
        radiobuttonHidden.setChecked(True)
        



    #def finalize(self):
     #   global radiobuttonHidden
     #   radiobuttonHidden.setChecked(True)

    #arr = [0, 0, 0, 1.2, 34, 23, 0, 66, 23, 43, 12, 23, 12, 12 ,11]

   
    #import matplotlib.pyplot as plt
    #import matplotlib.image as mpimg

    #arr = [0, 0, 0, 7.2, 1, 0.3, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
    
    #img=mpimg.imread('current.jpg')
    #imgplot = plt.imshow(img)
    #plt.show()



class ProcessingThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        
    def __del__(self):
        self.wait()

    def f_u(self, x):
        global radio_val, process, iteration, radiobuttonHidden, cold_start
        
        print("Iteration: "+str(iteration))
        # plt.figure(1)
        print(x[0])

        # im = x.reshape(1, 1, 3).repeat(3, axis=0).repeat(3, axis=1)
        # plt.imshow(im)
        # plt.show(block=False)
        #while True:
        #     res = input('Grade? (1 to 5) ')
        #     if res in ['1', '2', '3', '4', '5']:
        #         res = int(res)
        #         # plt.close(1)
        #         return res
        
        if(cold_start):
            picUrl = "https://www.nyhabitat.com/blog/wp-content/uploads/2014/04/etiquette-guide-new-york-times-square-cabs.jpg" #https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/1024px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
            pictureRequestThread = PictureRequestThread(x[0],picUrl)
            pictureRequestThread.start()
        while True:
            sleep(1)
            if radio_val in [1, 2, 3, 4, 5]:
                #print("Optimizing with RANK: "+str(radio_val))
                val = radio_val
                radio_val = -1
                iteration += 1

                #generate a picture
                #print("PICTURE GENERATION PARAMETERS")
                #arr = [0, 0, 0, 1.2, 0.3, 1, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
                #print(arr)

                picUrl = "https://www.nyhabitat.com/blog/wp-content/uploads/2014/04/etiquette-guide-new-york-times-square-cabs.jpg" #https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/1024px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
                pictureRequestThread = PictureRequestThread(x[0],picUrl)
                pictureRequestThread.start()
                return val

    def run_bo(self, max_iter):
        bounds = [{'name': 'R', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'G', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'B', 'type': 'continuous', 'domain': (0, 1)},
                  {'name': 'color_hue', 'type': 'continuous', 'domain': (0, 2*np.pi)},
                  {'name': 'brush_radius', 'type': 'continuous', 'domain': (0.1, 2)},
                  {'name': 'blur_radius', 'type': 'continuous', 'domain': (0.1, 2)},
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
        n_iter = 1000
        # run BO
        bo = self.run_bo(n_iter)
        # run random for comparison
        # ra = run_random(n_iter)

        bo_xs, bo_ys = bo.get_evaluations()
        # ra_xs, ra_ys = ra
        
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

class App(QWidget):

    def __init__(self):
        super().__init__()
        path_to_raw_image = ""
        self.title = 'PyQt5 button - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()
        
        
    
    def initUI(self):
        global pixmap_prev_label, pixmap_current_label
        pixmap_prev_label = QLabel(self)
        pixmap_current_label = QLabel(self)
       
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.layout_main = QGridLayout()
        
        self.layout_home = QGridLayout()

        #print('Start Optimization')
        
        
        #btn1 = QPushButton('Browse', self)
        
        #self.layout_home.addWidget(btn1, 0, 0,1,1)
        #btn1.setToolTip('Please pick up an image')
        #btn1.move(IMAGE_POS_X, IMAGE_POS_Y/4)
        #btn1.clicked.connect(self.browse_click)  
        #self.layout_home.addWidget(btn1, 0, 0,1,1)
      
        #btn2 = QPushButton('Start', self)
        #btn2.setToolTip('Start Optimization')
        #btn2.move(IMAGE_POS_X + 100, IMAGE_POS_Y/4)
        #btn2.clicked.connect(self.start_click)        
        #self.layout_home.addWidget(btn2, 0, 1,1,1)
      
        #self.label_team = QLabel(self)
        #self.pixmap = QPixmap('team.jpg')
        #self.pixmap = self.pixmap.scaledToWidth(1000)       
        #self.label.move(IMAGE_POS_X,IMAGE_POS_Y)
        #self.label_team.setPixmap(self.pixmap)        
        #self.resize(self.pixmap.width() + 2 * IMAGE_POS_X, self.pixmap.height() + 2 * IMAGE_POS_Y)
        #self.layout_home.addWidget(self.label_team, 1, 0,1,2)
        #self.setLayout(layout)
        
        #self.layout_main.addLayout(self.layout_home, 1, 0);
        layout=self.init_UI_optimization()
        self.layout_main.addLayout(layout, 0, 0);
        self.setLayout(self.layout_main)

        self.layout_main.keyPressEvent = self.keyPressEvent

        self.show()

    def init_UI_optimization(self):
        layout = QGridLayout()
        global  radiobuttonHidden

        radiobuttonHidden = radiobuttonHidden = QRadioButton("READY FOR NEW RATING")
        radiobuttonHidden.setChecked(True)
        radiobuttonHidden.country = "-1"
        layout.addWidget(radiobuttonHidden, 1, 0,1,2)

        radiobutton = QRadioButton("Much worse")
        radiobutton.country = "1"
        radiobutton.toggled.connect(self.on_radio_button_clicked)
        layout.addWidget(radiobutton, 2, 0,1,2)

        radiobutton = QRadioButton("Worse")
        radiobutton.country = "2"
        radiobutton.toggled.connect(self.on_radio_button_clicked)
        layout.addWidget(radiobutton, 3, 0,1,2)

        radiobutton = QRadioButton("About the same")
        radiobutton.country = "3"
        radiobutton.toggled.connect(self.on_radio_button_clicked)
        layout.addWidget(radiobutton, 4, 0,1,2)
        
        radiobutton = QRadioButton("Better")
        radiobutton.country = "4"
        radiobutton.toggled.connect(self.on_radio_button_clicked)
        layout.addWidget(radiobutton, 5, 0,1,2)
        
        radiobutton = QRadioButton("Much better")
        radiobutton.country = "5"
        radiobutton.toggled.connect(self.on_radio_button_clicked)
        layout.addWidget(radiobutton, 6, 0,1,2)
    
        
        button = QPushButton('START AGAIN', self)
        layout.addWidget(button, 7, 0,1,1)
        button.clicked.connect(self.start_again_click)

        global pixmap_prev_label, pixmap_current_label
        
        pixmap_prev = QPixmap('previous.jpg')
        pixmap_prev = pixmap_prev.scaledToWidth(IMAGE_WIDTH)
        #pixmap_prev_label = QLabel(self)
        pixmap_prev_label.setPixmap(pixmap_prev)
        
        pixmap_current = QPixmap('current.jpg')
        pixmap_current = pixmap_current.scaledToWidth(IMAGE_WIDTH)
        pixmap_current_label.setPixmap(pixmap_current)

        layout.addWidget(pixmap_prev_label, 0, 0, 1,4)
        layout.addWidget(pixmap_current_label, 0, 4, 1,4)

        return layout
    
    def on_radio_button_clicked(self):
        global radio_val
        radioButton = self.sender()
        if radioButton.isChecked():
            radio_val = (int)(radioButton.country)
            print("data: Chosen rank is %i" % (radio_val))
   
    def browse_click(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                           './',"Image files (*.jpg)")
        path_to_raw_image = fname[0]
        self.pixmap = QPixmap(fname[0])
        self.pixmap = self.pixmap.scaledToWidth(2*IMAGE_WIDTH)
        self.label_team.setPixmap(self.pixmap)    

    def start_click(self):
        #print('Start Optimization')
        #print("path_to_raw_image: "+ path_to_raw_image)
        layout=self.init_UI_optimization()
        self.layout_main.addLayout(layout, 0, 0);
        self.layout_main.keyPressEvent = self.keyPressEvent
        
        #self.initBayOpt()
        
        #t1 = threading.Thread(target=self.initBayOpt())
        #t1.start()
        #t1.join()

        #self.initBayOpt()
        #t = threading.Thread(target=self.initBayOpt())
        #t.daemon = True
        #t.start()
        global processingThread
        processingThread = ProcessingThread()
        processingThread.start()
        

        # BayOpt.initBayOpt()

    def start_again_click(self):
        global processingThread, radio_val, iteration, cold_start
        #processingThread.join()
        iteration = 1
        radio_val = -1
        radiobuttonHidden.setChecked(True)
        processingThread = ProcessingThread()
        processingThread.start()
        cold_start = True

        #process=True


    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            # here accept the event and do something
            #print(event.key() - 48)
            event.accept()
        else:
            event.ignore()

    def randomArr():
        arr =  np.hstack((np.random.rand(3), #0-2 color
                  2*np.pi*np.random.rand(1), #3 color_dominance:hue
                  (2-0.1)*np.random.rand(1),#4 oil_painting:brush_radius_multiplier
                  (2-0.1)*np.random.rand(1), #5 oil_painting:blur_radius_multiplier
                  np.array(np.random.randint(2)), #6 pointilism
                  100*np.random.rand(1), #7 split_toning:balance
                  360*np.random.rand(1), #8 split_toning:shadow_hue
                  360*np.random.rand(1), #9 split_toning:highlight_hue
                  100*np.random.rand(1), #10 split_toning:shadow_saturation
                  100*np.random.rand(1), #11 split_toning:highlight_saturation
                  20*np.random.rand(1), #12 channel_shift:horizontal_offset
                  20*np.random.rand(1))) #13 channel_shift:vertical_offset
        newArr = []
        
        for i in arr:
            newArr.append(round(i,1))
        return newArr

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())