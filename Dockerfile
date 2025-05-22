# 1. Python 3.8 기반 이미지 사용
FROM python:3.8-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
# 폰트 복사
COPY NanumGothic.ttf /app/NanumGothic.ttf
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. 프로젝트 전체 복사
COPY . .

# 7. Gunicorn을 통해 Flask 앱 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "application:app"]
