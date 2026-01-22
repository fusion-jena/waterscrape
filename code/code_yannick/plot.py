import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("post_sentiments.csv")

print(f"Loaded {len(df)} sentiment-scored posts")

stats = (
    df.groupby("keyword")
      .agg(
          avg_sentiment=("sentiment", "mean"),
          n_posts=("sentiment", "count")
      )
)

stats = stats[stats["n_posts"] >= 100]

stats = stats.sort_values("avg_sentiment", ascending=False)

print(stats)

plt.figure(figsize=(12, max(6, 0.35 * len(stats))))
bars = plt.barh(stats.index[::-1], stats["avg_sentiment"].values[::-1])

plt.xlabel("Average Sentiment Score (-1 = negative, +1 = positive)")
plt.title("Average Sentiment per Keyword (with Post Counts)")

for bar, n in zip(bars, stats["n_posts"].values[::-1]):
    width = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    plt.text(
        width * 0.95,
        y,
        f"{n}",
        va="center",
        ha="right",
        fontsize=9,
        color="black"
    )

plt.tight_layout()
plt.show()

