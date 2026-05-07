import cv2
import numpy as np

class ImagePreprocessor:
    def __init__(self):
        pass

    def get_contour_points(self, image):
        """Finds the corners of the receipt/document."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 75, 200)

        # Find contours and keep the largest one
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # If our approximated contour has four points, we found our receipt
            if len(approx) == 4:
                return approx
        return None

    def perspective_transform(self, image, pts):
        """Warps the image to a 'bird's eye view'."""
        rect = pts.reshape(4, 2)

        # Order coordinates: top-left, top-right, bottom-right, bottom-left
        s = rect.sum(axis=1)
        diff = np.diff(rect, axis=1)

        ordered_pts = np.zeros((4, 2), dtype="float32")
        ordered_pts[0] = rect[np.argmin(s)]
        ordered_pts[2] = rect[np.argmax(s)]
        ordered_pts[1] = rect[np.argmin(diff)]
        ordered_pts[3] = rect[np.argmax(diff)]

        (tl, tr, br, bl) = ordered_pts

        # Compute width and height of the new image
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        matrix = cv2.getPerspectiveTransform(ordered_pts, dst)
        return cv2.warpPerspective(image, matrix, (max_width, max_height))

    def final_cleanup(self, image):
        """Binarization to make text pop for the OCR engine."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Using OTSU thresholding which automatically finds the best threshold value
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # BUG FIX: Convert 1-channel binary image back to 3-channel BGR
        # so PaddleOCR does not crash when checking img.shape[2]
        thresh_3_channel = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        return thresh_3_channel

    def process(self, image_path):
        img = cv2.imread(image_path)
        corners = self.get_contour_points(img)

        if corners is not None:
            # Successfully found corners, warp it
            img = self.perspective_transform(img, corners)

        return self.final_cleanup(img)