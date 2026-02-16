import sys
import ctypes
import tkinter as tk
from PIL import ImageGrab
import pytesseract

# Make process DPI-aware so coordinates match physical screen pixels
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# Auto-detect Tesseract on Windows if not on PATH
import shutil
import os

if not shutil.which("tesseract"):
    win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(win_path):
        pytesseract.pytesseract.tesseract_cmd = win_path
    else:
        print("Error: Tesseract OCR not found. Install it from:")
        print("  https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)


class RegionSelector:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.bbox = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(cursor="cross")

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=2
        )

    def on_drag(self, event):
        if self.rect:
            # Use canvas-relative coords for drawing
            sx = self.start_x - self.root.winfo_rootx()
            sy = self.start_y - self.root.winfo_rooty()
            self.canvas.coords(self.rect, sx, sy, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x_root)
        y1 = min(self.start_y, event.y_root)
        x2 = max(self.start_x, event.x_root)
        y2 = max(self.start_y, event.y_root)

        if x2 - x1 > 5 and y2 - y1 > 5:
            self.bbox = (x1, y1, x2, y2)

        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.bbox


def main():
    print("Select a region on screen (press Escape to cancel)...")

    selector = RegionSelector()
    bbox = selector.run()

    if bbox is None:
        print("No region selected.")
        sys.exit(0)

    # Hide the overlay fully before capturing
    screenshot = ImageGrab.grab(bbox=bbox)
    text = pytesseract.image_to_string(screenshot).strip()

    if text:
        print("\n--- Extracted Text ---")
        print(text)
        print("--- End ---")
    else:
        print("No text detected in the selected region.")


if __name__ == "__main__":
    main()
