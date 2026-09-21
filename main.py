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

  # 제작 국가 결측치 처리
  if "nation" in df.columns:
    df["nation"] = df["nation"].fillna("기타")

  # 숫자형 데이터 변환 (변환 불가 값은 NaN 처리 후 0으로 채우기)
  numeric_cols = [
      "total_audi",
      "first_scrn",
      "first_week_audi",
      "first_show",
      "days_in_top10",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

  return df


df = load_data()

# 타이틀 및 소개
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 10위권에 진입한 영화 중 해당 기간 개봉한 **216편**의"
    " 데이터를 바탕으로 제작한 무지개빛 시각화 도감입니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 도넛 그래프 (무지개 컬러)
# -------------------------------------------------------------------------
st.subheader("📊 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Alphabet,
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
# 두 번째 그래프: 장르 내 영화별 총 관객 트리맵 (무지개 컬러)
# -------------------------------------------------------------------------
st.subheader("🗺️ 장르별 영화 관객 수 트리맵")

fig_treemap = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    color="genre",
    color_discrete_sequence=px.colors.qualitative.Vivid,
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

fig_hist.update_traces(marker_color="rgb(99, 110, 250)")
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
# 네 번째 그래프: 개봉일 스크린수와 총 관객 산점도 (무지개 컬러)
# -------------------------------------------------------------------------
st.subheader("📉 개봉일 스크린수 vs 총 관객수 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    color_discrete_sequence=px.colors.qualitative.Safe,
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
# 다섯 번째 그래프: 영화 편수 10편 이상인 장르별 총 관객 박스플롯 (무지개)
# -------------------------------------------------------------------------
st.subheader("📦 장르별 총 관객수 상자 그림 (영화 10편 이상)")

valid_genres = genre_counts[genre_counts["count"] >= 10]["genre"].tolist()
df_filtered = df[df["genre"].isin(valid_genres)]

fig_box = px.box(
    df_filtered,
    x="genre",
    y="total_audi",
    color="genre",
    color_discrete_sequence=px.colors.qualitative.Pastel,
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

st.markdown("---")

# -------------------------------------------------------------------------
# 여섯 번째 그래프: 첫 주 관객 버블 그래프 (무지개 컬러)
# -------------------------------------------------------------------------
st.subheader("🫧 개봉일 스크린수 vs 총 관객수 (첫 주 관객 버블 그래프)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre": "장르",
        "first_week_audi": "첫 주 관객",
    },
    custom_data=["movieNm", "genre", "first_scrn", "first_week_audi", "total_audi"],
)

fig_bubble.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{customdata[0]}<br>"
        "<b>장르:</b> %{customdata[1]}<br>"
        "<b>개봉일 스크린수:</b> %{customdata[2]:,}개<br>"
        "<b>첫 주 관객:</b> %{customdata[3]:,}명<br>"
        "<b>총 관객수:</b> %{customdata[4]:,}명<br>"
        "<extra></extra>"
    )
)

fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수", yaxis_title="총 관객수", height=600
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "점의 크기로 표현된 첫 주 관객수(버블 크기)를 통해, 초기 상영 규모와"
    " 총 관객 규모뿐만 아니라 **개봉 첫 주에 얼마나 폭발적인 관객을"
    " 모았는지** 입체적인 흥행 패턴을 한눈에 비교할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 일곱 번째 그래프: 제작 국가에서 장르로 내려가는 선버스트 그래프 (무지개)
# -------------------------------------------------------------------------
st.subheader("☀️ 제작 국가 및 장르별 영화 편수 선버스트 그래프")

fig_sunburst = px.sunburst(
    df,
    path=["nation", "genre"],
    color="genre",
    color_discrete_sequence=px.colors.qualitative.Dark24,
    labels={"nation": "제작 국가", "genre": "장르"},
)

fig_sunburst.update_traces(textinfo="label+percent parent")
fig_sunburst.update_layout(margin=dict(t=30, b=30, l=30, r=30), height=600)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "제작 국가(안쪽 원)를 기준으로 어떤 국가의 영화들이 주로 수급되며,"
    " 각 국가별로 어떤 장르(바깥쪽 원)가 주를 이루어 제작·배급되는지 영화"
    " 편수 기준의 계층적 비중을 시각적으로 파악할 수 있습니다."
)

st.markdown("---")

# -------------------------------------------------------------------------
# 여덟 번째 그래프: 제작 국가별 영화의 총 관객수는 차이가 어떤가 (무지개 스트립/박스)
# -------------------------------------------------------------------------
st.subheader("제작 국가별 영화의 총 관객수는 차이가 어떤가")

fig_nation_audi = px.strip(
    df,
    x="nation",
    y="total_audi",
    color="nation",
    color_discrete_sequence=px.colors.qualitative.Set2,
    labels={"nation": "제작 국가", "total_audi": "총 관객 수"},
    custom_data=["movieNm", "nation", "genre", "total_audi"],
)

fig_nation_audi.update_traces(
    hovertemplate=(
        "<b>영화명:</b> %{customdata[0]}<br>"
        "<b>제작 국가:</b> %{customdata[1]}<br>"
        "<b>장르:</b> %{customdata[2]}<br>"
        "<b>총 관객 수:</b> %{customdata[3]:,}명<br>"
        "<extra></extra>"
    ),
    marker=dict(size=8, opacity=0.8),
)

fig_nation_audi.update_layout(
    xaxis_title="제작 국가",
    yaxis_title="총 관객 수",
    showlegend=False,
    height=600,
)

st.plotly_chart(fig_nation_audi, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    "국가별 영화들의 총 관객 수 분포 양상과 각 국가에서 개별 영화들이"
    " 기록한 흥행 성적을 점(스트립) 형태로 비교하여, 국가별 영화 산업의"
    " 규모 차이와 흥행 편차를 입체적으로 확인할 수 있습니다."
)
