import argparse
import os
import mysql.connector
from bsky_db import extract_bsky_db
from mstdn_db import extract_mastodon_db
from topics.hierarchy import get_keyword_dict
from dotenv import load_dotenv


def scrape_with_keywords(platform, keywords, keyword_category):
    if platform == "mastodon":
        extract_mastodon_db(keywords[0], keyword_category[0])
    elif platform == "bluesky":
        extract_bsky_db(keywords[0], keyword_category[0])
    else:
        raise ValueError("Invalid social media platform provided.")


def scrape_all_keywords(platform, k=None):
    if k:
        load_dotenv()

        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT keywords
            FROM posts
            WHERE keywords IS NOT NULL
            GROUP BY keywords
            HAVING COUNT(*) >= {k}
        """)

        valid_keywords = {row[0] for row in cursor.fetchall()}

    for keyword, keyword_category in get_keyword_dict().items():
        if valid_keywords and keyword not in valid_keywords:
            print(f"Skipping {keyword} with < {k} posts")
            continue

        print("Scraping keyword", keyword)
        if platform == "mastodon":
            extract_mastodon_db(keyword, keyword_category)
        elif platform == "bluesky":
            extract_bsky_db(keyword, keyword_category)
        else:
            raise ValueError("Invalid social media platform provided.")


def main():
    parser = argparse.ArgumentParser(
        description="Main script for scraping of water-based data"
                    "from Mastodon and BlueSky."
    )
    parser.add_argument(
        "platforms",
        type=str,
        nargs="+",
        help="Platforms to parse",
        choices=["mastodon", "bluesky"]
    )
    parser.add_argument(
        "--keywords",
        type=str,
        nargs=1,
        help="Keywords to query for (enclosed in quotation marks)",
        choices=["water scarcity", "water crisis"]
    )
    parser.add_argument(
        "--keyword_category",
        type=str,
        nargs=1,
        help="Category of keywords (enclosed in quotation marks",
        choices=["water conflict"]
    )
    parser.add_argument(
        "k",
        type=int,
        default=None,
        help="Only keep keywords with >= k posts"
    )

    args = parser.parse_args()

    platforms, keywords, keyword_category, k = (
        args.platforms, args.keywords, args.keyword_category, args.k
    )

    assert len(platforms) == 1
    if keywords:
        scrape_with_keywords(platforms[0], keywords, keyword_category)
    else:
        # TODO: Make this dynamic
        print(
            "No keyword provided, using keywords from "
            "topics/hierarchy-social-media.txt"
        )
        scrape_all_keywords(platforms[0], k)


if __name__ == '__main__':
    main()
