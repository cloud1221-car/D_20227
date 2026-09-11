import datetime
import requests
import pandas as pd
import pytz
import streamlit as st


# ==========================================
# 1. 페이지 기본 설정 및 스타일 정의
# ==========================================
st.set_page_config(
    page_title="일별 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 일별 박스오피스 조회")
st.caption("영화진흥위원회(KOBIS) Open API 데이터를 기반으로 제공됩니다.")


# ==========================================
# 2. 날짜 계산 및 API 데이터 수집 (캐시 적용)
# ==========================================
def get_yesterday_date_kst():
    """
    서버의 위치와 관계없이 항상 한국 표준시(KST) 기준으로 '어제' 날짜(datetime.date 객체)를 구합니다.
    """
    tz_kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.datetime.now(tz_kst)
    yesterday_kst = now_kst - datetime.timedelta(days=1)
    return yesterday_kst.date()


# 동일한 API 키와 날짜 조합에 대해 1시간(3600초) 동안 결과를 기억(캐싱)합니다.
@st.cache_data(ttl=3600)
def fetch_daily_box_office(api_key, target_date_str):
    """
    KOBIS Open API를 호출하여 데이터를 가져옵니다.
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date_str
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {str(e)}"


# ==========================================
# 3. 날짜 선택기 UI 및 API 요청 준비
# ==========================================

# 한국 시간 기준 '어제' 날짜 계산
max_date = get_yesterday_date_kst()

# 달력(Date Input) 생성: 기본값은 어제, 고를 수 있는 가장 늦은 날짜(max_value)도 어제
selected_date = st.date_input(
    label="📅 조회할 날짜를 선택하세요 (오늘 날짜는 아직 집계 전입니다)",
    value=max_date,
    max_value=max_date,
    min_value=datetime.date(2004, 1, 1)  # KOBIS 데이터 시작 시점 근처
)

# API 규격에 맞는 YYYYMMDD 문자열로 변환
target_date_str = selected_date.strftime('%Y%m%d')
formatted_date = selected_date.strftime('%Y년 %m월 %d일')


# ==========================================
# 4. 메인 로직 실행
# ==========================================

# Streamlit Secrets(비밀 금고)에서 KOBIS_KEY 불러오기
api_key = st.secrets.get("KOBIS_KEY")

# 🔑 [예외 처리 1] 비밀 금고에 키가 없는 경우
if not api_key:
    st.error("⚠️ KOBIS API 인증키(KOBIS_KEY)를 찾을 수 없습니다.")
    st.info("""
    **확인 및 조치 방법:**
    1. **로컬 실행 시**: `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = "발급받은_키"`를 추가해 주세요.
    2. **Streamlit Cloud 배포 시**: App Settings > Secrets에 `KOBIS_KEY = "발급받은_키"`를 등록해 주세요.
    """)
    st.stop()

# API 데이터 불러오기
data, error_msg = fetch_daily_box_office(api_key, target_date_str)

# 🌐 [예외 처리 2] 네트워크 요청 실패 시
if error_msg:
    st.error("⚠️ API 호출 중 에러가 발생했습니다.")
    st.info(f"**상세 내용**: {error_msg}\n\n인터넷 연결 상태를 확인하시거나 잠시 후 다시 시도해 주세요.")
    st.stop()

# 🔑 [예외 처리 3] API 인증 실패 / faultInfo 에러 수신 시
if "faultInfo" in data:
    fault = data["faultInfo"]
    st.error("⚠️ 영화진흥위원회 API 에러 응답이 도착했습니다.")
    st.warning(f"**오류 메시지**: {fault.get('message', '알 수 없는 에러')}\n\n**오류 코드**: {fault.get('errorCode', 'N/A')}")
    st.info("""
    **확인해야 할 사항:**
    - Secrets에 입력한 `KOBIS_KEY`가 올바른 키인지 확인해 주세요.
    - 영화진흥위원회 오픈API 창구(KOBIS)에서 키가 정상적으로 발급 및 활성화되어 있는지 확인해 주세요.
    """)
    st.stop()

# 📦 [예외 처리 4] 영화 목록이 비어 있는 경우
box_office_result = data.get("boxOfficeResult", {})
movie_list = box_office_result.get("dailyBoxOfficeList", [])

if not movie_list:
    st.warning(f"⚠️ {formatted_date}일자 박스오피스 데이터를 찾을 수 없습니다.")
    st.info("""
    **그날은 아직 집계 전입니다.**
    - 영화진흥위원회 API에서 해당 날짜의 일별 박스오피스를 아직 제공하지 않거나 집계 중일 수 있습니다.
    - 다른 날짜를 선택하여 조회해 주세요.
    """)
    st.stop()


# ==========================================
# 5. 데이터 가공 (숫자 변환, 기호 추가, 트로피 부착)
# ==========================================
df = pd.DataFrame(movie_list)

# 숫자로 변환할 컬럼 지정
numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 순위 기준 정렬
df["rank"] = df["rank"].astype(int)
df = df.sort_values(by="rank", ascending=True)

# 1) 순위 증감(rankInten) 화살표 기호 생성 함수
def format_rank_change(inten):
    inten = int(inten)
    if inten > 0:
        return f"▲ {inten}"
    elif inten < 0:
        return f"▼ {abs(inten)}"
    else:
        return "-"

df["rank_change"] = df["rankInten"].apply(format_rank_change)

# 2) 누적 관객수 100만 이상 트로피 이모지 부착 함수
def add_trophy_if_million(row):
    movie_name = row["movieNm"]
    audi_acc = row["audiAcc"]
    if audi_acc >= 1000000:
        return f"🏆 {movie_name}"
    return movie_name

df["display_movieNm"] = df.apply(add_trophy_if_million, axis=1)


# ==========================================
# 6. 화면 구성 (지표 카드, 그래프, 데이터 표)
# ==========================================

st.write(f"📅 **조회 날짜**: {formatted_date}")

# --- [A] 1위 영화 지표 카드 세 장 ---
top_movie = df.iloc[0]

st.subheader(f"🥇 1위 영화: {top_movie['display_movieNm']}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="일별 관객수",
        value=f"{int(top_movie['audiCnt']):,} 명"
    )

with col2:
    st.metric(
        label="누적 관객수",
        value=f"{int(top_movie['audiAcc']):,} 명"
    )

with col3:
    st.metric(
        label="상영 스크린수",
        value=f"{int(top_movie['scrnCnt']):,} 개"
    )

st.divider()


# --- [B] 관객수 상위 5편 막대그래프 ---
st.subheader("📊 관객수 상위 5개 영화")

top5_df = df.head(5)

st.bar_chart(
    data=top5_df,
    x="movieNm",
    y="audiCnt",
    color="#FF4B4B"
)

st.divider()


# --- [C] 전체 박스오피스 순위표 ---
st.subheader(f"📋 {formatted_date} 박스오피스 전체 순위")

# 화면에 표시할 컬럼 정리
display_df = df[["rank", "rank_change", "display_movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "순위변동", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

# 표 출력 및 포맷 설정
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "순위": st.column_config.NumberColumn(format="%d위"),
        "순위변동": st.column_config.TextColumn(
            label="순위변동",
            help="▲: 상승, ▼: 하강, -: 변동없음"
        ),
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    }
)
