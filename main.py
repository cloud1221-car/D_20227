import pandas as pd
import streamlit as st

# CSV 파일이나 엑셀 파일 경로에 맞게 수정해주세요
df = pd.read_csv("your_data_file.csv")
import pandas as pd
import plotly.express as px

# 데이터프레임 변수명이 'df'라고 가정합니다.
# 실제 사용 중이신 데이터프레임명으로 변경해 주세요.

# Plotly를 이용한 인터랙티브 산점도 생성
fig = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',  # 장르별로 점 색상 구분
    hover_name='movie_name',  # 마우스 오버 시 표시될 영화명 (컬럼명은 실제 데이터에 맞게 수정 필요)
    labels={
        'first_scrn': '개봉일 스크린수',
        'total_audi': '총 관객수',
        'genre': '장르',
    },
    title='개봉일 스크린수 vs 총 관객수 (장르별)',
)

# 레이아웃 다듬기
fig.update_traces(marker=dict(size=8, opacity=0.8))
fig.update_layout(
    xaxis_title='개봉일 스크린수',
    yaxis_title='총 관객수',
    legend_title='장르',
)

# 그래프 출력
fig.show()
