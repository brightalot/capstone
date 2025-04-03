# db_test.py
from db import get_connection

def test_connection():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        print(f"[INFO] DB 연결 테스트 성공: {result}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] DB 연결 테스트 실패: {e}")

if __name__ == "__main__":
    test_connection()