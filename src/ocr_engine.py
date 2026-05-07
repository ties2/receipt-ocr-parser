import cv2
import numpy as np
import os
from paddleocr import PaddleOCR as BasePaddleOCR

class OCRHandler:
    def __init__(self, lang='en'):
        # Added ocr_version='PP-OCRv4' to bypass the Mac/v5 bug!
        self.engine = BasePaddleOCR(
            use_angle_cls=True,
            lang=lang,
            ocr_version='PP-OCRv4'
        )

    def read_text(self, img):
        """Runs the OCR and normalizes the output format for our pipeline."""
        raw_result = self.engine.ocr(img)

        # Safety check for empty results
        if not raw_result or raw_result[0] is None:
            return [[]]

        img_res = raw_result[0]
        normalized_lines = []

        # --- ADAPTER: Handle new PaddleX Dictionary Format ---
        if isinstance(img_res, dict) or hasattr(img_res, 'keys'):
            boxes = img_res.get('dt_polys', [])
            texts = img_res.get('rec_text', [])

            # Reconstruct into the standard format our visualizer expects: [box, [text, score]]
            for box, text in zip(boxes, texts):
                normalized_lines.append([box, [text, 1.0]])

        # --- ADAPTER: Handle Old PaddleOCR List Format ---
        elif isinstance(img_res, list):
            normalized_lines = img_res

        return [normalized_lines]

def draw_visual_debug(image, ocr_result, save_path="data/output/debug_result.jpg"):
    """
    Draws green boxes around detected text and red labels for recognized words.
    """
    annotated_img = image.copy()

    # Convert grayscale back to BGR so we can draw colored boxes
    if len(annotated_img.shape) == 2:
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_GRAY2BGR)

    for line in ocr_result[0]:
        # PaddleOCR coordinates format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        box = np.array(line[0]).astype(np.int32).reshape((-1, 1, 2))
        text_label = str(line[1][0])

        # Draw the box (Green)
        cv2.polylines(annotated_img, [box], isClosed=True, color=(0, 255, 0), thickness=2)

        # Put the recognized text (Red)
        cv2.putText(annotated_img, text_label, (box[0][0][0], box[0][0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Ensure the output directory exists before saving!
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, annotated_img)
    return save_path