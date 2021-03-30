import pyqtgraph as pg
from math import log10
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np

app = pg.mkQApp("MultiPlot Benchmark Results")
pg.setConfigOptions(antialias=True, background="w", foreground="k")

penWidth = 3
symbolSize = 7

oneLinePenColor = "#b2df8a"
tenLinePenColor = "#a6cee3"
hundredLinePenColor = "#DCD0FF"
infiniteLineColor = "#FFB74D"

oneLineSymbol = "o"
tenLineSymbol = "t1"
hundredLineSymbol = "s"

# collected data
x = np.array([100, 1000, 10000, 100000, 1000000, 10000000], dtype=float)
oneLineData = np.array([2.33, 3.49, 9.08, 52.92, 490.53, 5449.26], dtype=float)
tenLineData = np.array([7.34, 9.96, 31.03, 240.66, 2441.94], dtype=float)
hundredLineData = np.array([34.544, 51.49, 224.36, 1909.70], dtype=float)

win = pg.GraphicsLayoutWidget()

pointsPerCurve = win.addPlot()
pointsPerCurve.axes["bottom"]["item"].enableAutoSIPrefix(False)
pointsPerCurve.addLegend()
pointsPerCurve.plot(
    x=x,
    y=oneLineData,
    name="1 Line",
    pen={
        "color":oneLinePenColor,
        "width": penWidth,
    },
    symbolBrush=oneLinePenColor,
    symbolPen="k",
    symbolSize=symbolSize,
    symbol=oneLineSymbol
)
pointsPerCurve.plot(
    x=x[:-1],
    y=tenLineData,
    name="10 Lines",
    pen={
        "color": tenLinePenColor,
        "width": penWidth
    },
    symbolBrush=tenLinePenColor,
    symbolSize=symbolSize,
    symbol=tenLineSymbol,
    symbolPen="k"
)
pointsPerCurve.plot(
    x=x[:-2],
    y=hundredLineData,
    name="100 Lines",
    pen={
        "color": hundredLinePenColor,
        "width": penWidth
    },
    symbolBrush=hundredLinePenColor,
    symbolSize=symbolSize,
    symbol=hundredLineSymbol,
    symbolPen="k"
)
pointsPerCurve.setLabel("left", "Time to Update Frame (ms)")
pointsPerCurve.setLabel("bottom", "Points per Curve")
pointsPerCurve.addLine(
    y=log10(1000 / 60),  # having to log10 due to log mode bug
    label="60 FPS",
    pen={
        "color": infiniteLineColor,
        "width": penWidth
    },
    labelOpts={
        "position":1.0,
        "color": "#212121",
        "anchors":[(0.0, 0.0), (1.0, 0.0)]
    }
)
pointsPerCurve.addLine(
    y=log10(1000 / 10),  # having to log10 due to log mode bug
    label="10 FPS",
    pen={
        "color": infiniteLineColor,
        "width": penWidth
    },
    labelOpts={
        "position":1.0,
        "color":"#212121",
        "anchors":[(0.0, 0.0), (1.0, 0.0)]
        }
    )

pointsPerCurve.setLogMode(x=True, y=True)


updateTimePerPoint = win.addPlot()
updateTimePerPoint.axes["bottom"]["item"].enableAutoSIPrefix(False)

updateTimePerPoint.addLegend(offset=(-30, 30))
updateTimePerPoint.setLabel("left", "Update Time per Point (µs)")
updateTimePerPoint.setLabel("bottom", "Total Points")

totalPointsOneLine = x.copy()
totalPointsTenLine = x[:-1] * 10
totalPointsHundredLine = x[:-2] * 100 

perPointUpdateDurationOneLine = 1_000 * oneLineData / totalPointsOneLine
perPointUpdateDurationsTenLines = 1_000 * tenLineData / totalPointsTenLine
perPointUpdateDurationsHundredLines = 1_000 * hundredLineData / totalPointsHundredLine

updateTimePerPoint.addLine(
    y=log10(200 / 1_000),
    pen={
        "color": "k",
        "width": penWidth - 2,
        "style": QtCore.Qt.DashLine
    },
    label="200 ns",
    labelOpts={
        "position":0.0,
        "color":"#212121",
        "anchors": [(0.0, 0.0), (0.0, 1.0)]
    }
)

updateTimePerPoint.plot(
    x=totalPointsOneLine,
    y=perPointUpdateDurationOneLine,
    pen={
        "color": oneLinePenColor,
        "width": penWidth
    },
    symbol=oneLineSymbol,
    symbolPen="k",
    symbolSize=symbolSize,
    symbolBrush=oneLinePenColor,
    name="1 Line"
)
updateTimePerPoint.plot(
    x=totalPointsTenLine,
    y=perPointUpdateDurationsTenLines,
    pen={
        "color": tenLinePenColor,
        "width": penWidth
    },
    symbol=tenLineSymbol,
    symbolPen="k",
    symbolSize=symbolSize,
    symbolBrush=tenLinePenColor,
    name="10 Lines"
)
updateTimePerPoint.plot(
    x=totalPointsHundredLine,
    y=perPointUpdateDurationsHundredLines,
    pen={
        "color": hundredLinePenColor,
        "width": penWidth
    },
    symbol=hundredLineSymbol,
    symbolPen="k",
    symbolSize=symbolSize,
    symbolBrush=hundredLinePenColor,
    name="100 Lines"
)

updateTimePerPoint.setLogMode(x=True, y=True)
win.show()

if __name__ == '__main__':
    pg.mkQApp().exec_()