"""Готовит служебные шрифты темы. Запускать вручную, если меняются шрифты:

    pip install fonttools brotli
    python3 src/tools/fonts.py

Сборке темы (src/build.py) fontTools не нужен: она берёт готовые woff2 из src/assets/fonts.

1. gothic-extra-*.woff2 — «», …, [], № для готики: в Wolgadeutsche «» нарисованы как "",
   а …, № и [] нет вовсе. Берутся из Ubuntu Mono Bold.
2. initial-blank.woff2 — пустые знаки препинания нулевой ширины. Стоят первыми в шрифтах
   буквицы: если абзац начинается с «Сера», ::first-letter захватывает «С, и без этого
   кавычка вышла бы огромной. Шрифт рисуется с нуля, из чужих шрифтов в нём ничего нет.
"""
import unicodedata
from pathlib import Path

from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

FONTS = Path(__file__).resolve().parents[1] / 'assets' / 'fonts'
# те же диапазоны стоят в unicode-range у «Ars Blank» в theme.src.css
BLANK_RANGES = [(0x21, 0x2F), (0x3A, 0x40), (0x5B, 0x60), (0x7B, 0x7E), (0xA1, 0xBF), (0x2010, 0x205E)]


def extra():
    for part, codes in (('latin', 'U+005B,U+005D,U+00AB,U+00BB,U+2026'), ('cyrillic', 'U+2116')):
        out = FONTS / f'gothic-extra-{part}.woff2'
        subset.main([str(FONTS / f'ubuntu-mono-{part}-700-normal.woff2'), f'--unicodes={codes}',
                     '--flavor=woff2', f'--output-file={out}'])
        print(out.name, out.stat().st_size, 'байт')


def blank():
    cmap = {cp: 'blank' for a, b in BLANK_RANGES for cp in range(a, b + 1)
            if unicodedata.category(chr(cp)).startswith('P')}
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'blank'])
    fb.setupCharacterMap(cmap)
    # у .notdef есть контур: шрифт, где все глифы пустые, браузер отбрасывает как битый
    pen = TTGlyphPen(None)
    pen.moveTo((50, 0)); pen.lineTo((50, 700)); pen.lineTo((450, 700)); pen.lineTo((450, 0)); pen.closePath()
    fb.setupGlyf({'.notdef': pen.glyph(), 'blank': TTGlyphPen(None).glyph()})
    fb.setupHorizontalMetrics({'.notdef': (500, 50), 'blank': (0, 0)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({'familyName': 'Ars Blank', 'styleName': 'Regular', 'psName': 'ArsBlank-Regular',
                       'copyright': 'NOEASY, MIT', 'version': 'Version 1.000'})
    fb.setupOS2(version=4, sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    fb.setupPost()
    fb.font.flavor = 'woff2'
    out = FONTS / 'initial-blank.woff2'
    fb.save(out)
    print(out.name, len(cmap), 'знаков,', out.stat().st_size, 'байт')


if __name__ == '__main__':
    extra()
    blank()
