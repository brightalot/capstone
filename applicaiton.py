from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
from stock_info.stock_price import get_stock_price, code_by_name

app = Flask(__name__)

# .env 파일 로드
load_dotenv()

# .env 파일에서 환경 변수 가져오기
price_info_block_id = os.getenv("PRICE_INFO_BLOCK_ID")
chart_info_block_id = os.getenv("CHART_INFO_BLOCK_ID")
home_block_id = os.getenv("HOME_BLOCK_ID")
stock_info_block_id = os.getenv("STOCK_INFO_BLOCK_ID")


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)