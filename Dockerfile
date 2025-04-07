FROM apache/airflow:2.10.5-python3.9

USER root
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev

# requirements.txt 파일 의존성 설치
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

