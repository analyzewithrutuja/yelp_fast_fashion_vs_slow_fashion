import json
import csv
from collections import defaultdict

with open("fashion_clothing_data/clothing_business_ids.txt", encoding="utf-8") as f:
    ids = set(l.strip() for l in f if l.strip())

fashion_type_lookup = {}
with open("fashion_clothing_data/clothing_businesses.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fashion_type_lookup[row["business_id"]] = row["fashion_type"]


def parse_hours(hours_dict):
    if not hours_dict:
        return None
    total = 0.0
    open_days = 0
    for day, span in hours_dict.items():
        if not span:
            continue
        try:
            start, end = span.split("-")
            sh, sm = [int(x) for x in start.split(":")]
            eh, em = [int(x) for x in end.split(":")]
        except ValueError:
            continue
        start_min = sh * 60 + sm
        end_min = eh * 60 + em
        if end_min <= start_min:
            end_min += 24 * 60  # overnight hours
        duration = (end_min - start_min) / 60
        if duration > 0:
            total += duration
            open_days += 1
    return total, open_days


rows = []
with open("yelp_academic_dataset_business.json", encoding="utf-8") as f:
    for line in f:
        biz = json.loads(line)
        bid = biz["business_id"]
        if bid not in ids:
            continue
        parsed = parse_hours(biz.get("hours"))
        if parsed is None:
            continue
        weekly_hours, open_days = parsed
        rows.append({
            "business_id": bid,
            "name": biz.get("name"),
            "fashion_type": fashion_type_lookup.get(bid),
            "weekly_hours": round(weekly_hours, 1),
            "open_days": open_days,
        })

with open("fashion_clothing_data/clothing_hours.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["business_id", "name", "fashion_type", "weekly_hours", "open_days"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Businesses with hours data: {len(rows)} of 3100")

sums = defaultdict(float)
counts = defaultdict(int)
for r in rows:
    sums[r["fashion_type"]] += r["weekly_hours"]
    counts[r["fashion_type"]] += 1

print()
print("Average weekly hours by fashion_type:")
for ft in sums:
    print(f"  {ft:15s} avg={sums[ft]/counts[ft]:.1f} hrs/week  n={counts[ft]}")
