import pyqtgraph as pg
from math import log10
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np

app = pg.mkQApp("MultiPlot Benchmark Results")

penWidth = 3
pg.setConfigOptions(antialias=True, background="w", foreground="k")

x = np.array([100, 1000, 10000, 100000, 1000000, 10000000], dtype=float)
oneLineData = np.array([2.33, 3.49, 9.08, 52.92, 490.53, 5449.26], dtype=float)
tenLineData = np.array([7.34, 9.96, 31.03, 240.66, 2441.94], dtype=float)
hundredLineData = np.array([34.544, 51.49, 224.36, 1909.70], dtype=float)

# oneLine = pg.PlotCurveItem(x=x, y=oneLineData)
# tenLine = pg.PlotCurveItem(x=x[:-1], y=tenLineData)
# hundredLine = pg.PlotCurveItem(x=x[:-2], y=hundredLineData)

oneLinePenColor = "#5D4037"
tenLinePenColor = "#0D47A1"
hundredLinePenColor = "#880E4F"


win = pg.GraphicsLayoutWidget()

pointsPerCurve = win.addPlot()

pointsPerCurve.addLegend()
pointsPerCurve.plot(x=x, y=oneLineData, name="One Line", pen=oneLinePenColor)
pointsPerCurve.plot(x=x[:-1], y=tenLineData, name="Ten Lines", pen=tenLinePenColor)
pointsPerCurve.plot(x=x[:-2], y=hundredLineData, name="Hundred Lines", pen=hundredLinePenColor)
pointsPerCurve.setLabel("left", "Time to Update Frame (ms)")
pointsPerCurve.setLabel("bottom", "Points per curve")
pointsPerCurve.addLine(y=log10(1000 / 60), label="60 FPS", pen="#D84315", labelOpts={"position":1.0, "color":"#212121", "anchors":[(0.0, 0.0), (1, 0)]})
pointsPerCurve.addLine(y=log10(1000 / 10), label="10 FPS", pen="#D84315", labelOpts={"position":1.0, "color":"#212121", "anchors":[(0.0, 0.0), (1, 0)]})

pointsPerCurve.setLogMode(x=True, y=True)


updateTimePerPoint = win.addPlot()
updateTimePerPoint.addLegend()
updateTimePerPoint.setLabel("left", "Update time per point (µs)")
updateTimePerPoint.setLabel("bottom", "Total points")

totalPointsOneLine = x.copy()
totalPointsTenLine = x[:-1] * 10
totalPointsHundredLine = x[:-2] * 100 

perPointUpdateDurationOneLine = 1_000 * oneLineData / totalPointsOneLine
perPointUpdateDurationsTenLines = 1_000 * tenLineData / totalPointsTenLine
perPointUpdateDurationsHundredLines = 1_000 * hundredLineData / totalPointsHundredLine

updateTimePerPoint.plot(
    x=totalPointsOneLine,
    y=perPointUpdateDurationOneLine,
    pen=oneLinePenColor,
    name="1 Line"
)
updateTimePerPoint.plot(
    x=totalPointsTenLine,
    y=perPointUpdateDurationsTenLines,
    pen=tenLinePenColor,
    name="10 Lines"
)
updateTimePerPoint.plot(
    x=totalPointsHundredLine,
    y=perPointUpdateDurationsHundredLines,
    pen=hundredLinePenColor,
    name="100 Lines"
)


updateTimePerPoint.setLogMode(x=True, y=True)




win.show()

if __name__ == '__main__':
    pg.mkQApp().exec_()