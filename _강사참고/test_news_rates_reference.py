import unittest
from pathlib import Path
import tempfile
from news_rates_reference import read_rates, rate_for, join_news, moving_average

SAMPLE = Path(__file__).resolve().parent / 'sample_rates.csv'
NEWS = [{'title': f'보도자료 {n}', 'url': f'https://example.invalid/{n}', 'date': d, 'source': '한국은행'}
        for n, d in enumerate(['2026-09-10', '2026-08-27', '2026-08-25', '2026-08-11', '2026-08-04'], 1)]


class ReferenceTests(unittest.TestCase):
    def test_unit_rate_for(self):                      # R-01
        self.assertEqual(rate_for(read_rates(SAMPLE), '2026-08')['label'], '4.29%')

    def test_unit_missing_is_not_zero(self):           # R-02
        result = rate_for(read_rates(SAMPLE), '2026-09')
        self.assertEqual(result['state'], 'missing')
        self.assertIsNone(result['value'])

    def test_unit_invalid_row(self):                   # R-03
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'bad.csv'
            bad.write_text('month,rate_percent,data_kind\n2026-08,abc,observed\n')
            self.assertEqual(rate_for(read_rates(bad), '2026-08')['state'], 'invalid')

    def test_unit_moving_average_waits(self):          # R-04
        self.assertTrue(all(v is None for _, v in moving_average([('d1', 10), ('d2', 20)], 20)))
        filled = moving_average([(f'd{i}', 10) for i in range(20)], 20)
        self.assertEqual(filled[-1][1], 10)

    def test_unit_moving_average_skips_blank(self):    # R-04 · 결측 계약
        # 빈 값을 0 으로 채우면 5 가 나온다. 건너뛰면 15 다. 차트와 같은 답이어야 한다.
        self.assertEqual(moving_average([('d1', 10), ('d2', None), ('d3', 20)], 2)[-1][1], 15)

    def test_integration_shipped_shape(self):          # R-01 + R-02 통합
        rows = join_news(NEWS, read_rates(SAMPLE))     # 배포 자료 그대로
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(r['rate']['state'] == 'ok' for r in rows), 4)
        self.assertEqual(sum(r['rate']['state'] == 'missing' for r in rows), 1)

    def test_integration_adding_month_fills_all(self):  # R-01 통합
        rates = read_rates(SAMPLE) + [{'month': '2026-09', 'rate_percent': '4.31'}]
        self.assertTrue(all(r['rate']['state'] == 'ok' for r in join_news(NEWS, rates)))

    def test_integration_rejects_bad_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'bad.csv'
            bad.write_text('date,close\n2026-08-01,100\n')
            with self.assertRaises(ValueError):
                read_rates(bad)


if __name__ == '__main__':
    unittest.main()
