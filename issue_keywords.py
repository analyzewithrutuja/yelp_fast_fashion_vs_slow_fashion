import csv
import re
from collections import defaultdict

ISSUE_CATEGORIES = {
    "Quality": ["cheap", "cheaply", "thin", "broken", "poor quality", "flimsy", "material", "fell apart", "quality"],
    "Price": ["expensive", "overpriced", "price", "pricey", "cost too much", "not worth"],
    "Service/Staff": ["rude", "employee", "staff", "cashier", "manager", "unhelpful", "customer service"],
    "Fit/Sizing": ["doesn't fit", "didn't fit", "too small", "too big", "too tight", "sizing", "size run"],
    "Returns": ["return policy", "refund", "wouldn't return", "couldn't return", "exchange"],
    "Selection/Stock": ["sold out", "out of stock", "limited selection", "no selection", "poor selection"],
}


def find_categories(text):
    text_lower = text.lower()
    found = set()
    for category, keywords in ISSUE_CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                found.add(category)
                break
    return found


counts = defaultdict(lambda: defaultdict(int))
totals = defaultdict(int)

with open("fashion_clothing_data/fashion_analysis.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["sentiment_label"] != "negative":
            continue
        ft = row["fashion_type"]
        totals[ft] += 1
        cats = find_categories(row["text"] or "")
        for c in cats:
            counts[ft][c] += 1

print(f"{'Category':18s} {'Fast Fashion':>14s} {'Slow Fashion':>14s} {'Mixed Retail':>14s}")
for cat in ISSUE_CATEGORIES:
    row = [cat]
    for ft in ["Fast Fashion", "Slow Fashion", "Mixed Retail"]:
        n = counts[ft][cat]
        pct = 100 * n / totals[ft] if totals[ft] else 0
        row.append(f"{pct:.1f}%")
    print(f"{row[0]:18s} {row[1]:>14s} {row[2]:>14s} {row[3]:>14s}")

print()
print("Total negative reviews:", dict(totals))
