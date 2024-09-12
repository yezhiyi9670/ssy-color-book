from specsy import SpecSYColor, RGBTriplet, CMYKCoords

class ColorEntry:
    def __init__(self, color: SpecSYColor, name: str):
        self.origin = color
        self.srgb = color.get_srgb_triplet()
        self.adobergb = color.get_adobergb_triplet()
        self.displayp3 = color.get_displayp3_triplet()
        self.cmyk = color.get_cmyk_coords()
        self.name = name
        self.chromasample_flag = False
    
    @staticmethod
    def chromasample_from(color: SpecSYColor, name: str):
        ret = ColorEntry(color, name)
        ret.cmyk = None
        ret.srgb = ret.srgb.get_chromasample()
        ret.adobergb = ret.adobergb.get_chromasample()
        ret.displayp3 = ret.displayp3.get_chromasample()
        ret.chromasample_flag = True
        return ret
    
    @staticmethod
    def get_css_specifier(gamut: str):
        css_color_specifiers = {
            'sRGB': 'srgb',
            'DisplayP3': 'display-p3',
            'AdobeRGB': 'a98-rgb',
        }
        return css_color_specifiers[gamut]
    
    def is_chromasample(self):
        return self.chromasample_flag
    
    def get_triplet(self, gamut: str):
        specifier = self.get_css_specifier(gamut)
        if specifier == 'srgb':
            triplet = self.srgb
        elif specifier == 'display-p3':
            triplet = self.displayp3
        elif specifier == 'a98-rgb':
            triplet = self.adobergb
        else:
            raise NotImplementedError(f'Unexpected css color specifier `{specifier}`')
        return triplet
    
    def css_color_code(self, gamut: str):
        specifier = self.get_css_specifier(gamut)
        triplet = self.get_triplet(gamut)
        if not triplet.is_normal():
            return None
        return 'color(%s %.3f %.3f %.3f)' % (specifier, triplet.r, triplet.g, triplet.b)
    
    def hex_code(self, gamut: str):
        triplet = self.get_triplet(gamut)
        if not triplet.is_normal():
            return None
        return '{:02X}{:02X}{:02X}'.format(*[
            int(round(x * 255))
            for x in (triplet.r, triplet.g, triplet.b)
        ])
        
    def coord_code(self, gamut: str):
        if gamut == 'CMYK':
            if not self.cmyk:
                return None
            return 'cmyk(%.3f %.3f %.3f %.3f)' % (
                self.cmyk.c, self.cmyk.m, self.cmyk.y, self.cmyk.k
            )
        specifier = self.get_css_specifier(gamut)
        triplet = self.get_triplet(gamut)
        return 'color(%s %.3f %.3f %.3f)' % (specifier, triplet.r, triplet.g, triplet.b)
    
    def xyy_coord(self):
        if self.is_chromasample():
            return None
        return 'xyY(%.3f %.3f %.3f)' % self.origin.get_xyy_color().get_value_tuple()

    def ssy_coord(self):
        return 'ssy(%d %.3f %.3f)' % (self.origin.spec, self.origin.saturation, self.origin.Y)

    def is_dark(self):
        return self.origin.Y < 0.25

class HTMLColorCardWriter:
    def __init__(self, filename: str):
        self.fp = open(filename, 'w', encoding='utf-8')
        self.buffer = ''
        self.displayable_count = 0
        self.printable_count = 0
        pass
    
    def is_ok(self):
        return self.fp.writable()
    
    def write(self, content: str):
        self.buffer += content

    '''
    Add color gamut indicator.
    '''
    def gamut_indicator(self, gamut: str):
        ColorEntry.get_css_specifier(gamut)
        self.write(f'''
            <div class="gamut-indicator">
                <div class="gamut-indicator-pic">
                    <span class="gamut-indicator-icon" data-gamut="{gamut}">
                        <svg class="w-3 h-3 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"></path>
                        </svg>
                    </span>
                </div>
                <div class="gamut-indicator-text">{gamut}</div>
            </div>
        ''')
    
    '''
    Add page title
    '''
    def page_title(self, title: str):
        self.write(f'''
            <title>{title}</title>
        ''')
    
    '''
    Add main title of the card.
    '''
    def title(self, title: str, subtitle: str):
        self.write(f'''
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        ''')
    
    def other_editions(self, gamut: str):
        version = open('VERSION', 'r', encoding='utf-8').read().strip()
        self.write(f'''
            <p class="select-color-space">v{version} |
        ''')
        first = True
        for g in ['sRGB', 'DisplayP3', 'AdobeRGB']:
            if first:
                first = False
            else:
                self.write(f''' · ''')
            if g == gamut:
                self.write(f'''<b>{g}</b>''')
            else:
                self.write(f'''<a href="./{g.replace('/', '_')}.html">{g}</a>''')
        self.write('</p>')
            
    def __color_display(self, color: ColorEntry, gamut: str):
        css_color_code = color.css_color_code(gamut)
        coord_srgb, hex_srgb = color.coord_code('sRGB'), color.hex_code('sRGB')
        coord_adobergb, hex_adobergb = color.coord_code('AdobeRGB'), color.hex_code('AdobeRGB')
        coord_displayp3, hex_displayp3 = color.coord_code('DisplayP3'), color.hex_code('DisplayP3')
        coord_cmyk = color.coord_code('CMYK')
        coord_xyy = color.xyy_coord()
        coord_ssy = color.ssy_coord()
        is_chromasample = color.is_chromasample()
        
        if css_color_code and not is_chromasample:
            self.displayable_count += 1
            if color.cmyk and color.cmyk.is_normal():
                self.printable_count += 1
        
        # uses box shadow instead of background color. Ensures correct printing.
        self.write(f'''
            <div class="color-display {
                'chromasample' if is_chromasample else ''
            } {
                'undisplayable' if css_color_code == None else ''
            } {
                'dark' if css_color_code and color.is_dark() else ''
            } {
                'srgb-unavailable' if not color.srgb.is_normal() else ''
            } {
                'displayp3-unavailable' if not color.displayp3.is_normal() else ''
            } {
                'cmyk-unavailable' if (color.cmyk and not color.cmyk.is_normal()) else ''
            }">
                <a
                    aria-label="{color.name}"
                    class="color-display-block" href="javascript:;"
                    style="box-shadow: inset 0 0 0 5em {css_color_code or 'transparent'}"
                    onclick="showColorDetails(this, {'{'}
                        name: '{color.name}',
                        css: '{css_color_code or '--'}',
                        srgb: [{'true' if hex_srgb else 'false'}, '{coord_srgb}', '{hex_srgb or '--'}'],
                        adobergb: [{'true' if hex_adobergb else 'false'}, '{coord_adobergb}', '{hex_adobergb or '--'}'],
                        displayp3: [{'true' if hex_displayp3 else 'false'}, '{coord_displayp3}', '{hex_displayp3 or '--'}'],
                        cmyk: [{'true' if (color.cmyk and color.cmyk.is_normal()) else 'false'}, '{coord_cmyk or '--'}'],
                        xyy: [{'true' if coord_xyy else 'false'}, '{coord_xyy or '--'}'],
                        ssy: [{'true' if coord_ssy else 'false'}, '{coord_ssy or '--'}'],
                        isChromasample: {'true' if is_chromasample else 'false'},
                    {'}'})"
                    ondragstart="return false;"
                >
                </a>
                <div class="color-display-label">{color.name}</div>
            </div>
        ''')
    
    def __color_group_chromasample(self, chromasample: ColorEntry, gamut: str):
        self.__color_display(chromasample, gamut)
    
    def __color_group_plots(self, plots: list[list[ColorEntry]], gamut: str):
        for row in plots:
            self.write(f'''
                <div class="plots-row {'large' if len(row) >= 16 else ''}">
            ''')
            for entry in row:
                if entry:
                    self.__color_display(entry, gamut)
                else:
                    # put a placeholder here
                    self.write('<div class="color-display whitespace"></div>')
            self.write(f'''
                </div>
            ''')
    
    '''
    Add color group.
    '''
    def color_group(self, chromasample: ColorEntry, plots: list[list[ColorEntry]], gamut: str):
        ColorEntry.get_css_specifier(gamut)
        self.write(f'''
            <div class="color-group">
                <div class="chromasample-table">
        ''')
        self.__color_group_chromasample(chromasample, gamut)
        self.write(f'''
                </div>
                <div class="plots-table">
        ''')
        self.__color_group_plots(plots, gamut)
        self.write(f'''
                </div>
            </div>
        ''')
    
    '''
    Write to output file and terminate.
    '''
    def commit(self):
        self.buffer = self.buffer.replace('<!--PRINTABLE_COUNT-->', str(self.printable_count))
        self.buffer = self.buffer.replace('<!--DISPLAYABLE_COUNT-->', str(self.displayable_count))
        template_text = open('assets/template.html', 'r', encoding='utf-8').read()
        self.fp.write(template_text.replace('<!--ROOT_CONTENT-->', self.buffer))
        self.fp.close()
