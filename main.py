import datetime
import requests
import pandas as pd
import pytz
import streamlit as st


# ==========================================
# 1. 페이지 기본 설정 및 스타일 정의
# ==========================================
st.set_page_config(
    page_title="어제 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제의 일별 박스오피스")
st.caption("영화진흥위원회(KOBIS) Open API 데이터를 기반으로 제공됩니다.")


# ==========================================
# 2. 날짜 계산 및 API 데이터 수집 (캐시 적용)
# ==========================================
def get_yesterday_kst():
    """
    서버의 위치와 관계없이 항상 한국 표준시(KST) 기준으로 '어제' 날짜를 yyyymmdd 형식으로 계산합니다.
    """
    tz_kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.datetime.now(tz_kst)
    yesterday_kst = now_kst - datetime.timedelta(days=1)
    return yesterday_kst.strftime('%Y%m%d')


# same key/date로 다시 호출할 때 API 요청을 줄이기 위해 결과를 1시간(3600초) 동안 캐싱합니다.
@st.cache_data(ttl=3600)
def fetch_daily_box_office(api_key, target_date):
    """
    KOBIS Open API를 호출하여 데이터를 가져옵니다.
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        # API 서버에 HTTP GET 요청을 보냅니다. (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)
        
        # HTTP 응답 상태 코드가 200(성공)이 아닌 경우 에러를 발생시킵니다.
        response.raise_for_status()
        
        # JSON 형식으로 응답 데이터를 파싱하여 반환합니다.
        return response.json(), None
    except requests.exceptions.RequestException as e:
        # 네트워크 통신 오류나 HTTP 에러 발생 시 처리
        return None, f"네트워크 통신 오류가 발생했습니다: {str(e)}"


# ==========================================
# 3. 메인 로직 실행
# ==========================================

# Streamlit Secrets(비밀 금고)에서 KOBIS_KEY를 가져옵니다.
api_key = st.secrets.get("KOBIS_KEY")

# 🔑 [예외 처리 1] 비밀 금고에 키가 설정되어 있지 않은 경우
if not api_key:
    st.error("⚠️ KOBIS API 인증키(KOBIS_KEY)를 찾을 수 없습니다.")
    st.info("""
    **확인 및 조치 방법:**
    1. **로컬 실행 시**: 프로젝트 폴더 안에 `.streamlit/secrets.toml` 파일을 만들고 아래 내용을 작성해 주세요.
       ```toml
       KOBIS_KEY = "발급받은_인증키_입력"
       ```
    2. **Streamlit Cloud 배포 시**: App Settings > Secrets 메뉴에 `KOBIS_KEY = "발급받은_인증키_입력"`을 등록했는지 확인해 주세요.
    """)
    st.stop()

# 한국 시간 기준 어제 날짜 구하기
yesterday_str = get_yesterday_kst()
formatted_date = f"{yesterday_str[:4]}년 {yesterday_str[4:6]}월 {yesterday_str[6:]}일"

st.write(f"📅 **조회 기준일 (한국 시간 기준 어제)**: {formatted_date}")

# API 데이터 불러오기
data, error_msg = fetch_daily_box_office(api_key, yesterday_str)

# 🌐 [예외 처리 2] 네트워크 요청 실패 시
if error_msg:
    st.error(f"⚠️ API 호출 중 에러가 발생했습니다.")
    st.info(f"**상세 내용**: {error_msg}\n\n인터넷 연결 상태를 확인하시거나 잠시 후 다시 시도해 주세요.")
    st.stop()

# 🔑 [예외 처리 3] API 키 오류 등으로 faultInfo 상자가 반환된 경우
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

# 📦 [예외 처리 4] 응답 구조가 이상하거나 영화 목록이 비어 있는 경우
box_office_result = data.get("boxOfficeResult", {})
movie_list = box_office_result.get("dailyBoxOfficeList", [])

if not movie_list:
    st.warning("⚠️ 조회된 박스오피스 영화 목록이 없습니다.")
    st.info("""
    **확인해야 할 사항:**
    - 아직 해당 날짜의 박스오피스 집계가 완료되지 않았을 수 있습니다.
    - API 서비스의 일시적인 점검일 수 있으니 잠시 후 다시 시도해 주세요.
    """)
    st.stop()


# ==========================================
# 4. 데이터 가공 (문자열 -> 숫자 변환)
# ==========================================
df = pd.DataFrame(movie_list)

# 숫자로 변환할 컬럼 지정 (문자열 -> 숫자)
numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 데이터 타입 맞춤 (정수형 변환)
df["rank"] = df["rank"].astype(int)
df["audiCnt"] = df["audiCnt"].astype(int)
df["audiAcc"] = df["audiAcc"].astype(int)
df["scrnCnt"] = df["scrnCnt"].astype(int)

# 순위 기준으로 오름차순 정렬
df = df.sort_values(by="rank", ascending=True)


# ==========================================
# 5. 화면 구성 (지표 카드, 그래프, 데이터 표)
# ==========================================

# --- [A] 1위 영화 지표 카드 세 장 ---
top_movie = df.iloc[0]

st.subheader(f"🏆 1위 영화: {top_movie['movieNm']}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="일별 관객수",
        value=f"{top_movie['audiCnt']:,} 명"
    )

with col2:
    st.metric(
        label="누적 관객수",
        value=f"{top_movie['audiAcc']:,} 명"
    )

with col3:
    st.metric(
        label="상영 스크린수",
        value=f"{top_movie['scrnCnt']:,} 개"
    )

st.divider()


# --- [B] 관객수 상위 5편 막대그래프 ---
st.subheader("📊 관객수 상위 5개 영화")

# 상위 5개 영화만 추출
top5_df = df.head(5)

# Streamlit 내장 차트로 막대그래프 출력 (x축: 영화명, y축: 관객수)
st.bar_chart(
    data=top5_df,
    x="movieNm",
    y="audiCnt",
    color="#FF4B4B"
)

st.divider()


# --- [C] 전체 박스오피스 순위표 ---
st.subheader("📋 어제 박스오피스 전체 순위 (Top 10)")

# 보여줄 컬럼 선택 및 이름 변경
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

# 표 형태로 화면 출력 (인덱스 숨김)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "순위": st.column_config.NumberColumn(format="%d위"),
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    }
)
