import os
import json
import base64

from specsy import SpecSYColor, RGBTriplet, CMYKCoords
from writer import ColorEntry, HTMLColorCardWriter

MAIN_TITLE = 'Sparks Lab SSY Color Book'

def generate_color_set():
    # spec_list = [ str(x) for x in range(400, 701, 10) ]
    # spec_list += [ 'L' + str(x) for x in range(10, 100, 10) ]
    # hand picked list
    spec_list = [
        '400', '465', '480', '486', '490', '493', '495', '500',
        '510', '550', '560', '565', '570', '573',
        '577', '580', '585', '590', '600', '620', '700',
        'L05', 'L08', 'L12', 'L20', 'L30', 'L45', 'L70'
    ]
    hex_digits = '0123456789ABC'
    
    ret: list[tuple[ColorEntry, list[list[ColorEntry]]]] = []
    
    ret.append((
        ColorEntry.chromasample_from(SpecSYColor.from_code('00'), '0'),
        [[
            ColorEntry(SpecSYColor.from_code('0' + str(x)), '0' + str(x))
            for x in hex_digits
        ]]
    ))
    
    for spec in spec_list:
        chromasample = ColorEntry.chromasample_from(SpecSYColor.from_code(spec + '99'), spec)
        system = []
        ret.append((chromasample, system))
        for y in hex_digits:
            if y == '0' or y == 'C': continue
            stripe = []
            system.append(stripe)
            s_digits = hex_digits
            if y == '1':
                s_digits = '369BC'
            elif y == '2':
                s_digits = '2468ABC'
            elif y == '3':
                s_digits = '2456789ABC'
            for s in hex_digits:
                if s == '0': continue
                code = spec + s + y
                if s in s_digits:
                    stripe.append(ColorEntry(SpecSYColor.from_code(code), code))
                else:
                    stripe.append(None)
                
    return ret

def card_test():
    writer = HTMLColorCardWriter('book/test-card.html')
    writer.gamut_indicator('sRGB')
    writer.page_title(MAIN_TITLE + ' (sRGB)')
    writer.title(MAIN_TITLE, 'Test: Selection Reference Card')
    
    writer.color_group(
        ColorEntry.chromasample_from(SpecSYColor.from_code('54F9'), 'test'),
        [
            [
                ColorEntry(SpecSYColor.from_code('54F9'), '54F9'),
                ColorEntry(SpecSYColor.from_code('5466'), '5466'),
                ColorEntry(SpecSYColor.from_code('L463'), 'L463'),
            ],
            [
                ColorEntry(SpecSYColor.from_code('00'), '00'),
                ColorEntry(SpecSYColor.from_code('01'), '01'),
                ColorEntry(SpecSYColor.from_code('02'), '02'),
                ColorEntry(SpecSYColor.from_code('03'), '03'),
                ColorEntry(SpecSYColor.from_code('04'), '04'),
                ColorEntry(SpecSYColor.from_code('05'), '05'),
                ColorEntry(SpecSYColor.from_code('06'), '06'),
                ColorEntry(SpecSYColor.from_code('07'), '07'),
                ColorEntry(SpecSYColor.from_code('08'), '08'),
                ColorEntry(SpecSYColor.from_code('09'), '09'),
                ColorEntry(SpecSYColor.from_code('0A'), '0A'),
                ColorEntry(SpecSYColor.from_code('0B'), '0B'),
                ColorEntry(SpecSYColor.from_code('0C'), '0C'),
                ColorEntry(SpecSYColor.from_code('0D'), '0D'),
                ColorEntry(SpecSYColor.from_code('0E'), '0E'),
                ColorEntry(SpecSYColor.from_code('0F'), '0F'),
            ]
        ],
        'sRGB'
    )
    
    writer.commit()
    
def card_color_book(color_set: list, gamut: str):
    print(gamut)
    
    # ==== Write HTML book ====
    
    writer = HTMLColorCardWriter(f'book/{gamut.replace("/", "_")}.html')
    writer.gamut_indicator(gamut)
    writer.page_title(MAIN_TITLE + f' ({gamut})')
    writer.title(MAIN_TITLE, f'A device-independent color book, for {gamut} (<!--DISPLAYABLE_COUNT--> colors)')
    
    writer.other_editions(gamut)
    
    for group in color_set:
        writer.color_group(group[0], group[1], gamut)
        
    writer.commit()
    
    # ==== Write JSON palette ====
    
    if gamut == 'AdobeRGB/CMYK': return
    
    json_palette = []
    
    for group in color_set:
        group = group[1]
        for row in group:
            for item in row:
                if item == None: continue
                hex = item.hex_code(gamut)
                if hex == None: continue
                json_palette.append({
                    'colorName': '#' + hex,
                    'company': 0,
                    'name': f'SSY/{gamut} {item.name}'
                })
    
    json_str = json.dumps({
        'm_colorInfos': json_palette
    }, indent='    ')
    open(f'palette/Sparks Lab SSY {gamut}.json', 'w', encoding='utf-8').write(json_str)
    b64_str = base64.encodebytes(json_str.encode(encoding='utf-8'))
    open(f'palette/Sparks Lab SSY {gamut}.scl', 'wb').write(b64_str)

if __name__ == '__main__':
    os.makedirs('./palette', exist_ok=True)
    os.makedirs('./book', exist_ok=True)
    
    color_set = generate_color_set()

    # card_test()
    card_color_book(color_set, 'sRGB')
    card_color_book(color_set, 'DisplayP3')
    card_color_book(color_set, 'AdobeRGB')
    card_color_book(color_set, 'AdobeRGB/CMYK')
    
