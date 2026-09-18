스트림릿 앱(main.py)을 새로 만들어 줘. 제목은 '영화 데이터 그래프 도감 2 - 분포와 관계'.
- 데이터는 이 주소에서 불러와:
  https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv
  1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 216편의 요약표야. 열은
  movieCd(영화코드) · movieNm(영화명) · openDt(개봉일, 여덟 자리 숫자) ·
  genre(장르 - 세로막대 기호로 여러 개 적힌 영화는 첫 번째 장르만 써) · nation(제작 국가) ·
  first_scrn(개봉일 스크린수) · first_show(개봉일 상영횟수) · first_week_audi(개봉 첫 주 관객) ·
  total_audi(총 관객) · days_in_top10(10위권에 머문 날수).
- 첫 그래프: 장르별 영화 편수를 플롯리 도넛 그래프로 보여 줘. 조각에 마우스를 올리면 편수와 비율이 보이게.
- 그래프마다 아래에 '이 그래프로 알 수 있는 것' 한 문장을 넣을 자리를 만들고, 구역을 나눠 줘.
- 필요한 라이브러리 목록(requirements.txt)도 같이 줘. 버전 숫자 없이 이름만.
