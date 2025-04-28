from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import font_manager as fm
from utils.image_upload import upload_to_s3 # 이미지 업로드 관련 모듈
from utils.get_hash_key import get_hash # 해쉬키 발급
from stock_info.stock_news import get_finance_news, get_stock_news
from stock_info.draw_chart import draw_chart, get_stock_price, code_by_name
from stock_info.stock_rank import get_volume_rank


app = Flask(__name__)
font_path = '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf'
font_prop = fm.FontProperties(fname=font_path)
rc('font', family=font_prop.get_name())    
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# .env 파일 로드
load_dotenv()

# .env 파일에서 환경 변수 가져오기
price_info_block_id = os.getenv("PRICE_INFO_BLOCK_ID")
chart_info_block_id = os.getenv("CHART_INFO_BLOCK_ID")
home_block_id = os.getenv("HOME_BLOCK_ID")
stock_info_block_id = os.getenv("STOCK_INFO_BLOCK_ID")
mock_balance_id=os.getenv("MOCK_BALANCE_ID")

@app.route("/")
def hello():
    return "Hello"

@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    print("Received data:", data)

    # 사용자가 입력한 종목명
    user_message = data['userRequest']['utterance'].strip()

    # 예제 응답
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"테스트 응답: '{user_message}'"
                    }
                }
            ]
        }
    }

    return jsonify(response)

# 가격 조회 API
@app.route('/price', methods=['POST'])
def price():
    data = request.get_json()
    print("Received data:", data)

    # 컨텍스트에서 종목명 가져오기
    stock_name = None
    for context in data.get('contexts', []):
        if context['name'] == "stock_name":
            stock_name = context['params'].get('ans_stock_name', {}).get('resolvedValue')
            break
    
    # 컨텍스트에 없으면 params에서 가져오기
    if not stock_name:
        stock_name = data['action']['params'].get('stock_name')
    
    # 가격 유형 가져오기
    price_type = data['action']['params'].get('price_type', "현재가")  # 기본값: 현재가

    # 가격 정보 가져오기
    stock_price = get_stock_price(stock_name, price_type)

    # 응답 메시지 생성
    response_text = f"📊 {stock_name}의 {price_type}는 {stock_price}원입니다."

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": response_text}}
            ],
            "quickReplies": [
                {"label": "🔄 다른 정보 조회", "action": "block", "blockId": price_info_block_id},
                {"label": "📈 차트 보기", "action": "block", "blockId": chart_info_block_id},
                {"label": "🏠 처음으로", "action": "block", "blockId": home_block_id}
            ]
        }
    })

@app.route("/chart", methods=['POST'])
def chart():
    data = request.get_json()
    print("Received data:", data)

    # 종목명 가져오기 (컨텍스트 > params 순서로 확인)
    stock_name = None

    # 컨텍스트에서 가져오기
    for context in data.get('contexts', []):
        if context['name'] == "stock_name":
            stock_name = context['params'].get('stock_name', {}).get('resolvedValue')
            break

    # params에서 가져오기 (컨텍스트가 없을 경우)
    if not stock_name:
        stock_name = data['action']['params'].get('stock_name')
    
    # 차트 유형 가져오기 (일, 주, 월 등)
    chart_type = data['action']['params']['chart_type']

    # 종목명이 없으면 종목 입력 블록으로 바로 이동
    if not stock_name:
        return jsonify({
            "version": "2.0",
            "template": {
                "redirect": {
                    "blockId": "search_stock_block"
                }
            }
        })

    # 종목명 + 차트 타입을 기반으로 차트 이미지 생성
    image_url = draw_chart(chart_type, stock_name)
    print(image_url)
    # 응답 메시지
    response_text = f"📊 {stock_name} {chart_type} 차트입니다."
    
    price_type = data['action']['params'].get('price_type', "현재가")  # 기본값: 현재가

    # 가격 정보 가져오기
    stock_price = get_stock_price(stock_name, price_type)

    # 응답 메시지 생성
    price_response_text = f"📊 {stock_name}의 {price_type}는 {stock_price}원입니다."

    return jsonify(
        {
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": response_text}},
                    {"simpleImage": {"imageUrl": image_url, "altText": f"{stock_name} 차트"}},
                    {"simpleText": {"text": price_response_text}},
                ],
                "quickReplies": [
                    {"label": "🔄 다른 정보 조회", "action": "block", "blockId": chart_info_block_id},
                    {"label": "📈 주가 보기", "action": "block", "blockId": price_info_block_id},
                    # {"label": "📰 뉴스 보기", "action": "block", "blockId": ""},
                    {"label": "🏠 처음으로", "action": "block", "blockId": home_block_id}
                ]
            }
        }
    )

@app.route('/news', methods=['POST'])
def news():
    data = request.get_json()
    print("Received data:", data)
    user_message = data['userRequest']['utterance']
    # 기본 응답 메시지
    response_text = "뉴스제공"
    news_items = get_finance_news()
    # 챗봇 응답 구성
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": "최신 금융 뉴스"
                        },
                        "items": news_items,  # 리스트 그대로 삽입
                        "buttons": [
                            {
                                "label": "더보기",
                                # "action": "block",
                                "action": "webLink",
                                "webLinkUrl": "https://m.stock.naver.com/investment/news/flashnews?category=ranknews",
                                # "extra": {
                                #     "key1": "value1",
                                #     "key2": "value2"
                                # }
                            },
                            {
                                "label": "처음으로",
                                "action": "block",
                                "blockId": home_block_id,
                                # "extra": {
                                #     "key1": "value1",
                                #     "key2": "value2"
                                # }
                            }
                        ]
                    }
                }
            ]
        }
    }
    return jsonify(response)

#종목 뉴스
@app.route('/stock_news', methods=['POST'])
def stock_news():
    data = request.get_json()
    print("Received data:", data)

    stock_name = data['userRequest']['utterance'].strip()
    if not stock_name:
        stock_name = "삼성전자"  # 기본값 (테스트용)
    stock_code = code_by_name(stock_name)
    news_items = get_stock_news(stock_code)
    # 상위 5건만 사용 예시
    # news_items = news_items[:5]
    print(news_items)
    
    # 응답 메시지 (리스트카드 예시)
    response_text = f"{stock_name} 종목 뉴스"
    # 종목코드로 만든 naver.com/item/news 링크(추가로 '더보기' 버튼에 연결하기 위함)
    more_link = f"https://finance.naver.com/item/news.naver?code={stock_code}" if stock_code else "https://finance.naver.com"

    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": response_text
                        },
                        "items": news_items,  # get_stock_news() 결과
                        "buttons": [
                            {
                                "label": "더보기",
                                "action": "webLink",
                                "webLinkUrl": more_link
                            },
                            {
                                "label": "처음으로",
                                "action": "block",
                                "blockId": home_block_id
                            }
                        ]
                    }
                }
            ]
        }
    }

    return jsonify(response)

@app.route('/volume-rank', methods=['POST'])
def volume_rank():
    """
    [국내주식] 거래량 순위 API
    """
    data = request.get_json()
    print("Received data:", data)

    stock_list = get_volume_rank()  # stock_rank.py에 있는 함수 호출

    # API 호출 실패 시 오류 메시지 반환
    if isinstance(stock_list, dict) and "error" in stock_list:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": stock_list["error"]}}
                ]
            }
        })

    # 응답 메시지 생성 (ListItem 형식)
    output_items = [
        {
            "title": stock["name"],  # 종목명
            "description": f"💰 현재가: {stock['price']}원 | 📊 거래량: {stock['volume']}",
            "action": "block",
            "blockId": "STOCK_DETAIL_BLOCK",  # 상세 정보 블록 ID
            "extra": {
                "stock_code": stock["code"]  # 종목 코드 추가 (추후 상세 조회용)
            }
        }
        for stock in stock_list
    ]

    # Kakao i 오픈빌더 응답 JSON (ListCard 사용)
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "listCard": {
                        "header": {
                            "title": "📊 거래량 상위 5개 종목"
                        },
                        "items": output_items,
                        "buttons": [
                            {
                                "label": "더보기",
                                "action": "block",
                                "blockId": stock_info_block_id
                            },
                            {
                                "label": "처음으로",
                                "action": "block",
                                "blockId": home_block_id
                            }
                        ]
                    }
                }
            ],
        }
    })

@app.route('/mock_order_buy', methods=['POST'])
def mock_order():
    data = request.get_json()

    # 컨텍스트에서 주문 정보 추출
    stock_name = data['action']['params'].get('stock_name')
    print(data['action']['params'])
    # 종목코드 변환
    stock_code = code_by_name(stock_name)
    
    quantity = data['action']['params'].get('order_quantity')
    price = data['action']['params'].get('price_type')
    order_type = data['action']['params'].get('order_type', '매수')  # 기본값: 매수
    
    
    # 주문 정보로 해시키 발급 및 주문 처리
    order_data = {
        "CANO": os.getenv("MOCK_ACC_NO"),
        "ACNT_PRDT_CD": "01",
        "PDNO": stock_code,
        "ORD_DVSN": "01",  # 시장가 주문 고정
        "ORD_QTY": str(quantity),
        "ORD_UNPR": "0" # 시장가 주문
    }
    print(order_data)
    # 해시키 발급
    # hash_key = get_hash(order_data) 필수 헤더 아님
    # print(hash_key)
    # if isinstance(hash_key, dict) and "error" in hash_key:
    #     return jsonify({
    #         "version": "2.0",
    #         "template": {
    #             "outputs": [{"simpleText": {"text": f"주문 처리 중 오류가 발생했습니다: {hash_key['error']}"}}]
    #         }
    #     })
    
    # 주문 API URL (매수/매도에 따라 TR ID 달라짐)
    order_url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"
    token = os.getenv("MOCK_KI_TOKEN")
    app_key = os.getenv("MOCK_APP_KEY")
    app_secret = os.getenv("MOCK_SECRET_KEY")
    # 주문 유형에 따른 TR ID 설정
    tr_id = "VTTC0802U"  # 모의투자 매수/매도 TR ID
    
    # 주문 API 헤더
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": tr_id
        # "hashkey": hash_key
    }
    
    try:
        # 주문 API 호출
        response = requests.post(order_url, headers=headers, data=json.dumps(order_data))

        if response.status_code != 200:
            print("❗ 서버 응답 코드:", response.status_code)
            print("❗ 서버 응답 내용:", response.text)
            raise Exception(f"주문 실패 - 서버 응답 코드 {response.status_code}")
        
        result = response.json()
        print(result)
        # ✅ 모의투자 장 종료 예외처리
        if result.get('msg_cd') == '40580000':
            raise Exception("모의투자 장 종료로 주문이 불가능합니다.")
            
        order_no = result.get('output', {}).get('ODNO', '(주문번호 없음)')

        # 주문 성공 응답
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": f"✅ {stock_name} {quantity}주 {order_type} 주문이 접수되었습니다.\n주문번호: {order_no}"}},
                ],
                "quickReplies": [
                    {"label": "처음으로", "action": "block", "blockId": home_block_id},
                    {"label": "잔고보기", "action": "block", "blockId": mock_balance_id}
                ]
            }
        })

    except Exception as e:
        print(e)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": f"❌ {str(e)}"}}
                ],
                "quickReplies": [
                    {"label": "처음으로", "action": "block", "blockId": home_block_id},
                    {"label": "잔고보기", "action": "block", "blockId": mock_balance_id}
                ]
            }
        })

@app.route('/mock_inquire_balance', methods=['POST'])
def mock_inquire_balance():
    # 계좌번호 및 기타 정보는 환경변수에서 가져오기
    cano = os.getenv("MOCK_ACC_NO")
    acnt_prdt_cd = "01"  # 2자리 상품코드 고정

    # API URL
    balance_url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/inquire-balance"

    # 쿼리스트링 파라미터
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "01",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }

    # 헤더
    token = os.getenv("MOCK_KI_TOKEN")
    app_key = os.getenv("MOCK_APP_KEY")
    app_secret = os.getenv("MOCK_SECRET_KEY")

    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}',
        'appkey': app_key,
        'appsecret': app_secret,
        'tr_id': 'VTTC8434R'  # 모의투자 잔고조회 TR ID
    }

    try:
        # 잔고조회 API 호출
        response = requests.get(balance_url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        print(result)

        # 성공 응답 처리
        balance_info = result.get('output1', [])
        account_summary = result.get('output2', [{}])[0]  # [0] 추가

        # text_response = "\\n".join([
        #     f"{item.get('prdt_name', '(종목명없음)')}: {item.get('hldg_qty', 0)}주"
        #     for item in balance_info
        # ])
        # 종목 보유 정보 정리
        if balance_info:
            text_response = "\\n".join([
                f"{item.get('prdt_name', '(종목명없음)')}: {item.get('hldg_qty', 0)}주"
                for item in balance_info
            ])
        else:
            text_response = "📭 보유 종목이 없습니다."

        total_assets = account_summary.get('tot_evlu_amt', '0')  # 정상작동!

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": f"📈 보유 종목\n{text_response}\n\n총 평가금액: {total_assets}원"}}
                ],
                "quickReplies": [
                    {"label": "처음으로", "action": "block", "blockId": os.getenv("HOME_BLOCK_ID")}
                ]
            }
        })

    except Exception as e:
        print(e)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": f"❌ 잔고 조회 중 오류 발생: {str(e)}"}}
                ],
                "quickReplies": [
                    {"label": "처음으로", "action": "block", "blockId": os.getenv("HOME_BLOCK_ID")}
                ]
            }
        })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)