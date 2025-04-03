# news/sentiment.py
import psycopg2
from transformers import pipeline
from db import get_connection

sentiment_pipeline = pipeline("sentiment-analysis", model="kakaobank/kf-deberta-base")

def analyze_sentiment(text):
    result = sentiment_pipeline(text[:512])[0]
    label_raw = result["label"]
    score_raw = result["score"]
    if label_raw == "LABEL_1":
        return "positive", round(score_raw, 4)
    elif label_raw == "LABEL_0":
        return "negative", round(-score_raw, 4)
    else:
        return "neutral", 0.0

def analyze_and_update_sentiment_db():
    conn = get_connection()
    cur = conn.cursor()
    # 본문이 존재하지만 감정 분석 결과가 없는 기사 선택
    cur.execute("SELECT id, body FROM news_articles WHERE body IS NOT NULL AND sentiment_score IS NULL")
    rows = cur.fetchall()
    updated = 0
    for news_id, body in rows:
        label, score = analyze_sentiment(body)
        cur.execute("""
            UPDATE news_articles 
            SET sentiment_label = %s, sentiment_score = %s 
            WHERE id = %s
        """, (label, score, news_id))
        updated += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"[INFO] Sentiment analysis updated for {updated} articles.")

if __name__ == "__main__":
    analyze_and_update_sentiment_db()