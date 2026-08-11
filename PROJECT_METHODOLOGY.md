# Yelp Fashion Industry Analysis — Methodology Documentation

## Quick reference — the merge

**4 tables merged into 1 final table** (`fashion_analysis.csv`, 65,729 rows — after the beauty-salon cleanup in Section 13):

| Table | Role in merge |
|---|---|
| `clothing_businesses.csv` | Gave `fashion_type`, `name`, `city`, `state` (joined on `business_id`) |
| `clothing_reviews.csv` | Main data — stars, text, date (`source="review"`) |
| `clothing_tips.csv` | Main data — text, date, no stars (`source="tip"`) |
| `clothing_users.csv` | Gave reviewer profile — review_count, average_stars, elite (joined on `user_id`) |

`clothing_checkins.csv` was **not** merged in — kept separate for later footfall/seasonal analysis (it's business-level, not review-level).

**Used for / planned for:**
1. Fast Fashion vs Slow Fashion vs Mixed Retail rating comparison — done (Slow Fashion 3.77, Fast Fashion 3.70, Mixed Retail 3.12)
2. Rating validity / credibility check — done (single-review accounts are 6% of reviews, more polarized, but barely move the averages: +0.03 to +0.04)
3. Sentiment analysis on review text — planned
4. Reviewer-profile-weighted analysis (elite vs regular) — planned

---

## 1. Project goal
Analyze the Yelp Academic Dataset to compare **Fast Fashion** vs **Slow Fashion** (and Mixed Retail) clothing businesses — customer sentiment, ratings, and patterns.

## 2. Source data
Five raw files (line-delimited JSON), joined via two keys:
- `business_id` — links `business.json` to `review.json`, `tip.json`, `checkin.json`
- `user_id` — links `review.json`/`tip.json` to `user.json`

| File | Size | Role |
|---|---|---|
| business.json | 114MB | Store info: name, location, categories, attributes |
| review.json | 5GB | Full-length customer reviews with star ratings |
| tip.json | 173MB | Short customer tips (no star rating) |
| checkin.json | 274MB | Visit timestamps per business |
| user.json | 3.2GB | Reviewer profiles |

## 3. Scope decision — clothing only
Decided to focus **only on clothing**, not shoes/jewelry/accessories, because those can exist as standalone industries (e.g. a luxury jewelry store) unrelated to fast fashion. Blindly including "Shoe Stores"/"Jewelry"/"Accessories" categories would have pulled in unrelated businesses.

## 4. Business filter — which categories count as clothing
Filtered `business.json` on the `categories` field for these 6 keywords:
- `Women's Clothing`, `Men's Clothing`, `Children's Clothing`
- `Bespoke Clothing`, `Bridal`, `Formal Wear`

**Result: 3,100 businesses matched** (out of full dataset; this already reflects the beauty-salon exclusion rule added in Section 13 — see that section for why).

Filtering is done by **category tag match, not by review text** — a business's `categories` field (business-level attribute) decides inclusion. This means reviews under a matched business are kept even if the review text itself never mentions "fashion" or "clothing" (e.g. "great service, fast delivery" still counts, because it belongs to a clothing business_id).

## 5. Cascading the filter to other tables
Using the 3,100 matched `business_id`s, filtered:
- `review.json` → 58,890 reviews
- `tip.json` → 6,839 tips
- `checkin.json` → 2,909 businesses (fewer than 3,100 because some clothing businesses have zero recorded check-ins)
- `user.json` → 46,236 unique users (filtered by `user_id`, collected from the reviews + tips above — this is why the count doesn't match business_id counts, it's a different key with a different relationship)

**Why row counts differ across tables**: `businesses.csv` and `checkins.csv` have at most 1 row per business_id; `reviews.csv`/`tips.csv` have many rows per business_id (one row per review/tip — a one-to-many relationship).

## 6. Why separate CSVs instead of one merged file (staging approach)
Chose to filter each raw file into its own intermediate CSV first, rather than filtering + joining in a single step, because:
1. **Raw files are huge** (5GB, 3.2GB) — filtering once avoids re-scanning them for every later step.
2. **Each stage can be validated independently** — counts, nulls, duplicates can be checked before they cascade into a final join, making errors easier to isolate.

## 7. fashion_type classification
Store-level label (not item/product-level — Yelp has no SKU data, so classification reflects the store's overall business model, not every item in it).

```
if 'Department Stores' in categories:
    fashion_type = 'Mixed Retail'
elif 'Bespoke Clothing' or 'Bridal' or 'Formal Wear' in categories:
    fashion_type = 'Slow Fashion'
elif "Women's/Men's/Children's Clothing" in categories:
    fashion_type = 'Fast Fashion'
else:
    fashion_type = 'Unclassified'   # never triggers on this dataset — every matched business already has one of the 6 filter keywords
```

**Why "Mixed Retail" is separate from Fast Fashion**: Department stores (Macy's, Kohl's, Dillard's, Nordstrom) sell both fast-fashion brands and premium/designer lines under one roof. Labeling them "Fast Fashion" would misrepresent their mixed inventory.

**Why "Slow Fashion" instead of "Other Fashion"**: Slow Fashion is the recognized industry term that directly opposes Fast Fashion (custom-made, made-to-order, low turnover) — more defensible for a report than a generic "Other" label.

**Result:**
| fashion_type | Businesses |
|---|---|
| Fast Fashion | 1,974 |
| Slow Fashion | 718 |
| Mixed Retail | 408 |
| Unclassified | 0 |

## 8. Final merged table
`fashion_analysis.csv` — one row per review or tip (65,729 rows), combining:
- Review/tip text, stars, date
- Business name, city, state, `fashion_type` (joined on `business_id`)
- Reviewer profile: review_count, average_stars, elite status (joined on `user_id`)

## 9. Data quality check — rating validity
Investigated whether ratings could be unreliable (fake accounts, review-bombing, venting).

**Finding 1 — overall shape**: Ratings are J-shaped (20% 1-star, 48% 5-star, only 16% in the 2-3 star middle). This is normal for review platforms in general (people mostly review when very happy or very upset) — not on its own evidence of fraud.

**Finding 2 — single-review accounts**: Accounts with only 1 review ever made up **~6% of all reviews** (measured pre-cleanup, on 60,098 reviews) — a small share, so they don't meaningfully distort overall averages.

**Finding 3 — but their behavior is more extreme**: Single-review accounts gave 1-star **39.1%** of the time vs **18.7%** for experienced (multi-review) reviewers, and used the middle 2-3 star range far less (7.6% vs 16.1%). This matches the pattern of accounts created specifically to vent (or occasionally to praise) rather than give a considered rating.

**Conclusion**: Some low-credibility reviews likely exist but are a small fraction (~6%) — doesn't invalidate the dataset, but worth flagging. Planned fix: add a `review_credibility` column (`low` if `user_review_count <= 1`, else `normal`) so analysis can optionally filter or compare by credibility.

## 10. Analysis findings so far
- **Fast Fashion** has the most review/tip volume (37,865 — the majority of all clothing feedback), consistent with having the most stores (1,974).
- **Slow Fashion** has the highest average rating (3.77) vs Fast Fashion (3.70) and Mixed Retail (3.12) — custom/bespoke/bridal stores get somewhat higher satisfaction.
- **Mixed Retail** (department stores) has the lowest average rating — possibly less personal service at scale.

## 11. Sentiment analysis (VADER)
Added `sentiment_compound` (-1 to +1) and `sentiment_label` (positive/neutral/negative) columns to `fashion_analysis.csv` using VADER (lexicon-based, no training needed — well suited to short review-style text).

| fashion_type | avg sentiment | % positive | % negative |
|---|---|---|---|
| Fast Fashion | 0.611 | 81.9% | 14.1% |
| Slow Fashion | 0.629 | 82.8% | 15.1% |
| Mixed Retail | 0.412 | 69.4% | 22.7% |

**Sentiment confirms the star-rating pattern**: Mixed Retail (department stores) is both lowest-rated and most negative in text — customers seem less satisfied at scale/mixed-inventory stores than at dedicated clothing stores.

## 12. Topic modeling (TF-IDF + LDA)
Fit a shared TF-IDF vocabulary across all reviews/tips, then compared mean TF-IDF per term within each fashion_type group. Also ran LDA (5 topics per group) via scikit-learn.

- **Fast Fashion**: generic shopping vocabulary — store, clothes, staff, love, good. No single dominant theme.
- **Slow Fashion**: heavily wedding/bridal-focused — dress, wedding, bridal, appointment, recommend.
- **Mixed Retail**: dominated by actual brand names (Macy's, Nordstrom, Ross) plus transactional complaint language — return, line, manager, told — suggesting complaints skew toward service/checkout experience rather than product itself.

## 13. Data quality fix — beauty salons misclassified as Slow Fashion
LDA topics for Slow Fashion surfaced unexpected words: "hair", "salon", "cut". Investigated and found **28 businesses** (e.g. "ReJuv Medspa", "The Blonde Salon & Spa") had only qualified for the dataset via the `Bridal` category tag, but were actually hair/beauty salons offering bridal hair & makeup — not clothing sellers. They had no actual clothing category tag (`Women's/Men's/Children's/Bespoke Clothing`, `Formal Wear`).

**Fix**: Added an exclusion rule in `filter_clothing.py` — a business tagged `Bridal` is dropped if it also carries a beauty/salon tag (`Hair Salons`, `Makeup Artists`, `Nail Salons`, etc.) AND has no actual clothing category tag. 3 businesses that had both salon services and a real clothing tag were kept.

**Impact after re-running the full pipeline**: 3,128 → **3,100 businesses**, 58,890 reviews, 6,839 tips, 2,909 checkins, 46,236 users. Sentiment and rating conclusions barely moved (e.g. Slow Fashion avg sentiment 0.634 → 0.629) — confirms the earlier findings were already robust, but the dataset is now more defensible (no salons counted as clothing stores).

## 14. review_credibility column
Added `review_credibility` to `fashion_analysis.csv` — `"low"` if `user_review_count <= 1` (account has never posted more than this one review/tip), else `"normal"`.

Result: **3,727 rows (5.7%) are "low" credibility**, 62,002 (94.3%) "normal" — consistent with the earlier finding (~6%). Confirmed earlier that excluding these barely moves star averages (+0.03 to +0.04); the column exists so it can be used as an optional filter for sentiment/topic analysis or to check for anomalies concentrated on a single business, not because it changes the headline rating comparison.

## 15. Time trend analysis
Computed each fashion_type's **share of total review+tip volume per year** (not raw counts, since raw counts grow with Yelp's overall adoption over time — share isolates the relative trend). Used 2010-2021: 2005-2009 had too few samples, 2022 is a partial year (dataset cutoff).

| Year | Fast Fashion % | Slow Fashion % | Mixed Retail % |
|---|---|---|---|
| 2010 | 70.2 | 14.5 | 15.2 |
| 2014 | 55.0 | 28.0 | 17.0 |
| 2016 | 52.6 | 31.3 | 16.1 |
| 2018 | 55.9 | 29.4 | 14.6 |
| 2021 | 55.4 | 31.2 | 13.4 |

**Finding (counter to the "fast fashion is taking over" assumption)**: Fast Fashion's share of review activity **declined** from 70.2% (2010) to ~55% (2021). Slow Fashion's share **more than doubled**, from 14.5% to ~31%. Mixed Retail stayed roughly flat/slightly declining. This lines up with the real-world conscious-consumerism / sustainable-fashion trend — Yelp reviewer attention has been shifting toward bespoke/bridal/formal (Slow Fashion) businesses relative to mass-market chains over the decade.

## 16. Geographic analysis
Computed `fashion_type` distribution by state (from `clothing_businesses.csv`, `state` column) across all 14 states/provinces in the dataset.

**Top states by business count** (Fast Fashion % / Slow Fashion %): PA 707 (62.2% / 25.9%), FL 394 (59.9% / 21.6%), TN 314 (70.7% / 20.7%), LA 268 (72.8% / 19.8%), IN 234 (61.5% / 25.2%), MO 230 (55.2% / 28.7%), AB(Canada) 175 (81.1% / 14.3%), CA 157 (81.5% / 12.7%).

**Highest Slow Fashion share**: Illinois (37.9%), Delaware (36.0%), New Jersey (32.1%), Missouri (28.7%) — all well above the ~24% dataset average.
**Lowest Slow Fashion share / most Fast-Fashion-dominant**: California (12.7%), Alberta/Canada (14.3%).

**Key discovery — the dataset is not a random national sample.** Plotting real business latitude/longitude (from `business.json`, not originally saved to any CSV — extracted separately into `clothing_businesses_geo.csv`) showed businesses cluster into isolated blobs rather than spreading across the country. Cross-checking against `city` confirmed the Yelp Academic Dataset covers a fixed set of ~11 metro areas: Philadelphia (329 clothing businesses), Nashville (225), New Orleans (183), Tampa (183), Edmonton-Canada (168), Indianapolis (150), Tucson (149), Santa Barbara (131), Reno (120), Saint Louis (108), Boise (55). Any geographic finding in this project describes these specific metros, not the US as a whole — a limitation worth stating explicitly in the report.

**Deliverable**: an interactive US choropleth artifact (state-level, Slow Fashion share, red sequential shading, labeled) — [Slow Fashion Share by State](https://claude.ai/code/artifact/8748645b-4322-433c-8377-d793a648e40d). Built from a public-domain blank US states SVG (Wikimedia Commons, "Blank US Map (states only).svg"), colored by binning each state's Slow Fashion share into 5 classes.

## 17. Reviewer-profile-weighted analysis (elite vs regular)
Split `fashion_analysis.csv` by whether `user_elite` is non-empty (Yelp Elite status in at least one year) vs empty (regular user), and compared average stars and average sentiment.

| | Elite avg stars | Regular avg stars | Elite avg sentiment | Regular avg sentiment |
|---|---|---|---|---|
| Overall | 3.89 | 3.54 | 0.691 | 0.539 |
| Fast Fashion | 3.98 | 3.57 | 0.724 | 0.555 |
| Slow Fashion | 4.01 | 3.73 | 0.743 | 0.608 |
| Mixed Retail | 3.53 | 2.83 | 0.567 | 0.295 |

**Finding**: Elite reviewers rate and write more positively than regular reviewers across every fashion_type — the opposite of the common assumption that experienced/power reviewers are more critical. **The gap is largest for Mixed Retail** (0.70-star gap vs 0.28-0.41 for Fast/Slow Fashion) — regular/casual reviewers are disproportionately harsher on department stores specifically, echoing the earlier single-review-account finding (Section 9) that less-experienced reviewers skew more extreme/emotional in their feedback.

This completes the three planned analyses (time trend, geographic, reviewer-profile-weighted) beyond the initial rating/sentiment/topic-modeling work.

## 18. Weekly operating hours
Extracted the `hours` field from `business.json` (not previously saved to any CSV) for all 3,100 clothing businesses; parsed each day's `HH:MM-HH:MM` span into total weekly open hours. 2,772 businesses (89%) had hours data.

| fashion_type | mean hrs/week | median | stdev |
|---|---|---|---|
| Mixed Retail | 80.6 | 76.0 | 18.3 |
| Fast Fashion | 60.7 | 60.0 | 18.4 |
| Slow Fashion | 54.2 | 53.0 | 18.2 |

**Finding**: Mixed Retail (department stores) is open far longer than the other two — consistent with a walk-in, high-traffic model. Slow Fashion is open the least, consistent with an appointment-based (bridal/bespoke) model that doesn't need long walk-in hours. **Spread (stdev) is essentially identical across all three (~18 hours)** — no group is meaningfully more or less consistent in scheduling than another.

## 19. Negative-review issue categories
Tagged each **negative** review/tip (per the VADER `sentiment_label` from Section 11) against 6 keyword-based issue buckets (Quality, Price, Service/Staff, Fit/Sizing, Returns, Selection/Stock) and measured what % of each fashion_type's negative feedback mentions each issue.

| Issue | Fast Fashion | Slow Fashion | Mixed Retail |
|---|---|---|---|
| Service/Staff | 52.3% | 55.0% | 53.8% |
| Quality | 49.6% | 49.0% | 43.4% |
| Price | 20.8% | 18.0% | 14.9% |
| Fit/Sizing | 2.2% | 7.9% | 1.2% |
| Returns | 9.9% | 8.0% | 6.4% |
| Selection/Stock | 1.0% | 0.8% | 1.8% |

**Findings**:
- **Service/Staff is the #1 complaint everywhere** (52-55%) — the biggest lever for improvement is customer experience, not the product itself.
- **Price complaints are highest for Fast Fashion** (20.8%) — counterintuitive given Fast Fashion's low-price positioning; suggests a perceived value gap rather than an absolute price problem.
- **Fit/Sizing is Slow Fashion's distinct weak point** (7.9%, ~4x Fast Fashion and ~7x Mixed Retail) — high-stakes given Slow Fashion includes bridal/formal wear, where a fit issue is far more costly to the customer than in casual clothing.

## 20a. BERT sentiment validation (checking VADER against a second method)

Section 09's stated limitation was "lexicon sentiment, not a transformer model — misses sarcasm and mixed-sentiment nuance." Rather than leave that as a caveat, ran a second, independent sentiment pass with a transformer model to see how much it actually mattered.

**Method**: `distilbert-base-uncased-finetuned-sst-2-english` (DistilBERT fine-tuned on SST-2) via Hugging Face `transformers`, run on all 65,729 rows in `fashion_analysis.csv` (CPU only, ~4 hrs wall time due to a mid-run CPU-contention incident, ~2.5 hrs at clean throughput). Text truncated to 256 tokens (covers the p90 review length). Added `bert_label` (positive/negative — DistilBERT SST-2 is binary, no neutral class), `bert_score` (confidence, 0-1), and `bert_compound` (signed score, -1 to +1, for shape-comparability with VADER's compound).

**Result:**

| fashion_type | BERT avg compound | % positive | % negative | Agreement with VADER |
|---|---|---|---|---|
| Fast Fashion | 0.324 | 66.2% | 33.8% | 80.2% |
| Slow Fashion | 0.337 | 66.8% | 33.2% | 81.8% |
| Mixed Retail | **-0.023** | 48.9% | 51.1% | 72.0% |

(Agreement measured only on rows where VADER called positive/negative, excluding VADER's "neutral" bucket since BERT's model has no neutral class.)

**Finding**: Both methods agree on the *ranking* (Slow Fashion ≈ Fast Fashion > Mixed Retail) — the headline conclusion holds. But they diverge sharply on Mixed Retail specifically: VADER read it as 69.4% positive (Section 11), while BERT reads the same reviews as **51.1% negative** — a net-negative verdict VADER never reached. Agreement between the two methods is also lowest for Mixed Retail (72.0% vs ~81% for the other two groups) — the two models disagree most exactly where the department-store complaints live.

**Why this matters**: This isn't a contradiction to gloss over — it's the transformer catching context/nuance (sarcasm, backhanded phrasing, mixed-clause reviews) that a lexicon model structurally can't. If anything, BERT's read suggests the original VADER-based Mixed Retail finding (Section 11) was **understating** how negative that segment's feedback actually is, not overstating it. This strengthens rather than undercuts Section 20's Mixed Retail recommendations.

## 20. Business recommendations
Synthesizing all findings (Sections 10-19) into actionable takeaways:

**For Fast Fashion brands**
- Service/staff training is the single highest-leverage fix — 52% of negative feedback mentions it, more than product quality.
- Investigate the price-perception gap: despite being the "affordable" segment, Fast Fashion draws the most price complaints (20.8%) of the three groups — communicate value more clearly, or reconsider markup on frequently-complained items.
- Streamline returns (highest complaint share of the three, 9.9%) — friction here compounds the price-perception problem.
- Relative market share (Section 15) has been declining for over a decade (70%&rarr;55%) while Slow Fashion's has grown — this is a long-run warning sign worth tracking, not just a snapshot metric.

**For Slow Fashion / bespoke brands**
- Fit/sizing is a distinct, addressable weakness (7.9% of negative reviews) — worth disproportionate investment in fitting consultations given how costly a bad fit is in bridal/formal wear specifically.
- This segment already has the highest ratings and sentiment — protect it; don't chase Fast Fashion's long-hours, high-volume model, since the appointment-based approach isn't a competitive weakness (spread in hours is the same as everyone else's).
- Growing relative share (15%&rarr;31%) plus states like Illinois, Delaware, New Jersey, and Missouri showing above-average Slow Fashion concentration suggest good regions for expansion.

**For Mixed Retail / department stores**
- Lowest ratings and most negative sentiment of the three groups — the biggest single improvement opportunity in this dataset.
- The elite-vs-regular rating gap is largest here (0.70 stars, Section 17) — regular/casual shoppers have a notably worse experience than loyal ones; onboarding, wayfinding, and staff attentiveness for less-frequent shoppers is worth prioritizing.
- Long hours (80.6/week) aren't converting to satisfaction — this isn't an access problem, it's an in-store experience problem.

**For researchers / analysts using this dataset**
- Single-review accounts (~6% of feedback, Section 9) skew toward extreme ratings — don't let a handful of them dominate a small business's aggregate score.
- This Yelp Academic Dataset covers a fixed set of ~11 metro areas (Section 16) — findings describe those metros, not the US as a whole.
- Classify at the business/store level, not the product level — a "Fast Fashion" label describes a store's overall model, not every item it carries, and mixed-inventory retailers (department stores) don't fit a binary Fast/Slow split, which is why this project uses three categories instead of two.

## 21. Reviewer social network analysis

Extends the project beyond ratings/sentiment/text into the **social graph** connecting clothing reviewers, using the `friends` field in `user.json` (not previously extracted to any CSV).

**Method**: `extract_friends.py` streamed `user.json` once (1,987,897 total Yelp users), keeping only friend-edges where **both** endpoints are among the 46,236 clothing reviewers — i.e. the subgraph of the full Yelp friend graph induced by this project's reviewer set, not the reviewers' full friend lists. Result: **135,151 unique edges**. `network_analysis.py` then builds this as an undirected graph (`networkx`) and analyzes it.

### Reviewer categories
Split reviewers into 6 categories combining elite status, elite tenure, and activity level — thresholds picked from the actual distribution, not arbitrary:

| Category | Rule | Count | % of dataset |
|---|---|---|---|
| Veteran Elite | elite, years-elite ≥ 5 | 3,748 | 8.1% |
| New Elite | elite, years-elite 1-4 | 4,217 | 9.1% |
| Power User | non-elite, review_count ≥ 50 | 4,346 | 9.4% |
| Moderate | non-elite, review_count 10-49 | 14,904 | 32.2% |
| Light | non-elite, review_count 2-9 | 15,419 | 33.3% |
| Single-review | non-elite, review_count ≤ 1 | 3,602 | 7.8% |

**Why these cutoffs**: 5 years is the **median** tenure among the 7,965 elite users (53%/47% split either side). 50 reviews is ~p90 of non-elite review_count (top ~11% most-active non-elite reviewers), and a round number close to the natural percentile break. The "Single-review" cutoff (`review_count ≤ 1`) intentionally reuses the `review_credibility` definition from Section 14, since that group was already shown to behave differently (more polarized ratings).

### Network topology
| Metric | Value |
|---|---|
| Nodes (clothing reviewers) | 46,236 |
| Edges (within-set friendships) | 135,151 |
| Density | 0.000126 |
| Isolated users (0 in-set friends) | 28,241 (61.1%) |
| Mean degree | 5.846 |
| Max degree | 1,455 |
| Connected components | 28,613 |
| Largest component | 17,182 nodes (37.2% of network) |
| Avg. clustering coefficient (largest component) | 0.2555 |

**Finding**: Most clothing reviewers (61.1%) have zero friends who are also clothing reviewers — expected, since sharing a specific shopping niche with a friend is a low-probability coincidence out of everything two friends might have in common on Yelp. But over a third of reviewers (37.2%) sit in one large connected component, and the clustering coefficient (0.26) shows real triadic closure — friends-of-friends are friends with each other far more than random chance would produce, the standard signature of a genuine social network rather than random pairing.

### Network position by reviewer category
| Category | Mean degree | Isolated % |
|---|---|---|
| Veteran Elite | 44.0 | 2.0% |
| New Elite | 15.3 | 6.9% |
| Power User | 4.2 | 44.5% |
| Moderate | 1.1 | 66.8% |
| Light | 0.4 | 82.9% |
| Single-review | 0.2 | 89.0% |

**Finding**: A clean, monotonic gradient — network connectivity rises with reviewer commitment at every step from Single-review up to Veteran Elite. Veteran Elite reviewers are **~44x more connected** within the clothing-reviewer community than Single-review accounts, and are 44x less likely to be isolated. This extends Section 17's finding (elite reviewers rate more positively) into a new dimension: elite status also predicts social embeddedness, not just rating behavior — elite reviewers aren't just nicer raters, they're structurally central to the reviewer community.

### Fashion-type homophily
Tested whether friend pairs share the same dominant `fashion_type` (Fast/Slow/Mixed, from Section 7) more than random chance would predict.

| | Rate |
|---|---|
| Observed (friends sharing same dominant fashion_type) | 52.4% |
| Expected under random pairing | 43.3% |

**Finding**: Friends share a dominant fashion_type **9.1 percentage points more often than chance** — real homophily, not coincidence. Reviewers' clothing-shopping taste correlates with who they're friends with on Yelp, consistent with the general homophily principle in social network research ("birds of a feather").

**Pair-level breakdown** (observed % of friend edges vs. expected % under random pairing, for each fashion_type combination):

| Pair | Observed | Expected | Gap |
|---|---|---|---|
| Fast Fashion – Fast Fashion | 45.5% | 32.5% | +13.0pt |
| Slow Fashion – Slow Fashion | 2.2% | 9.2% | −7.0pt |
| Mixed Retail – Mixed Retail | 4.7% | 1.6% | **+3.1pt (~3x)** |
| Fast Fashion – Slow Fashion | 16.5% | 34.6% | **−18.1pt** |
| Fast Fashion – Mixed Retail | 26.0% | 14.4% | +11.6pt |
| Slow Fashion – Mixed Retail | 5.2% | 7.7% | −2.5pt |

**Finding**: The aggregate 52.4%/43.3% number hides a sharper pattern. **Mixed Retail–Mixed Retail pairs are the most over-represented of any combination** (~3x expected) — department-store reviewers cluster tightly with each other. **Fast Fashion–Slow Fashion cross-pairs are the most under-represented** (observed less than half of what chance predicts) — casual mass-market reviewers and bespoke/bridal reviewers largely avoid each other's friend circles. Slow Fashion same-type pairing is also below chance (unlike Fast Fashion and Mixed Retail), suggesting Slow Fashion reviewers' friendships are driven more by other factors (e.g. geography, life stage) than by shared bespoke/bridal taste specifically.

### Geographic network analysis
Extends the homophily test to **location** instead of fashion_type, using the ~11 fixed metro areas already discovered in Section 16. Since `clothing_users.csv` has no location field, each business was assigned to a metro via **k-means clustering (k=11)** on business lat/long (`clothing_businesses_geo.csv`), labeling each cluster by its most common real city name — this reproduces Section 16's metro discovery programmatically rather than relying on raw `city` strings (272 distinct raw city/suburb names exist, too fragmented to use directly). Each user was then assigned a "dominant metro" the same way dominant `fashion_type` was computed (most-reviewed metro among their businesses).

| | Rate |
|---|---|
| Observed same-metro rate | 70.5% |
| Expected under random pairing | 14.7% |
| Cross-metro edges | 29.5% (39,911 of 135,151) |

**Finding**: Geographic homophily is, unsurprisingly, far stronger than fashion-type homophily (friends are usually in the same city) — but nearly **30% of friend edges cross metro lines**, which is a meaningful long-distance signal, not noise. The single busiest cross-metro link is **New Orleans–Philadelphia** (3,448 edges), followed by Nashville–Philadelphia and Nashville–New Orleans — Philadelphia (the largest metro, 13,554 reviewers) and New Orleans/Nashville show up disproportionately in cross-metro pairs simply because they're among the largest pools, not necessarily because of a unique connection between those specific cities.

**Per-metro network stats:**

| Metro | Reviewers | Mean degree | Isolated % |
|---|---|---|---|
| Philadelphia | 13,554 | 5.07 | 63.6% |
| Nashville | 5,642 | 4.49 | 64.4% |
| Tampa | 5,465 | 8.13 | 61.2% |
| New Orleans | 4,185 | 8.20 | 54.7% |
| Reno | 3,668 | 6.85 | 55.0% |
| Indianapolis | 3,253 | 6.58 | 52.5% |
| Santa Barbara | 3,117 | 3.61 | 66.5% |
| Saint Louis | 3,052 | 6.31 | 61.4% |
| Tucson | 2,409 | 4.40 | 62.3% |
| Boise | 972 | 3.02 | 72.5% |
| Edmonton | 919 | 7.52 | 52.2% |

**Finding**: Network connectivity varies a lot by metro independent of size — **New Orleans and Tampa have the highest mean degree (~8.1–8.2) and lowest isolation (~55–61%)**, while **Boise is the most isolated (72.5%)** despite not being the smallest metro. Philadelphia, despite having by far the most reviewers, is only mid-pack on connectivity (mean degree 5.07) — a bigger reviewer pool doesn't automatically mean a more tightly-knit one.

**Scripts**: `extract_friends.py` (builds `clothing_friend_edges.csv`), `network_analysis.py` (topology, categories, fashion-type homophily), `geo_network_analysis.py` (metro clustering and geographic homophily).
