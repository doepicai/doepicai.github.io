# Графика Gemini для doepic.ai

Сайт собран слоями. Пока картинок нет, работает векторный запасной вариант. Каждый слой можно заменить рендером из Gemini.
Сохраните файлы в `gemini-raw/` под указанными именами и запустите `python tools/import_gemini.py`.
Можно добавлять по одному, недостающие слои пропускаются.

**Общий стиль для всех промптов (добавляйте в начало):**

> 3D glassy style: translucent glass and crystal surfaces, soft subsurface glow, glossy specular highlights, volumetric light, rich depth. Cinematic, polished 3D render look. NOT pixel art, NOT flat, no text, no logos, no watermarks.
> Color palette only: deep navy #051f39, indigo #28225d, purple #4a2480, plum #882f8f, magenta #c53a9d, rose #e2648f, coral #ff8e80, blush #ffa4a4.

| Файл | Фон | Как используется |
|---|---|---|
| `sky.png` | сам кадр | небо, самый дальний слой |
| `sun.png` | чисто чёрный | солнце, чёрное становится прозрачным (blend screen) |
| `city-far.png` / `city-mid.png` / `city-near.png` | чисто зелёный `#00FF00` | три слоя города, зелёный вырезается скриптом |
| `water.png` | сам кадр | вода внизу, отражения |
| `glass.png` | чисто чёрный | лист стеклянных объектов, скрипт режет на спрайты |

Форматы: небо и вода 21:9 или шире, города 21:6, солнце и лист объектов 1:1 или 16:9. Чем больше разрешение, тем лучше (от 2560 px по ширине).

---

## sky.png (21:9)

```
Epic dawn sky panorama, 21:9. The sun is just below the horizon and NOT visible as a disc; its glow lights huge layered cloud banks from below in coral #ff8e80, rose #e2648f and blush #ffa4a4. Soft god rays fan upward. The upper third fades to deep navy #051f39 and indigo #28225d with a few tiny stars. Glassy, luminous, volumetric clouds with translucent edges. No ground, no buildings, no water, no sun disc, the bottom 8% is a bright blush horizon glow.
```

## sun.png (1:1, на чёрном)

```
An EPIC cinematic 3D glass SUN centered on a PURE BLACK #000000 background, front view, symmetrical, filling about 80 percent of the frame. A huge round solar disk with a blazing hot white-yellow #faffc2 core, glowing through blush #ffa4a4 and coral #ff8e80 into rose #e2648f and magenta #c53a9d near the edge, under a glossy translucent glass dome with soft specular highlights; fine detail inside: swirling plasma flames, solar granulation, luminous concentric glass rings. NO black ring, NO mechanical parts, NO gap: the disk edge melts into a bright glowing corona. From the corona burst 12 large tapered glass sun rays in the style of a sunrise logo, rounded at the tips, alternating long and short, each ray bright and hot near the sun and fading smoothly to transparent toward its tip, colored blush, coral and rose. Between them dozens of thin long light beams, strong bloom, volumetric god rays, a subtle lens flare, and a wide soft rose halo fading to black. Polished photoreal 3D render, translucent glass, powerful radiant glow. No text, no horizon, no clouds, nothing else, the background must be perfectly black.
```
(Первая версия с «чёрным кольцом» выглядела как кнопка, эта версия принята в сайт.)
## city-far.png (21:6, на зелёном)

```
Panoramic futuristic city skyline, 21:6, on a SOLID PURE GREEN #00FF00 background (flat chroma key, no gradient, no sky, no ground shadow). Distant layer: hazy purple #882f8f and #4a2480 glass towers seen through atmosphere, very diverse silhouettes: slender needles, stepped skyscrapers, glass domes, twin towers with a sky bridge, spires, a cable-stayed bridge with pylons, tower cranes. 3D glassy translucent buildings with faint specular edges and tiny warm windows. All buildings stand on one straight flat baseline at the very bottom edge of the image and touch it.
```

## city-mid.png (21:6, на зелёном)

```
Same panorama format and green #00FF00 chroma-key background. Middle layer of the city: deeper purple #4a2480 to indigo #28225d glass buildings, different layout from the far layer, more varied: curved towers, obelisks, round cylinder towers, buildings with glass domes, sloped roofs, antennas, skybridges, a ferris wheel. Glossy glass facades with soft rim light in blush from the sunrise behind, warm lit windows. Flat baseline at the bottom edge.
```

## city-near.png (21:6, на зелёном)

```
Same format and green #00FF00 chroma-key background. Foreground layer of the city: darkest navy #051f39 and indigo #28225d glass skyscrapers, tall and dramatic, lowest and widest buildings at the edges, many lit windows in coral #ff8e80 and blush #ffa4a4, glossy reflective glass with bright rim light along the edges facing the sunrise, a few rooftop details and antennas. Varied heights and shapes. Flat baseline at the bottom edge.
```

## water.png (21:7)

```
Calm glassy water surface at dawn, 21:7, seen from low angle. The top edge is the bright blush #ffa4a4 horizon line; the water below reflects the glowing coral and rose sky and, softly blurred, the dark skyline silhouettes. A bright vertical sun glitter path in the middle-right (about 68% from the left), fine glassy ripples, gradient down to deep indigo #28225d at the bottom. No sky, no buildings above the horizon, no boats, no text.
```

## glass.png (16:9, на чёрном)

```
A sprite sheet of 8 to 10 separate floating 3D glass objects on a PURE BLACK #000000 background, 16:9, wide spacing between objects so none touch: glass spheres of different sizes, a faceted crystal, a thick glass ring, a shard, a glass cube with rounded corners, a pill shape. Translucent with colored refraction in magenta #c53a9d, coral #ff8e80 and blush #ffa4a4, glossy white specular highlights, soft inner glow. Nothing else, the background must be perfectly black.
```

---

## Природа и сезоны (ключ — синий `#0000FF`, скрипт определяет цвет фона по краям сам)

Общий префикс: `3D glassy style, translucent glass-like leaves and surfaces, soft subsurface glow, glossy specular highlights, polished cinematic 3D render, no text, not pixel art. SOLID PURE BLUE #0000FF background (flat chroma-key blue, no gradient, no sky, no water).`

### hills.png (21:5)
```
Very wide panorama 21:5. Layered misty mountains and forested hills. Three overlapping ridges in hazy indigo #28225d, purple #4a2480 and plum #882f8f with soft atmospheric haze, glassy faceted mountain faces with a soft blush #ffa4a4 rim light as if the sun rises behind, dark pine forests on the slopes, the nearest ridge darkest. All mountains stand on one straight flat baseline at the very bottom edge and touch it, nothing below.
```

### shore-spring / shore-summer / shore-autumn / shore-winter (21:4)
Тот же формат, меняется описание берега: *SPRING* — цветущие вишни в blush `#ffa4a4` и rose `#e2648f`, цветущие кусты, камыш, лепестки; *SUMMER* — густые деревья и плакучая ива, изумрудная листва с коралловыми бликами, светлячки; *AUTUMN* — клёны, берёзы и дубы с янтарной, золотой, коралловой и красной листвой, тыквы, сухой камыш, кружащиеся листья; *WINTER* — заснеженные ели и сосны, голые берёзы с ледяными кристаллами, сосульки, холодный снег с фиолетовыми тенями. Везде: «a low embankment seen from the side, a row of trees of varied heights up to 70 percent of the frame, a thin stone edge at the very bottom, everything stands on one straight flat bottom edge».

### branch-spring / branch-summer / branch-autumn / branch-winter (16:9)
```
A large overhanging <cherry blossom | leafy | maple | frosted> branch entering from the TOP-LEFT corner of the frame and sweeping toward the center, occupying the upper-left half of the image, <season details>, depth of field: far parts softly blurred, near ones sharp. Nothing else, the right and bottom parts of the frame stay empty blue.
```
(Правая ветвь на сайте — зеркальная копия левой.)