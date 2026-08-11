import json
import csv

with open("fashion_clothing_data/clothing_business_ids.txt", encoding="utf-8") as f:
    business_ids = set(line.strip() for line in f if line.strip())

fashion_type_lookup = {}
with open("fashion_clothing_data/clothing_businesses.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fashion_type_lookup[row["business_id"]] = row["fashion_type"]

count = 0
with open("yelp_academic_dataset_business.json", encoding="utf-8") as fin, \
     open("fashion_clothing_data/clothing_businesses_geo.csv", "w", newline="", encoding="utf-8") as fout:
    writer = csv.writer(fout)
    writer.writerow(["business_id", "latitude", "longitude", "state", "fashion_type"])
    for line in fin:
        biz = json.loads(line)
        bid = biz["business_id"]
        if bid in business_ids:
            writer.writerow([
                bid, biz.get("latitude"), biz.get("longitude"),
                biz.get("state"), fashion_type_lookup.get(bid),
            ])
            count += 1

print(f"Wrote {count} businesses with coordinates.")
