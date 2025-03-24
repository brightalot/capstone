import os
import requests
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

def get_volume_rank():
    """
    국내 주식 거래량 순위 조회 (거래량 기준)
    """
    base_url = os.getenv("KI_BASE_URL")
    token = os.getenv("KI_TOKEN")
    app_key = os.getenv("KI_APPKEY")
    app_secret = os.getenv("KI_APPSECRET")

    if not base_url or not token or not app_key or not app_secret:
        return {"error": "환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요."}

    url = f"{base_url}/uapi/domestic-stock/v1/ranking/fluctuation"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",       # 시장 분류 코드 (J: 주식)
        "FID_COND_SCR_DIV_CODE": "20171",    # 화면 분류 코드 (20171)
        "FID_INPUT_ISCD": "0002",            # 입력 종목 코드 (0002: 전체)
        "FID_DIV_CLS_CODE": "0",             # 분류 구분 코드 (0: 전체)
        "FID_BLNG_CLS_CODE": "0",            # 소속 구분 코드 (0: 평균 거래량)
        "FID_TRGT_CLS_CODE": "111111111",    # 대상 구분 코드
        "FID_TRGT_EXLS_CLS_CODE": "000000",  # 대상 제외 구분 코드
        "FID_INPUT_PRICE_1": "0",            # 가격 하한
        "FID_INPUT_PRICE_2": "0",            # 가격 상한
        "FID_VOL_CNT": "0",                  # 거래량 하한
        "FID_INPUT_DATE_1": "0"              # 입력 날짜
    }

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "FHPST01710000"  # 거래량 순위 TR ID
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result_json = response.json()

        # ✅ API 응답 확인
        print("🔍 API 응답 데이터:", result_json)

        # ✅ output을 리스트로 가져오기
        output_list = result_json.get("output", [])

        # ✅ 데이터가 비어 있는 경우 처리
        if not output_list:
            print("⚠️ 거래량 상위 종목 데이터가 없음!")
            return {"error": "거래량 상위 종목 데이터를 찾을 수 없습니다."}

    except requests.exceptions.RequestException as e:
        print("❌ API 호출 실패:", e)
        return {"error": f"API 호출 실패: {e}"}

    # ✅ 응답 데이터 정리 (상위 5개 종목)
    stock_list = [
    {
        "name": item.get("hts_kor_isnm", "N/A"),  # 종목명
        "price": item.get("stck_prpr", "N/A"),    # 현재가
        "volume": item.get("acml_vol", "N/A"),    # 거래량
        "code": item.get("stck_shrn_iscd", "N/A")
    }
        for item in output_list[:5]
    ]

    print("✅ 최종 주식 리스트:", stock_list)  # 결과 출력
    return stock_list

