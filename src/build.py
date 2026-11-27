#!/usr/bin/env python3
"""Собирает theme.css из src/theme.src.css: вшивает шрифты, шум, логотип и пиксельные значки.

Запуск из корня репозитория:  python3 src/build.py
"""
import base64
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
ASSETS = SRC / 'assets'


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')


def pixels(rows, fill='black'):
    """Пиксельный рисунок из строк вида '..xx..' → SVG c прямоугольниками 1×1."""
    rects = ''.join(
        f'<rect x="{x}" y="{y}" width="1" height="1"/>'
        for y, row in enumerate(rows) for x, c in enumerate(row) if c == 'x')
    w, h = len(rows[0]), len(rows)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" fill="{fill}">{rects}</svg>')


# крест паттэ 11×11 — маркер списка первого уровня
_top = ['..xxxxxxx..', '...xxxxx...', 'x...xxx...x', 'xx...x...xx', 'xxx..x..xxx']
CROSS = pixels(_top + ['xxxxxxxxxxx'] + _top[::-1])

# галочка Windows 95, 7×7
CHECK = pixels(['......x', '.....xx', 'x...xxx', 'xx.xxx.', 'xxxxx..', '.xxx...', '..x....'])

OUTLINE = '#1c140e'


def folder(fill, hi):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 14">'
            f'<path d="M.5 2.5h5l1.5 1.5h8.5v9.5H.5Z" fill="{fill}" stroke="{OUTLINE}" stroke-width="1"/>'
            f'<path d="M.5 5.5h15" stroke="{hi}" stroke-width="1"/></svg>')


def folder_open(fill, back):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 14">'
            f'<path d="M.5 2.5h5l1.5 1.5h7v2H3.5l-3 7.5Z" fill="{back}" stroke="{OUTLINE}"/>'
            f'<path d="M3.5 6h12l-3 7.5H.5Z" fill="{fill}" stroke="{OUTLINE}"/></svg>')


def note(paper):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 16">'
            f'<path d="M2.5 1.5h6l3 3v10h-9Z" fill="{paper}" stroke="{OUTLINE}"/>'
            f'<path d="M8.5 1.5v3h3M4.5 8h5M4.5 10h5M4.5 12h3" stroke="{OUTLINE}" fill="none" stroke-width=".8"/></svg>')


SVGS = {
    'cross': CROSS,
    'check': CHECK,
    # светлая тема — пергамент
    'folder-light': folder('#e2d3b2', '#f2e9d4'),
    'folder-open-light': folder_open('#e2d3b2', '#c2ad88'),
    'note-light': note('#ece1c6'),
    # тёмная тема — умбра
    'folder-dark': folder('#9a7550', '#bb946a'),
    'folder-open-dark': folder_open('#9a7550', '#73563a'),
    'note-dark': note('#d9cbb0'),
}


def replace(match):
    kind, name = match.group(1), match.group(2)
    if kind == 'FONT':
        return 'data:font/woff2;base64,' + b64((ASSETS / 'fonts' / name).read_bytes())
    if kind == 'IMG':
        mime = 'image/png' if name.endswith('.png') else 'image/webp'
        return f'data:{mime};base64,' + b64((ASSETS / 'img' / name).read_bytes())
    if kind == 'SVG':
        return 'data:image/svg+xml;base64,' + b64(SVGS[name].encode('utf-8'))
    raise KeyError(match.group(0))


def main():
    src = (SRC / 'theme.src.css').read_text(encoding='utf-8')
    out = re.sub(r'\{\{(FONT|IMG|SVG):([^}]+)\}\}', replace, src)
    left = re.findall(r'\{\{[^}]*\}\}', out)
    if left:
        raise SystemExit(f'не подставлено: {left}')
    (ROOT / 'theme.css').write_text(out, encoding='utf-8')
    print(f'theme.css: {len(out.encode("utf-8")) / 1024:.0f} КБ')


if __name__ == '__main__':
    main()
