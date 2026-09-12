// 핵심 기능 — 화면과 분리해 두면 검사를 자동으로 만들 수 있습니다.
// 요구사항 명세 R-01~R-04 와 이 파일의 함수가 1:1로 이어집니다.
//   R-01 정상   뉴스의 발행월 관측이 있으면 값·연월·출처
//   R-02 빈 값  관측이 없으면 「미공개」 — 0 으로 채우지 않습니다
//   R-03 오류   숫자가 아니면 잘못된 월 관측을 참조하는 행만 「확인 필요」 — 다른 월은 그대로
//   R-04 계산   창이 다 차기 전에는 이동평균을 계산하지 않습니다
function parseCSV(text) {
  const lines = String(text).trim().split(/\r?\n/).filter(line => line.trim() && !line.trim().startsWith('#'));
  if (lines.length < 2) return [];
  const head = lines[0].split(',').map(s => s.trim());
  return lines.slice(1).map(line => {
    const cols = line.split(',');
    const row = {};
    head.forEach((h, i) => { row[h] = (cols[i] ?? '').trim(); });
    return row;
  });
}

// R-01 / R-02 / R-03 — 상태를 숫자로 뭉개지 않습니다.
function rateFor(rates, month) {
  const hit = rates.find(r => String(r[0]) === month);
  if (!hit) return { state: 'missing', label: '미공개', month: month, value: null };
  const raw = hit[1];
  const cleaned = typeof raw === 'string' ? raw.trim() : raw;
  const value = Number(cleaned);
  if (cleaned === '' || cleaned === '.' || cleaned == null || !['string', 'number'].includes(typeof cleaned) || !Number.isFinite(value)) {
    return { state: 'invalid', label: '확인 필요', month: month, value: null, raw: raw };
  }
  return { state: 'ok', label: value.toFixed(2) + '%', month: month, value: value };
}

// 뉴스 한 건 = 한 행. 한 행이 실패해도 나머지 행은 그대로 둡니다.
function joinNews(news, rates) {
  return news.map(function (n) {
    return { title: n.title, url: n.url, date: n.date, source: n.source,
             rate: rateFor(rates, String(n.date).slice(0, 7)) };
  });
}

// R-04 — 빌더의 공통 함수 원천에서 차트(chart/chart.js)와 같은 코드를 생성합니다.
// 이동평균 — 강의 전체가 «한 규칙»만 씁니다 (2026-09-12 통일).
//  ① 값이 없는 날(null · 빈칸 · 점)은 건너뜁니다. 0으로 채우지 않습니다.
//  ② 숫자가 아닌 글자가 섞이면 계산을 멈추고 그 줄을 알려 줍니다.
//  ③ 관측값이 window 개 모이기 전에는 null 입니다 — 「없음」이지 0 이 아닙니다.
// 왜 한 곳에 적나: 9/12 실측에서 차트와 검사가 같은 입력에 다른 답을 냈습니다
// (10, null, 20 / 창 2 → 한쪽 10 · 다른 쪽 15). 규칙이 둘이면 어느 쪽도 못 믿습니다.
function movingAverage(rows, window) {
  if (!Number.isInteger(window) || window < 1) throw new Error('관측 창은 양의 정수여야 합니다');
  const out = [], buf = [];
  for (const [label, raw] of rows) {
    const cleaned = typeof raw === 'string' ? raw.trim() : raw;
    if (cleaned === null || cleaned === undefined || cleaned === '' || cleaned === '.') {
      out.push([label, null]);
      continue;
    }
    if (!['string', 'number'].includes(typeof cleaned) || !Number.isFinite(Number(cleaned))) {
      throw new Error(label + ': 숫자가 아닌 값이 있습니다 — ' + raw);
    }
    buf.push(Number(cleaned));
    if (buf.length > window) buf.shift();
    out.push([label, buf.length === window ? buf.reduce((a, b) => a + b, 0) / window : null]);
  }
  return out;
}

function render(el, result) {
  el.textContent = result.state === 'ok' ? result.label : result.label;
  el.dataset.state = result.state;
  return el;
}
