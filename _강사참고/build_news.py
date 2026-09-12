"""Local extraction and attributed excerpt report; no LLM or network calls."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from news_reference_builder import extract


def build(source, excerpts, output):
    items = extract(source)
    if len(items) != 5:
        raise ValueError('Expected five distinct items')
    refs = {r['id']: r for r in json.loads(Path(excerpts).read_text())['items']}
    for item in items:
        ref = refs.get(item['id'])
        if ref:
            if ref['url'] != item['url'] or ref['body_status'] != 'EXCERPT_ONLY':
                raise ValueError('Source identity mismatch')
            for key in ['published_on', 'body_status', 'excerpt_id', 'excerpt', 'summary', 'limit', 'location']:
                item[key] = ref[key]
            item['summary_method'] = 'TEACHER_PARAPHRASE_OF_EXCERPT_NOT_LLM_EXECUTION'
        else:
            item['limit'] = '본문·발췌 미확보. 요약과 발행일은 미확인.'
        item['index_sha256'] = hashlib.sha256(Path(source).read_bytes()).hexdigest()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'news_items.json').write_text(json.dumps(items, ensure_ascii=False, indent=2))
    cells = []
    for item in items:
        content = '<h2>' + html.escape(item['title']) + '</h2>'
        content += '<p><a href="' + html.escape(item['url'], quote=True) + '">금융위원회 원문</a> · ' + html.escape(item.get('published_on') or '발행일 미확인') + '</p>'
        content += '<p>확보: ' + item['body_status'] + '</p>'
        if item.get('excerpt'):
            content += '<blockquote>' + html.escape(item['excerpt']) + '</blockquote><p>근거: ' + html.escape(item['excerpt_id']) + '</p>'
        content += '<p>교육용 요지: ' + html.escape(item.get('summary') or '요약 보류') + '</p><p>한계: ' + html.escape(item['limit']) + '</p>'
        cells.append('<section>' + content + '</section>')
    page = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>금융 자료 확인 기록</title><style>body{font:18px/1.7 system-ui;margin:32px auto;max-width:920px;padding:0 20px;color:#202124;background:#fff}section{border-top:2px solid #ddd;padding:20px 0}h2{font-size:23px}blockquote{border-left:4px solid #188575;padding:12px;margin:15px 0}a{color:#1559a5}p,blockquote{overflow-wrap:anywhere}</style><h1>금융 자료 확인 기록</h1><p>목록 5건 · 짧은 발췌 2건 · 본문 전문 0건. 교육용 참고 결과이며 최신 제도 안내나 학생 수행 결과가 아닙니다.</p>' + ''.join(cells) + '</html>'
    (output / 'news_report.html').write_text(page)
    return items


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--excerpts', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    items = build(args.input, args.excerpts, args.out)
    print(json.dumps({'items': len(items), 'excerpts': sum(i['body_status'] == 'EXCERPT_ONLY' for i in items), 'full_bodies': 0, 'network_requests': 0}))
