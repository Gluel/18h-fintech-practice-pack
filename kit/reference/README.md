# 참고 결과물 — 「금융 뉴스 옆 주식 투자 지표 보기」

3일차에 만들 결과물의 **완성 예시**입니다. 그대로 베끼지 말고 «어디까지 하면 되는지»를 보세요.

## 여는 순서

1. `index.html` — 진입 화면 (여기부터)
2. `report.html` — 뉴스 리포트 + 관련 지표
3. `chart/index.html` — 차트와 검산
4. `feature.html` — 핵심 기능 (정상·미공개·확인 필요)
5. `test.html` — 자동 테스트 R-01~R-04
6. `landing.html` — 소개 페이지 (M6에서 새로 만든 것)
5. `test.html` — 자동 테스트 4/4

## 규칙

- 인터넷 없이 열립니다. 외부 글꼴·CDN·fetch 를 쓰지 않습니다.
- 데이터는 `data/*.js` 로 감싸 `<script src>` 로 읽습니다.
- 계산은 전부 페이지 JavaScript 가 합니다. 숫자를 옮겨 적지 않았습니다.
- 결제·광고·가입 폼이 없습니다. 하단에 「수업 과제 데모 · 투자 판단 근거 아님」을 적었습니다.

## 기획 문서

`docs/lean_canvas.md` · `docs/persona_journey.md` · `docs/requirements.md` · `docs/qa_scenarios.md` · `data/source_card.md`

> 사례는 **교육용 가상 예시**입니다. 실제 사용자 조사나 학생 성과가 아닙니다.
> 뉴스 제목·주소·발행일은 2026-09-11 한국은행 RSS 에서 확보한 실제 값이며 본문은 담지 않았습니다.
