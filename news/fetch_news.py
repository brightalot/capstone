# news/fetch_news.py
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse
from db import get_connection

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
STOCK_KEYWORDS = ["삼성전자"]

def get_source(link):
    return urlparse(link).netloc

def fetch_naver_news_api(keyword, max_results, start_index):
    print(f"[INFO] Fetching news for: {keyword} (via Naver API)")
    
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {
        "query": keyword,
        "display": max_results,
        "start": str(start_index),
        "sort": "date"
    }
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"[ERROR] Naver API Error: {response.status_code}")
        return []
    
    data = response.json()
    news_list = []
    for item in data.get("items", []):
        pub_date = datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S +0900")
        formatted_date = pub_date.strftime("%Y-%m-%d")
        news_list.append({
            "pub_date": formatted_date,
            "keyword": keyword,
            "title": item["title"].replace("<b>", "").replace("</b>", ""),
            "link": item["link"],
            "source": get_source(item["link"])
        })
    return news_list

def fetch_naver_news_api_target_date(keyword, max_results, start_index, target_date):
    print(f"[INFO] Fetching news for: {keyword} for target date {target_date}")
    
    url = "https://openapi.naver.com/v1/search/news.json"
    params = {
        "query": keyword,
        "display": max_results,
        "start": str(start_index),
        "sort": "sim"
    }
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"[ERROR] Naver API Error: {response.status_code}")
        return []
    
    data = response.json()
    news_list = []
    for item in data.get("items", []):
        pub_date = datetime.strptime(item["pubDate"], "%a, %d %b %Y %H:%M:%S +0900")
        formatted_date = pub_date.strftime("%Y-%m-%d")
        if target_date and formatted_date != target_date:
            continue
        news_list.append({
            "pub_date": formatted_date,
            "keyword": keyword,
            "title": item["title"].replace("<b>", "").replace("</b>", ""),
            "link": item["link"],
            "source": get_source(item["link"])
        })
    return news_list

def save_news_to_db(news_list):
    if not news_list:
        print("[INFO] No news data to save.")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    for news in news_list:
        try:
            cur.execute("""
                INSERT INTO news_articles (pub_date, keyword, title, link, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING;
            """, (
                news["pub_date"],
                news["keyword"],
                news["title"],
                news["link"],
                news["source"]
            ))
            inserted += 1
        except Exception as e:
            print(f"[ERROR] Inserting news failed: {e}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"[INFO] Inserted {inserted} new news articles into database.")

# Example execution:
if __name__ == "__main__":
    all_news = []
    for keyword in STOCK_KEYWORDS:
        # 예시: 특정 날짜로 수집
        news_results = fetch_naver_news_api_target_date(keyword, 20, 1, "2025-03-27")
        all_news.extend(news_results)
        time.sleep(1)
    save_news_to_db(all_news)