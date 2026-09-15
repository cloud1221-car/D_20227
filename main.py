import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# [1. 데이터 불러오기 및 캐싱]
# 앱이 실행될 때 매번 데이터를 불러오지 않고,
# 메모리에 저장(캐시)해두어 재사용합니다.
# ==========================================


@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"

  # pandas를 이용해 CSV 파일 읽기
  df = pd.read_csv(url)

  # [2. 날짜 전처리]
  # 1) 결측치가 포함된 행 삭제
  df = df.dropna()

  # 2) "기준일자" 컬럼을 날짜(datetime) 형식으로 변환
  df["기준일자"] = pd.to_datetime(df["기준일자"])

  # 3) 전체 데이터를 기준일자 순서대로 오름차순 정렬
  df = df.sort_values("기준일자")

  return df


# 데이터 불러오기 실행
df = load_data()

# 웹앱 제목 설정
st.title("🎬 영화 박스오피스 분석 웹앱")
st.write("KOBIS 데이터를 바탕으로 영화별 관객수 변화를 확인해보세요.")

# ==========================================
# [3. 영화 선택 기능]
# ==========================================
# 영화별 누적관객수의 최댓값을 구해 내림차순으로 정렬합니다.
# (가장 흥행한 영화가 목록 상단에 오도록 설정)
movie_ranking = df.groupby("영화명")["누적관객수"].max().reset_index()
movie_ranking = movie_ranking.sort_values(by="누적관객수", ascending=False)
movie_list = movie_ranking["영화명"].tolist()

# 사용자가 선택할 수 있는 셀렉트박스 생성
selected_movie = st.selectbox(
    "관람할(분석할) 영화를 선택하세요 (누적관객수 순)", movie_list
)

# 선택한 영화의 데이터만 필터링
movie_df = df[df["영화명"] == selected_movie]

# ==========================================
# [5. 기타 - 첫 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [4. 첫 번째 그래프: 일일 관객수 선그래프]
# ==========================================
st.header("📈 일일 관객수 변화 추이")

# Plotly를 이용해 인터랙티브 선 그래프 생성
fig1 = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}' 일자별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수"},
    markers=True,  # 데이터 포인트 표시
)

# 스트림릿에 Plotly 선 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 선택한 영화가 상영 기간 동안 날짜별로"
    " 몇 명의 관객을 모았는지 확인할 수 있으며, 주말이나 특정일에 관객이"
    " 급증하는 흥행 패턴을 파악할 수 있습니다."
)

# ==========================================
# [5. 기타 - 두 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [두 번째 그래프: 누적관객수 영역차트]
# ==========================================
st.header("📉 누적 관객수 변화 추이")

# Plotly를 이용해 영역차트(area chart) 생성
fig2 = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}' 일자별 누적관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "총 누적 관객수"},
)

# 스트림릿에 Plotly 영역차트 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 영화가 상영되는 동안 시간이 지남에 따라"
    " 관객이 총 몇 명까지 누적되어 증가했는지, 흥행의 전체적인 속도와"
    " 장기 상영 여부를 시각적으로 확인할 수 있습니다."
)

# ==========================================
# [5. 기타 - 세 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [세 번째 그래프: 조건 필터링 후 Top 5 다중 선그래프]
# ==========================================
st.header("🏆 장기 상영 TOP5 영화 누적관객수 비교")

# 1) 영화별로 TOP10에 등장한 일수(데이터 건수) 계산
top10_counts = df["영화명"].value_counts()

# 2) 등장 일수가 20일 이상인 영화들의 이름 목록 추출
valid_movies = top10_counts[top10_counts >= 20].index

# 3) 20일 이상 등장한 영화들만 필터링한 후, 영화별 최대 누적관객수 기준 상위 5개 선정
filtered_df = df[df["영화명"].isin(valid_movies)]
top_5_filtered_ranking = (
    filtered_df.groupby("영화명")["누적관객수"]
    .max()
    .reset_index()
    .sort_values(by="누적관객수", ascending=False)
)
top_5_movies = top_5_filtered_ranking.head(5)["영화명"].tolist()

# 4) 최종 선정된 상위 5개 영화 데이터 추출
top_5_df = df[df["영화명"].isin(top_5_movies)]

# 5) Plotly를 이용해 영화별 색상과 범례가 포함된 다중 선그래프 생성
fig3 = px.line(
    top_5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별로 선 색상을 다르게 지정하고 범례 자동 생성
    title="TOP10 20일 이상 진입 영화 중 누적관객수 상위 5개 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수", "영화명": "영화"},
)

# 스트림릿에 다중 선그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권에 20일 이상 꾸준히"
    " 머무르며 장기 흥행한 주요 영화들의 누적 관객수 증가 추이를 비교할 수"
    " 있습니다. 단기 반짝 흥행작을 제외하고 진정한 스테디셀러들의 흥행 속도를"
    " 파악할 수 있습니다."
)

# ==========================================
# [5. 기타 - 네 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [네 번째 그래프: 전체 TOP10 관객수 합계 및 7일 이동평균선]
# ==========================================
st.header("📊 전체 TOP10 영화 일일 관객수 합계 및 7일 이동평균")

# 1) 기준일자별로 전체 TOP10 영화의 '해당일관객수' 합계 구하기
daily_total_df = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2) 합계값에 대해 7일 이동평균(Rolling Mean) 구하기
daily_total_df["7일이동평균"] = (
    daily_total_df["해당일관객수"].rolling(window=7).mean()
)

# 3) Plotly Graph Objects를 사용하여 원본 선(연하게)과 이동평균 선(진하게) 함께 그리기
fig4 = go.Figure()

# 원본 합계 선 (연한 색상 및 투명도 설정)
fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["해당일관객수"],
        mode="lines",
        name="일일 합계 관객수 (원본)",
        line=dict(color="lightblue", width=1.5),
        opacity=0.6,
    )
)

# 7일 이동평균선 (진한 색상)
fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="blue", width=3),
    )
)

# 레이아웃 제목 및 축 이름 설정
fig4.update_layout(
    title="전체 TOP10 영화 일일 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객수",
    legend=dict(x=0.01, y=0.99),
)

# 스트림릿에 네 번째 그래프 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 극장 전체 시장의 일별 총 관객수 변동과"
    " 단기적인 요일별 등락(주말 효과 등)을 상쇄한 **7일 이동평균 추세선**을"
    " 함께 확인함으로써, 전체 영화 시장의 전반적인 관객 수요 흐름과 증감"
    " 추세를 객관적으로 파악할 수 있습니다."
)

# ==========================================
# [5. 기타 - 다섯 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [다섯 번째 그래프: 월별 관객수 합계 막대그래프]
# ==========================================
st.header("📅 월별 전체 관객수 합계")

# 1) 기준일자에서 연-월(YYYY-MM) 문자열 컬럼 추출
daily_total_df["연월"] = daily_total_df["기준일자"].dt.to_period("M").astype(str)

# 2) 월별로 관객수 합계 구하기
monthly_total_df = (
    daily_total_df.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3) Plotly를 이용해 월별 막대그래프 생성
fig5 = px.bar(
    monthly_total_df,
    x="연월",
    y="해당일관객수",
    title="월별 전체 영화 관객수 합계",
    labels={"연월": "월", "해당일관객수": "총 관객수"},
    text_auto=".2s",  # 막대 위에 값 표시
)

# 스트림릿에 다섯 번째 그래프 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 월 단위로 영화 관객 수요의 규모를"
    " 비교할 수 있으며, 성수기(방학 시즌, 명절 등)와 비수기에 따라 전체"
    " 극장가 관객 수가 어떻게 증감하는지 거시적인 패턴을 파악할 수 있습니다."
)

# ==========================================
# [5. 기타 - 여섯 번째 구역 구분선]
# ==========================================
st.divider()

# ==========================================
# [여섯 번째 그래프: 캘린더 히트맵]
# ==========================================
st.header("🗓️ 주차별·요일별 관객수 캘린더 히트맵")

# 1) 날짜 데이터 복사본 생성 후 월, 요일, 주차 정보 추출
heatmap_df = daily_total_df.copy()
heatmap_df["월"] = heatmap_df["기준일자"].dt.strftime("%Y-%m")
heatmap_df["요일번호"] = heatmap_df["기준일자"].dt.dayofweek  # 월(0)~일(6)

# 요일 이름을 순서대로 매핑하기 위한 딕셔너리
dow_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일",
}
heatmap_df["요일"] = heatmap_df["요일번호"].map(dow_map)

# 해당 월 내에서의 주차(Week of Month) 계산 로직 추가
heatmap_df["주차"] = (
    heatmap_df["기준일자"].dt.day - 1
) // 7 + 1  # 1주차 ~ 5주차
heatmap_df["주차표시"] = heatmap_df["주차"].astype(str) + "주차"

# 날짜 문자열 포맷팅 (마우스 오버 시 yyyy-mm-dd 표시용)
heatmap_df["날짜문자열"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

# 2) 월(주차별) × 요일별 피벗 테이블 생성 (데이터가 없는 경우 0 또는 빈값 처리)
pivot_df = heatmap_df.pivot_table(
    index=["월", "주차표시"],
    columns="요일",
    values="해당일관객수",
    aggfunc="sum",
).reset_index()

# 요일 순서 고정 (월요일부터 일요일 순서)
dow_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# 결측치를 0으로 채우기
pivot_df = pivot_df.fillna(0)

# 행 정렬을 위해 월 + 주차 조합 레이블 생성
pivot_df["월-주차"] = pivot_df["월"] + " " + pivot_df["주차표시"]

# 3) Plotly 히트맵 구현을 위해 행렬 데이터 구성
# Y축 레이블(월-주차), X축(요일 순서)
days_present = [d for d in dow_order if d in pivot_df.columns]

# 정확한 X, Y, Z 매트릭스 구성
heatmap_matrix = pivot_df[days_present].values
y_labels = pivot_df["월-주차"].values

# 마우스 올렸을 때 정확한 날짜(yyyy-mm-dd)를 보여주기 위해 날짜 매트릭스도 함께 구성
# (동일한 주차-요일 구조에 대응하는 날짜 매핑)
date_pivot = heatmap_df.pivot_table(
    index=["월", "주차표시"],
    columns="요일",
    values="날짜문자열",
    aggfunc="first",
).reset_index()
date_matrix = date_pivot[days_present].values

fig6 = go.Figure(
    data=go.Heatmap(
        z=heatmap_matrix,
        x=days_present,
        y=y_labels,
        customdata=date_matrix,
        hovertemplate=(
            "날짜: %{customdata}<br>요일: %{x}<br>관객수 합계:"
            " %{z:,.0f}명<extra></extra>"
        ),
        colorscale="YlOrRd",  # 진할수록 관객이 많은 컬러 스케일
        colorbar=dict(title="관객수"),
    )
)

fig6.update_layout(
    title="월별 주차 및 요일별 일일 관객수 히트맵",
    xaxis_title="요일",
    yaxis_title="월 및 주차",
    yaxis=dict(autorange="reversed"),  # 최신순 혹은 상단 배치를 위해 역순 정렬 옵션
)

# 스트림릿에 여섯 번째 그래프 출력
st.plotly_chart(fig6, use_container_width=True)

# 그래프 아래 '이 그래프로 알 수 있는 것' 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 특정 월의 어느 주차, 어떤 요일에 관객이"
    " 가장 많이 집중되는지 직관적인 색상 농도를 통해 파악할 수 있으며, 마우스"
    " 포인터를 올려 구체적인 날짜(yyyy-mm-dd)와 관객 수치를 정밀하게"
    " 대조해 볼 수 있습니다."
)

# ==========================================
# [5. 기타 - 앞으로 추가될 구역 미리보기]
# ==========================================
st.divider()
st.header("📊 추가 분석 영역 (예정)")
st.write("추후 다른 시각화 그래프가 이 구역에 추가될 예정입니다.")
