# Screen OCR

A lightweight Python tool that lets you select any region of your screen and instantly extract text from it using OCR.

## How It Works

1. Run the script
2. A translucent overlay appears over your entire screen
3. Click and drag to select a region containing text
4. The selected area is captured and processed with Tesseract OCR
5. Extracted text is printed to your terminal

Press **Escape** at any time to cancel the selection.

## Requirements

- **Python 3.8+**
- **Tesseract OCR** installed on your system

### Install Tesseract

```
winget install UB-Mannheim.TesseractOCR
```

Or download directly from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

The script auto-detects the default Windows install path (`C:\Program Files\Tesseract-OCR\tesseract.exe`). If Tesseract is on your PATH, it works anywhere.

### Install Python Dependencies

```
pip install Pillow pytesseract
```

## Usage

```
python screen_ocr.py
```

Example output:

```
Select a region on screen (press Escape to cancel)...

--- Extracted Text ---
The quick brown fox jumps over the lazy dog.
--- End ---
```

## Running Tests

```
pip install pytest
python -m pytest test_screen_ocr.py -v
```

All tests are fully mocked and run without a display or Tesseract installed.

## License

MIT
