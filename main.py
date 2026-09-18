import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)


# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
  df = pd.read_csv(url)
  # 장르가 세로막대(|)로 구분된 경우 첫 번째 장르만 추출
  if "genre" in df.columns:
    df["genre"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0])
  return df


df = load_data()

# 타이틀 및 소개
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 10위권에 진입한 영화 중 해당 기간 개봉한 **216편**의"
    " 데이터를 바탕으로 제작한 시각화 도감입니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 도넛 그래프
# -------------------------------------------------------------------------
st.subheader("📊 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

# Plotly 도넛 그래프 생성
fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.4,  # 도넛 형태를 위한 구멍 크기
    labels={"genre": "장르", "count": "편수"},
)
fig_genre.update_traces(textposition="inside", textinfo="percent+label")
fig_genre.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=500)

# 그래프 출력
st.plotly_chart(fig_genre, use_container_width=True)

# '이 그래프로 알 수 있는 것' 구역
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "전체 박스오피스 상위권에 진입한 영화들 중 특정 장르가 차지하는 비중과"
    " 관객들의 선택을 받는 주요 장르의 분포 경향을 한눈에 확인할 수 있습니다."
)
