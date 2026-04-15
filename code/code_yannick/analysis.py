import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from tqdm import tqdm

# TODO: How many languages? more languages necessary? interface with `language` field?
MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"

print(f"Loading tokenizer and model: '{MODEL_NAME}'...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
print("Model and tokenizer loaded successfully.\n")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}\n")
model = model.to(device)

def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=-1)
    score = torch.arange(1, 6).float().to(device)
    sentiment = (probs * score).sum().item()
    sentiment = (sentiment - 3) / 2
    return sentiment

print("Loading posts from CSV...")
df = pd.read_csv("posts.csv")
print(f"Loaded {len(df)} posts.\n")

print("Starting sentiment analysis...\n")
keywords_list = df['keyword'].unique()

results = []
for i, keyword in enumerate(keywords_list, start=1):
    keyword_posts = df[df['keyword'] == keyword]
    print(f"[{i}/{len(keywords_list)}] Processing keyword: '{keyword}' ({len(keyword_posts)} posts)...")

    for _, row in tqdm(keyword_posts.iterrows(), total=len(keyword_posts), desc=f"  '{keyword}'", unit="post"):
        sentiment_score = get_sentiment(row['content'])
        results.append({
            'keyword': row['keyword'],
            'post_id': row['post_id'],
            'date': row['date'],
            'sentiment': sentiment_score
        })

    print(f"  ✓ Done with '{keyword}'.\n")

print(f"Sentiment analysis complete. Total posts processed: {len(results)}\n")

results_df = pd.DataFrame(results)
output_file = "post_sentiments_time.csv"
results_df.to_csv(output_file, index=False)
print(f"Saved {len(results_df)} sentiment scores to '{output_file}'.")
