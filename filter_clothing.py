import json
import csv

CATEGORY_KEYWORDS = [
    "Women's Clothing",
    "Men's Clothing",
    "Children's Clothing",
    "Bespoke Clothing",
    "Bridal",
    "Formal Wear",
]

# Businesses that only qualify via "Bridal" but are actually hair/beauty salons
# offering bridal hair & makeup (no actual clothing category) get excluded.
BEAUTY_KEYWORDS = [
    "Hair Salons", "Hair Stylists", "Makeup Artists", "Nail Salons",
    "Barbers", "Blow Dry/Out Services", "Eyelash Service",
]
ACTUAL_CLOTHING_KEYWORDS = [
    "Women's Clothing", "Men's Clothing", "Children's Clothing",
    "Bespoke Clothing", "Formal Wear",
]

BUSINESS_FILE = "yelp_academic_dataset_business.json"
REVIEW_FILE = "yelp_academic_dataset_review.json"
TIP_FILE = "yelp_academic_dataset_tip.json"
CHECKIN_FILE = "yelp_academic_dataset_checkin.json"

OUT_DIR = "fashion_clothing_data"


def matches_clothing(categories):
    if not categories:
        return False
    if not any(keyword in categories for keyword in CATEGORY_KEYWORDS):
        return False
    is_beauty_tagged = any(k in categories for k in BEAUTY_KEYWORDS)
    has_actual_clothing = any(k in categories for k in ACTUAL_CLOTHING_KEYWORDS)
    if is_beauty_tagged and not has_actual_clothing:
        return False
    return True


def filter_business():
    business_ids = set()
    rows = []
    with open(BUSINESS_FILE, encoding="utf-8") as f:
        for line in f:
            biz = json.loads(line)
            if matches_clothing(biz.get("categories")):
                business_ids.add(biz["business_id"])
                rows.append({
                    "business_id": biz["business_id"],
                    "name": biz.get("name"),
                    "city": biz.get("city"),
                    "state": biz.get("state"),
                    "stars": biz.get("stars"),
                    "review_count": biz.get("review_count"),
                    "is_open": biz.get("is_open"),
                    "categories": biz.get("categories"),
                    "attributes": json.dumps(biz.get("attributes")),
                })

    with open(f"{OUT_DIR}/clothing_businesses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open(f"{OUT_DIR}/clothing_business_ids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(business_ids)))

    print(f"Businesses matched: {len(business_ids)}")
    return business_ids


def filter_reviews(business_ids):
    count = 0
    with open(REVIEW_FILE, encoding="utf-8") as fin, \
         open(f"{OUT_DIR}/clothing_reviews.csv", "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["review_id", "business_id", "user_id", "stars", "useful", "funny", "cool", "date", "text"])
        for line in fin:
            rev = json.loads(line)
            if rev.get("business_id") in business_ids:
                writer.writerow([
                    rev.get("review_id"), rev.get("business_id"), rev.get("user_id"),
                    rev.get("stars"), rev.get("useful"), rev.get("funny"), rev.get("cool"),
                    rev.get("date"), rev.get("text"),
                ])
                count += 1
    print(f"Reviews matched: {count}")


def filter_tips(business_ids):
    count = 0
    with open(TIP_FILE, encoding="utf-8") as fin, \
         open(f"{OUT_DIR}/clothing_tips.csv", "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["business_id", "user_id", "date", "compliment_count", "text"])
        for line in fin:
            tip = json.loads(line)
            if tip.get("business_id") in business_ids:
                writer.writerow([
                    tip.get("business_id"), tip.get("user_id"), tip.get("date"),
                    tip.get("compliment_count"), tip.get("text"),
                ])
                count += 1
    print(f"Tips matched: {count}")


def filter_checkins(business_ids):
    count = 0
    with open(CHECKIN_FILE, encoding="utf-8") as fin, \
         open(f"{OUT_DIR}/clothing_checkins.csv", "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["business_id", "dates"])
        for line in fin:
            chk = json.loads(line)
            if chk.get("business_id") in business_ids:
                writer.writerow([chk.get("business_id"), chk.get("date")])
                count += 1
    print(f"Checkins matched: {count}")


if __name__ == "__main__":
    ids = filter_business()
    filter_reviews(ids)
    filter_tips(ids)
    filter_checkins(ids)
    print("Done.")
