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

  # 숫자형 데이터 변환 (변환 불가 값은 NaN 처리 후 0으로 채우기)
  numeric_cols = ["total_audi", "first_scrn"]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

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

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.4,
    labels={"genre": "장르", "count": "편수"},
)
fig_genre.update_traces(textposition="inside", textinfo="percent+label")
fig_genre.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=500)

st.plotly_chart(fig_genre, use_container_width=True)

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

fig_treemap = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "genre", "total_audi"],
)

fig_treemap.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{customdata[0]}<br>"
        "<b>장르:</b> %{customdata[1]}<br>"
        "<b>총 관객:</b> %{customdata[2]:,}명<br>"
        "<extra></extra>"
    )
)
fig_treemap.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=600)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "장르별 그룹 내에서 어떤 개별 영화가 압도적인 총 관객 수를 기록하며"
    " 블록버스터 역할을 하였는지, 장르 간 및 장르 내 규모의 차이를 직관적으로"
    " 파악할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 세 번째 그래프: 총 관객 히스토그램
# -------------------------------------------------------------------------
st.subheader("📈 총 관객수 분포 히스토그램")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객 수", "count": "영화 편수"},
)

fig_hist.update_layout(
    xaxis_title="총 관객 수", yaxis_title="영화 편수 (빈도)", height=500
)

st.plotly_chart(fig_hist, use_container_width=True)

max_audi_movie = df.loc[df["total_audi"].idxmax()]
max_title = max_audi_movie["movieNm"]
max_audi = max_audi_movie["total_audi"]

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    f"대다수의 영화가 낮은 관객 수 구간(좌측)에 집중되어 있어 흥행 영화의"
    f" 편중 현상이 뚜렷함을 알 수 있습니다. 이 기간 중 가장 관객이 많은"
    f" 영화는 **'{max_title}'**이며, 총 **{max_audi:,.0f}명**의 관객을"
    " 기록했습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 네 번째 그래프: 개봉일 스크린수와 총 관객 산점도
# -------------------------------------------------------------------------
st.subheader("📉 개봉일 스크린수 vs 총 관객수 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre": "장르",
    },
    custom_data=["movieNm", "genre", "first_scrn", "total_audi"],
)

fig_scatter.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{customdata[0]}<br>"
        "<b>장르:</b> %{customdata[1]}<br>"
        "<b>개봉일 스크린수:</b> %{customdata[2]:,}개<br>"
        "<b>총 관객수:</b> %{customdata[3]:,}명<br>"
        "<extra></extra>"
    )
)

fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수", yaxis_title="총 관객수", height=600
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "개봉일 스크린수와 최종 총 관객수 사이에는 일반적으로 강한 양의 상관관계가"
    " 존재하여, 초기 상영 규모가 흥행 성적에 큰 영향을 미친다는 것을 장르별"
    " 분포와 함께 확인할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 다섯 번째 그래프: 영화 편수 10편 이상인 장르별 총 관객 박스플롯
# -------------------------------------------------------------------------
st.subheader("📦 장르별 총 관객수 상자 그림 (영화 10편 이상)")

# 편수가 10편 이상인 장르 목록 추출
valid_genres = genre_counts[genre_counts["count"] >= 10]["genre"].tolist()
df_filtered = df[df["genre"].isin(valid_genres)]

# Plotly 박스플롯 생성 (hover_data에 영화명 포함)
fig_box = px.box(
    df_filtered,
    x="genre",
    y="total_audi",
    color="genre",
    labels={"genre": "장르", "total_audi": "총 관객수"},
    hover_data=["movieNm"],
)

fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수",
    showlegend=False,
    height=600,
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "상영작이 풍부한 주요 장르들 간의 관객 수 중앙값과 분포 범위를"
    " 비교할 수 있으며, 특히 상자 밖으로 튀어나온 이상치(아웃라이어)를 통해"
    " 각 장르별 초대박 흥행작들의 특성과 편차를 파악할 수 있습니다."
)
