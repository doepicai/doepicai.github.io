# doepic.ai

Личная витрина проектов. Статический сайт без сборки и без внешних скриптов.

## Дизайн

Сейчас: **Dawn City** — 3D glass поверх слоёв сцены (небо, солнце, три слоя города, вода, стеклянные спрайты). Палитра `#051f39 #28225d #4a2480 #882f8f #c53a9d #e2648f #ff8e80 #ffa4a4`.

Прошлые дизайны восстанавливаются из git:

| Дизайн | Тег | Ветка |
|---|---|---|
| Glass 3D (v1) | `design-glass-v1` | `design/glass-v1` |
| Sunset, плоский (v2) | `design-sunset-v2` | `design/sunset-v2` |

Посмотреть: `git checkout design-sunset-v2` (вернуться: `git checkout main`).
Вернуть на сайт: `git checkout design-sunset-v2 -- index.html img/social.png`, закоммитить и запушить.

## Графика Gemini

Сцена работает и без картинок (векторный запасной вариант). Чтобы подключить рендеры Gemini:

1. Сгенерируйте картинки по промптам из `docs/gemini/PROMPTS.md`.
2. Положите их в `gemini-raw/` (`sky`, `sun`, `city-far`, `city-mid`, `city-near`, `water`, `glass`).
3. `python tools/import_gemini.py` (нужны Pillow, numpy, scipy) вырежет зелёный фон, порежет лист стеклянных объектов на спрайты и запишет `img/scene/*` и `scene.json`.
4. Закоммитьте `img/scene` и `scene.json`. Слои можно добавлять по одному.

## Как добавить проект

Новый объект в массив `PROJECTS` в начале скрипта `index.html` (картинки в `img/`). Релизы подтягиваются из GitHub (`FEEDS`).

## Логотип

`img/logo.svg` (иконка), `favicon.svg`, `img/logo.png`, превью `img/social.png`. Логотип общий для всех дизайнов.
