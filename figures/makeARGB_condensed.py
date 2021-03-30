# condensed variant, full code at:
# https://github.com/pyqtgraph/pyqtgraph/blob/pyqtgraph-0.12.0/pyqtgraph/functions.py#L1102-L1331


def makeARGB(data, lut=None, levels=None, scale=None, useRGBA=False, output=None):
    """
    **Arguments:**
    data           numpy array of int/float types.
    levels         List [min, max]; optionally rescale data before converting through the
                   lookup table. The data is rescaled such that min->0 and max->*scale*::

                      rescaled = (clip(data, min, max) - min) * (*scale* / (max - min))

                   It is also possible to use a 2D (N,2) array of values for levels. In this case,
                   it is assumed that each pair of min,max values in the levels array should be
                   applied to a different subset of the input data (for example, the input data may
                   already have RGB values and the levels are used to independently scale each
                   channel). The use of this feature requires that levels.shape[0] == data.shape[-1].
    scale          The maximum value to which data will be rescaled before being passed through the
                   lookup table (or returned if there is no lookup table). By default this will
                   be set to the length of the lookup table, or 255 if no lookup table is provided.
    lut            Optional lookup table (array with dtype=ubyte).
                   Values in data will be converted to color by indexing directly from lut.
                   The output data shape will be input.shape + lut.shape[1:].
                   Lookup tables can be built using ColorMap or GradientWidget.
    useRGBA        If True, the data is returned in RGBA order (useful for building OpenGL textures).
                   The default is False, which returns in ARGB order for use with QImage
                   (Note that 'ARGB' is a term used by the Qt documentation; the *actual* order
                   is BGRA).
    """
    xp = cp.get_array_module(data) if cp else np

    # Decide on maximum scaled value
    if scale is None:
        if lut is not None:
            scale = lut.shape[0]
        else:
            scale = 255.0

    # Decide on the dtype we want after scaling
    if lut is None:
        dtype = xp.ubyte
    else:
        dtype = xp.min_scalar_type(lut.shape[0] - 1)

    nanMask = None
    if data.dtype.kind == "f" and xp.isnan(data.min()):
        nanMask = xp.isnan(data)
        if data.ndim > 2:
            nanMask = xp.any(nanMask, axis=-1)
    # Apply levels if given
    if levels is not None:
        if isinstance(levels, xp.ndarray) and levels.ndim == 2:
            # we are going to rescale each channel independently
            newData = xp.empty(data.shape, dtype=int)
            for i in range(data.shape[-1]):
                minVal, maxVal = levels[i]
                if minVal == maxVal:
                    maxVal = xp.nextafter(maxVal, 2 * maxVal)
                rng = maxVal - minVal
                rng = 1 if rng == 0 else rng
                newData[..., i] = rescaleData(data[..., i], scale / rng, minVal, dtype=dtype)
            data = newData
        else:
            # Apply level scaling unless it would have no effect on the data
            minVal, maxVal = levels
            if minVal != 0 or maxVal != scale:
                if minVal == maxVal:
                    maxVal = xp.nextafter(maxVal, 2 * maxVal)
                rng = maxVal - minVal
                rng = 1 if rng == 0 else rng
                data = rescaleData(data, scale / rng, minVal, dtype=dtype)

    # apply LUT if given
    if lut is not None:
        data = applyLookupTable(data, lut)
    else:
        if data.dtype != xp.ubyte:
            data = xp.clip(data, 0, 255).astype(xp.ubyte)

    # this will be the final image array
    if output is None:
        imgData = xp.empty(data.shape[:2] + (4,), dtype=xp.ubyte)
    else:
        imgData = output

    # decide channel order
    if useRGBA:
        order = [0, 1, 2, 3]  # array comes out RGBA
    else:
        order = [2, 1, 0, 3]  # for some reason, the colors line up as BGR in the final image.

    # attempt to library function to copy data into image array
    fastpath = try_fastpath_argb(xp, data, imgData, useRGBA)

    if fastpath:
        pass
    elif data.ndim == 2:
        for i in range(3):
            imgData[..., i] = data
    elif data.shape[2] == 1:
        for i in range(3):
            imgData[..., i] = data[..., 0]
    else:
        for i in range(0, data.shape[2]):
            imgData[..., i] = data[..., order[i]]

    # add opaque alpha channel if needed
    if data.ndim == 3 and data.shape[2] == 4:
        alpha = True
    else:
        alpha = False
        if not fastpath:  # fastpath has already filled it in
            imgData[..., 3] = 255

    # apply nan mask through alpha channel
    if nanMask is not None:
        alpha = True
        imgData[nanMask, 3] = 0

    return imgData, alpha


def try_fastpath_argb(xp, ain, aout, useRGBA):
    # we only optimize for certain cases
    # return False if we did not handle it
    can_handle = xp is np and ain.dtype == xp.ubyte and ain.flags["C_CONTIGUOUS"]
    if not can_handle:
        return False

    nrows, ncols = ain.shape[:2]
    nchans = 1 if ain.ndim == 2 else ain.shape[2]

    Format = QtGui.QImage.Format

    if nchans == 1:
        in_fmt = Format.Format_Grayscale8
    elif nchans == 3:
        in_fmt = Format.Format_RGB888
    else:
        in_fmt = Format.Format_RGBA8888

    if useRGBA:
        out_fmt = Format.Format_RGBA8888
    else:
        out_fmt = Format.Format_ARGB32

    if in_fmt == out_fmt:
        aout[:] = ain
        return True

    qimg = QtGui.QImage(ain, ncols, ain.shape[0], ain.strides[0], in_fmt)
    qimg = qimg.convertToFormat(out_fmt)
    aout[:] = imageToArray(qimg, copy=False, transpose=False)

    return True
