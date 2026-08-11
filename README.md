# Fast Fashion vs. Slow Fashion — Yelp Dataset Analysis

Analyzes 65,729 Yelp reviews and tips across 3,100 U.S. clothing businesses to compare **Fast Fashion**, **Slow Fashion** (bespoke/bridal/formal), and **Mixed Retail** (department stores) on customer rating, sentiment, a decade-long trend in relative review share, geography, reviewer profile, and operating hours.

Full write-up with charts: [analyzewithrutuja.github.io/projects/fast_fashion_vs_slow_fashion.html](https://analyzewithrutuja.github.io/projects/fast_fashion_vs_slow_fashion.html)

Full methodology, every decision and its reasoning: [PROJECT_METHODOLOGY.md](PROJECT_METHODOLOGY.md)

## Data

Built from the [Yelp Academic Dataset](https://www.yelp.com/dataset) (`business.json`, `review.json`, `tip.json`, `checkin.json`, `user.json`) — not included in this repo per Yelp's dataset terms. Download it separately and place the 5 raw files in the working directory to run the pipeline.

## Pipeline (run in order)

| Script | What it does |
|---|---|
| `filter_clothing.py` | Filters raw files down to clothing businesses (6 category keywords) and cascades the filter to reviews/tips/checkins via `business_id` |
| `add_fashion_type.py` | Classifies each business as Fast Fashion / Slow Fashion / Mixed Retail |
| `filter_users.py` | Filters `user.json` down to reviewers who appear in the filtered reviews/tips |
| `merge_final.py` | Joins businesses (`business_id`) and users (`user_id`) into one final table, `fashion_analysis.csv` |
| `sentiment_analysis.py` | VADER sentiment scoring on review/tip text |
| `topic_modeling.py` | TF-IDF distinctive terms + LDA topic modeling per fashion_type |
| `add_credibility.py` | Flags single-review accounts (`review_credibility` column) |
| `analyze_hours.py` | Parses the `hours` field into total weekly operating hours |
| `issue_keywords.py` | Tags negative reviews against 6 keyword-based issue categories |
| `extract_geo.py` | Extracts latitude/longitude for the geographic map |

## Stack

Python · pandas · scikit-learn (TF-IDF, LDA) · VADER Sentiment
