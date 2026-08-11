import csv

IN_FILE = "fashion_clothing_data/clothing_businesses.csv"


def classify(categories):
    if "Department Stores" in categories:
        return "Mixed Retail"
    if any(k in categories for k in ["Bespoke Clothing", "Bridal", "Formal Wear"]):
        return "Slow Fashion"
    if any(k in categories for k in ["Women's Clothing", "Men's Clothing", "Children's Clothing"]):
        return "Fast Fashion"
    return "Unclassified"


def main():
    with open(IN_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["fashion_type"]
        rows = list(reader)

    for row in rows:
        row["fashion_type"] = classify(row["categories"])

    with open(IN_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {len(rows)} rows with fashion_type column.")


if __name__ == "__main__":
    main()
