"""Reference bridge: validated long CSV -> wide CSV -> local browser data."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from reference_checks import inspect_csv, SERIES


def build(source, template, output):
    result = inspect_csv(source)
    if result['status'] != 'PASS':
        raise ValueError('; '.join(result['errors']))
    output = Path(output)
    template = Path(template)
    model = json.loads((template / 'data/macro_sample.json').read_text())
    columns = ['year'] + [name for name, unit in SERIES.values()]
    rows = result['wide_rows']
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'clean_macro.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    # Read the produced CSV, so the browser handoff actually uses this artifact.
    with (output / 'clean_macro.csv').open(encoding='utf-8', newline='') as stream:
        cleaned = list(csv.DictReader(stream))
    for series in model['series']:
        field = SERIES[series['series_id']][0]
        series['values'] = [[int(row['year']), row[field]] for row in cleaned]
    chart = output / 'my_chart'
    (chart / 'data').mkdir(parents=True, exist_ok=True)
    page=(template / 'index.html').read_text()
    if '</body>' not in page:raise ValueError('Unexpected reference template')
    (chart / 'index.html').write_text(page.replace('</body>','<script src="chart_labels.js"></script></body>'))
    shutil.copy2(Path(__file__).with_name('chart_labels.js'),chart/'chart_labels.js')
    (chart / 'data/macro_sample.js').write_text('window.MACRO_DATA = ' + json.dumps(model, ensure_ascii=False) + ';\n')
    (chart / 'data/macro_sample.json').write_text(json.dumps(model, ensure_ascii=False, indent=2))
    (output / 'calculations.json').write_text(json.dumps(rows, indent=2))
    result.update(clean_row_count=len(cleaned), clean_columns=columns,
                  clean_sha256=hashlib.sha256((output / 'clean_macro.csv').read_bytes()).hexdigest(),
                  browser_input='my_chart/data/macro_sample.js', live_api=False)
    (output / 'pipeline_receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = build(args.csv, args.template, args.out)
    except ValueError as error:
        parser.exit(1, 'FAIL: ' + str(error) + '\n')
    print(json.dumps({'status': receipt['status'], 'raw_rows': receipt['row_count'], 'wide_rows': receipt['clean_row_count']}))
