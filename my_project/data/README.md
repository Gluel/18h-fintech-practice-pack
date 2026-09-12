# data — 내 작업용 자료 사본

- 기본 입력: `stock_sample.csv` (date,close / 120관측), `kr_ltir.csv` (month,ltir / 20관측).
- CSV와 같은 값의 JS: `stock_sample.js`→`window.DATA_STOCK`, `kr_ltir.js`→`window.DATA_KR_LTIR`.
- `news_sample.js`→`window.DATA_NEWS`: 한국은행 제목·URL·발행일·출처 5건.
- 원천은 `../../kit/data/`에 보존합니다. 시험용 변경은 이 작업 사본에서만 합니다.
- 출처는 `.source.md`와 각 JS의 source/unit/limit를 읽고 `../docs/source_card.md`에 적습니다.
- 주가 1~6월과 뉴스 8~9월은 기간이 달라 뉴스 전후 효과를 비교하지 않습니다.
- 개인 자유주제의 다른 입력이 필요하면 `../../topics/`에서 선택하고 요구사항을 그 입력에 맞춥니다.
