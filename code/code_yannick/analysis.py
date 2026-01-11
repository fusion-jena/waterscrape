import os
import pandas as pd
import mysql.connector
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from dotenv import load_dotenv

MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

cursor.execute("SELECT DISTINCT keywords FROM posts WHERE keywords IS NOT NULL")
keywords_list = [row[0] for row in cursor.fetchall()]

def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=-1)
    # nlptown model outputs 1-5 stars, convert to -1..1
    score = torch.arange(1, 6).float()
    sentiment = (probs * score).sum().item()
    sentiment = (sentiment - 3) / 2
    return sentiment

data = []

for keyword in keywords_list:
    cursor.execute("""
        SELECT post_id, content
        FROM posts
        WHERE keywords = %s AND content IS NOT NULL
        LIMIT 500
    """, (keyword,))
    
    rows = cursor.fetchall()
    print(f"Processing keyword: '{keyword}' ({len(rows)} posts)")

    for post_id, content in rows:
        sentiment_score = get_sentiment(content)
        data.append({'keyword': keyword, 'post_id': post_id, 'sentiment': sentiment_score})

cursor.close()
conn.close()

df = pd.DataFrame(data)
df.to_csv("post_sentiments.csv", index=False)
print("Saved sentiment scores to post_sentiments.csv")
