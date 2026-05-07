import cv2
import numpy as np
from paddleocr import PaddleOCR as BasePaddleOCR

class OCRHandler:
    def __init__(self, lang='en'):
        # Initialize the actual PaddleOCR engine
        # use_angle_cls=True helps detect text that is sideways or upside down
        self.engine = BasePaddleOCR(use_angle_cls=True, lang=lang)

    def read_text(self, img):
        """Runs the OCR and returns raw results."""
        return self.engine.ocr(img)

def draw_visual_debug(image, ocr_result, save_path="data/output/debug_result.jpg"):
    """
    Draws green boxes around detected text and red labels for recognized words.
    This is your visual debugging tool!
    """
    annotated_img = image.copy()

    # If the image is grayscale (binarized), convert to BGR so we can see colors
    if len(annotated_img.shape) == 2:
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_GRAY2BGR)

    for line in ocr_result[0]:
        # PaddleOCR coordinates format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        box = np.array(line[0]).astype(np.int32).reshape((-1, 1, 2))
        text_label = line[1][0]

        # Draw the box (Green)
        cv2.polylines(annotated_img, [box], isClosed=True, color=(0, 255, 0), thickness=2)

        # Put the recognized text (Red)
        cv2.putText(annotated_img, text_label, (box[0][0][0], box[0][0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imwrite(save_path, annotated_img)
    return save_path

