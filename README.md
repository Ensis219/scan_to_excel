# Receipt OCR Scanner — сканер чеков в Excel

Десктоп-приложение на Python для распознавания текста с фото чеков и выгрузки данных в Excel. Работает полностью офлайн, без видеокарты — проверено на Ryzen 5 3500U.

## Возможности
- Загрузка фото чека/накладной (через GUI).
- Поиск документа на фото и выравнивание перспективы (OpenCV).
- Предобработка изображения: масштабирование, выравнивание освещения (CLAHE).
- Распознавание русского и английского текста (Tesseract OCR).
- Извлечение строк и чисел, экспорт в Excel.
- Работает на CPU (без GPU).

## Стек
- Python 3.x
- OpenCV (`cv2`)
- Tesseract OCR + `pytesseract`
- `openpyxl` (для Excel)
- Tkinter (GUI)

## Как запустить
1. Установи Tesseract: [ссылка на установщик](https://github.com/UB-Mannheim/tesseract/wiki) (версия 5.x). При установке выбери языки `eng` и `rus`.
2. Установи зависимости:
   ```bash
   pip install opencv-python pytesseract openpyxl pillow
