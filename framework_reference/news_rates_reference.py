"""강사 참고 전용: 수강생 앱의 검사가 아니다.

브라우저 실습실(lab.js)과 같은 기능을 같은 요구 ID 로 구현한다.
  R-01 정상   뉴스 한 건 → 발행월 지표의 값·연월·출처
  R-02 빈 값  그 달 관측이 없으면 「미공개」 — 0 으로 채우지 않는다
  R-03 오류   숫자가 아니면 그 행만 「확인 필요」 — 나머지 행은 유지
  R-04 계산   창이 다 차기 전에는 이동평균을 계산하지 않는다
"""
import csv
from pathlib import Path

REQUIRED = ['month', 'rate_percent', 'data_kind']


def read_rates(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != REQUIRED:
            raise ValueError(f'columns must be {REQUIRED}')
        rows, seen = [], set()
        for number, row in enumerate(reader, 2):
            month = (row.get('month') or '').strip()
            if len(month) != 7 or month[4] != '-':
                raise ValueError(f'row {number}: month must be YYYY-MM')
            if month in seen:
                raise ValueError(f'row {number}: duplicated month')
            seen.add(month)
            if row.get('data_kind') != 'observed':
                raise ValueError(f'row {number}: observed data only')
            rows.append({'month': month, 'rate_percent': (row.get('rate_percent') or '').strip()})
        return rows


def rate_for(rates, month):
    """R-01 / R-02 / R-03 — 상태를 숫자로 뭉개지 않는다."""
    hit = next((r for r in rates if r['month'] == month), None)
    if hit is None:
        return {'state': 'missing', 'label': '미공개', 'month': month, 'value': None}
    raw = hit['rate_percent']
    try:
        value = float(raw)
    except ValueError:
        return {'state': 'invalid', 'label': '확인 필요', 'month': month, 'value': None, 'raw': raw}
    return {'state': 'ok', 'label': f'{value:.2f}%', 'month': month, 'value': value}


def join_news(news, rates):
    """뉴스 한 건 = 한 행. 한 행이 실패해도 나머지 행은 그대로 둔다."""
    return [dict(item, rate=rate_for(rates, str(item['date'])[:7])) for item in news]


def moving_average(pairs, window):
    """R-04 — 이동평균 계약 (2026-09-12 통일).

    빈 값(None·''·'.')은 건너뛴다. 0 으로 채우지 않는다.
    20개가 모이기 전에는 None — 부분 평균을 만들지 않는다.
    """
    out, buffer = [], []
    for label, raw in pairs:
        if raw is None or (isinstance(raw, str) and raw.strip() in ('', '.')):
            out.append((label, None))
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f'{label}: not a number -> {raw}')
        buffer.append(value)
        if len(buffer) > window:
            buffer.pop(0)
        out.append((label, sum(buffer) / window if len(buffer) == window else None))
    return out
