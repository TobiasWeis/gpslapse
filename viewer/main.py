#!/usr/bin/python -W ignore::DeprecationWarning
import sys

import os
import glob
import random
import cv2
import numpy as np
from plotter import *
from metaloader import *
from math import *
import datetime
from xml2dict import *

import context

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *

qtCreatorFile = "viewer.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, argv):

        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)


        self.files = []
        self.cnt = 0
        self.startframe = 0

        self.timer = QtCore.QTimer(self)
        self.play = False
        
        self.p = Plotter()

        if len(argv) > 1:
            self.dbtype = "XML"
            self.folder = argv[1]
            print "Folder set to ", self.folder
            self.find_files_XML()
        else:
            self.dbtype = "SQLite"
            self.ml = MetaloaderSQLite()

            # populate self.listWidget_sequences
            self.all_sequences = self.ml.getAllSequences()
            for s in self.all_sequences:
                mystr = "%d - %s" % (s.id, s.start_datetime)
                self.listWidget_sequences.addItem(mystr)

            #self.find_files_SQLite()

    def listWidget_doubleclick(self, index):
        self.ml.clear()
        id_sequence = int(self.listWidget_sequences.currentItem().text().split(' ')[0])
        print "Getting sequence with id |",id_sequence,"|"
        self.find_files_SQLite(id_sequence)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        if e.key() == QtCore.Qt.Key_F:
            self.fwd_clicked()
        if e.key() == QtCore.Qt.Key_B:
            self.bwd_clicked()
        if e.key() == QtCore.Qt.Key_P:
            if self.play == False:
                self.timer.setInterval(1)
                self.timer.timeout.connect(self.fwd_clicked)
                self.timer.start()
                self.play = True
            else:
                self.timer.stop()
                self.play = False

    def display_image(self):
        if self.dbtype == "XML":
            self.img_number.setText("%d/%d" % (self.cnt, len(self.files)))
            self.slider.setSliderPosition(self.cnt)
            pixmap_t = QPixmap(self.folder + self.files[self.cnt])
            painter = QPainter(pixmap_t)
            line = QLine(0.0, 240.0, 640.0, 240.0);
            painter.drawLine(line)

            if False:
                pixmap = pixmap_t.transformed(QTransform().scale(-1, -1)) # flip image
            else:
                pixmap = pixmap_t
            #spixmap = pixmap.scaled(self.img.size(), QtCore.Qt.KeepAspectRatio)
            spixmap = pixmap
            self.img.setPixmap(spixmap)
            self.img.show()
        elif self.dbtype == "SQLite":
            self.img_number.setText("%d/%d" % (self.cnt, len(self.frames)))
            self.slider.setSliderPosition(self.cnt)
            print "Opening image file: %s" % (self.folder + self.frames[self.cnt].img_uri)
            pixmap_t = QPixmap(self.folder + self.frames[self.cnt].img_uri)

            # draw annotations
            painter = QPainter(pixmap_t)
            for a in self.ml.annotCars[self.cnt]:
                if a.brakelight == 0:
                    painter.setPen(QtGui.QColor(255, 255, 255))
                else:
                    painter.setPen(QtGui.QColor(255, 0, 0))
                ul = (a.bbox_ul_x, a.bbox_ul_y)
                lr = (a.bbox_lr_x, a.bbox_lr_y)
                line = QtCore.QLine(ul[0], ul[1], lr[0], ul[1]); # upper horiz line
                painter.drawLine(line)
                line = QtCore.QLine(ul[0], lr[1], lr[0], lr[1]); # lower horiz line
                painter.drawLine(line)
                line = QtCore.QLine(ul[0], ul[1], ul[0], lr[1]); # left vertical
                painter.drawLine(line)
                line = QtCore.QLine(lr[0], ul[1], lr[0], lr[1]); # right vertical
                painter.drawLine(line)

            if False:
                pixmap = pixmap_t.transformed(QTransform().scale(-1, -1)) # flip image
            else:
                pixmap = pixmap_t
            #spixmap = pixmap.scaled(self.img.size(), QtCore.Qt.KeepAspectRatio)
            spixmap = pixmap
            self.img.setPixmap(spixmap)
            self.img.show()
        else:
            print "DisplayImage: do not recognize dbtype ", self.dbtype

        #tmp = cv2.imread(self.folder + self.files[self.cnt])
        # check if already labeled
        self.updateMeta()

    def slider_moved(self):
        self.cnt = self.slider.sliderPosition()
        self.display_image()

    def fwd_clicked(self):
        if self.dbtype == "XML":
            if self.cnt < len(self.files):
                self.cnt += 1
                self.display_image()
        elif self.dbtype == "SQLite":
            if self.cnt < len(self.frames):
                self.cnt += 1
                self.display_image()

    def bwd_clicked(self):
        if self.dbtype == "XML":
            if self.cnt > 0:
                self.cnt -= 1
                self.display_image()
        elif self.dbtype == "SQLite":
            if self.cnt > 0:
                self.cnt -= 1
                self.display_image()


    def jump_to_unlabeled(self):
        pass

    def label_selected(self):
        pass

    def add_label_clicked(self):
        pass

    def imageOpenCv2ToQImage (self, cv_img):
        height, width, bytesPerComponent = cv_img.shape
        bytesPerLine = bytesPerComponent * width;
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return QtGui.QImage(cv_img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)

    def updateMeta(self):
        msg = self.ml.getFrameMeta(self.cnt)[1]

        self.img_label.setText(msg)

        img_tmp = self.p.plot(self.cnt)
        img = cv2.cvtColor(img_tmp, cv2.cv.CV_BGR2RGB)
        qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        qpm = QtGui.QPixmap.fromImage(qimg)
        self.stats_img.setPixmap(qpm)

        try:
            img_tmp = self.p.plot_map(self.cnt)
            img = cv2.cvtColor(img_tmp, cv2.cv.CV_BGR2RGB)
            qimg = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
            qpm = QtGui.QPixmap.fromImage(qimg)
            self.gps_img.setPixmap(qpm)
        except:
            print "Can not plot gps plot"


    '''
    button on stats-page should select a label,
    then pictures with that label should be selected
    and put into the listview
    '''
    def selected_labels_clicked(self):
        pass

    # update label text
    def export_slider_value_changed(self):
        pass

    def export_button_clicked(self):
        pass

    def preload(self):
        '''
        use the preloaded sequnce of values from metaloader
        to create plots about the whole sequence
        '''
        self.p.coordinates = self.ml.coordinates
        self.p.values = self.ml.speedinfo
        self.p.imu_values = self.ml.imu_values

        self.cnt = 0
        self.display_image()

    def find_files_SQLite(self, id_sequence):
        # metaloader has been initialized above
        self.folder, self.frames = self.ml.parseSequenceMeta(id_sequence)
        self.preload()
        self.slider.setRange(0, len(self.frames))

    def find_files_XML(self):
        self.img_folder.setText(self.folder)
        self.files = [os.path.basename(x) for x in glob.glob(self.folder + '/*.png')]
        self.files.sort()
        self.files = self.files[self.startframe:]
        if len(self.files) > 0:
            # Give the folder to the metaloader
            self.ml = MetaloaderXML(self.folder, self.startframe)
            self.ml.parseSequenceMeta()
            # create statistics of hole sequence
            self.preload()
        else:
            print "No image files found "
        self.slider.setRange(0, len(self.files))


    def img_folder_clicked(self):
        new_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.folder = str(new_folder)

        if not os.path.isdir(self.folder):
            QtGui.QMessageBox.information(self, 'Error', 'The selected folder does not exist.')
            return

        if self.folder[-1] != "/": # FIXME: linux-only ?
            self.folder += "/"
        self.find_files()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp(sys.argv)
    window.show()
    sys.exit(app.exec_())
