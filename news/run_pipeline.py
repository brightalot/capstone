# run_pipeline.py
import time
from fetch_news import fetch_naver_news_api, save_news_to_db
from crawl_body import crawl_and_update_news_body_db
from sentiment import analyze_and_update_sentiment_db


### 뉴스 키워드 설정 ###
STOCK_KEYWORDS = ["삼성전자"]

if __name__ == "__main__":
    # Step 1: 뉴스 수집 및 DB 저장
    for keyword in STOCK_KEYWORDS:
        #200개 뉴스 가져오기
        # news = fetch_naver_news_api(keyword, 100, 1)
        # save_news_to_db(news)
        # time.sleep(1)
        ############################################################
        #################### 뉴스 여러개 수집 ##########################

        all_news = []
        # 예: 1부터 501까지 20개씩 가져오기 (총 500개 뉴스)
        for start_index in range(1, 1000, 100):
            news_results = fetch_naver_news_api("삼성전자", 100, start_index)
            all_news.extend(news_results)
            time.sleep(1)  # API 호출 제한을 고려하여 지연 추가
        save_news_to_db(all_news)

        #################### 뉴스 여러개 수집 ##########################
        ############################################################
        
    
    # Step 2: 본문 크롤링 (네이버 뉴스에 한정)
    crawl_and_update_news_body_db()
    
    # Step 3: 감정 분석 업데이트
    analyze_and_update_sentiment_db()

    