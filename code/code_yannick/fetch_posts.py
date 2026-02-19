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

for i, keyword in enumerate(keywords_list, start=1):
    cursor.execute("""
        SELECT post_id, content, created_at
        FROM posts
        WHERE keywords = %s AND content IS NOT NULL
        ORDER BY created_at
        LIMIT 500
    """, (keyword,))

    rows = cursor.fetchall()
    print(f"[{i}/{len(keywords_list)}] Fetched {len(rows)} posts for keyword: '{keyword}'")

    for post_id, content, created_at in rows:
        data.append({
            'keyword': keyword,
            'post_id': post_id,
            'date': created_at,
            'content': clean_html(content)
        })

cursor.close()
conn.close()
print("Database connection closed.\n")

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

output_file = "posts.csv"
df.to_csv(output_file, index=False)
print(f"Saved {len(df)} posts to '{output_file}'.")
