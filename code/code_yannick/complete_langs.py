import os
import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm
import requests
from html import unescape
from utils import is_noise

load_dotenv()

print("Connecting to database...")
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
print(f"Connected successfully to '{os.getenv('DB_NAME')}' at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}.\n")

cursor = conn.cursor(dictionary=True)
update_cursor = conn.cursor()

# Fetch all posts with no language data
cursor.execute("""
    SELECT p.post_id, p.from_platform, p.instance_name, p.account_id
    FROM posts p
    LEFT JOIN post_languages pl ON p.post_id = pl.post_id
    WHERE pl.post_id IS NULL
""")
rows = cursor.fetchall()
print(f"Found {len(rows)} posts with missing language data.\n")


updated = 0
failed = 0

def fetch_bluesky_language(post_id, account_id):
    """Fetch language for a Bluesky post using the AT Protocol API."""
    try:
        response = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts",
            params={"uris": f"at://{account_id}/app.bsky.feed.post/{post_id}"},
            timeout=10
        )
        response.raise_for_status()
        posts = response.json().get("posts", [])
        if posts:
            langs = posts[0].get("record", {}).get("langs")
            if langs:
                return ",".join(langs)
    except Exception:
        pass
    return None

def fetch_mastodon_language(post_id, instance):
    """Fetch language for a Mastodon post using the instance API."""
    try:
        response = requests.get(
            f"https://{instance}/api/v1/statuses/{post_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("language")
    except Exception:
        pass
    return None


try:
    for i, row in enumerate(tqdm(rows, desc="Fetching languages", unit="post")):
        post_id    = row['post_id']
        platform   = row['from_platform']
        instance   = row['instance_name']
        account_id = row['account_id']

        lang = None

        if platform == "BlueSky":
            lang = fetch_bluesky_language(post_id, account_id)
        elif platform == "Mastodon":
            lang = fetch_mastodon_language(post_id, instance)

        if not lang:
            failed += 1
            continue

        try:
            update_cursor.execute(
                "UPDATE posts SET languages = %s WHERE post_id = %s",
                (lang, post_id)
            )

            lang_rows = [
                (post_id, l.strip())
                for l in lang.split(",")
                if l.strip()
            ]

            update_cursor.executemany(
                "INSERT IGNORE INTO post_languages (post_id, language) VALUES (%s, %s)",
                lang_rows
            )

            updated += 1

        except mysql.connector.Error:
            conn.rollback()
            raise  # fail fast, no retry

        # periodic commit (reduces lock time)
        if updated > 0 and updated % 100 == 0:
            conn.commit()

    conn.commit()

    print(f"\nDone — {updated} posts updated, {failed} could not be resolved.")

except Exception:
    conn.rollback()
    raise

finally:
    update_cursor.close()
    conn.close()
    print("Database connection closed.\n")
