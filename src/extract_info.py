import re

def parse_information(text_list):
    data = {
        "merchant_name": "Not Found",
        "date": "Not Found",
        "total_amount": "Not Found"
    }

    if not text_list:
        return data

    # 1. Merchant Name: Usually the first 1-2 lines
    data["merchant_name"] = text_list[0]

    full_text = " ".join(text_list)

    # 2. More Robust Date Regex
    # Matches MM/DD/YYYY, DD-MM-YY, YYYY.MM.DD, etc.
    date_pattern = r'(\d{1,4}[./-]\d{1,2}[./-]\d{2,4})'
    date_matches = re.findall(date_pattern, full_text)
    if date_matches:
        data["date"] = date_matches[0]

    # 3. More Robust Total Amount
    # We look for "Total", "Amount", "Due", or "Balance"
    total_keywords = ['total', 'amount', 'due', 'balance', 'grand']

    for i, text in enumerate(text_list):
        # Check if the current line contains a keyword
        if any(key in text.lower() for key in total_keywords):
            # Look at this line and the next 2 lines for a price pattern ($XX.XX)
            context = " ".join(text_list[i:i+3])
            # Matches numbers like 10.00, 1,200.50, etc.
            price_match = re.search(r'(\d+[.,]\d{2})', context)
            if price_match:
                data["total_amount"] = price_match.group(1)
                break # Stop once we find the likely total

    return data