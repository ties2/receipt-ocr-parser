import argparse
from src.preprocess import ImagePreprocessor
from src.ocr_engine import OCRHandler, draw_visual_debug
from src.extract_info import parse_information
import cv2

def main(img_path):
    # 1. Initialize our custom classes
    preprocessor = ImagePreprocessor()
    ocr = OCRHandler(lang='en')

    # 2. Preprocess the image (Deskew and binarize)
    print("Step 1: Preprocessing...")
    processed_img = preprocessor.process(img_path)

    # 3. OCR Detection & Recognition
    print("Step 2: Running OCR...")
    # Using our custom read_text method from OCRHandler
    result = ocr.read_text(processed_img)

    # 4. Visualize the bounding boxes
    print("Step 3: Saving Visual Debugging image...")
    draw_visual_debug(processed_img, result)

    # 5. Information Extraction (Regex logic)
    print("Step 4: Parsing Data...")
    # PaddleOCR's raw output is nested. This loop extracts just the text strings.
    text_list = [line[1][0] for line in result[0]]
    structured_data = parse_information(text_list)

    print("\n--- Final Extracted Data ---")
    import json
    print(json.dumps(structured_data, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to receipt image")
    args = parser.parse_args()
    main(args.image)