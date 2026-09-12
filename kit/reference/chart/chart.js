// 라이브러리 없이 SVG 로 그리는 선 그래프. CDN 을 쓰지 않습니다.
// 계산은 전부 이 파일에서 합니다 — AI 가 암산한 숫자를 적어 넣지 않기 위해서입니다.
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

function changeRate(prev, now) {
  if (prev === null || now === null || prev === 0) return null;
  return (now / prev - 1) * 100;
}

function lineChart(el, series, opts) {
  const W = 860, H = 320, PAD = { l: 70, r: 20, t: 18, b: 34 };
  const values = series.flatMap(s => s.rows.map(r => r[1]).filter(v => v !== null));
  if (!values.length) { el.innerHTML = '<p>자료가 없습니다.</p>'; return; }
  const lo = Math.min(...values), hi = Math.max(...values);
  const pad = (hi - lo) * 0.12 || 1;
  const min = lo - pad, max = hi + pad;
  const n = Math.max(...series.map(s => s.rows.length));
  const x = i => PAD.l + (W - PAD.l - PAD.r) * (n > 1 ? i / (n - 1) : 0);
  const y = v => PAD.t + (H - PAD.t - PAD.b) * (1 - (v - min) / (max - min));
  let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${opts.title}">`;
  for (let t = 0; t <= 4; t++) {
    const v = min + (max - min) * t / 4, yy = y(v);
    svg += `<path d="M${PAD.l} ${yy} H${W - PAD.r}" stroke="#d8e0e8" stroke-width="1" stroke-dasharray="4 6"/>`;
    svg += `<text x="${PAD.l - 10}" y="${yy + 4}" font-size="12" fill="#5f6e7d" text-anchor="end">${v.toFixed(opts.decimals ?? 0)}</text>`;
  }
  series.forEach((s, si) => {
    let d = '', started = false;
    s.rows.forEach((r, i) => {
      if (r[1] === null) { started = false; return; }      // 값이 없는 구간은 선을 잇지 않습니다
      d += (started ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(r[1]).toFixed(1) + ' ';
      started = true;
    });
    svg += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="2.6" stroke-linejoin="round"/>`;
  });
  const first = series[0].rows[0][0], last = series[0].rows[series[0].rows.length - 1][0];
  svg += `<text x="${PAD.l}" y="${H - 10}" font-size="12" fill="#5f6e7d">${first}</text>`;
  svg += `<text x="${W - PAD.r}" y="${H - 10}" font-size="12" fill="#5f6e7d" text-anchor="end">${last}</text>`;
  svg += '</svg>';
  el.innerHTML = svg;
}
