import cv2
import numpy as np
import pytesseract

# Укажи свой путь, если ставил не по умолчанию:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def find_document_contour(image):
    """Ищет самый большой четырёхугольник (лист документа) на фото."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Берём самый большой контур
    biggest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(biggest) < image.shape[0] * image.shape[1] * 0.1:
        return None  # слишком маленький — наверное, мусор

    peri = cv2.arcLength(biggest, True)
    approx = cv2.approxPolyDP(biggest, 0.02 * peri, True)
    if len(approx) == 4:
        return approx.reshape(4, 2)
    return None


def order_points(pts):
    """Сортирует 4 точки: лево-верх, право-верх, право-низ, лево-низ."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]       # верх-лево
    rect[2] = pts[np.argmax(s)]       # низ-право
    rect[1] = pts[np.argmin(diff)]    # верх-право
    rect[3] = pts[np.argmax(diff)]    # низ-лево
    return rect


def perspective_crop(image, pts):
    """Вырезает документ с выравниванием (как скан)."""
    rect = order_points(pts.astype("float32"))
    (tl, tr, br, bl) = rect
    width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    if width < 50 or height < 50:
        return image  # вырезка не удалась — вернём как есть

    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
                   dtype="float32")
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (width, height))


def preprocess_for_ocr(image, mode="clahe"):
    # увеличиваем, пока высота не станет >= 1500 px — Tesseract любит крупный текст
    h, w = image.shape[:2]
    if h < 1500:
        scale = 1500 / h
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if mode == "threshold":
        # старый вариант: жёсткая бинаризация
        return cv2.adaptiveThreshold(gray, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 11)

    # новый вариант: выравниваем освещение мягко, без порогов
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)



def extract_rows(image, mode="clahe") -> list:
    processed = preprocess_for_ocr(image, mode=mode)
    config = "--psm 6"
    text = pytesseract.image_to_string(processed, lang="rus+eng", config=config)

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Достаём все числа из строки (с запятой или точкой)
        numbers = []
        for token in line.split():
            cleaned = token.replace(",", ".").strip(".,;:")
            try:
                numbers.append(float(cleaned))
            except ValueError:
                continue
        if numbers:
            rows.append({"text": line, "numbers": numbers})
    return rows


def process_image(path: str):
    """Полный конвейер: загрузка → вырезка → OCR. Возвращает (обработанное фото, строки)."""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Не удалось открыть файл: {path}")

    contour = find_document_contour(image)
    if contour is not None:
        image = perspective_crop(image, contour)

    rows = extract_rows(image)
    return image, rows