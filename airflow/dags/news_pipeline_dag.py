from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import time

# 명시적으로 경로 추가 (컨테이너 내 경로 기준)
sys.path.insert(0, '/opt/airflow')

def collect_news():
    """네이버 뉴스 API를 호출해 '삼성전자' 관련 뉴스를 수집하고 DB에 저장하는 함수"""
    from news.fetch_news import fetch_naver_news_api, save_news_to_db

    # all_news = []
    # for start_index in range(1, 101, 100):
    #     news_results = fetch_naver_news_api("삼성전자", 100, start_index)
    #     all_news.extend(news_results)
    # save_news_to_db(all_news)
    
    all_news = []
    # 예: 1부터 501까지 20개씩 가져오기 (총 500개 뉴스)
    for start_index in range(1, 1000, 100):
        news_results = fetch_naver_news_api("삼성전자", 100, start_index)
        all_news.extend(news_results)
        time.sleep(1)  # API 호출 제한을 고려하여 지연 추가
    save_news_to_db(all_news)

def crawl_body():
    """뉴스 본문을 크롤링하여 DB에 저장하는 함수"""
    from news.crawl_body import crawl_and_update_news_body_db
    
    crawl_and_update_news_body_db()

def analyze_sentiment():
    """뉴스 본문의 감정 분석을 수행하는 함수"""
    from news.sentiment import analyze_and_update_sentiment_db
    
    analyze_and_update_sentiment_db()


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'news_pipeline_dag',
    default_args=default_args,
    description='뉴스 수집, 본문 크롤링, 감정 분석 파이프라인',
    schedule_interval=timedelta(days=1),  # 매일 실행하도록 스케줄
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id='collect_news',
        python_callable=collect_news
    )

    t2 = PythonOperator(
        task_id='crawl_body',
        python_callable=crawl_body
    )

    t3 = PythonOperator(
        task_id='sentiment_analysis',
        python_callable=analyze_sentiment
    )

    t1 >> t2 >> t3