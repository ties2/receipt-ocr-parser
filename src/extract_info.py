import re

def parse_information(text_list):
    """
    Takes a list of strings extracted from OCR and uses regex
    to find specific fields like Date, Total, and Merchant.
    """
    data = {
        "merchant_name": "Not Found",
        "date": "Not Found",
        "total_amount": "Not Found"
    }

    # 1. Merchant Name Heuristic: Usually the very first line of a receipt
    if len(text_list) > 0:
        data["merchant_name"] = text_list[0]

    # Combine all text into one giant string for easier regex searching
    full_text = " ".join(text_list)

    # 2. Date Extraction
    # Matches formats like 12/31/2026, 1-5-26, etc.
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
    date_match = re.search(date_pattern, full_text)
    if date_match:
        data["date"] = date_match.group(1)

    # 3. Total Amount Extraction
    # Looks for the word "Total", ignores random characters in between, and finds a price (X.XX)
    total_pattern = r'Total.*?(\d+\.\d{2})'
    total_match = re.search(total_pattern, full_text, re.IGNORECASE)
    if total_match:
        data["total_amount"] = total_match.group(1)

    return data