import csv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

OUT_DIR = "fashion_clothing_data"

texts_by_type = {"Fast Fashion": [], "Slow Fashion": [], "Mixed Retail": []}

with open(f"{OUT_DIR}/fashion_analysis.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ft = row["fashion_type"]
        text = row["text"]
        if ft in texts_by_type and text:
            texts_by_type[ft].append(text)

for ft, texts in texts_by_type.items():
    print(f"{ft}: {len(texts)} documents")

all_texts = []
group_labels = []
for ft, texts in texts_by_type.items():
    all_texts.extend(texts)
    group_labels.extend([ft] * len(texts))
group_labels = np.array(group_labels)

print()
print("=== Fitting shared TF-IDF vocabulary on all reviews/tips ===")
tfidf = TfidfVectorizer(stop_words="english", min_df=10, max_df=0.6, max_features=3000)
tfidf_matrix = tfidf.fit_transform(all_texts)
terms = np.array(tfidf.get_feature_names_out())

print()
print("=== Top 15 distinctive terms per fashion_type (by mean TF-IDF within group) ===")
for ft in texts_by_type:
    mask = group_labels == ft
    group_mean = np.asarray(tfidf_matrix[mask].mean(axis=0)).ravel()
    top_idx = group_mean.argsort()[::-1][:15]
    top_terms = [(terms[i], round(group_mean[i], 4)) for i in top_idx]
    print(f"\n{ft}:")
    for term, score in top_terms:
        print(f"  {term:20s} {score}")

print()
print("=== LDA topic modeling (5 topics per fashion_type, top 10 words each) ===")
for ft, texts in texts_by_type.items():
    print(f"\n--- {ft} ---")
    cv = CountVectorizer(stop_words="english", min_df=10, max_df=0.6, max_features=2000)
    counts = cv.fit_transform(texts)
    cv_terms = np.array(cv.get_feature_names_out())

    lda = LatentDirichletAllocation(n_components=5, max_iter=15, learning_method="online", random_state=42)
    lda.fit(counts)

    for topic_idx, topic in enumerate(lda.components_):
        top_words = [cv_terms[i] for i in topic.argsort()[::-1][:10]]
        print(f"  Topic {topic_idx + 1}: {', '.join(top_words)}")

print()
print("Done.")
