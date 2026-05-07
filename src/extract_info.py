import re

def parse_information(text_list):
    data = {
        "merchant_name": "Not Found",
        "date": "Not Found",
        "total_amount": "Not Found"
    }

    if not text_list:
        return data

    # 1. Merchant Name: Longest of first 3 lines avoids noise on line 0
    data["merchant_name"] = max(text_list[:3], key=len)

    full_text = " ".join(text_list)

    # 2. Date: Anchored pattern, realistic year, won't match prices
    date_pattern = r'\b(\d{1,2}[./-]\d{1,2}[./-](?:19|20)\d{2}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b'
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        data["date"] = date_matches[0]

    # 3. Total: Priority-ordered keywords, skip payment lines, robust price pattern
    total_keywords = ['grand total', 'total due', 'total', 'due', 'balance', 'amount']
    skip_keywords  = ['tendered', 'cash', 'change', 'subtotal', 'tax']

    for i, text in enumerate(text_list):
        lower = text.lower()
        if any(skip in lower for skip in skip_keywords):
            continue
        if any(key in lower for key in total_keywords):
            context = " ".join(text_list[i:i+3])
            price_match = re.search(r'\$?\s*(\d{1,3}(?:,\d{3})*\.\d{2})', context)
            if price_match:
                data["total_amount"] = price_match.group(1)
                break

    return data