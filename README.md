# 🧾 Smart Receipt & Invoice Parser (OCR)

An end-to-end Computer Vision pipeline that extracts structured information (Date, Total Amount, Merchant Name) from messy, real-world photos of receipts and invoices.

## 🚀 Project Overview

Extracting data from documents is a classic Computer Vision problem. This project moves beyond simple digital text reading and tackles the challenges of real-world document AI: perspective distortion, varied lighting, and complex layouts.

This pipeline processes raw images, performs Optical Character Recognition (OCR), and utilizes rule-based heuristics to output structured JSON data.

### 🧠 Under the Hood (SOTA Context)
This project leverages modern approaches to Document AI. While legacy systems relied heavily on Tesseract, this project utilizes **PaddleOCR**, which uses a two-stage deep learning pipeline:
1. **Text Detection:** Inspired by architectures like CRAFT (Character Region Awareness for Text Detection), the model first localizes text bounding boxes at the character/word level.
2. **Text Recognition:** A CRNN (Convolutional Recurrent Neural Network) reads the localized sequences.

*Note: For large-scale enterprise deployments in 2026, specialized vision models like PaddleOCR-VL or Document Foundation Models (like LayoutLMv3) are often used to understand spatial relationships. This project implements a lightweight, edge-deployable alternative using Regex heuristics for layout parsing.*

## ⚙️ The Pipeline

1. **Preprocessing (OpenCV):** Grayscaling, Gaussian blur, and Adaptive Binarization to separate text from noisy backgrounds.
2. **OCR Engine (PaddleOCR):** State-of-the-art open-source text detection and recognition.
3. **Information Extraction:** Regular expressions (Regex) designed to dynamically catch varying date formats and monetary totals regardless of spatial layout.

## 🛠️ Installation

1. Clone the repository:
```bash
git clone [https://github.com/yourusername/receipt-ocr-parser.git](https://github.com/yourusername/receipt-ocr-parser.git)
cd receipt-ocr-parser
# prepare environment
conda create -n rec_ocr python=3.12 -y
conda activate rec_ocr
pip install -r requirements.txt

```