import re

NOISE_PATTERNS = [
    r'^acct_',
    r'^[A-Z0-9_]{15,}$',
    r'^\d+$',
]

def is_noise(text):
    return any(re.match(p, text.strip()) for p in NOISE_PATTERNS)

def parse_information(text_list):
    data = {
        "merchant_name": "Not Found",
        "date": "Not Found",
        "total_amount": "Not Found"
    }

    if not text_list:
        return data

    # 1. Merchant: first clean line in top 5
    for line in text_list[:5]:
        if line.strip() and not is_noise(line):
            data["merchant_name"] = line.strip()
            break

    full_text = " ".join(text_list)

    # 2. Date: month-name format first, then numeric
    date_patterns = [
        r'\b([A-Z][a-z]{2,8}\.?\s*\d{1,2},?\s*(?:19|20)\d{2})\b',
        r'\b(\d{1,2}[./-]\d{1,2}[./-](?:19|20)\d{2}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, full_text)
        if match:
            data["date"] = match.group(1)
            break

    # 3. Total: two-pass search — compound phrases first, then simple keywords
    #    FIX 1: require $ prefix so dates like "Nov.21,2023" never match
    #    FIX 2: \d[\d,]* matches any length (4+ digit amounts like $7139)
    price_pattern = r'\$\s*(\d[\d,]*(?:\.\d{2})?)\s*(?:USD|EUR|GBP)?'

    priority_keywords = ['amount due', 'total due', 'grand total']  # compound first
    fallback_keywords = ['total', 'balance']                        # simple second
    skip_keywords     = ['tendered', 'cash', 'change', 'subtotal',
                         'sub total', 'unit_price', 'quantity']

    def search_total(keywords):
        for i, text in enumerate(text_list):
            lower = text.lower()
            if any(skip in lower for skip in skip_keywords):
                continue
            if any(key in lower for key in keywords):
                context = " ".join(text_list[i:i+3])
                match = re.search(price_pattern, context)
                if match:
                    return match.group(1)
        return None

    # Try priority keywords first, then fall back
    result = search_total(priority_keywords) or search_total(fallback_keywords)
    if result:
        data["total_amount"] = result

    return data