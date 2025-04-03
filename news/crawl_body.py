# news/crawl_body.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from db import get_connection

def is_naver_news(url):
    return urlparse(url).netloc == "n.news.naver.com"

def extract_naver_body(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("#dic_area")
        return content.text.strip() if content else None
    except Exception as e:
        print(f"[ERROR] 본문 크롤링 실패: {url}\n{e}")
        return None

def crawl_and_update_news_body_db():
    conn = get_connection()
    cur = conn.cursor()
    # 본문이 없는 기사 중 네이버 뉴스만 선택
    cur.execute("SELECT id, link FROM news_articles WHERE body IS NULL AND source = %s", ("n.news.naver.com",))
    rows = cur.fetchall()
    updated = 0
    for news_id, link in rows:
        if is_naver_news(link):
            body = extract_naver_body(link)
            if body:
                cur.execute("UPDATE news_articles SET body = %s WHERE id = %s", (body, news_id))
                updated += 1
            else:
                print(f"[SKIP] 본문 없음: {link}")
        else:
            print(f"[SKIP] 네이버 뉴스 아님: {link}")
    conn.commit()
    cur.close()
    conn.close()
    print(f"[INFO] Updated body for {updated} articles.")

if __name__ == "__main__":
    crawl_and_update_news_body_db()