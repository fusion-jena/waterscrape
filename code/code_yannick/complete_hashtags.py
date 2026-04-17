import os
import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm
import requests
from html import unescape
from utils import is_noise

load_dotenv()


def fetch_mastodon_hashtags(post_id, instance):
    try:
        response = requests.get(
            f"https://{instance}/api/v1/statuses/{post_id}",
            timeout=10
        )
        response.raise_for_status()
        status = response.json()
        return [tag["name"] for tag in status.get("tags", [])]
    except Exception as e:
        print(f"[WARN] Mastodon fetch failed for {post_id}@{instance}: {e}")
        return []


def fetch_bluesky_hashtags(post_id, account_id):
    try:
        response = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts",
            params={"uris": f"at://{account_id}/app.bsky.feed.post/{post_id}"},
            timeout=10
        )
        response.raise_for_status()
        posts = response.json().get("posts", [])

        if not posts:
            return []

        record = posts[0].get("record")
        if not record or not record.get("facets"):
            return []

        tags = []
        for facet in record["facets"]:
            features = facet.get("features", [])
            if features and "tag" in features[0]:
                tags.append(features[0]["tag"])
        return tags
    except Exception as e:
        print(f"[WARN] BlueSky fetch failed for {post_id}: {e}")
        return []


def main():
    print("Connecting to database...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print(f"Connected successfully to '{os.getenv('DB_NAME')}' at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}.\n")

    read_cursor = conn.cursor(dictionary=True)
    read_cursor.execute("""
        SELECT post_id, from_platform, instance_name, account_id
        FROM posts
    """)
    rows = read_cursor.fetchall()
    read_cursor.close()

    write_cursor = conn.cursor(dictionary=True)
    updated = 0

    try:
        for i, row in enumerate(tqdm(rows, desc="Backfilling hashtags", unit="post")):
            post_id    = row["post_id"]
            platform   = row["from_platform"]
            instance   = row["instance_name"]
            account_id = row["account_id"]

            if platform == "BlueSky":
                tags = fetch_bluesky_hashtags(post_id, account_id)
            elif platform == "Mastodon":
                tags = fetch_mastodon_hashtags(post_id, instance)
            else:
                tags = []

            if not tags:
                continue

            for tag in tags:
                tag = unescape(tag).strip().lower().lstrip("#")

                if not tag or is_noise(tag):
                    continue

                # 1. Try insert first (fast path)
                write_cursor.execute(
                    "INSERT IGNORE INTO hashtags (hashtag) VALUES (%s)",
                    (tag,)
                )

                # 2. Always fetch id (safe, no race condition)
                write_cursor.execute(
                    "SELECT hashtag_id FROM hashtags WHERE hashtag=%s",
                    (tag,)
                )
                row_tag = write_cursor.fetchone()
                if not row_tag:
                    print(f"[ERROR] Could not find hashtag_id for #{tag}, skipping")
                    continue
                hashtag_id = row_tag["hashtag_id"]

                # 3. Insert edge
                write_cursor.execute("""
                    INSERT IGNORE INTO post_hashtags (post_id, hashtag_id)
                    VALUES (%s, %s)
                """, (post_id, hashtag_id))

                if write_cursor.rowcount == 1:
                    print(f"[LINKED] {post_id} -> #{tag} ({hashtag_id})")
                    updated += 1

            # Commit based on actual links added, not row index
            if updated > 0 and updated % 200 == 0:
                conn.ping(reconnect=True)
                conn.commit()
                print(f"[COMMIT] {updated} links committed so far...")

        # Final commit for remainder
        conn.ping(reconnect=True)
        conn.commit()
        print(f"\nDone — {updated} links added")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        try:
            conn.rollback()
            print("[ROLLBACK] Transaction rolled back.")
        except Exception as rb_err:
            print(f"[WARN] Rollback failed (connection lost?): {rb_err}")
        raise

    finally:
        try:
            write_cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        print("Database connection closed.\n")


if __name__ == "__main__":
    main()
