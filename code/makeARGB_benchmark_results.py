import numpy as np
import pyqtgraph as pg

import pandas as pd
from math import log10

data = pd.read_csv(
    "code/makeARGB_benchmark_results.csv",
    names=["size", "CuPy", "dtype", "levels", "LUT", "time"],
    converters={
        "CuPy": lambda x: x == "cupy",
        "levels": lambda x: x == "levels"
    },
    header=0
)

app = pg.mkQApp("Video Speed Test Results")
pg.setConfigOptions(antialias=True, background="w", foreground="k")

penWidth = 3
legendFontSize = "12pt"
titleFontSize = "14pt"

gray = "#757575"
blue = "#41A7DC"
purple = "#B65FD3"
fillColor = "#00004040"

pen_noCUDA_yesLevels_noLUT = pg.mkPen(purple, style=pg.QtCore.Qt.DashLine, width=penWidth)
pen_yesCUDA_yesLevels_noLUT = pg.mkPen(purple, width=penWidth)

# pen_noCUDA_noLevels_noLUT = pg.mkPen(colors[1], style=pg.QtCore.Qt.DashLine, width=penWidth)
# pen_yesCUDA_noLevels_noLUT = pg.mkPen(colors[1], width=penWidth)

# pen_noCUDA_yesLevels_unint8LUT = pg.mkPen(colors[2], style=pg.QtCore.Qt.DashLine, width=penWidth)
# pen_yesCUDA_yesLevels_uint8LUT = pg.mkPen(colors[2], width=penWidth)

# pen_noCUDA_noLevels_uint8LUT = pg.mkPen(colors[3], style=pg.QtCore.Qt.DashLine, width=penWidth)
# pen_yesCUDA_noLevels_uint8LUT = pg.mkPen(colors[3], width=penWidth)


pen_noCUDA_yesLevels_uint16LUT = pg.mkPen(blue, style=pg.QtCore.Qt.DashLine, width=penWidth)
pen_yesCUDA_yesLevels_uint16LUT = pg.mkPen(blue, width=penWidth)

# pen_noCUDA_noLevels_uint16LUT = pg.mkPen(colors[5], style=pg.QtCore.Qt.DashLine, width=penWidth)
# pen_yesCUDA_noLevels_uint16LUT = pg.mkPen(colors[5], width=penWidth)


infiniteLineColorSetName = "inferno"
infiniteLineColorMap = pg.colormap.get(infiniteLineColorSetName, source="matplotlib")
infiniteLineColors = infiniteLineColorMap.getLookupTable(start=0.1, stop=0.9, nPts=4, mode="byte")

def getSeries(df):
    series = {}
    series["yesCUDA_yesLevels_noLUT"] = df[(df["CuPy"]) & (df["levels"]) & (df["LUT"] == "nolut")]["time"].to_numpy() * 1_000
    series["yesCUDA_yesLevels_uint8LUT"] = df[(df["CuPy"]) & (df["levels"]) & (df["LUT"] == "uint8lut")]["time"].to_numpy() * 1_000
    series["yesCUDA_yesLevels_uint16LUT"] = df[(df["CuPy"]) & (df["levels"]) & (df["LUT"] == "uint16lut")]["time"].to_numpy() * 1_000

    series["yesCUDA_noLevels_noLUT"] = df[(df["CuPy"]) & (df["levels"] == False) & (df["LUT"] == "nolut")]["time"].to_numpy() * 1_000
    series["yesCUDA_noLevels_uint8LUT"] = df[(df["CuPy"]) & (df["levels"] == False) & (df["LUT"] == "uint8lut")]["time"].to_numpy() * 1_000
    series["yesCUDA_noLevels_uint16LUT"] = df[(df["CuPy"]) & (df["levels"] == False) & (df["LUT"] == "uint16lut")]["time"].to_numpy() * 1_000

    series["noCUDA_yesLevels_noLUT"] = df[(df["CuPy"] == False) & (df["levels"]) & (df["LUT"] == "nolut")]["time"].to_numpy() * 1_000
    series["noCUDA_yesLevels_uint8LUT"] = df[(df["CuPy"] == False) & (df["levels"]) & (df["LUT"] == "uint8lut")]["time"].to_numpy() * 1_000
    series["noCUDA_yesLevels_uint16LUT"] = df[(df["CuPy"] == False) & (df["levels"]) & (df["LUT"] == "uint16lut")]["time"].to_numpy() * 1_000

    series["noCUDA_noLevels_noLUT"] = df[(df["CuPy"] == False) & (df["levels"] == False) & (df["LUT"] == "nolut")]["time"].to_numpy() * 1_000
    series["noCUDA_noLevels_uint8LUT"] = df[(df["CuPy"] == False) & (df["levels"] == False) & (df["LUT"] == "uint8lut")]["time"].to_numpy() * 1_000
    series["noCUDA_noLevels_uint16LUT"] = df[(df["CuPy"] == False) & (df["levels"] == False) & (df["LUT"] == "uint16lut")]["time"].to_numpy() * 1_000

    return series


win = pg.GraphicsLayoutWidget()

x = np.square([256, 512, 1024, 2048, 3072, 4096])

uint8Data = getSeries(data.loc[data["dtype"] == "uint8"])
uint16Data = getSeries(data.loc[data["dtype"] == "uint16"])
floatData = getSeries(data.loc[data["dtype"] == "float"])

floatPlot = win.addPlot()


floatPlot.setTitle("makeARGB Runtime for float dtype", size=titleFontSize)
floatPlot.axes["bottom"]["item"].enableAutoSIPrefix(False)

floatLegend = floatPlot.addLegend(brush="w", pen="k")
floatLegend.setLabelTextSize(legendFontSize)
noLUTyesCUDA = floatPlot.plot(
    x=x,
    y=floatData["yesCUDA_yesLevels_noLUT"],
    name="no LUT - CUDA enabled",
    pen=pen_yesCUDA_yesLevels_noLUT
)

noLUTnoCUDA = floatPlot.plot(
    x=x,
    y=floatData["noCUDA_yesLevels_noLUT"],
    name="no LUT - NumPy only",
    pen=pen_noCUDA_yesLevels_noLUT
)


yesLUTyesCUDA = floatPlot.plot(
    x=x,
    y=floatData["yesCUDA_yesLevels_uint16LUT"],
    name="16-bit LUT - CUDA enabled",
    pen=pen_yesCUDA_yesLevels_uint16LUT
)

yesLUTnoCUDA = floatPlot.plot(
    x=x,
    y=floatData["noCUDA_yesLevels_uint16LUT"],
    name="16-bit LUT - NumPy Only",
    pen=pen_noCUDA_yesLevels_uint16LUT
)

floatPlot.setLogMode(x=True, y=True)

yesCUDAFillBetween = pg.FillBetweenItem(noLUTyesCUDA, yesLUTyesCUDA, brush=fillColor)
floatPlot.addItem(yesCUDAFillBetween)

noCUDAFillBetween = pg.FillBetweenItem(noLUTnoCUDA, yesLUTnoCUDA, brush=fillColor)
floatPlot.addItem(noCUDAFillBetween)

floatPlot.showGrid(x=True, y=True)
floatPlot.setLabel("left", "makeARGB Runtime (ms)")
floatPlot.setLabel("bottom", "Pixels in Image")



uint16Plot = win.addPlot()
uint16Plot.setTitle("makeARGB Runtime for uint16 dtype", size=titleFontSize)
uint16Plot.axes["bottom"]["item"].enableAutoSIPrefix(False)

uint16Legend = uint16Plot.addLegend(brush="w", pen="k")
uint16Legend.setLabelTextSize(legendFontSize)
noLUTyesCUDA = uint16Plot.plot(
    x=x,
    y=uint16Data["yesCUDA_yesLevels_noLUT"],
    name="no LUT - CUDA enabled",
    pen=pen_yesCUDA_yesLevels_noLUT
)

noLUTnoCUDA = uint16Plot.plot(
    x=x,
    y=uint16Data["noCUDA_yesLevels_noLUT"],
    name="no LUT - NumPy only",
    pen=pen_noCUDA_yesLevels_noLUT
)


yesLUTyesCUDA = uint16Plot.plot(
    x=x,
    y=uint16Data["yesCUDA_yesLevels_uint16LUT"],
    name="16-bit LUT - CUDA enabled",
    pen=pen_yesCUDA_yesLevels_uint16LUT
)

yesLUTnoCUDA = uint16Plot.plot(
    x=x,
    y=uint16Data["noCUDA_yesLevels_uint16LUT"],
    name="16-bit LUT - NumPy Only",
    pen=pen_noCUDA_yesLevels_uint16LUT
)

uint16Plot.setLogMode(x=True, y=True)

yesCUDAFillBetween = pg.FillBetweenItem(noLUTyesCUDA, yesLUTyesCUDA, brush=fillColor)
uint16Plot.addItem(yesCUDAFillBetween)

noCUDAFillBetween = pg.FillBetweenItem(noLUTnoCUDA, yesLUTnoCUDA, brush=fillColor)
uint16Plot.addItem(noCUDAFillBetween)

uint16Plot.showGrid(x=True, y=True)
uint16Plot.setLabel("left", "makeARGB Runtime (ms)")
uint16Plot.setLabel("bottom", "Pixels in Image")

floatPlot.setYLink(uint16Plot)

win.resize(1000, 500)
win.show()

if __name__ == '__main__':
    pg.mkQApp().exec_()