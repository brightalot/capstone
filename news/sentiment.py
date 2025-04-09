# news/sentiment.py
import psycopg2
import time
from transformers import pipeline
from .db import get_connection

# 함수 호출시 최초 한 번만 모델을 로드하도록 전역 변수로 선언
sentiment_pipeline = None

def get_sentiment_pipeline():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        print("[INFO] 감정 분석 모델 로딩 중...")
        sentiment_pipeline = pipeline("sentiment-analysis", model="kakaobank/kf-deberta-base")
    return sentiment_pipeline

def analyze_sentiment(text):
    if not text:
        return "neutral", 0.0
    
    pipeline = get_sentiment_pipeline()
    result = pipeline(text[:512])[0]
    label_raw = result["label"]
    score_raw = result["score"]
    
    if label_raw == "LABEL_1":
        return "positive", round(score_raw, 4)
    elif label_raw == "LABEL_0":
        return "negative", round(-score_raw, 4)
    else:
        return "neutral", 0.0

def analyze_and_update_sentiment_db(batch_size=50):
    """
    배치 처리 방식으로 뉴스 감정 분석
    
    Args:
        batch_size: 한 번에 처리할 뉴스 기사 수
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # 처리해야 할 전체 기사 수 확인
    cur.execute("SELECT COUNT(*) FROM news_articles WHERE body IS NOT NULL AND sentiment_score IS NULL")
    total_count = cur.fetchone()[0]
    
    if total_count == 0:
        print("[INFO] 감정 분석이 필요한 기사가 없습니다.")
        cur.close()
        conn.close()
        return
    
    print(f"[INFO] 총 {total_count}개 기사에 대해 감정 분석을 수행합니다.")
    
    # 배치 처리를 위한 오프셋 초기화
    offset = 0
    updated = 0
    
    # 모델 사전 로드
    get_sentiment_pipeline()
    
    while offset < total_count:
        # 배치 단위로 데이터 가져오기
        cur.execute("""
            SELECT id, body FROM news_articles 
            WHERE body IS NOT NULL AND sentiment_score IS NULL
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (batch_size, offset))
        
        rows = cur.fetchall()
        if not rows:
            break
            
        print(f"[INFO] 배치 처리 중: {offset+1}~{offset+len(rows)}/{total_count}")
        batch_start_time = time.time()
        
        # 감정 분석 수행
        for news_id, body in rows:
            try:
                label, score = analyze_sentiment(body)
                cur.execute("""
                    UPDATE news_articles 
                    SET sentiment_label = %s, sentiment_score = %s 
                    WHERE id = %s
                """, (label, score, news_id))
                updated += 1
                
                # 10개마다 커밋
                if updated % 10 == 0:
                    conn.commit()
                    print(f"[INFO] {updated}/{total_count} 기사 처리 완료")
                    
            except Exception as e:
                print(f"[ERROR] ID {news_id}의 감정 분석 중 오류 발생: {e}")
        
        # 배치 처리 완료 후 커밋
        conn.commit()
        batch_time = time.time() - batch_start_time
        print(f"[INFO] 배치 {offset+1}~{offset+len(rows)} 처리 완료 (소요시간: {batch_time:.2f}초)")
        time.sleep(1)
        
        # 다음 배치를 위해 오프셋 증가
        offset += batch_size
    
    cur.close()
    conn.close()
    print(f"[INFO] 감정 분석 완료: 총 {updated}개 기사 처리됨")

if __name__ == "__main__":
    analyze_and_update_sentiment_db()