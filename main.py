import os
import json
import base64

from specsy import SpecSYColor, RGBTriplet, CMYKCoords
from writer import ColorEntry, EmptyEntry, HTMLColorCardWriter

MAIN_TITLE = 'Sparks Lab SSY Color Book'

def generate_color_set():
    # spec_list = [ str(x) for x in range(400, 701, 10) ]
    # spec_list += [ 'L' + str(x) for x in range(10, 100, 10) ]
    # hand picked list
    spec_list = [
        '400', '465', '480', '486', '490', '493', '496', '500',
        '507', '550', '560', '565', '570', '573',
        '577', '580', '585', '590', '595', '600', '620',
        'L03', 'L07', 'L12', 'L20', 'L30', 'L45', 'L70'
    ]
    y_digits = '0123456789ABC'
    y_aug_digits = '0nr1s2t3456789AyBzC'
    
    ret: list[tuple[ColorEntry, list[list[ColorEntry]]]] = []
    
    ret.append((
        ColorEntry.chromasample_from(SpecSYColor.from_code('00'), '0'),
        [[
            ColorEntry(SpecSYColor.from_code('0' + str(x)), '0' + str(x), x not in y_digits)
            for x in y_aug_digits
        ]]
    ))
    
    for spec in spec_list:
        chromasample = ColorEntry.chromasample_from(SpecSYColor.from_code(spec + 'CC'), spec)
        system = []
        ret.append((chromasample, system))
        for y in y_aug_digits:
            if y == '0' or y == 'C': continue
            stripe = []
            system.append(stripe)
            s_unfiltered_digits = '0123456789ABC'
            s_unfiltered_aug_digits = '0r1s2t3456789ABC'
            s_digits = s_unfiltered_digits
            s_aug_digits = s_unfiltered_aug_digits
            if y == 'n':
                s_aug_digits = '13456789ABC'
            elif y == 'r':
                s_aug_digits = '13456789ABC'
            elif y == '1':
                s_digits = '369BC'
                s_aug_digits = '13456789ABC'
            elif y == 's':
                s_aug_digits = '123456789ABC'
            elif y == '2':
                s_digits = '2468ABC'
                s_aug_digits = '123456789ABC'
            elif y == 't':
                s_aug_digits = '12t3456789ABC'
            elif y == '3':
                s_digits = '2456789ABC'
                s_aug_digits = '1s2t3456789ABC'
            for s in s_unfiltered_aug_digits:
                if s == '0': continue
                code = spec + s + y
                current_is_aug = y not in y_digits or s not in s_digits
                if s in s_aug_digits:
                    # Displayable slot
                    stripe.append(ColorEntry(SpecSYColor.from_code(code), code, current_is_aug))
                else:
                    # Definitely empty slot
                    stripe.append(EmptyEntry(current_is_aug))
                if s in s_unfiltered_digits and current_is_aug:
                    # Complementary for filtered-out cell in non-augmentation mode
                    stripe.append(EmptyEntry('counter'))

            stripe.append(EmptyEntry('counter'))
                
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
                ColorEntry(SpecSYColor.from_code('54F9'), '54F9', False),
                ColorEntry(SpecSYColor.from_code('5466'), '5466', False),
                ColorEntry(SpecSYColor.from_code('L463'), 'L463', False),
            ],
            [
                ColorEntry(SpecSYColor.from_code('00'), '00', False),
                ColorEntry(SpecSYColor.from_code('01'), '01', False),
                ColorEntry(SpecSYColor.from_code('02'), '02', False),
                ColorEntry(SpecSYColor.from_code('03'), '03', False),
                ColorEntry(SpecSYColor.from_code('04'), '04', False),
                ColorEntry(SpecSYColor.from_code('05'), '05', False),
                ColorEntry(SpecSYColor.from_code('06'), '06', False),
                ColorEntry(SpecSYColor.from_code('07'), '07', False),
                ColorEntry(SpecSYColor.from_code('08'), '08', False),
                ColorEntry(SpecSYColor.from_code('09'), '09', False),
                ColorEntry(SpecSYColor.from_code('0A'), '0A', False),
                ColorEntry(SpecSYColor.from_code('0B'), '0B', False),
                ColorEntry(SpecSYColor.from_code('0C'), '0C', False),
                ColorEntry(SpecSYColor.from_code('0D'), '0D', False),
                ColorEntry(SpecSYColor.from_code('0E'), '0E', False),
                ColorEntry(SpecSYColor.from_code('0F'), '0F', False),
            ]
        ],
        'sRGB'
    )
    
    writer.commit('sRGB')
    
def card_color_book(color_set: list, edition: str):
    print('Writing book', edition)
    
    gamut = edition
    filter_cmyk = False
    if edition.endswith('/CMYK'):
        gamut = edition[:-5]
        filter_cmyk = True
    
    # ==== Write HTML book ====
    
    writer = HTMLColorCardWriter(f'book/{edition.replace("/", "_")}.html')
    writer.gamut_indicator(gamut)
    writer.page_title(MAIN_TITLE + f' ({edition})')
    writer.title(
        MAIN_TITLE,
        f'For {gamut} displays (<span class="count-non-aug"><!--PRINTABLE_COUNT-->/<!--DISPLAYABLE_COUNT--></span><span class="count-aug"><!--PRINTABLE_COUNT_AUG-->/<!--DISPLAYABLE_COUNT_AUG--></span> colors)'
    )
    
    writer.edition_switcher(edition)
    writer.set_filter_cmyk(filter_cmyk)
    
    for group in color_set:
        writer.color_group(group[0], group[1], gamut)
        
    writer.commit(gamut)
    
    # ==== Write JSON palette ====
    
    if filter_cmyk:
        return
    
    json_palette = []
    
    for group in color_set:
        group = group[1]
        for row in group:
            for item in row:
                if isinstance(item, EmptyEntry): continue
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
    
    # ==== Write text palette ====
    
    text_palette = ''
    for group in color_set:
        group = group[1]
        for row in group:
            for item in row:
                if isinstance(item, EmptyEntry): continue
                triplet = item.get_triplet(gamut)
                if not triplet.is_normal(): continue
                triplet = [
                    int(round(item * 255))
                    for item in [ triplet.r, triplet.g, triplet.b ]
                ]
                text_palette += (
                    f'{triplet[0]} {triplet[1]} {triplet[2]} SSY/{gamut} {item.name}\n'
                )

    open(f'palette/Sparks Lab SSY {gamut}.gpl', 'w', encoding='utf-8').write(text_palette)

if __name__ == '__main__':
    os.makedirs('./palette', exist_ok=True)
    os.makedirs('./book', exist_ok=True)
    
    print('Generating color set')
    
    color_set = generate_color_set()

    # card_test()
    card_color_book(color_set, 'sRGB')
    card_color_book(color_set, 'DisplayP3')
    card_color_book(color_set, 'AdobeRGB')
