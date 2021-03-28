import random
import numpy as np
from pyqtgraph.parametertree import Parameter, ParameterTree
import cv2 as cv
import pyqtgraph as pg
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from utilitys.widgets import EasyWidget
import time
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from skimage import data, morphology as morph
from skimage import io
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure

app = pg.mkQApp()
pg.setConfigOptions(imageAxisOrder='row-major')

opts = [
    dict(name='kernel size', type='int', value=3, step=2, limits=[-101, 101]),
    dict(name='binarize', type='bool', value=False),
    dict(name='strel shape', type='list',
         limits={'disk': morph.disk, 'square': morph.square}),
    dict(name='image', type='list', limits=['camera', 'hubble_deep_field', 'eagle'])
]
param = Parameter.create(name='Options', type='group', children=opts)

img = data.camera()
tree = ParameterTree()
tree.setParameters(param)

def changeImg():
    global img
    img = getattr(data, param['image'])()
param.child('image').sigValueChanged.connect(changeImg)


def applyOp():
    ksize = param['kernel size']
    op = cv.MORPH_DILATE
    if ksize < 0:
        op = cv.MORPH_ERODE
        ksize = -ksize
    newImg = cv.morphologyEx(img, op, param['strel shape'](ksize))
    if param['binarize']:
        newImg = newImg > 127
    return newImg

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.subplots()
        self.ax.set_axis_off()
        self.updateTime = 0.0
        self.addToolBar(NavigationToolbar(self.canvas, self))


        self.setCentralWidget(self.canvas)
        param.sigTreeStateChanged.connect(self.update)
        self.update()

    def update(self):
        newImg = applyOp()
        start = time.perf_counter()
        self.ax.imshow(newImg.astype('uint8'))
        self.canvas.draw()
        self.updateTime = time.perf_counter() - start
        self.statusBar().showMessage(f'Update time: {self.updateTime}')

class MyPlotWidget(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        pw = self.pw = pg.PlotWidget()
        param.sigTreeStateChanged.connect(self.update)
        self.imgItem = pg.ImageItem()
        pw.addItem(self.imgItem)
        pw.getViewBox().invertY()
        pw.getViewBox().setAspectLocked()
        self.update()
        self.updateTime = 0.0
        self.setCentralWidget(pw)

    def update(self):
        newImg = applyOp()
        start = time.perf_counter()
        self.imgItem.setImage(newImg)
        self.updateTime = time.perf_counter() - start
        self.statusBar().showMessage(f'Update time: {self.updateTime}')

if __name__ == "__main__":
    import sys

    w1 = MainWindow()
    w2 = MyPlotWidget()
    lbl = QtWidgets.QLabel()
    win = EasyWidget.buildMainWin([w1, w2, [tree, lbl]], layout='H')
    param.sigTreeStateChanged.connect(
        lambda: lbl.setText(f'PyQtGraph speedup: {w1.updateTime/w2.updateTime:3.2f}x'))
    win.show()
    sys.exit(app.exec_())