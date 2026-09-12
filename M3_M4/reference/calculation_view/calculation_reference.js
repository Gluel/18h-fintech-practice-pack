/* Teacher comparison view; the learner starts from the unchanged my_chart. */
(() => {
  const panel = document.querySelector('#calculation-reference');
  const data = window.MACRO_DATA;
  const show = () => {
    const id = document.querySelector('[data-id].active')?.dataset.id;
    const series = data.series.find(s => s.id === id);
    const period = document.querySelector('#period').value;
    const rows = series.values.filter(([y]) => period === 'all' || (period === 'recent' ? y >= 2022 : y >= 2025));
    if (!rows.length) {
      panel.textContent = '선택 기간의 자료가 없어 계산하지 않습니다.';
      return;
    }
    const [year, value] = rows.at(-1);
    const prior = series.values.find(([y]) => y === year - 1);
    const base = series.values.find(([y]) => y === 2015);
    let label, answer, method;
    if (series.series_id === 'FP.CPI.TOTL.ZG') {
      label = '상승률의 전년 대비 차이';
      answer = prior ? (Number(value) - Number(prior[1])).toFixed(2) + '%p' : '계산 불가';
      method = '올해 상승률 - 전년 상승률. 가격 수준의 하락을 뜻하지 않습니다.';
    } else {
      label = series.series_id === 'PA.NUS.FCRF' ? '연평균 환율의 전년 대비 변화율' : '명목 달러 GDP의 전년 대비 변화율';
      answer = prior && Number(prior[1]) !== 0 ? ((Number(value) / Number(prior[1]) - 1) * 100).toFixed(2) + '%' : '계산 불가';
      method = '(올해 값 / 전년 값 - 1) × 100. 실질 성장률·실시간 시세·투자 판단이 아닙니다.';
    }
    panel.replaceChildren();
    for (const [tag, text] of [['h3', year + '년 · ' + label], ['p', answer], ['p', method]]) {
      const el = document.createElement(tag); el.textContent = text; panel.append(el);
    }
    if (series.series_id === 'PA.NUS.FCRF') {
      const el = document.createElement('p');
      el.textContent = '2015=100 기준: ' + (base && Number(base[1]) !== 0 ? (Number(value) / Number(base[1]) * 100).toFixed(2) : '계산 불가');
      panel.append(el);
    }
    const foot = document.createElement('p');
    foot.textContent = '교사 참고 계산 · 첫해2015의 전년비는 입력에2014가 없어 미계산 · 원본 값 표와 독립 재검산';
    panel.append(foot);
  };
  document.querySelector('#series').addEventListener('click', () => queueMicrotask(show));
  document.querySelector('#period').addEventListener('change', show);
  show();
})();
