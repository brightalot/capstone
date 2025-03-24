import mojito
import pandas as pd
import matplotlib.pyplot as plt

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# .env 파일에서 환경 변수 가져오기
my_key = os.getenv("MY_APP_KEY")
my_secret = os.getenv("MY_APP_SECRET_KEY")
my_acc_no = os.getenv("MY_ACC_NO")


#개인 정보 저장
broker = mojito.KoreaInvestment(
    api_key = my_key,
    api_secret = my_secret,
    acc_no = my_acc_no
)

code = "005930"

def code_by_name(name):
    for i in range(len(dict(kospi_symbols)['한글명'])):
        if dict(kospi_symbols)['한글명'][i] == name:
            return dict(kospi_symbols)['단축코드'][i]
        
    for i in range(len(dict(kosdaq_symbols)['한글명'])):
        if dict(kosdaq_symbols)['한글명'][i] == name:
            return dict(kosdaq_symbols)['단축코드'][i]

    return None  # 해당 종목이 없으면 None 반환

# 종목코드로 주가 정보 조회
def get_stock_price(code):
    if code is None:
        return None
    return broker.fetch_price(code)

# 시가, 고가, 저가, 종가, 현재가 가져오기
def get_price_by_type(code, price_type):
    stock_info = get_stock_price(code)
    if not stock_info:
        return "정보 없음"

    price_mapping = {
        "현재가": "stck_prpr",
        "시가": "stck_oprc",
        "고가": "stck_hgpr",
        "저가": "stck_lwpr",
        "종가": "stck_prpr"
    }

    return stock_info['output'].get(price_mapping.get(price_type, "stck_prpr"), "정보 없음")

#종목코드로 가격 정보들 불러오기
def stck_by_code(code):
    if code == None:
        return False
    return broker.fetch_price(code)

#시, 고, 저, 종가 함수
def oprc(code):
    info = stck_by_code(code)
    if not info:
        return '정보 없음'
    else:
        return info['output']['stck_oprc']

    #고
def hgpr(code):
    info = stck_by_code(code)
    if not info:
        return '정보 없음'
    else:
        return info['output']['stck_hgpr']

    #저
def lwpr(code):
    info = stck_by_code(code)
    if not info:
        return '정보 없음'
    else:
        return info['output']['stck_lwpr']

    #종가
def prpr(code):
    info = stck_by_code(code)
    if not info:
        return '정보 없음'
    else:
        return info['output']['stck_prpr']

    
    
#봉의 단위를 설정하여 해당정보들을 리턴
#인자로 문자 'Y', 'M', 'W', 'D'을 받는데 각각 연, 월, 주, 일봉을 의미
def resp_Time(T):
    resp = broker.fetch_ohlcv(
        symbol = code,
        timeframe = T,
        adj_price = True
    )
    return resp

#인자로 받은 주가 데이터를 그래프로 저장
def save_pic(chart_type):
    if chart_type == "일":
        chart_type = 'D'
    elif chart_type == "주":
        chart_type = 'W'
    elif chart_type == "월":
        chart_type = 'M'
    else:
        chart_type = 'Y'
        
    df = pd.DataFrame(resp_Time(chart_type)['output2'])
    dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
    lst = []

    for i in df['stck_oprc']:
        lst += [int(i)]

    #차트 저장 후 출력
    plt.plot(dt, lst)

    #PNG파일로 저장 .py 파일이 있는 같은 폴더내에 저장 됩니다
    plt.savefig('imagesaveexample.png')

# print(oprc(code))
# print(hgpr(code))
# print(lwpr(code))
# print(prpr(code))
save_pic("월")

print(stck_bsop_code(code))

