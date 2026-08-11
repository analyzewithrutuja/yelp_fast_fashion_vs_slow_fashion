import csv

FILE = "fashion_clothing_data/fashion_analysis.csv"


def credibility(user_review_count):
    try:
        rc = int(user_review_count)
    except (ValueError, TypeError):
        return "normal"
    return "low" if rc <= 1 else "normal"


def main():
    with open(FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["review_credibility"]
        rows = list(reader)

    for row in rows:
        row["review_credibility"] = credibility(row["user_review_count"])

    with open(FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    low = sum(1 for r in rows if r["review_credibility"] == "low")
    print(f"Total rows: {len(rows)}")
    print(f"Low credibility: {low} ({100*low/len(rows):.1f}%)")
    print(f"Normal credibility: {len(rows)-low} ({100*(len(rows)-low)/len(rows):.1f}%)")


if __name__ == "__main__":
    main()
