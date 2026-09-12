"""Extract a bounded local FSC index and render an escaped local report."""
import argparse
import hashlib
import html
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class NewsIndexParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.current, self.parts, self.items = None, [], []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        path = urlsplit(attrs.get("href", "")).path
        parts = path.strip("/").split("/")
        self.current = path if len(parts) == 2 and parts[0] == "no010101" and parts[1].isdigit() and attrs.get("href", "").startswith("/") and not attrs.get("href", "").startswith("//") else None
        self.parts = []

    def handle_data(self, data):
        if self.current:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag != "a":
            return
        if self.current and not any(item["id"] == self.current.split("/")[-1] for item in self.items):
            self.items.append({"id": self.current.split("/")[-1], "title": " ".join("".join(self.parts).split()), "url": "https://www.fsc.go.kr" + self.current, "published_on": None, "body_status": "BODY_NOT_ACQUIRED", "summary": None})
        self.current = None
        self.parts = []


def extract(path):
    parser = NewsIndexParser()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser.items[:5]


def report(items):
    rows = []
    for item in items:
        url = item["url"]
        safe = urlsplit(url)
        if safe.scheme != "https" or safe.netloc != "www.fsc.go.kr":
            url = ""
        summary = item.get("summary") if item.get("body_status") == "BODY_VIEWED_WEB_NOT_ARCHIVED" else None
        cells = [
            '<a href="' + html.escape(url, quote=True) + '">' + html.escape(item["title"]) + "</a>",
            html.escape(item.get("published_on") or "미확인"),
            html.escape(item["body_status"]),
            html.escape(summary or "본문 미확인: 제목만으로 요약하지 않습니다."),
        ]
        rows.append("<tr>" + "".join("<td>" + cell + "</td>" for cell in cells) + "</tr>")
    return """<!doctype html><html lang="ko"><meta charset="utf-8"><title>금융 자료 확인 기록</title>
<style>body{font:16px/1.7 system-ui;margin:32px;color:#202124;background:white}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{border:1px solid #bbb;padding:12px;overflow-wrap:anywhere;text-align:left;vertical-align:top}th:nth-child(1){width:32%}th:nth-child(2){width:12%}th:nth-child(3){width:22%}a{color:#1559a5}</style>
<h1>금융 자료 확인 기록</h1><p>교육용 참고 결과. 목록 확보와 본문 확인을 구분합니다. 전문·첨부 확보 및 현재 제도 적용 여부를 보장하지 않습니다.</p>
<table><thead><tr><th>제목·출처</th><th>발행일</th><th>확보 상태</th><th>확인 범위 내 요지</th></tr></thead><tbody>""" + "".join(rows) + "</tbody></table></html>"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    items = extract(args.input)
    if len(items) != 5:
        raise SystemExit("Expected five distinct records; extraction needs review.")
    if args.reference:
        refs = {item["id"]: item for item in json.loads(args.reference.read_text())["items"]}
        digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
        for item in items:
            ref = refs.get(item["id"])
            if not ref or ref["url"] != item["url"] or ref["source_sha256"] != digest:
                raise SystemExit("Reference/source mismatch; do not silently reuse.")
            for key in ("published_on", "date_evidence", "body_status", "summary", "body_checked_on", "summary_evidence_location"):
                item[key] = ref.get(key)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "news_items.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "news_report.html").write_text(report(items), encoding="utf-8")
    print(json.dumps({"count": len(items), "body_reference_count": sum(i["body_status"] == "BODY_VIEWED_WEB_NOT_ARCHIVED" for i in items), "network_requests": 0}))
