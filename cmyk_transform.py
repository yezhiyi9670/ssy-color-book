import littlecms, ctypes

profile_XYZ = littlecms.cmsCreateXYZProfile()
profile_CMYK = littlecms.cmsOpenProfileFromFile('./icc/JapanColor2001Coated.icc', 'r')
trans_XYZ_CMYK = littlecms.cmsCreateTransform(
    profile_XYZ, littlecms.TYPE_XYZ_DBL,
    profile_CMYK, littlecms.TYPE_CMYK_DBL,
    littlecms.INTENT_PERCEPTUAL, 0
)
trans_CMYK_XYZ = littlecms.cmsCreateTransform(
    profile_CMYK, littlecms.TYPE_CMYK_DBL,
    profile_XYZ, littlecms.TYPE_XYZ_DBL,
    littlecms.INTENT_PERCEPTUAL, 0
)

def xyz_to_cmyk(xyz_tuple: tuple[float, float, float]):
    inbuf = littlecms.doubleArray(3)
    for i in range(0, 3):
        inbuf[i] = xyz_tuple[i]
    outbuf = littlecms.doubleArray(4)
    littlecms.cmsDoTransform(trans_XYZ_CMYK, inbuf, outbuf, 1)
    return (outbuf[0] / 100, outbuf[1] / 100, outbuf[2] / 100, outbuf[3] / 100)

def cmyk_to_xyz(cmyk_tuple: tuple[float, float, float, float]):
    inbuf = littlecms.doubleArray(4)
    for i in range(0, 4):
        inbuf[i] = cmyk_tuple[i] * 100
    outbuf = littlecms.doubleArray(3)
    littlecms.cmsDoTransform(trans_CMYK_XYZ, inbuf, outbuf, 1)
    return (outbuf[0], outbuf[1], outbuf[2])
