# Графика Gemini для doepic.ai (low-poly)

Сцена состоит из лёгких низкополигональных слоёв. Небо и вода рисуются CSS (без картинок).
Картинки генерируются в Gemini (gemini.google.com) через встроенный браузер и принимаются локальным
приёмником (`tools/receiver.py`, описание в README), затем `python tools/import_gemini.py` вырезает фон,
сжимает в WebP и пишет `img/lp/*` и `scene.json`.

Файл в `gemini-raw/` → слой на сайте:

| Файл | Фон | Слой |
|---|---|---|
| `sun-lp` | чисто чёрный | солнце (CSS `screen`) |
| `hills-lp` | синий `#0000FF` | горы |
| `city-far-lp`, `city-near-lp` | синий | два слоя города |
| `shore-lp-spring/summer/autumn/winter` | синий | берег каждого сезона |

Общий префикс: `Low-poly 3D style: clean faceted triangular polygons with flat shading and soft gradients, minimal simple geometry, soft glow, polished render, no text, not pixel art.`
Палитра: navy `#051f39`, indigo `#28225d`, purple `#4a2480`, plum `#882f8f`, magenta `#c53a9d`, rose `#e2648f`, coral `#ff8e80`, blush `#ffa4a4`.

## sun-lp (1:1, на чёрном)
```
A low-poly faceted SUN centered on a PURE BLACK #000000 background, front view, symmetrical: a round disk built from triangular facets in a gradient from hot white-yellow #faffc2 at the center through blush #ffa4a4 and coral #ff8e80 to rose #e2648f and magenta #c53a9d at the rim, surrounded by 12 triangular faceted rays alternating long and short in blush and coral, a soft glow around it, filling about 80 percent of the frame. Nothing else, the background must be perfectly black.
```

## hills-lp (21:5, синий фон)
```
SOLID PURE BLUE #0000FF background (flat chroma-key blue, no gradient, no sky). A low-poly mountain range: three overlapping faceted ridges in hazy indigo #28225d, purple #4a2480 and plum #882f8f, with a soft blush #ffa4a4 light on the facets facing the sunrise, small low-poly pine trees on the slopes, the nearest ridge darkest. All mountains stand on one straight flat baseline at the very bottom edge and touch it, nothing below.
```

## city-far-lp / city-near-lp (21:5, синий фон)
Дальний слой: дымчатые фиолетовые `#882f8f` / `#4a2480` башни (иглы, ступенчатые небоскрёбы, купол, башни-близнецы с мостом, шпили, вантовый мост, кран). Ближний: самые тёмные navy/indigo небоскрёбы, самый высокий справа от центра, колесо обозрения, купол, антенны, много окон-граней в coral и blush, светлая кромка со стороны рассвета. Везде: «All buildings stand on one straight flat baseline at the very bottom edge and touch it, nothing below.»

## shore-lp-spring / summer / autumn / winter (21:4, синий фон)
Низкий берег сбоку, ряд низкополигональных деревьев разной высоты (до 70% кадра), всё стоит на одной ровной нижней кромке:
- spring: цветущие вишни blush/rose, светло-зелёные кусты, лепестки;
- summer: изумрудные и салатовые кроны, плакучая ива, коралловые блики, тростник, цветы;
- autumn: клёны, берёзы, дубы янтарные/золотые/коралловые/красные, тыквы, сухой тростник;
- winter: заснеженные ели и сосны, голые берёзы, заснеженные камни, сосульки, холодный снег с фиолетовыми тенями.
