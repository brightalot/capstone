import mojito
import pandas as pd
import matplotlib.pyplot as plt
from utils.image_upload import upload_to_s3 # 이미지 업로드 관련 모듈
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# .env 파일에서 환경 변수 가져오기
my_app_key = os.getenv("MY_APP_KEY")
my_app_secret_key = os.getenv("MY_APP_SECRET_KEY")

my_key = os.getenv("MY_APP_KEY_2")
my_secret = os.getenv("MY_APP_SECRET_KEY_2")
my_acc_no = os.getenv("MY_ACC_NO_2")


#개인 정보 저장
broker = mojito.KoreaInvestment(
    api_key = my_key,
    api_secret = my_secret,
    acc_no = my_acc_no
)

#전역 변수로 코스피 / 코스닥 심볼 저장
kospi_symbols = broker.fetch_kospi_symbols()
kosdaq_symbols = broker.fetch_kosdaq_symbols()

def code_by_name(name):
    for i in range(len(dict(kospi_symbols)['한글명'])):
        if dict(kospi_symbols)['한글명'][i] == name:
            return dict(kospi_symbols)['단축코드'][i]
        
    for i in range(len(dict(kosdaq_symbols)['한글명'])):
        if dict(kosdaq_symbols)['한글명'][i] == name:
            return dict(kosdaq_symbols)['단축코드'][i]

    return None  # 해당 종목이 없으면 None 반환

def get_stock_price(stock_name, price_type="현재가"):
    stock_code = code_by_name(stock_name)
    if not stock_code:
        return "⚠️ 해당 종목을 찾을 수 없습니다."

    stock_info = broker.fetch_price(stock_code)
    if not stock_info or "output" not in stock_info:
        return "⚠️ 주가 정보를 가져올 수 없습니다."
    
    output = stock_info["output"]

    price_mapping = {
        "현재가": "stck_prpr",
        "시가": "stck_oprc",
        "고가": "stck_hgpr",
        "저가": "stck_lwpr",
        "종가": "stck_prpr"
    }
    
    price = output.get(price_mapping.get(price_type, "stck_prpr"), "정보 없음")

    # 현재가일 경우, 등락 정보도 함께 제공
    if price_type == "현재가":
        change_sign = output.get("prdy_vrss_sign")  # '1' 하락, '2' 상승, '3' 보합
        change_rate = output.get("prdy_ctrt", "0.00")
        print(f"\nchange_sign : {change_sign}\n")
        if change_sign == "5":
            change_symbol = "▼"
        elif change_sign == "2":
            change_symbol = "▲"
        else:
            change_symbol = "-"

        return price, f"{stock_name}의 현재가는 {price}원 ({change_symbol}{change_rate}%)입니다."

    return price, f"{stock_name}의 {price_type}는 {price}원입니다."


#봉의 단위를 설정하여 해당정보들을 리턴
#인자로 문자 'Y', 'M', 'W', 'D'을 받는데 각각 연, 월, 주, 일봉을 의미
def resp_Time(code, T):
    resp = broker.fetch_ohlcv(
        symbol = code,
        timeframe = T,
        adj_price = True
    )
    print("----------------------")
    print(resp)
    print("----------------------")
    return resp

#인자로 받은 주가 데이터를 그래프로 저장
def draw_chart(chart_type, stock_name):
    plt.clf()  # 이전 차트 데이터 초기화
    save_path = os.path.join(os.getcwd(), "chart_images", "stock_chart3.png")
    
    # 종목명을 단축코드로 변환
    stock_code = code_by_name(stock_name)
    if not stock_code:
        print(f"종목 코드 변환 실패: {stock_name}")
        return None  # 변환 실패 시 None 반환

    print(f"✅ {stock_name} ({stock_code}) 차트 생성")

    # 차트 타입 변환
    chart_map = {"일": "D", "주": "W", "월": "M", "연": "Y"}
    chart_type = chart_map.get(chart_type, "D")  # 기본값: 일봉(D)
    
    df = pd.DataFrame(resp_Time(stock_code, chart_type)['output2'])
    dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
    lst = []

    for i in df['stck_oprc']:
        lst += [int(i)]
    #차트 저장 후 출력
    plt.plot(dt, lst)
    plt.title(f"{stock_name}")
    plt.legend()
    plt.grid()

    #PNG파일로 저장 .py 파일이 있는 같은 폴더내에 저장 됩니다
    plt.savefig(save_path)
    # S3에 업로드
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    object_name = date + 'chart.png'
    s3_url = upload_to_s3(save_path, object_name)
    if s3_url:
        print(f"Chart uploaded to CloudFront: {s3_url}")
    else:
        print("Failed to upload chart to CloudFront.")

    return s3_url