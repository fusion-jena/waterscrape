from flask import Flask, jsonify, request, send_from_directory
import mysql.connector
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# SERVE DASHBOARD
@app.route("/")
def index():
    return send_from_directory("frontend", "dashboard.html")


def keywords_like(keywords):
    return f"%{keywords}%"


@app.route("/api/keywords")
def keywords():
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT keywords, COUNT(*) AS total
            FROM posts
            GROUP BY keywords
            HAVING total >= 1000
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        return jsonify([r["keywords"] for r in rows])
    finally:
        conn.close()

# ── /api/weekly-counts ─────────────────────────────────────────────────────────
@app.route("/api/weekly-counts")
def weekly_counts():
    keywords = request.args.get("keywords")
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        if keywords and keywords != "all":
            cursor.execute("""
                SELECT
                    DATE(DATE_SUB(created_at, INTERVAL WEEKDAY(created_at) DAY)) AS date,
                    keywords,
                    COUNT(*) AS n_posts
                FROM posts
                WHERE keywords LIKE %s
                  AND created_at >= '2018-01-01'
                GROUP BY date, keywords
                ORDER BY date
            """, (keywords_like(keywords),))
        else:
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
        cursor.close()

        # 3-week rolling average, grouped per keyword so series don't bleed
        by_kw = defaultdict(list)
        for r in rows:
            if r["date"] is None:
                continue
            r["date"] = r["date"].isoformat()
            by_kw[r["keywords"]].append(r)

        result = []
        for kw_rows in by_kw.values():
            for i, r in enumerate(kw_rows):
                window = kw_rows[max(0, i - 3): i + 4]
                r["n_posts_smooth"] = round(
                    sum(w["n_posts"] for w in window) / len(window), 1
                )
                result.append(r)

        return jsonify(result)
    finally:
        conn.close()


@app.route("/api/hashtags")
def hashtags():
    keywords = request.args.get("keywords", "")
    limit   = int(request.args.get("limit", 15))
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT h.hashtag, COUNT(*) AS freq
            FROM post_hashtags ph
            JOIN hashtags h ON ph.hashtag_id = h.hashtag_id
            JOIN posts p ON ph.post_id = p.post_id
            WHERE p.keywords LIKE %s
            GROUP BY h.hashtag
            ORDER BY freq DESC
            LIMIT %s
        """, (keywords_like(keywords), limit))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows)
    finally:
        conn.close()


@app.route("/api/engagement")
def engagement():
    keywords = request.args.get("keywords", "")
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
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
        """, (keywords_like(keywords),))
        row = cursor.fetchone()
        cursor.close()
        return jsonify(row)
    finally:
        conn.close()


@app.route("/api/post-types")
def post_types():
    keywords = request.args.get("keywords", "")
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                SUM(in_reply_to_id IS NOT NULL) AS replies,
                SUM(in_reply_to_id IS NULL)     AS originals
            FROM posts
            WHERE keywords LIKE %s
        """, (keywords_like(keywords),))
        type_row = cursor.fetchone()

        cursor.execute("""
            SELECT from_platform AS platform, COUNT(*) AS count
            FROM posts
            WHERE keywords LIKE %s
            GROUP BY from_platform
            ORDER BY count DESC
        """, (keywords_like(keywords),))
        platform_rows = cursor.fetchall()
        cursor.close()

        return jsonify({
            "originals":   int(type_row["originals"] or 0),
            "replies":     int(type_row["replies"]   or 0),
            "by_platform": platform_rows,
        })
    finally:
        conn.close()


@app.route("/api/top-posts")
def top_posts():
    keywords = request.args.get("keywords", "")
    limit   = int(request.args.get("limit", 5))
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                post_id, created_at, from_platform, instance_name,
                content, likes_count, replies_count, reblogs_count
            FROM posts
            WHERE keywords LIKE %s
              AND content IS NOT NULL
            ORDER BY likes_count DESC
            LIMIT %s
        """, (keywords_like(keywords), limit))
        rows = cursor.fetchall()
        cursor.close()

        for r in rows:
            if r.get("created_at"):
                r["created_at"] = r["created_at"].isoformat()

        return jsonify(rows)
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
