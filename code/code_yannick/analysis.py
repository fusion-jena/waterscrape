import os
import pandas as pd
import mysql.connector
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from dotenv import load_dotenv
from tqdm import tqdm


MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"

print(f"Loading tokenizer and model: '{MODEL_NAME}'...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
print("Model and tokenizer loaded successfully.\n")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}\n")
model = model.to(device)

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

def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=-1)
    score = torch.arange(1, 6).float().to(device)
    sentiment = (probs * score).sum().item()
    sentiment = (sentiment - 3) / 2
    return sentiment

data = []
total_posts = 0

print("Starting sentiment analysis...\n")
for i, keyword in enumerate(keywords_list, start=1):
    cursor.execute("""
        SELECT post_id, content, created_at
        FROM posts
        WHERE keywords = %s AND content IS NOT NULL
        ORDER BY created_at
        LIMIT 500
    """, (keyword,))

    rows = cursor.fetchall()
    print(f"[{i}/{len(keywords_list)}] Processing keyword: '{keyword}' ({len(rows)} posts)...")

    for post_id, content, created_at in tqdm(rows, desc=f"  '{keyword}'", unit="post"):
        sentiment_score = get_sentiment(content)
        data.append({
            'keyword': keyword,
            'post_id': post_id,
            'date': created_at,
            'sentiment': sentiment_score
        })

    total_posts += len(rows)
    print(f"  ✓ Done with '{keyword}'.\n")

print(f"Sentiment analysis complete. Total posts processed: {total_posts}\n")

cursor.close()
conn.close()
print("Database connection closed.\n")

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

output_file = "post_sentiments_time.csv"
df.to_csv(output_file, index=False)
print(f"Saved {len(df)} sentiment scores to '{output_file}'.")
