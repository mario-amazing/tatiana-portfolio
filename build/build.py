#!/usr/bin/env python3
"""Собирает index.html портфолио из build/template.html.

Ролики и их постеры лежат в clips/ и подставляются относительными ссылками —
поэтому страница весит меньше мегабайта, а видео грузится только по нажатию play.
Шрифты, портрет и скриншот сайта вшиваются прямо в страницу как data URI:
внешних запросов у страницы нет вообще.

    python3 build/build.py

После сборки: git add -A && git commit && git push — GitHub Pages подхватит сам.
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'build' / 'assets'
TEMPLATE = ROOT / 'build' / 'template.html'
OUT = ROOT / 'index.html'

# Порядок роликов в разделах. Имя файла = clips/<имя>.mp4 + clips/<имя>.jpg (постер).
CLIP_GROUPS = {
    '__CLIPS_MASSAGE__': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'],
    '__CLIPS_SWEETS__': ['c1', 'c2', 'c3', 'c4', 'c5'],
    '__CLIPS_OTHER__': ['o1', 'o2', 'o3', 'o4', 'o5'],
}

INLINE_ASSETS = {
    '__FONT_UNB_CY__': 'fonts/Unbounded-Cyrillic.woff2',
    '__FONT_UNB_LAT__': 'fonts/Unbounded-Latin.woff2',
    '__FONT_NUN_REG__': 'fonts/Nunito-Regular.woff2',
    '__FONT_NUN_BOLD__': 'fonts/Nunito-Bold.woff2',
    '__IMG_PORTRAIT__': 'portrait.jpg',
    '__IMG_SITE__': 'site_cert.jpg',
}

HEAD = (
    '<!doctype html>\n<html lang="ru">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="theme-color" content="#0e1311">\n'
)


def b64(path):
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode('ascii')


def main():
    html = TEMPLATE.read_text(encoding='utf-8')

    for placeholder, names in CLIP_GROUPS.items():
        blocks = []
        for name in names:
            for suffix in ('.mp4', '.jpg'):
                target = ROOT / 'clips' / f'{name}{suffix}'
                assert target.exists(), f'нет файла {target}'
            blocks.append(f'''<figure class="clip">
          <video controls playsinline preload="none" poster="clips/{name}.jpg">
            <source src="clips/{name}.mp4" type="video/mp4">
          </video>
        </figure>''')
        html = html.replace(placeholder, '\n        '.join(blocks))

    for placeholder, relative in INLINE_ASSETS.items():
        html = html.replace(placeholder, b64(ASSETS / relative))

    for token in ('__FONT_', '__IMG_', '__CLIPS_'):
        assert token not in html, f'в шаблоне осталась незаполненная метка {token}'

    head_end, _, rest = html.partition('</style>')
    html = HEAD + head_end + '</style>\n</head>\n<body>\n' + rest + '\n</body>\n</html>\n'

    OUT.write_text(html, encoding='utf-8')
    print(f'собрано {OUT} — {len(html) / 1024 / 1024:.2f} МБ, роликов: '
          f'{sum(len(v) for v in CLIP_GROUPS.values())}')


if __name__ == '__main__':
    main()
