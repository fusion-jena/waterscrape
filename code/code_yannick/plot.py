import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("post_sentiments_time.csv")
df = df.dropna(subset=['date'])
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df[df['date'] >= '2000-01-01']

weekly_sentiment = (
    df
    .groupby([pd.Grouper(key='date', freq='W'), 'keyword'])
    ['sentiment']
    .mean()
    .reset_index()
)

weekly_sentiment['sentiment_smooth'] = (
    weekly_sentiment
    .groupby('keyword')['sentiment']
    .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
)

weekly_counts = (
    df
    .groupby([pd.Grouper(key='date', freq='W'), 'keyword'])
    .size()
    .reset_index(name='n_posts')
)

weekly_counts['n_posts_smooth'] = (
    weekly_counts
    .groupby('keyword')['n_posts']
    .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
)

print(f"Loaded {len(df)} sentiment-scored posts")

def plot_time(keywords, smooth=True):
    if keywords == "all":
        plt.figure()

        for kw in weekly_sentiment['keyword'].unique():
            subset = weekly_sentiment[weekly_sentiment['keyword'] == kw]
            plt.plot(subset['date'], subset['sentiment'], label=kw)

        plt.xlabel("Date")
        plt.ylabel("Average sentiment")
        plt.title("Sentiment over time by keyword")
        plt.legend()
        plt.show()
    else:
        subset = weekly_sentiment[
            weekly_sentiment['keyword'] == keywords
        ]
        if smooth:
            y_col = "sentiment_smooth"
            label = "Smoothed weekly sentiment"
        else:
            y_col = "sentiment"
            label = "Weekly sentiment"
        plt.figure()
        plt.plot(subset['date'], subset[y_col])
        plt.title(f"{label} for '{keywords}'")
        plt.xlabel("Date")
        plt.ylabel("Sentiment")
        plt.show()


def plot_total():
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


def plot_frequency(keywords, smooth=True):
    if keywords == "all":
        plt.figure()

        for kw in weekly_counts['keyword'].unique():
            subset = weekly_counts[weekly_counts['keyword'] == kw]
            y_col = "n_posts_smooth" if smooth else "n_posts"
            plt.plot(subset['date'], subset[y_col], label=kw)

        plt.xlabel("Date")
        plt.ylabel("Number of posts")
        plt.title("Post frequency over time by keyword")
        plt.legend()
        plt.show()

    else:
        subset = weekly_counts[
            weekly_counts['keyword'] == keywords
        ]

        y_col = "n_posts_smooth" if smooth else "n_posts"
        label = "Smoothed weekly frequency" if smooth else "Weekly frequency"

        plt.figure()
        plt.plot(subset['date'], subset[y_col])
        plt.title(f"{label} for '{keywords}'")
        plt.xlabel("Date")
        plt.ylabel("Number of posts")
        plt.show()


def main():
    plot_frequency(keywords="water crisis", smooth=True)
    # plot_time(keywords="water crisis", smooth=True)


if __name__ == "__main__":
    main()
