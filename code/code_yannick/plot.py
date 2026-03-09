import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

sigma = 2

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
    .transform(lambda s: gaussian_filter1d(s.values, sigma=sigma))
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
    .transform(lambda s: gaussian_filter1d(s.values, sigma=sigma))
)

print(f"Loaded {len(df)} sentiment-scored posts")

def plot_time(keywords, smooth=True):
    import math
    import mplcursors
    import matplotlib.dates as mdates

    if keywords == "all":
        all_keywords = weekly_sentiment['keyword'].unique()
        n = len(all_keywords)
        ncols = 3
        nrows = math.ceil(n / ncols)

        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, min(nrows * 3, 12)), sharex=True, sharey=True)
        # fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 3), sharex=True, sharey=True)
        axes_flat = axes.flatten()

        for i, kw in enumerate(all_keywords):
            ax = axes_flat[i]

            sent_subset = weekly_sentiment[weekly_sentiment['keyword'] == kw]
            count_subset = weekly_counts[weekly_counts['keyword'] == kw]
            merged = pd.merge(sent_subset, count_subset, on=['date', 'keyword'], how='left').reset_index(drop=True)

            y_col = "sentiment_smooth" if smooth else "sentiment"
            n_col = "n_posts_smooth" if smooth else "n_posts"

            ax.plot(merged['date'], merged[y_col], linewidth=1.2, color='steelblue')
            ax.set_title(kw, fontsize=9)
            ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')

            line = ax.get_lines()[0]
            line._mpl_data = merged

            cursor = mplcursors.cursor(line, hover=True)

            @cursor.connect("add")
            def on_add(sel, _y=y_col, _n=n_col):
                row = sel.artist._mpl_data.iloc[int(sel.index)]
                sel.annotation.set_text(
                    f"{row['date'].date()}\nSentiment: {row[_y]:.3f}\nPosts: {int(row[_n])}"
                )

        for j in range(i + 1, len(axes_flat)):
            axes_flat[j].set_visible(False)

        fig.autofmt_xdate(rotation=30)
        fig.suptitle("Sentiment over time by keyword", fontsize=13, y=1.01)
        plt.tight_layout()
        plt.show()

    else:
        sent_subset = weekly_sentiment[weekly_sentiment['keyword'] == keywords]
        count_subset = weekly_counts[weekly_counts['keyword'] == keywords]
        merged = pd.merge(sent_subset, count_subset, on=['date', 'keyword'], how='left').reset_index(drop=True)

        y_col = "sentiment_smooth" if smooth else "sentiment"
        n_col = "n_posts_smooth" if smooth else "n_posts"
        label = "Smoothed weekly sentiment" if smooth else "Weekly sentiment"

        fig, ax = plt.subplots()
        line, = ax.plot(merged['date'], merged[y_col], color='steelblue')
        ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        line._mpl_data = merged

        cursor = mplcursors.cursor(line, hover=True)

        @cursor.connect("add")
        def on_add(sel, _y=y_col, _n=n_col):
            row = sel.artist._mpl_data.iloc[int(sel.index)]
            sel.annotation.set_text(
                f"{row['date'].date()}\nSentiment: {row[_y]:.3f}\nPosts: {int(row[_n])}"
            )

        ax.set_title(f"{label} for '{keywords}'")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sentiment")
        plt.tight_layout()
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


def plot_cooccurrence():
    import itertools
    from collections import Counter
    import matplotlib.pyplot as plt
    import numpy as np

    # Find all keywords that co-occur in the same post
    post_keywords = df.groupby('post_id')['keyword'].apply(list)

    # Count co-occurrences
    cooc = Counter()
    for kws in post_keywords:
        kws = list(set(kws))  # deduplicate within a post
        for pair in itertools.combinations(sorted(kws), 2):
            cooc[pair] += 1

    # Build a matrix
    all_kws = sorted(df['keyword'].unique())
    matrix = pd.DataFrame(0, index=all_kws, columns=all_kws)
    for (a, b), count in cooc.items():
        matrix.loc[a, b] = count
        matrix.loc[b, a] = count

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(max(8, len(all_kws) * 0.6), max(6, len(all_kws) * 0.5)))
    im = ax.imshow(matrix.values, cmap='YlOrRd')
    plt.colorbar(im, ax=ax, label='Co-occurrence count')

    ax.set_xticks(range(len(all_kws)))
    ax.set_yticks(range(len(all_kws)))
    ax.set_xticklabels(all_kws, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(all_kws, fontsize=8)

    # Annotate cells with counts
    for i in range(len(all_kws)):
        for j in range(len(all_kws)):
            v = matrix.values[i, j]
            if v > 0:
                ax.text(j, i, str(v), ha='center', va='center', fontsize=7,
                        color='black' if v < matrix.values.max() * 0.7 else 'white')

    ax.set_title("Keyword co-occurrence (same post)")
    plt.tight_layout()
    plt.show()


def plot_engagement_sentiment():
    posts_df = pd.read_csv("posts_likes.csv")
    merged = pd.merge(
        df[['post_id', 'sentiment']].drop_duplicates(subset='post_id'),
        posts_df[['post_id', 'likes_count']],
        on='post_id',
        how='inner'
    ).dropna(subset=['sentiment', 'likes_count'])

    merged['sentiment_bucket'] = pd.cut(
        merged['sentiment'],
        bins=[-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['-1.0', '-0.8', '-0.6', '-0.4', '-0.2', '0.0', '0.2', '0.4', '0.6', '0.8']
    )

    stats = merged.groupby('sentiment_bucket', observed=True)['likes_count'].agg(
        mean='mean',
        sem=lambda x: x.std() / np.sqrt(len(x)),
        n='count'
    ).reset_index()

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(range(len(stats)), stats['mean'], color='steelblue', linewidth=2, marker='o')
    ax.fill_between(range(len(stats)),
                    stats['mean'] - stats['sem'],
                    stats['mean'] + stats['sem'],
                    alpha=0.2, color='steelblue')

    ax.set_xticks(range(len(stats)))
    ax.set_xticklabels(stats['sentiment_bucket'].astype(str), rotation=45, ha='right', fontsize=9)
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Mean likes count")
    ax.set_title("Mean likes by sentiment (+- stddev)")

    for i, row in stats.iterrows():
        ax.text(i, ax.get_ylim()[0], f'n={int(row["n"])}', ha='center', va='bottom', fontsize=7, color='gray')

    plt.tight_layout()
    plt.show()


def plot_engagement_sentiment_with_keywords():
    posts_df = pd.read_csv("posts_likes.csv")
    merged = pd.merge(
        df[['post_id', 'sentiment', 'keyword']].drop_duplicates(subset='post_id'),
        posts_df[['post_id', 'likes_count']],
        on='post_id',
        how='inner'
    ).dropna(subset=['sentiment', 'likes_count'])

    merged['sentiment_bucket'] = pd.cut(
        merged['sentiment'],
        bins=[-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['-1.0', '-0.8', '-0.6', '-0.4', '-0.2', '0.0', '0.2', '0.4', '0.6', '0.8']
    )

    stats = merged.groupby('sentiment_bucket', observed=True)['likes_count'].agg(
        mean='mean',
        sem=lambda x: x.std() / np.sqrt(len(x)),
        n='count'
    ).reset_index()

    # Keyword distribution per bin
    keyword_counts = (
        merged.groupby(['sentiment_bucket', 'keyword'], observed=True)
        .size()
        .reset_index(name='count')
    )
    # Normalize within each bin so we see %
    bin_totals = keyword_counts.groupby('sentiment_bucket', observed=True)['count'].transform('sum')
    keyword_counts['share'] = keyword_counts['count'] / bin_totals

    # Keep only top k
    top_k = 12
    top_keywords = (
        keyword_counts.groupby('keyword')['count'].sum()
        .nlargest(top_k).index.tolist()
    )
    keyword_counts = keyword_counts[keyword_counts['keyword'].isin(top_keywords)]

    heatmap_data = keyword_counts.pivot_table(
        index='keyword', columns='sentiment_bucket', values='share', observed=True
    ).fillna(0)
    # Keep column order consistent with sentiment bins
    heatmap_data = heatmap_data.reindex(columns=stats['sentiment_bucket'].astype(str), fill_value=0)

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(11, 9),
        gridspec_kw={'height_ratios': [2, 3]},
        constrained_layout=True
    )

    # Same plot from before (engagement line plot)
    x = range(len(stats))
    ax_top.plot(x, stats['mean'], color='steelblue', linewidth=2, marker='o')
    ax_top.fill_between(x,
                        stats['mean'] - stats['sem'],
                        stats['mean'] + stats['sem'],
                        alpha=0.2, color='steelblue')
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([])
    ax_top.set_ylabel("Mean likes count")
    ax_top.set_title("Mean likes by sentiment (+- stddev)")
    for i, row in stats.iterrows():
        ax_top.text(i, ax_top.get_ylim()[0], f'n={int(row["n"])}',
                    ha='center', va='bottom', fontsize=7, color='gray')

    im = ax_bot.imshow(
        heatmap_data.values,
        aspect='auto',
        cmap='YlOrRd',
        interpolation='nearest'
    )
    ax_bot.set_xticks(range(len(stats)))
    ax_bot.set_xticklabels(stats['sentiment_bucket'].astype(str), rotation=45, ha='right', fontsize=9)
    ax_bot.set_yticks(range(len(heatmap_data)))
    ax_bot.set_yticklabels(heatmap_data.index, fontsize=9)
    ax_bot.set_xlabel("Sentiment bucket")
    ax_bot.set_title(f"Keyword share per sentiment bin (top {top_k} keywords)")

    cbar = fig.colorbar(im, ax=ax_bot, fraction=0.03, pad=0.02)
    cbar.set_label("Share within bin", fontsize=8)

    for row_i, keyword in enumerate(heatmap_data.index):
        for col_j, bucket in enumerate(heatmap_data.columns):
            val = heatmap_data.loc[keyword, bucket]
            if val > 0.01:   # skip near-zero cells
                ax_bot.text(col_j, row_i, f'{val:.0%}',
                            ha='center', va='center', fontsize=7,
                            color='black' if val < 0.5 else 'white')

    plt.show()


def main():
    # plot_cooccurrence()
    # plot_engagement_sentiment()
    # plot_frequency(keywords="water crisis", smooth=True)
    # plot_time(
    #     keywords="all",
    #     smooth=True
    # )
    plot_engagement_sentiment_with_keywords()


if __name__ == "__main__":
    main()
