# Receipt OCR Parser — Project Documentation

**Author:** nirvana  
**Repository:** https://github.com/ties2/receipt-ocr-parser  
**Environment:** Python 3.12, Conda env `rec_ocr`  
**Last Updated:** May 2026

---

## Project Overview

A command-line pipeline that takes a receipt or invoice image, runs OCR on it, and extracts structured data (merchant name, date, total amount) into JSON. Built on PaddleOCR (PaddleX backend) with OpenCV preprocessing.

The pipeline has four sequential stages:

```
Image → Preprocess → OCR → Visual Debug → Parse → JSON Output
```

---

## Environment Setup

```bash
conda activate rec_ocr

# Core dependencies
pip install paddlepaddle
pip install paddleocr
pip install opencv-python-headless
```
---

## Usage

```bash
python main.py --image data/sample_receipts/batch2_1/batch2-0001.jpg
```

**Output:**
- JSON printed to stdout with `merchant_name`, `date`, `total_amount`
- Visual debug image saved to `data/output/debug_result.jpg` (green bounding boxes + red text labels)

---

## Project Structure

```
receipt-ocr-parser/
│
├── main.py                  # Entry point — orchestrates the 4-step pipeline
├── src/
│   ├── preprocess.py        # Image preprocessing (deskew, perspective warp, cleanup)
│   ├── ocr_engine.py        # PaddleOCR wrapper + output format adapter
│   └── extract_info.py      # Regex-based structured data extraction
│
├── data/
│   ├── sample_receipts/     # Input images
│   └── output/              # Debug visualizations saved here
│
└── project_info.md          # This file
```

---

## Script Reference

### `main.py` — Pipeline Orchestrator

Entry point. Wires the four pipeline stages together in sequence.

**Flow:**
1. Instantiates `ImagePreprocessor` and `OCRHandler`
2. Calls `preprocessor.process(img_path)` → preprocessed image array
3. Calls `ocr.read_text(processed_img)` → normalized OCR result
4. Calls `draw_visual_debug(processed_img, result)` → saves annotated image
5. Extracts flat text list from result, calls `parse_information(text_list)` → JSON

**Key design decision:** Text is extracted from the normalized result as `[line[1][0] for line in result[0]]` — this assumes the adapter in `ocr_engine.py` has already converted PaddleX's dict format into the standard `[box, [text, score]]` list format.

**Known fragility:** If the adapter fails silently, `result[0]` is `[[]]` and the list comprehension returns `[]` with no error. Wrap in try/except to surface adapter bugs.

---

### `src/preprocess.py` — Image Preprocessor

Prepares the raw image for OCR via three steps: contour detection, perspective warp, and cleanup.

**Class:** `ImagePreprocessor`

**Methods:**

`get_contour_points(image)` — Finds the four corners of the receipt using Canny edge detection and contour approximation. Returns the largest 4-point contour, or `None` if no receipt boundary is detected.

`perspective_transform(image, pts)` — Warps the image to a flat bird's-eye view using the four corner points. Computes the output dimensions from the real-world distances between corner pairs.

`final_cleanup(image)` — Converts to grayscale and applies light denoising (`fastNlMeansDenoising`). Returns a 3-channel BGR image so PaddleOCR does not crash on `img.shape[2]`.

`process(image_path)` — Top-level method called by `main.py`. Reads the image, resizes if larger than 1500px on any side, runs the three steps above, and returns the processed array.

**Critical lesson learned:** Early versions applied OTSU binarization in `final_cleanup`. This produced a hard black/white image that stripped the gradient information PaddleOCR's neural network relies on, causing OCR to return empty results. Always pass grayscale or color images to deep learning OCR engines never binary.

**Future improvement ideas:**
- Add adaptive contrast enhancement (CLAHE) for low-light receipts
- Handle rotated images that fail the 4-corner contour check
- Add a fallback path when `get_contour_points` returns `None` (currently just skips the warp silently)

---

### `src/ocr_engine.py` — OCR Wrapper

Wraps PaddleOCR and adapts its output format for the rest of the pipeline.

**Class:** `OCRHandler`

**Initialization:**
```python
OCRHandler(lang='en')
```
Uses `PP-OCRv4` explicitly via `ocr_version='PP-OCRv4'` to avoid compatibility issues with the newer PaddleX v5 pipeline on macOS.

**Method: `read_text(img)`**

Calls `self.engine.ocr(img)` and adapts the result into a standard format: a list of `[box, [text, score]]` pairs, wrapped in an outer list → `[normalized_lines]`.

The adapter handles two possible output shapes from PaddleOCR:

- **New PaddleX dict format** (current): `raw_result[0]` is a dict with keys `dt_polys` (bounding boxes) and `rec_texts` (recognized strings). The adapter zips these into the standard format with a dummy score of `1.0`.
- **Old list format** (legacy): `raw_result[0]` is already a list of `[box, [text, score]]` — passed through unchanged.

**Critical lesson learned:** The PaddleX dict format uses the key `rec_texts` (plural). An early version used `rec_text` (no s), which silently returned an empty list from `.get()`, causing the entire pipeline to output nothing despite OCR running successfully. Always verify exact key names against the live debug output.

**Function: `draw_visual_debug(image, ocr_result, save_path)`**

Draws green bounding boxes and red text labels onto the preprocessed image and saves it to `data/output/debug_result.jpg`. Useful for verifying that OCR detected and read each text region correctly.

**Future improvement ideas:**
- Add confidence score threshold filtering (skip low-confidence detections)
- Support batch processing of multiple images
- Log per-line confidence scores alongside extracted text

---

### `src/extract_info.py` — Information Extractor

Uses regex patterns to extract three structured fields from the flat OCR text list.

**Main function:** `parse_information(text_list) → dict`

Returns: `{ "merchant_name": ..., "date": ..., "total_amount": ... }`

**Merchant name extraction:**
Iterates through the first 5 lines and returns the first line that is not noise. Noise is defined by `NOISE_PATTERNS`: account ID prefixes (`acct_`), long alphanumeric codes (15+ chars), or pure digit strings.

**Date extraction:**
Tries two regex patterns in priority order:
1. Month-name format: `Oct.19,2023` / `Nov. 21, 2023`
2. Numeric format: `19/10/2023` / `2023-10-19`

Both patterns require a 4-digit year starting with `19` or `20` to avoid matching prices.

**Total amount extraction:**
Two-pass search — compound keywords (`amount due`, `total due`, `grand total`) are tried before simple ones (`total`, `balance`) to avoid matching column headers like `"Amount"` before the real total line.

The price pattern requires a `$` prefix (`\$\s*(\d[\d,]*(?:\.\d{2})?)`) so that date strings like `Nov.21,2023` are never mistaken for prices. Matches both whole amounts (`$7139`) and decimal amounts (`$7,139.00`).

Lines containing skip keywords (`subtotal`, `tendered`, `cash`, `unit_price`, `quantity`) are excluded from the keyword search.

**Known limitations:**
- Merchant name is only reliable when the store name appears in the first 5 OCR lines. On messy receipts the name may appear lower.
- The `$` requirement in the price pattern means receipts without currency symbols will not match any total.
- Month-name date pattern is English only.

**Future improvement ideas:**
- Add currency-symbol-free price fallback for receipts without `$`
- Extract line items (description, quantity, unit price) into a structured list
- Add multi-language date support
- Use the spatial position of bounding boxes (from `ocr_engine.py`) to find the bottom-right total more reliably instead of keyword matching

---

## Known Issues & Lessons Learned

| Issue | Root Cause | Fix Applied |
|---|---|---|
| `cv2` import fails with `python`/`python3` | Shell alias points to Homebrew Python, not conda env | Remove alias from `~/.zshrc`, use full conda binary path |
| OCR returns `[]` despite models loading | `final_cleanup` applied OTSU binarization, blinding the neural net | Replaced with grayscale + denoise |
| OCR returns `[]` after binarization fix | Adapter used `rec_text` instead of `rec_texts` (missing `s`) | Fixed key name in `ocr_engine.py` |
| Total extracted as `21,202` instead of `7139` | `\d{1,3}` only matches 3 digits; date digits matched as price | Require `$` prefix; use `\d[\d,]*` for any length |
| `cls=True` TypeError | Newer PaddleOCR removed the `cls` argument from `.ocr()` | Removed `cls=True` |
| `paddlepaddle` not found | Base package missing from conda env | `pip install paddlepaddle` |

---

## Future Work

- **Line item extraction:** Parse the full table (description, quantity, unit price, amount) into a list of structured dicts
- **Multi-receipt batch mode:** Process an entire folder and output a CSV
- **Spatial parsing:** Use bounding box coordinates instead of keyword matching to find totals — the bottom-right region of a receipt is almost always the total
- **Confidence filtering:** Discard OCR results below a score threshold to reduce noise in parsing
- **Multi-language support:** Extend date and currency patterns beyond English/USD
- **Better merchant detection:** Cross-reference the first few lines against a known store database or use the largest font text (detectable via bounding box height)