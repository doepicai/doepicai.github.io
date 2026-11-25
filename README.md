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

Сцена собрана из слоёв (`img/scene/*`, список в `scene.json`). Если слоя нет, подставляется векторный запасной вариант. Графика сгенерирована в Gemini (gemini.google.com) прямо во встроенном браузере и принята локальным приёмным сервером:

1. `python tools/receiver.py 8777` поднимает приёмник на 127.0.0.1 (печатает токен; принимает только картинки).
2. Страница Gemini не даёт fetch на чужие адреса, поэтому картинка рисуется в canvas, кодируется в base64 и передаётся фрагментом URL на `http://127.0.0.1:8777/recv.html#имя.ext.данные`. Страница приёмника декодирует и загружает файл в `gemini-raw/`.
3. `python tools/import_gemini.py` (Pillow, numpy, scipy) вырезает зелёный фон, режет лист стекла на спрайты и обновляет `img/scene/*` и `scene.json`.

Промпты слоёв: `docs/gemini/PROMPTS.md` (sky, sun, city-far/mid/near, water, glass). Слои можно перегенерировать по одному.
## Как добавить проект

Новый объект в массив `PROJECTS` в начале скрипта `index.html` (картинки в `img/`). Релизы подтягиваются из GitHub (`FEEDS`).

## Логотип

`img/logo.svg` (иконка), `favicon.svg`, `img/logo.png`, превью `img/social.png`. Логотип общий для всех дизайнов.
