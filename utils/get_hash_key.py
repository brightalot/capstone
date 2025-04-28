import os
import json
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_hash(data):
    """
    한국투자증권 API 해시키 발급 함수
    
    Args:
        data (dict): 해시키를 발급받기 위한 데이터 (주문 정보 등)
        
    Returns:
        str or dict: 성공 시 해시키 문자열, 실패 시 에러 정보가 담긴 딕셔너리
    """
    url = "https://openapivts.koreainvestment.com:29443/uapi/hashkey"
    app_key = os.getenv("MOCK_APP_KEY")
    app_secret = os.getenv("MOCK_SECRET_KEY")

    if not app_key or not app_secret:
        return {"error": "환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요."}

    headers = {
        "content-type": "application/json",
        "appkey": app_key,
        "appsecret": app_secret,
    }

    try:
        # JSON 데이터 직렬화
        payload = json.dumps(data)
        
        # API 요청 실행
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        # 응답 확인
        result = response.json()
        print("✅ 해시키 발급 성공:", result)
        
        # HASH 필드 반환
        if "HASH" in result:
            return result["HASH"]
        else:
            print("⚠️ 응답에 해시키가 없습니다:", result)
            return {"error": "응답에 해시키가 없습니다", "response": result}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 호출 실패: {e}")
        return {"error": f"API 호출 실패: {e}"}
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return {"error": f"JSON 파싱 오류: {e}"}