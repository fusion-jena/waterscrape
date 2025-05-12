import argparse
from bsky_db import extract_bsky_db
from mstdn_db import extract_mastodon_db


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
    args = parser.parse_args()

    platforms, keywords, keyword_category = (
        args.platforms, args.keywords, args.keyword_category
    )

    for platform in platforms:
        if platform == "mastodon":
            extract_mastodon_db(keywords[0], keyword_category)
        elif platform == "bluesky":
            extract_bsky_db(keywords[0], keyword_category)
        else:
            raise ValueError("Invalid social media platform provided.")


if __name__ == '__main__':
    main()
