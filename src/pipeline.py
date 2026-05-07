import cv2
from paddleocr import PaddleOCR
import re
import json

class ReceiptParser:
    def __init__(self):
        # Initialize PaddleOCR (downloads lightweight models automatically)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def preprocess_image(self, image_path):
        # 1. Read image
        img = cv2.imread(image_path)
        # 2. Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 3. Apply adaptive thresholding to clean background noise
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        return thresh

    def extract_text(self, preprocessed_img):
        # Run PaddleOCR
        result = self.ocr.ocr(preprocessed_img, cls=True)
        # Extract just the text strings from the PaddleOCR output list
        extracted_text = [line[1][0] for line in result[0]]
        return extracted_text

    def parse_information(self, text_list):
        data = {"merchant": None, "date": None, "total": None}

        # Heuristic 1: The first line is usually the merchant name
        if text_list:
            data["merchant"] = text_list[0]

        # Combine text for regex searching
        full_text = " ".join(text_list)

        # Heuristic 2: Find Date (MM/DD/YYYY or similar)
        date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', full_text)
        if date_match:
            data["date"] = date_match.group(0)

        # Heuristic 3: Find Total Amount
        # Looks for the word "Total" followed by numbers/decimals
        total_match = re.search(r'Total.*?[^\d]*(\d+\.\d{2})', full_text, re.IGNORECASE)
        if total_match:
            data["total"] = total_match.group(1)

        return data

    def run(self, image_path):
        processed = self.preprocess_image(image_path)
        text = self.extract_text(processed)
        structured_data = self.parse_information(text)
        return json.dumps(structured_data, indent=4)

# Usage
# parser = ReceiptParser()
# print(parser.run("data/sample_receipts/receipt1.jpg"))