# plot_sentiment_db.py
import pandas as pd
import plotly.express as px
from db import get_connection

def load_data_from_db():
    """
    PostgreSQL 데이터베이스에서 news_articles 테이블의 데이터를 읽어와 DataFrame으로 반환합니다.
    """
    conn = get_connection()
    # 필요한 컬럼만 선택해도 되지만, 여기서는 전체 데이터를 불러옵니다.
    df = pd.read_sql("SELECT * FROM news_articles WHERE sentiment_label IN ('positive', 'negative') ", conn)
    conn.close()
    # 날짜 형식을 datetime으로 변환
    df["pub_date"] = pd.to_datetime(df["pub_date"])
    return df

def plot_sentiment_pie_from_db(save_path="outputs/sentiment_pie.html"):
    """
    DB에서 불러온 데이터를 이용하여 감정 분포 파이차트를 생성하고 HTML 파일로 저장합니다.
    """
    df = load_data_from_db()
    
    fig = px.pie(
        df,
        names="sentiment_label",
        title="뉴스 감정 분포",
        color="sentiment_label",
        color_discrete_map={
            "positive": "#4CD964",  # Apple 스타일 그린
            "negative": "#FF3B30",  # Apple 스타일 레드
            "neutral": "#C7C7CC"    # 깔끔한 그레이
        }
    )
    
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title_font=dict(family="Helvetica Neue", size=20, color="#000000"),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    
    fig.write_html(save_path)
    fig.show()
    print(f"[INFO] 감정 분포 파이차트가 {save_path}에 저장되었습니다.")

def plot_sentiment_trend_from_db(save_path="outputs/sentiment_trend.html"):
    """
    DB에서 불러온 데이터를 이용하여 날짜별 평균 감정 점수 라인차트를 생성하고 HTML 파일로 저장합니다.
    """
    df = load_data_from_db()
    # 날짜별 평균 감정 점수 계산 (pub_date 기준)
    df_trend = df.groupby("pub_date")["sentiment_score"].mean().reset_index()
    
    fig = px.line(
        df_trend,
        x="pub_date",
        y="sentiment_score",
        title="날짜별 평균 감정 점수 변화",
        markers=True,
        template="simple_white",
        color_discrete_sequence=["#007aff"]  # Apple Blue
    )
    
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        title_font=dict(family="Helvetica Neue", size=20, color="#000000"),
        xaxis_title="날짜",
        yaxis_title="평균 감정 점수",
        font=dict(family="Helvetica Neue", size=14),
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified"
    )
    
    # 0 기준선 추가
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.write_html(save_path)
    fig.show()
    print(f"[INFO] 감정 점수 추이 라인차트가 {save_path}에 저장되었습니다.")

if __name__ == "__main__":
    plot_sentiment_pie_from_db()
    plot_sentiment_trend_from_db()