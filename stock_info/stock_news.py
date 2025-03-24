import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from stock_info.draw_chart import code_by_name
# 대상 URL
url = "https://finance.naver.com/news/news_list.naver?mode=RANK"

def get_finance_news():
    _url = url
    # 페이지 가져오기
    response = requests.get(_url)
    response.encoding = 'euc-kr'  # 네이버 금융 페이지는 euc-kr 인코딩 사용
    html = response.text

    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(html, 'html.parser')

    # 뉴스 블록 찾기
    news_list = soup.select('li.block1 ul.simpleNewsList > li')

    # 뉴스 정보 추출
    news_data = []
    for news in news_list:
        title_tag = news.find('a')
        title = title_tag['title']
        link = "https://finance.naver.com/" + title_tag['href']
        # JSON 형태로 변환
        link_dict = {"web": "https://finance.naver.com/" + title_tag['href']}
        press = news.find('span', class_='press').get_text(strip=True)
        wdate = news.find('span', class_='wdate').get_text(strip=True)
        description = press + " | " + wdate
        print(link)
        print(title)
        news_data.append({
            "title": title,
            "description": description,
            "link": link_dict
        })
    return news_data[:5]


app = Flask(__name__)

# # 📰 특정 종목 뉴스 크롤링 함수
# def get_stock_news(stock_name):
#     startdate = datetime.datetime.strptime('2024-02-01', "%Y-%m-%d")  # 검색 시작 날짜
#     enddate = datetime.datetime.strptime('2024-02-08', "%Y-%m-%d")  # 검색 종료 날짜
#     news_list = []

#     # Chrome 드라이버 설정
#     serv = Service(ChromeDriverManager().install())
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--headless')  # GUI 없이 실행
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     driver = webdriver.Chrome(service=serv, options=chrome_options)

#     try:
#         # 뉴스 검색 URL 생성 (매일경제 기준)
#         startdate_str = startdate.strftime("%Y-%m-%d")
#         enddate_str = enddate.strftime("%Y-%m-%d")
#         url = f'https://www.mk.co.kr/search?word={stock_name}&dateType=direct&startDate={startdate_str}&endDate={enddate_str}&searchField=title'
#         driver.get(url)

#         # 뉴스 개수 확인
#         try:
#             n_news = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/section/div/div[2]/div/div/div[1]/section/header/div[1]/h2/span'))
#             ).text
#         except:
#             n_news = '0'

#         if n_news.isdigit() and int(n_news) > 0:
#             soup = bs(driver.page_source, 'html.parser')
#             news_date = soup.find_all("div", {"class": "txt_area"})

#             for n in news_date[:5]:  # 최신 5개 뉴스 제공
#                 date_text = n.find("div", {"class": "info_group"}).find("p", {"class": "time_info"}).text
#                 title_text = n.find("h3", {"class": "news_ttl"}).text
#                 news_list.append({"date": date_text, "title": title_text})

#     except Exception as e:
#         print("Error during news scraping:", e)

#     driver.quit()
#     return news_list


def get_stock_news(stock_code):
    iframe_url = f"https://finance.naver.com/item/news_news.naver?code={stock_code}&page=1"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/99.0.4844.51 Safari/537.36"
        )
    }

    res = requests.get(iframe_url, headers=headers)
    res.encoding = "euc-kr"
    html = res.text

    # 1) 혹시라도 내용이 비정상인지 확인해보세요.
    # print(html)

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.type5")
    if not table:
        return []  # 테이블 자체가 없으면 []

    rows = table.select("tbody > tr")

    news_data = []
    for row in rows:
        # relation 관련 클래스는 건너뛰기
        row_classes = row.get("class", [])
        if "relation_tit" in row_classes or "relation_lst" in row_classes:
            continue

        title_tag = row.select_one("td.title > a.tit")
        press_tag = row.select_one("td.info")
        date_tag = row.select_one("td.date")

        if title_tag and press_tag and date_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href")
            press = press_tag.get_text(strip=True)
            wdate = date_tag.get_text(strip=True)
            news_data.append({
                "title": title,
                "description": f"{press} | {wdate}",
                "link": {"web": link}
            })
    print(news_data)
    return news_data