from colormath.color_objects import SpectralColor, xyYColor, sRGBColor, AdobeRGBColor, XYZColor, LabColor
from colormath.color_conversions import convert_color
from colormath import color_diff
import numpy

from cmyk_transform import xyz_to_cmyk, cmyk_to_xyz
class SpecSYColor():
    def __init__(self, spec: int, saturation: float, Y: float):
        assert 400 <= spec <= 700 or -99 <= spec <= -1, 'Spectrum ordinal is out of the allowed range [400, 700] or [-99, -1]'
        self.spec = spec
        assert 0 <= saturation <= 1, 'Saturation is not within [0, 1]'
        self.saturation = saturation
        assert 0 <= Y <= 1, 'Y is not within [0, 1]'
        self.Y = Y

    def __repr__(self):
        return 'SpecSYColor(spec=%d, saturation=%.2f, Y=%.2f)' % (self.spec, self.saturation, self.Y)
    
    @staticmethod
    def from_code(code: str):
        assert len(code) == 5 or len(code) == 2, 'Code should be either 5-digits or 2-digits.'
        spec = 560
        if len(code) == 5:
            if code[0].upper() == 'L':
                spec = -int(code[1:3])
            else:
                spec = int(code[0:3])
            code = code[3:5]
        else:
            assert code[0] == '0', '2-digits code must have saturation 0'
        
        saturation = (int(code[0], base=13) / 12) ** 1.4
        
        Y = int(code[1], base=13) - 2
        if -2 <= Y <= 2:
            Y = Y / 2 + 1
        Y /= 10
        return SpecSYColor(spec, saturation, Y)

    def get_xyy_color(self):
        spec_color = None
        if self.spec > 0:
            # Pure spectral color
            start_name = 'spec_%02d0nm' % (self.spec // 10)
            end_name = 'spec_%02d0nm' % (self.spec // 10 + 1)
            start_ratio = 1 - (self.spec % 10) / 10
            end_ratio = (self.spec % 10) / 10
            spec_color = SpectralColor(**{
                (start_name): start_ratio,
                (end_name): end_ratio,
                'illuminant': 'd65'
            })
        else:
            # Mix between end points
            spec_color = SpectralColor(**{
                'spec_700nm': 1 - (-self.spec) / 100,
                'spec_400nm': (-self.spec) / 100,
                'illuminant': 'd65'
            })
        xyy_color = convert_color(spec_color, xyYColor)
        # Apply Y
        xyy_color.xyy_Y = self.Y
        # Apply saturation
        s = self.saturation
        white_xyy = convert_color(sRGBColor(1, 1, 1), xyYColor, target_illuminant='d65')
        xyy_color.xyy_x = s * xyy_color.xyy_x + (1 - s) * white_xyy.xyy_x
        xyy_color.xyy_y = s * xyy_color.xyy_y + (1 - s) * white_xyy.xyy_y
        return xyy_color
    
    def get_srgb_triplet(self):
        xyy_color = self.get_xyy_color()
        rgb_color = convert_color(xyy_color, sRGBColor)
        return RGBTriplet(rgb_color.rgb_r, rgb_color.rgb_g, rgb_color.rgb_b)
    
    def get_adobergb_triplet(self):
        xyy_color = self.get_xyy_color()
        rgb_color = convert_color(xyy_color, AdobeRGBColor)
        return RGBTriplet(rgb_color.rgb_r, rgb_color.rgb_g, rgb_color.rgb_b)
    
    def get_cmyk_coords(self):
        # xyy_color = self.get_xyy_color()
        # cmyk_color = convert_color(xyy_color, CMYKColor)
        # return CMYKCoords(cmyk_color.cmyk_c, cmyk_color.cmyk_m, cmyk_color.cmyk_y, cmyk_color.cmyk_k, False)
        xyy_color = self.get_xyy_color()
        xyz_color = convert_color(xyy_color, XYZColor)
        xyz_color.apply_adaptation('d50')
        
        xyz_tuples = xyz_color.get_value_tuple()
        cmyk_tuples = xyz_to_cmyk(xyz_tuples)
        xyz_rev_tuples = cmyk_to_xyz(cmyk_tuples)
        
        xyz_color_d65 = XYZColor(*xyz_tuples, illuminant='d50')
        xyz_color_d65.apply_adaptation('d65')
        xyz_rev_color_d65 = XYZColor(*xyz_rev_tuples, illuminant='d50')
        xyz_rev_color_d65.apply_adaptation('d65')
        
        far_off = color_diff.delta_e_cmc(
            convert_color(xyz_color_d65, LabColor),
            convert_color(xyz_rev_color_d65, LabColor)
        ) >= 3

        return CMYKCoords(
            cmyk_tuples[0], cmyk_tuples[1], cmyk_tuples[2], cmyk_tuples[3], far_off
        )
    
    def get_displayp3_triplet(self):
        gamma = 2.2
        xyy_color = self.get_xyy_color()
        rgb_color = convert_color(xyy_color, sRGBColor)
        rgb_vec = numpy.array([rgb_color.rgb_r ** gamma, rgb_color.rgb_g ** gamma, rgb_color.rgb_b ** gamma])
        xyz65_srgb = numpy.array([
            [ 0.4123908,  0.3575843,  0.1804808],
            [ 0.2126390,  0.7151687,  0.0721923],
            [ 0.0193308,  0.1191948,  0.9505322]
        ])
        displayp3_xyz65 = numpy.array([
            [ 2.4934969, -0.9313836, -0.4027108],
            [-0.8294890,  1.7626641,  0.0236247],
            [ 0.0358458, -0.0761724,  0.9568845]
        ])
        rgb_vec = displayp3_xyz65 @ xyz65_srgb @ rgb_vec
        for i in range(0, 3):
            rgb_vec[i] = RGBTriplet.near_normalize(rgb_vec[i])
        return RGBTriplet(rgb_vec[0] ** (1 / gamma), rgb_vec[1] ** (1 / gamma), rgb_vec[2] ** (1 / gamma))
    
class RGBTriplet():
    def __init__(self, r: float, g: float, b: float):
        self.r = self.near_normalize(r)
        self.g = self.near_normalize(g)
        self.b = self.near_normalize(b)
    
    def __repr__(self):
        return 'RGBTriplet(r=%.3f, g=%.3f, b=%.3f%s)' % (self.r, self.g, self.b, '' if self.is_normal() else ', abnormal')
    
    @staticmethod
    def near_normalize(x: float):
        if (0 - 1e-4) <= x < 0:
            x = 0
        if 1 < x <= (1 + 1e-4):
            x = 1
        return x
    
    @staticmethod
    def is_normal_value(x: float):
        return (0 - 1e-4) <= x <= (1 + 1e-4)
    
    def is_normal(self):
        return (
            self.is_normal_value(self.r) and
            self.is_normal_value(self.g) and
            self.is_normal_value(self.b)
        )
    
    # Construct the most saturated color suitable for display
    def get_chromasample(self):
        gamma = 2.2
        r, g, b = self.r, self.g, self.b
        if r < 0: r = 0
        if g < 0: g = 0
        if b < 0: b = 0
        r = r ** gamma
        g = g ** gamma
        b = b ** gamma
        top = max(r, g, b)
        if top > 0:
            r /= top
            g /= top
            b /= top
        return RGBTriplet(
            r ** (1 / gamma),
            g ** (1 / gamma),
            b ** (1 / gamma)
        )
        
class CMYKCoords():
    def __init__(self, c: float, m: float, y: float, k: float, out_of_gamut: bool):
        self.c = self.near_normalize(c)
        self.m = self.near_normalize(m)
        self.y = self.near_normalize(y)
        self.k = self.near_normalize(k)
        self.out_of_gamut = out_of_gamut
    
    def __repr__(self):
        return 'CMYKCoords(c=%.3f, m=%.3f, y=%.3f, k=%.3f%s)' % (
            self.c, self.m, self.y, self.k, '' if self.is_normal() else ', abnormal'
        )
    
    @staticmethod
    def near_normalize(x: float):
        if (0 - 1e-4) <= x < 0:
            x = 0
        if 1 < x <= (1 + 1e-4):
            x = 1
        return x
    
    @staticmethod
    def is_normal_value(x: float):
        return (0 - 1e-4) <= x <= (1 + 1e-4)
    
    def is_normal(self):
        return (
            not self.out_of_gamut and
            self.is_normal_value(self.c) and
            self.is_normal_value(self.m) and
            self.is_normal_value(self.y) and
            self.is_normal_value(self.k)
        )

if __name__ == '__main__':
    print(SpecSYColor.from_code('54099').get_srgb_triplet())
    print(SpecSYColor.from_code('L4063').get_srgb_triplet())
    print(SpecSYColor.from_code('01').get_srgb_triplet())

    print(SpecSYColor.from_code('54099').get_adobergb_triplet())
    print(SpecSYColor.from_code('L4063').get_adobergb_triplet())
    print(SpecSYColor.from_code('02').get_adobergb_triplet())

    print(SpecSYColor.from_code('54099').get_displayp3_triplet())
    print(SpecSYColor.from_code('L4063').get_displayp3_triplet())
    print(SpecSYColor.from_code('09').get_displayp3_triplet())

    print(SpecSYColor.from_code('54099').get_cmyk_coords())
    print(SpecSYColor.from_code('L4063').get_cmyk_coords())
    print(SpecSYColor.from_code('540CC').get_cmyk_coords())
    print(SpecSYColor.from_code('00').get_cmyk_coords())
    print(SpecSYColor.from_code('0C').get_cmyk_coords())
    print(SpecSYColor.from_code('573C6').get_cmyk_coords())
