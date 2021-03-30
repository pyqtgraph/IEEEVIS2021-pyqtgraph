def makeARGB(data, lut=None, levels=None, scale=None, useRGBA=False, output=None):
    # condensed variant, full code at:
    # https://github.com/pyqtgraph/pyqtgraph/blob/pyqtgraph-0.12.0/pyqtgraph/functions.py#L1102-L1331
    xp = cp.get_array_module(data) if cp else np
    if scale is None:
        if lut is not None:
            scale = lut.shape[0]
        else:
            scale = 255.0
    dtype = xp.ubyte

    nanMask = None
    if data.dtype.kind == "f" and xp.isnan(data.min()):
        nanMask = xp.isnan(data)
        if data.ndim > 2:
            nanMask = xp.any(nanMask, axis=-1)
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
            rng = maxVal - minVal
            data = rescaleData(data, scale / rng, minVal, dtype=dtype)

    data = applyLookupTable(data, lut)

    imgData = output
    if useRGBA:
        order = [0, 1, 2, 3]  # array comes out RGBA
    else:
        order = [2, 1, 0, 3]  # for some reason, the colors line up as BGR in the final image.

    # attempt to use library function to copy data into image array
    fastpath_success = try_fastpath_argb(xp, data, imgData, useRGBA)

    if fastpath_success:
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
        if not fastpath_success:  # fastpath has already filled it in
            imgData[..., 3] = 255
    # apply nan mask through alpha channel
    if nanMask is not None:
        alpha = True
        imgData[nanMask, 3] = 0
    return imgData, alpha
