import csv

OUT_DIR = "fashion_clothing_data"


def load_business_lookup():
    lookup = {}
    with open(f"{OUT_DIR}/clothing_businesses.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lookup[row["business_id"]] = {
                "business_name": row["name"],
                "city": row["city"],
                "state": row["state"],
                "business_stars": row["stars"],
                "fashion_type": row["fashion_type"],
            }
    return lookup


def load_user_lookup():
    lookup = {}
    with open(f"{OUT_DIR}/clothing_users.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lookup[row["user_id"]] = {
                "user_review_count": row["review_count"],
                "user_average_stars": row["average_stars"],
                "user_elite": row["elite"],
            }
    return lookup


def main():
    biz_lookup = load_business_lookup()
    user_lookup = load_user_lookup()

    out_fields = [
        "source", "business_id", "business_name", "city", "state", "fashion_type",
        "user_id", "user_review_count", "user_average_stars", "user_elite",
        "stars", "date", "text", "useful", "compliment_count",
    ]

    with open(f"{OUT_DIR}/fashion_analysis.csv", "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=out_fields)
        writer.writeheader()

        with open(f"{OUT_DIR}/clothing_reviews.csv", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                biz = biz_lookup.get(row["business_id"], {})
                user = user_lookup.get(row["user_id"], {})
                writer.writerow({
                    "source": "review",
                    "business_id": row["business_id"],
                    "business_name": biz.get("business_name"),
                    "city": biz.get("city"),
                    "state": biz.get("state"),
                    "fashion_type": biz.get("fashion_type"),
                    "user_id": row["user_id"],
                    "user_review_count": user.get("user_review_count"),
                    "user_average_stars": user.get("user_average_stars"),
                    "user_elite": user.get("user_elite"),
                    "stars": row["stars"],
                    "date": row["date"],
                    "text": row["text"],
                    "useful": row["useful"],
                    "compliment_count": "",
                })

        with open(f"{OUT_DIR}/clothing_tips.csv", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                biz = biz_lookup.get(row["business_id"], {})
                user = user_lookup.get(row["user_id"], {})
                writer.writerow({
                    "source": "tip",
                    "business_id": row["business_id"],
                    "business_name": biz.get("business_name"),
                    "city": biz.get("city"),
                    "state": biz.get("state"),
                    "fashion_type": biz.get("fashion_type"),
                    "user_id": row["user_id"],
                    "user_review_count": user.get("user_review_count"),
                    "user_average_stars": user.get("user_average_stars"),
                    "user_elite": user.get("user_elite"),
                    "stars": "",
                    "date": row["date"],
                    "text": row["text"],
                    "useful": "",
                    "compliment_count": row["compliment_count"],
                })

    print("Done writing fashion_analysis.csv")


if __name__ == "__main__":
    main()
