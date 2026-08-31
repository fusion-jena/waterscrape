import os
from datetime import datetime, timezone

import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from utils import clean_html

SNAP_ROOT = os.environ.get("SNAP_ROOT", os.path.expanduser("~/waterscrape/snapshots"))
MIN_COUNT = 1_000

load_dotenv()

print("Connecting to database...")
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)
print(f"Connected successfully to '{os.getenv('DB_NAME')}' at {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}.\n")

cursor = conn.cursor()

print("Fetching distinct keywords from posts...")
cursor.execute("SELECT DISTINCT keywords FROM posts WHERE keywords IS NOT NULL")
keywords_list = [row[0] for row in cursor.fetchall()]
print(f"Found {len(keywords_list)} keyword(s): {keywords_list}\n")

data = []

for i, keyword in enumerate(keywords_list, start=1):
    cursor.execute(
        """
        SELECT COUNT(*) FROM posts
        WHERE keywords = %s AND content IS NOT NULL AND content != ''
        AND created_at >= '2016-01-01'
        """,
        (keyword,),
    )
    count = cursor.fetchone()[0]

    if count < MIN_COUNT:
        print(f"[{i}/{len(keywords_list)}] Skipping keyword: '{keyword}' (only {count} posts)")
        continue

    cursor.execute(
        """
        SELECT post_id, content, created_at, likes_count
        FROM posts
        WHERE keywords = %s AND content IS NOT NULL AND content != ''
        AND content != ' ' AND created_at >= '2016-01-01'
        ORDER BY created_at
        """,
        (keyword,),
    )
    rows = cursor.fetchall()
    print(f"[{i}/{len(keywords_list)}] Fetched {len(rows)} posts for keyword: '{keyword}'")

    for post_id, content, created_at, likes_count in rows:
        if not isinstance(content, str) or not content.strip():
            continue
        data.append({
            'keyword': keyword,
            'post_id': post_id,
            'date': created_at,
            'content': clean_html(content),
            'likes_count': likes_count,
        })

cursor.close()
conn.close()
print("Database connection closed.\n")

if not data:
    print("No posts matched the criteria — nothing to write.")
    raise SystemExit(0)

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# just drop missing rows
df = df.dropna(subset=['date', 'content'])
df = df[df['content'].str.strip() != '']

# write into a fresh timestamped snapshot folder
snap_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
snap_dir = os.path.join(SNAP_ROOT, snap_id)
os.makedirs(snap_dir, exist_ok=True)

final_path = os.path.join(snap_dir, "data.csv")
tmp_path = final_path + ".partial"
df.to_csv(tmp_path, index=False)
os.replace(tmp_path, final_path)

print(f"Saved {len(df)} posts to '{final_path}'.")
