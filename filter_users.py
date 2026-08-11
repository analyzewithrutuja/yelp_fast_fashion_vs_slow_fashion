import json
import csv

OUT_DIR = "fashion_clothing_data"
USER_FILE = "yelp_academic_dataset_user.json"


def collect_user_ids():
    user_ids = set()
    for fname in [f"{OUT_DIR}/clothing_reviews.csv", f"{OUT_DIR}/clothing_tips.csv"]:
        with open(fname, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_ids.add(row["user_id"])
    print(f"Unique user_ids to match: {len(user_ids)}")
    return user_ids


def filter_users(user_ids):
    count = 0
    with open(USER_FILE, encoding="utf-8") as fin, \
         open(f"{OUT_DIR}/clothing_users.csv", "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["user_id", "name", "review_count", "average_stars", "yelping_since", "elite", "fans"])
        for line in fin:
            user = json.loads(line)
            if user.get("user_id") in user_ids:
                writer.writerow([
                    user.get("user_id"), user.get("name"), user.get("review_count"),
                    user.get("average_stars"), user.get("yelping_since"),
                    user.get("elite"), user.get("fans"),
                ])
                count += 1
    print(f"Users matched: {count}")


if __name__ == "__main__":
    ids = collect_user_ids()
    filter_users(ids)
    print("Done.")
