import csv
from collections import Counter, defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

OUT_DIR = "fashion_clothing_data"

sentiment_sum = defaultdict(float)
sentiment_count = defaultdict(int)
label_counter = defaultdict(Counter)

rows_out = []

with open(f"{OUT_DIR}/fashion_analysis.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + ["sentiment_compound", "sentiment_label"]
    for row in reader:
        text = row["text"] or ""
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        ft = row["fashion_type"]
        sentiment_sum[ft] += compound
        sentiment_count[ft] += 1
        label_counter[ft][label] += 1

        row["sentiment_compound"] = round(compound, 4)
        row["sentiment_label"] = label
        rows_out.append(row)

with open(f"{OUT_DIR}/fashion_analysis.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("=== Average sentiment (compound, -1 to 1) by fashion_type ===")
for ft in sentiment_sum:
    avg = sentiment_sum[ft] / sentiment_count[ft]
    print(f"{ft:15s} avg={avg:.4f}  n={sentiment_count[ft]}")

print()
print("=== Sentiment label distribution ===")
for ft, counter in label_counter.items():
    total = sum(counter.values())
    print(ft)
    for label in ["positive", "neutral", "negative"]:
        n = counter[label]
        print(f"  {label:9s} {n:6d} ({100*n/total:.1f}%)")

print()
print("Done. sentiment_compound and sentiment_label columns added to fashion_analysis.csv")
