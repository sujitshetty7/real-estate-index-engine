import pytest
from src.normalizers import normalize_area, normalize_price

def test_normalize_area():
    assert normalize_area("5 Guntha") == 5445.0
    assert normalize_area("5,445 sq ft") == 5445.0
    assert normalize_area("0.125 Acre") == 5445.0
    assert normalize_area("10 sqft") == 10.0
    assert normalize_area("1 bigha") == 14400.0

def test_normalize_price():
    assert normalize_price("₹92 Lakh") == 9200000.0
    assert normalize_price("1.10 Cr") == 11000000.0
    assert normalize_price("9500000") == 9500000.0
    assert normalize_price("Rs 5 Lacs") == 500000.0
