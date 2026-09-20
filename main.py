import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 데이터 불러오기 (실제 CSV 파일명으로 변경해주세요)
df = pd.read_csv('your_data_file.csv')

st.subheader('🎬 개봉일 스크린수 vs 총 관객수 (장르별)')

# 2. Plotly 산점도 생성
fig = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',  # 장르별로 점 색상 구분
    hover_name='movie_name',  # 마우스 오버 시 표시될 영화명
    labels={
        'first_scrn': '개봉일 스크린수',
        'total_audi': '총 관객수',
        'genre': '장르',
    },
    title='개봉일 스크린수와 총 관객수의 관계',
)

# 3. 레이아웃 조정 및 Streamlit에 출력
fig.update_traces(marker=dict(size=8, opacity=0.8))
fig.update_layout(
    xaxis_title='개봉일 스크린수',
    yaxis_title='총 관객수',
    legend_title='장르',
)

st.plotly_chart(fig, use_container_width=True)
