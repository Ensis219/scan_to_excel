import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from ocr_utils import process_image
from openpyxl import Workbook


class ScanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Скан накладных — фото в Excel")
        self.root.geometry("640x560")

        self.image = None
        self.rows = []

        tk.Button(root, text="📷 Выбрать фото", command=self.load_photo,
                  font=("Arial", 12, "bold"), bg="#007ACC", fg="white").pack(fill="x", padx=10, pady=(10, 5))

        self.preview_label = tk.Label(root, bg="#222222")
        self.preview_label.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Button(root, text="📊 Распознать и сохранить в Excel",
                  command=self.process, font=("Arial", 11),
                  bg="#4CAF50", fg="white").pack(fill="x", padx=10, pady=(0, 5))

        self.status = tk.Label(root, text="Готов", anchor="w", fg="gray")
        self.status.pack(fill="x", padx=12)

    def load_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.jpeg *.png")])
        if not path:
            return
        try:
            self.image = cv2.imread(path)
            self.show_preview(path)
            self.status.config(text=f"Загружено: {os.path.basename(path)}. Теперь нажми «Распознать».")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_preview(self, path):
        img = Image.open(path)
        img.thumbnail((600, 380))
        self.tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.tk_img)

    def process(self):
    if self.image is None:
        messagebox.showwarning("Нет фото", "Сначала выбери фото!")
        return
    self.status.config(text="Обрабатываю... распознавание может занять 5–15 секунд.")
    self.root.update()

    try:
        from ocr_utils import extract_rows
        self.rows = extract_rows(self.image)
        if not self.rows:
            messagebox.showinfo("Пусто", "Текст не распознан. Попробуй фото с лучшим освещением.")
            self.status.config(text="Готов")
            return
        if not any(r["numbers"] for r in self.rows):
            messagebox.showinfo("Без чисел", "Текст распознан, но чисел на фото не найдено. Сохраняю только текст.")
        self.save_excel()
    except Exception as e:
        messagebox.showerror("Ошибка распознавания", str(e))
        self.status.config(text="Ошибка")

    def save_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Распознано"
        ws.append(["Текст строки", "Числа"])
        for row in self.rows:
            ws.append([row["text"], ", ".join(str(n) for n in row["numbers"])])

        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel", "*.xlsx")])
        if path:
            wb.save(path)
            self.status.config(text=f"✅ Сохранено: {path}")

    # --- Копирование превью не нужно, но числа можно скопировать ---
    # (полный конвейер с вырезкой в find_document_contour используется при загрузке)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScanApp(root)
    root.mainloop()
