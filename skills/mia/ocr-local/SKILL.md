---
name: ocr-local
description: "Локальное распознавание текста с изображений через Tesseract OCR (rus+eng). Использовать когда Сергей отправляет картинку с текстом и просит прочитать."
version: 1.0.0
category: mia
---

# OCR Local — распознавание текста с картинок

Когда Сергей присылает изображение с текстом и просит его прочитать, используется локальный Tesseract OCR.

## Принцип работы

1. Изображение сохраняется как файл на диск (в `/home/mia/Mia/image_cache/`)
2. Python-скрипт с `pytesseract` + `PIL` извлекает текст
3. Результат возвращается Сергею как есть — без обработки, без анализа, без комментариев

## Команда

```bash
cd /home/mia/Mia/image_cache && python3 << 'PYEOF'
import pytesseract
from PIL import Image

img = Image.open('<имя_файла>')
print(f"Image size: {img.size}, mode: {img.mode}")
text = pytesseract.image_to_string(img, lang='rus+eng')
print("=== OCR RESULT ===")
print(text)
print("=== END ===")
PYEOF
```

## Требования

- `tesseract-ocr` — установлен системно (apt)
- `tesseract-ocr-rus` — пакет русского языка
- `pytesseract` — Python-обёртка (pip)
- `PIL` (Pillow) — для открытия изображений

## Pitfalls

- Tesseract не идеален — символы могут распознаться с ошибками. Передавать как есть, не додумывать
- Если текст нечитаемый — честно сказать «Tesseract не справился, вот сырой результат», НЕ придумывать
- Работает с RGB-изображениями. Если другой формат — конвертировать через Pillow
- Изображения из Telegram могут сохраняться в `/tmp/` как HTML-файлы с расширением `.jpg` (баг Hermes). Настоящие изображения лежат в `/home/mia/Mia/image_cache/`
