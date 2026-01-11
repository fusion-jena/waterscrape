import pandas as pd
import matplotlib.pyplot as plt

def plot_bar():
    df = pd.read_csv("post_sentiments.csv")

    print(f"Loaded {len(df)} sentiment-scored posts")

    avg_sentiment = (
        df.groupby("keyword")["sentiment"]
          .mean()
          .sort_values(ascending=False)
    )

    print("\nAverage sentiment per keyword:")
    print(avg_sentiment)

    plt.figure(figsize=(12, max(6, 0.35 * len(avg_sentiment))))
    plt.barh(avg_sentiment.index[::-1], avg_sentiment.values[::-1])
    plt.xlabel("Average Sentiment Score (-1 = negative, +1 = positive)")
    plt.title("Average Sentiment per Keyword")
    plt.tight_layout()
    plt.show()


def main():
    plot_bar()


if __name__ == "__main__":
    main()
