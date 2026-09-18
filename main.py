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

  # 장르 전처리 (결측값 처리 및 첫 번째 장르 추출)
  if "genre" in df.columns:
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .apply(lambda x: x.split("|")[0] if "|" in x else x)
    )

  # 총 관객수 숫자로 변환 (변환 불가 값은 NaN 처리 후 0으로 채우기)
  if "total_audi" in df.columns:
    df["total_audi"] = pd.to_numeric(
        df["total_audi"], errors="coerce"
    ).fillna(0)

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
    hole=0.4,
    labels={"genre": "장르", "count": "편수"},
)
fig_genre.update_traces(textposition="inside", textinfo="percent+label")
fig_genre.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=500)

# 그래프 출력
st.plotly_chart(fig_genre, use_container_width=True)

# '이 그래프로 알 수 있는 것' 구역 (첫 번째)
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "전체 박스오피스 상위권에 진입한 영화들 중 특정 장르가 차지하는 비중과"
    " 관객들의 선택을 받는 주요 장르의 분포 경향을 한눈에 확인할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 두 번째 그래프: 장르 내 영화별 총 관객 트리맵
# -------------------------------------------------------------------------
st.subheader("🗺️ 장르별 영화 관객 수 트리맵")

# Plotly 트리맵 생성
fig_treemap = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "genre", "total_audi"],
)

# 마우스 오버 시 표시될 정보 커스텀
fig_treemap.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{customdata[0]}<br>"
        "<b>장르:</b> %{customdata[1]}<br>"
        "<b>총 관객:</b> %{customdata[2]:,}명<br>"
        "<extra></extra>"
    )
)
fig_treemap.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=600)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# '이 그래프로 알 수 있는 것' 구역 (두 번째)
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "장르별 그룹 내에서 어떤 개별 영화가 압도적인 총 관객 수를 기록하며"
    " 블록버스터 역할을 하였는지, 장르 간 및 장르 내 규모의 차이를 직관적으로"
    " 파악할 수 있습니다."
)
