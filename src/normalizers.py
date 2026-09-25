import re

def normalize_area(raw_text: str) -> float:
    """
    Converts variations of area texts into standard area_sqft.
    1 Guntha / Gunta = 1089 sq.ft
    1 Acre = 43560 sq.ft
    1 Bigha = 14400 sq.ft (using a common standardization or tagging as required)
    """
    text = raw_text.lower().replace(',', '').strip()

    # Extract the numeric part
    match = re.search(r'([\d\.]+)', text)
    if not match:
        raise ValueError(f"Could not extract numeric value from area: {raw_text}")

    value = float(match.group(1))

    # Identify the unit
    if re.search(r'guntha|gunta', text):
        return value * 1089.0
    elif re.search(r'acre', text):
        return value * 43560.0
    elif re.search(r'bigha', text):
        # standardizing Bigha to a common value, e.g., 14400 sq ft for some regions
        return value * 14400.0
    elif re.search(r'sq\s*ft|square\s*feet|sqft', text):
        return value

    # If no unit is found but it's just a number, assume sqft for now
    return value


def normalize_price(raw_text: str) -> float:
    """
    Converts numeric strings with 'Lakh', 'Lacs', 'Cr', 'Crore', or raw integers into pure numeric INR values.
    """
    text = raw_text.lower().replace(',', '').replace('₹', '').replace('rs', '').strip()

    match = re.search(r'([\d\.]+)', text)
    if not match:
        raise ValueError(f"Could not extract numeric value from price: {raw_text}")

    value = float(match.group(1))

    if re.search(r'cr|crore', text):
        return value * 10_000_000.0
    elif re.search(r'lakh|lac', text):
        return value * 100_000.0

    return value
