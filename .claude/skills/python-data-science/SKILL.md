---
name: python-data-science
description: Use whenever the task is Python data analysis — pandas/numpy data wrangling, exploratory data analysis (EDA), cleaning messy data, feature engineering, or picking and evaluating a machine learning model. Reach for this any time the user pastes a dataset, csv, or dataframe question, asks "what's going on with this data," wants summary stats, or is building/debugging a Python analysis script — even if they don't say "data science" outright. For chart/plot creation specifically, load the dataviz skill instead (or alongside this one) for the actual visual design; this skill covers the analysis, not the pixels.
---

# Python Data Science

Practical pandas/numpy/stats knowledge for real analysis work — not academic ML theory.
Assume Python + pandas as the default toolchain (Derrick's stack), not R.

## The EDA workflow — do this before any modeling

1. **Shape and types first.** `df.shape`, `df.dtypes`, `df.info()`. Wrong dtypes (numbers
   read as strings, dates as objects) silently break everything downstream — fix them
   before anything else.
2. **Missing data.** `df.isnull().sum()`. Decide *why* it's missing (not recorded vs.
   genuinely doesn't apply vs. a join that dropped rows) before deciding how to handle it
   — the fix differs (impute, drop, or leave as a meaningful category).
3. **Distributions.** `df.describe()` for numeric columns, `df['col'].value_counts()` for
   categorical. Look for outliers, unexpected zeros, and cardinality (a "categorical"
   column with 50,000 unique values is probably an ID, not a category).
4. **Duplicates.** `df.duplicated().sum()` — check before aggregating, not after; a
   duplicate row silently inflates every sum and count downstream.
5. **Relationships.** `df.corr()` for numeric pairs, cross-tabs (`pd.crosstab`) for
   categorical pairs. This is where you find the actual story, but don't stop at
   correlation — it doesn't imply causation and misses non-linear relationships.

Only after this — not before — decide what question the analysis is actually answering.

## Pandas patterns worth having memorized

```python
# Indexing — .loc for labels, .iloc for position. Never chain-index for assignment
# (df[df.x>0]['y']=1 triggers SettingWithCopyWarning and may silently no-op).
df.loc[df['x'] > 0, 'y'] = 1

# GroupBy is pandas' answer to SQL's GROUP BY — same mental model
df.groupby('category')['revenue'].agg(['sum', 'mean', 'count'])
df.groupby('category').apply(lambda g: g.nlargest(3, 'revenue'))  # top-N per group

# Merge — same join semantics as SQL (how='inner'/'left'/'outer')
pd.merge(orders, customers, on='customer_id', how='left')

# Missing data
df.dropna(subset=['required_col'])          # drop only where a specific col is null
df['col'].fillna(df.groupby('category')['col'].transform('median'))  # group-aware impute

# Reshaping: long -> wide and back — the #1 source of "why won't this plot" confusion
df.pivot(index='date', columns='category', values='revenue')   # long to wide
df.melt(id_vars='date', var_name='category', value_name='revenue')  # wide to long

# Time series
df['date'] = pd.to_datetime(df['date'])
df.set_index('date').resample('M').sum()     # downsample to monthly
df['revenue'].rolling(window=7).mean()       # 7-period moving average
```

**Chaining vs. copies**: pandas ops mostly return copies, not views — chained filters
(`df[df.a > 0][df.b < 5]`) work but are slow and unclear on large data; prefer a single
boolean mask (`df[(df.a > 0) & (df.b < 5)]`).

## Feature engineering — turning raw columns into model-ready signal

- **Categorical → numeric**: one-hot encode (`pd.get_dummies`) low-cardinality categories;
  target/frequency encode high-cardinality ones (one-hot on a 10,000-category column
  creates 10,000 useless columns).
- **Dates**: don't feed a raw timestamp to a model — extract day-of-week, month,
  is-weekend, days-since-event. The raw value alone means nothing to most algorithms.
- **Binning/discretization**: `pd.cut` (equal-width bins) or `pd.qcut` (equal-population
  bins) turns a noisy continuous variable into a more robust categorical one.
- **Scaling**: standardize (`(x - mean) / std`) or min-max scale before distance-based or
  gradient-based models (KNN, SVM, neural nets, regularized regression). Tree-based
  models (random forest, gradient boosting) don't need this — don't waste time on it there.
- **Leakage is the #1 way feature engineering silently ruins a model**: never compute a
  feature using information that wouldn't be available at prediction time (e.g., using a
  customer's *total* lifetime orders to predict whether their *first* order converts).

## Statistics — the minimum that actually gets used

- **Mean vs. median**: report both when a distribution might be skewed — a mean pulled by
  outliers (income, latency, order value) misleads on its own.
- **Correlation ≠ causation**: always say which one you mean. A/B testing or a controlled
  comparison is how you actually establish causation, not a correlation coefficient.
- **p-values / significance**: a small p-value tells you an effect is unlikely to be pure
  noise given the sample size — it does *not* tell you the effect is large or that it
  matters practically. Always pair it with an effect size.
- **Sample size matters**: with enough rows, even a trivial, meaningless difference
  becomes "statistically significant." Sanity-check practical significance, not just p.

## Choosing a model — don't overthink this

Start simpler than you think you need to, and only add complexity the data justifies:

| Problem | Start here | Reach for later if needed |
|---|---|---|
| Predict a number | Linear regression | Gradient boosting (XGBoost/LightGBM) |
| Predict a category | Logistic regression | Random forest, gradient boosting |
| Find groups (no labels) | K-means | DBSCAN (irregular cluster shapes) |
| Find rare/odd rows | Z-score / IQR outliers | Isolation Forest |
| Text/sequence | TF-IDF + linear model | Fine-tuned transformer, only if the simpler thing genuinely underperforms |

Always hold out a test set (`train_test_split`) and evaluate on it, never on training
data. For imbalanced classes (fraud, churn), accuracy is a misleading metric — look at
precision/recall/F1 or AUC instead, and check the class balance before choosing a metric.

## Where this hands off

- Turning results into a chart/dashboard the client will actually read → **dataviz**
  skill (form heuristics, color, layout — load it before writing any plotting code).
- The pipeline that gets this data to you reliably → **sql-data-engineering** skill.
- Reporting model results as a business case (ROI, "is this worth building") →
  **data-business-strategy** skill.
