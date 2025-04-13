def get_month_number(month_text):
    month_variants = {
        "januari": 1, "january": 1, "jan": 1,
        "februari": 2, "february": 2, "feb": 2, "pebruari": 2,
        "maret": 3, "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "mei": 5, "may": 5,
        "juni": 6, "june": 6, "jun": 6,
        "juli": 7, "july": 7, "jul": 7,
        "agustus": 8, "august": 8, "aug": 8, "agt": 8,
        "september": 9, "sept": 9, "sep": 9,
        "oktober": 10, "october": 10, "okt": 10, "oct": 10,
        "november": 11, "nopember": 11, "nov": 11,
        "desember": 12, "december": 12, "des": 12, "dec": 12
    }
    month_text = month_text.lower()
    if month_text in month_variants:
        return month_variants[month_text]
    for key in month_variants.keys():
        if month_text in key or key in month_text:
            return month_variants[key]
    raise ValueError(f"Bulan '{month_text}' tidak dikenali")
