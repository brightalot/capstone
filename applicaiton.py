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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)