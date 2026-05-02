# ChampSim Automation Scripts (HW4)

Этот репозиторий содержит набор Python-скриптов для полной автоматизации экспериментов в симуляторе микроархитектуры [ChampSim](https://github.com/ChampSim/ChampSim). 

Проект выполнен в рамках домашнего задания по курсу «Введение в архитектуру вычислительных систем» и направлен на исследование влияния политик замещения (LRU, SHIP) и аппаратного префетчинга (SPP) на производительность L2-кэша при различных конфигурациях (sets/ways).

## Что делают эти скрипты?
Пайплайн разбит на 4 этапа:
1. **Автоматическая конфигурация и сборка** 15 различных бинарных файлов ChampSim (комбинации политик и размеров кэша от 128KB до 1024KB).
2. **Параллельный запуск симуляций** (45 тестов) с контролем пула потоков для предотвращения зависания системы.
3. **Парсинг логов (RegEx)**, расчет метрики L2 Hit Rate (включая геометрическое среднее по трассам) и экспорт данных в `JSON`.
4. **Построение графика** результатов с помощью `matplotlib`.

---

## Подготовка окружения (Установка ChampSim)

Для работы скриптов требуется настроенный репозиторий ChampSim и скачанные трассы.

**1. Клонирование и настройка симулятора:**
```bash
git clone --recursive [https://github.com/ChampSim/ChampSim.git](https://github.com/ChampSim/ChampSim.git)
cd ChampSim
vcpkg/bootstrap-vcpkg.sh
vcpkg/vcpkg install
```
**2. Скачивание трасс (SPEC CPU2006):**
В рамках данного исследования используются 3 трассы с интенсивной нагрузкой на память (bwaves, gobmk, leslie3d). Скачайте их в корень папки ChampSim:

```bash
wget [https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/603.bwaves_s-1080B.champsimtrace.xz](https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/603.bwaves_s-1080B.champsimtrace.xz)
wget [https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/445.gobmk-36B.champsimtrace.xz](https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/445.gobmk-36B.champsimtrace.xz)
wget [https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/437.leslie3d-271B.champsimtrace.xz](https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu/437.leslie3d-271B.champsimtrace.xz)
```
(Примечание: Если wget выдает ошибку тайм-аута, используйте прокси или скачайте файлы вручную в браузере). Вы можете использовать любые другие трассы, но для этого нужно поменять их названия в скрипте.

---

## Как запускать скрипты
Важно: Скопируйте все Python-скрипты из этого репозитория в корневую папку симулятора ChampSim/, так как они используют относительные пути к файлам конфигурации и бинарникам.

Для работы последнего скрипта потребуется установить библиотеку для графиков:

```bash
pip3 install matplotlib
```
**Шаг 1**: Сборка бинарных файлов
```bash
python3 build_all.py
```
Скрипт автоматически модифицирует champsim_config.json и параллельно (используя все ядра процессора make -j) компилирует 15 конфигураций симулятора. Исполняемые файлы сохраняются в директорию bin/.

**Шаг 2**: Запуск симуляций
```bash
python3 run_sims.py
```
Скрипт параллельно запускает 45 симуляций (15 конфигураций × 3 трассы) с параметрами:

warmup-instructions: 50 000 000

simulation-instructions: 100 000 000

Количество одновременно работающих потоков ограничено (по умолчанию MAX_WORKERS = 4 или 6, чтобы не перегружать систему). Все логи сохраняются в автоматически создаваемую папку results/.

**Шаг 3**: Сбор и анализ статистики
```bash
python3 analyze_results.py
```
Скрипт анализирует текстовые логи в папке results/, находит значения TOTAL ACCESS и HIT для L2C, высчитывает L2 Hit Rate и геометрическое среднее по трем трассам. Результат структурируется и экспортируется в файл l2_hit_rates.json.

**Шаг 4**: Визуализация
```bash
python3 plot_results.py
```
Скрипт считывает подготовленный JSON и генерирует график зависимости L2 Hit Rate от размера и геометрии кэша (sets/ways). Итоговое изображение сохраняется как l2_hit_rate_chart.png.