import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from utils import clean_html

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

cursor = conn.cursor()

print("Fetching distinct keywords from posts...")
cursor.execute("SELECT DISTINCT keywords FROM posts WHERE keywords IS NOT NULL")
keywords_list = [row[0] for row in cursor.fetchall()]
print(f"Found {len(keywords_list)} keyword(s): {keywords_list}\n")

# TODO: add valid_keywords logic from main script

data = []

MIN_COUNT = 1_000
MAX_COUNT = 10_000

for i, keyword in enumerate(keywords_list, start=1):
    cursor.execute("""
        SELECT COUNT(*) FROM posts
        WHERE keywords = %s AND content IS NOT NULL AND content != ''
        AND created_at >= '2016-01-01'
    """, (keyword,))

    count = cursor.fetchone()[0]

    if count < MIN_COUNT:
        print(f"[{i}/{len(keywords_list)}] Skipping keyword: '{keyword}' (only {count} posts)")
        continue
    cursor.execute(f"""
            SELECT post_id, content, created_at, likes_count
            FROM posts
            WHERE keywords = %s AND content IS NOT NULL AND content != ''
            AND content != ' ' AND created_at >= '2016-01-01'
            ORDER BY created_at
            LIMIT {MAX_COUNT}
    """, (keyword,))

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
            'likes_count': likes_count
        })
    # cursor.execute(f"""
    #     SELECT post_id, content, created_at
    #     FROM posts
    #     WHERE keywords = %s AND content IS NOT NULL AND content != ''
    #     AND content != ' ' AND created_at >= '2016-01-01'
    #     ORDER BY created_at
    #     LIMIT {MAX_COUNT}
    # """, (keyword,))
    #
    # rows = cursor.fetchall()
    # print(f"[{i}/{len(keywords_list)}] Fetched {len(rows)} posts for keyword: '{keyword}'")
    #
    # for post_id, content, created_at in rows:
    #     if not isinstance(content, str) or not content.strip(): 
    #         continue
    #
    #     data.append({
    #         'keyword': keyword,
    #         'post_id': post_id,
    #         'date': created_at,
    #         'content': clean_html(content)
    #     })

cursor.close()
conn.close()
print("Database connection closed.\n")

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

df = df.dropna()
df = df[df['content'].str.strip() != '']

output_file = "posts_likes.csv"
df.to_csv(output_file, index=False)
print(f"Saved {len(df)} posts to '{output_file}'.")
