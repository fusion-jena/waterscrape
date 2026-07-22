import os
import csv
import mysql.connector
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

DATA_MIN_POSTS = int(os.getenv("DATA_MIN_POSTS", 1000))
OUT_DIR = os.path.join(os.path.dirname(__file__), "data", "csv")
os.makedirs(OUT_DIR, exist_ok=True)

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)
cursor = conn.cursor(dictionary=True)

def write_csv(filename, rows, fieldnames=None):
    path = os.path.join(OUT_DIR, filename)
    if not rows:
        print(f"  [skip] {filename} — no rows")
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [ok]   {filename} ({len(rows)} rows)")


print("Exporting keywords...")
cursor.execute("""
    SELECT keywords, COUNT(*) AS total
    FROM posts
    GROUP BY keywords
    HAVING total >= %s
    ORDER BY total DESC
""", (DATA_MIN_POSTS,))
kw_rows = cursor.fetchall()
keywords = [r["keywords"] for r in kw_rows]
write_csv("keywords.csv", kw_rows, fieldnames=["keywords", "total"])


print("Exporting weekly counts...")
cursor.execute("""
    SELECT
        DATE(DATE_SUB(created_at, INTERVAL WEEKDAY(created_at) DAY)) AS date,
        keywords,
        COUNT(*) AS n_posts
    FROM posts
    WHERE created_at >= '2018-01-01'
    GROUP BY date, keywords
    ORDER BY date
""")
rows = cursor.fetchall()

# compute smoothed values per keyword
by_kw = defaultdict(list)
for r in rows:
    if r["date"] is None:
        continue
    r["date"] = r["date"].isoformat()
    by_kw[r["keywords"]].append(r)

weekly_rows = []
for kw_rows_list in by_kw.values():
    for i, r in enumerate(kw_rows_list):
        window = kw_rows_list[max(0, i - 3): i + 4]
        r["n_posts_smooth"] = round(
            sum(w["n_posts"] for w in window) / len(window), 1
        )
        weekly_rows.append(r)

write_csv("weekly_counts.csv", weekly_rows,
          fieldnames=["date", "keywords", "n_posts", "n_posts_smooth"])


print("Exporting engagement...")
eng_rows = []
for kw in keywords:
    like = f"%{kw}%"
    cursor.execute("""
        SELECT
            ROUND(AVG(replies_count), 1)  AS avg_replies,
            ROUND(AVG(reblogs_count), 1)  AS avg_reblogs,
            ROUND(AVG(likes_count),   1)  AS avg_likes,
            MAX(replies_count)            AS max_replies,
            MAX(reblogs_count)            AS max_reblogs,
            MAX(likes_count)              AS max_likes
        FROM posts
        WHERE keywords LIKE %s
    """, (like,))
    row = cursor.fetchone()
    row["keywords"] = kw
    eng_rows.append(row)

write_csv("engagement.csv", eng_rows,
          fieldnames=["keywords", "avg_replies", "avg_reblogs", "avg_likes",
                      "max_replies", "max_reblogs", "max_likes"])


print("Exporting post types...")
type_rows = []
platform_rows = []
for kw in keywords:
    like = f"%{kw}%"
    cursor.execute("""
        SELECT
            SUM(in_reply_to_id IS NOT NULL) AS replies,
            SUM(in_reply_to_id IS NULL)     AS originals
        FROM posts WHERE keywords LIKE %s
    """, (like,))
    t = cursor.fetchone()
    type_rows.append({
        "keywords": kw,
        "originals": int(t["originals"] or 0),
        "replies":   int(t["replies"]   or 0),
    })

    cursor.execute("""
        SELECT from_platform AS platform, COUNT(*) AS count
        FROM posts WHERE keywords LIKE %s
        GROUP BY from_platform ORDER BY count DESC
    """, (like,))
    for p in cursor.fetchall():
        platform_rows.append({"keywords": kw, **p})

write_csv("post_types.csv",   type_rows,     fieldnames=["keywords", "originals", "replies"])
write_csv("platforms.csv",    platform_rows, fieldnames=["keywords", "platform", "count"])


print("Exporting hashtags...")
hash_rows = []
for kw in keywords:
    like = f"%{kw}%"
    cursor.execute("""
        SELECT h.hashtag, COUNT(*) AS freq
        FROM post_hashtags ph
        JOIN hashtags h ON ph.hashtag_id = h.hashtag_id
        JOIN posts p ON ph.post_id = p.post_id
        WHERE p.keywords LIKE %s
        GROUP BY h.hashtag
        ORDER BY freq DESC
        LIMIT 15
    """, (like,))
    for row in cursor.fetchall():
        hash_rows.append({"keywords": kw, **row})

write_csv("hashtags.csv", hash_rows, fieldnames=["keywords", "hashtag", "freq"])


print("Exporting top posts...")
post_rows = []
for kw in keywords:
    like = f"%{kw}%"
    cursor.execute("""
        SELECT
            post_id, created_at, from_platform, instance_name,
            content, likes_count, replies_count, reblogs_count
        FROM posts
        WHERE keywords LIKE %s AND content IS NOT NULL
        ORDER BY likes_count DESC
        LIMIT 5
    """, (like,))
    for row in cursor.fetchall():
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        post_rows.append({"keywords": kw, **row})

write_csv("top_posts.csv", post_rows,
          fieldnames=["keywords", "post_id", "created_at", "from_platform",
                      "instance_name", "content", "likes_count",
                      "replies_count", "reblogs_count"])


cursor.close()
conn.close()
print("\nDone. CSVs written to", OUT_DIR)
