from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str) -> str:
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load image: {e}")

    try:
        text = pytesseract.image_to_string(img)
    except Exception as e:
        raise RuntimeError(f"Tesseract OCR error: {e}")

    return text