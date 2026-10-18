import unittest
from datetime import date
from scripts.update_deals import parsed_ranges, flyer_from_html, extract, inspect_flyer


class FlyerTests(unittest.TestCase):
    def test_date_formats_and_rollover(self):
        for text in ("2026年10月17日〜10月20日", "2026年10月17日～2026年10月20日",
                     "2026年10月17日–20日", "2026年10月17日—10月20日"):
            with self.subTest(text=text):
                self.assertEqual(parsed_ranges(text), [(date(2026,10,17),date(2026,10,20))])
        self.assertEqual(parsed_ranges("2026年12月30日〜1月2日"),
                         [(date(2026,12,30),date(2027,1,2))])

    def test_invalid_dates_and_corrupt_separator(self):
        for text in ("2026年2月30日〜3月2日", "2026年10月20日〜10月17日",
                     "2026年1月1日〜12月31日", "2026年10月17日?2026年10月20日"):
            self.assertEqual(parsed_ranges(text), [])

    def test_official_flyer_and_store_identity(self):
        html = '<title>町屋店 店舗情報 | コモディイイダ</title><h1>町屋店</h1><p>東京都荒川区町屋3-18-11</p><p class="flyer-period">2026年10月17日〜10月20日</p>'
        flyer = flyer_from_html(html, 'iida', 'https://example.com', '公式サイト',
                                'iida_official', date(2026,10,18))
        self.assertEqual(flyer['status'], 'current')
        self.assertEqual(flyer['period'], '2026-10-17〜2026-10-20')
        wrong = flyer_from_html(html.replace('町屋店','別店舗'), 'iida', '', '',
                                'iida_official', date(2026,10,18))
        self.assertEqual(wrong['status'], 'store_unverified')

    def test_guide_week_heading_and_archive_cannot_validate_flyer(self):
        html = '''<h1>コモディイイダ町屋店</h1>
        <h2>今週のチラシ（2026年10月12日〜10月18日）</h2>
        <div class="flyer_title">2026年10月14日〜10月16日</div>
        <h2>最近掲載していたチラシ</h2>
        <div class="flyer_title">2026年10月17日〜10月20日</div>'''
        flyer = flyer_from_html(html, 'iida', '', '', 'guide', date(2026,10,18))
        self.assertEqual(flyer['status'], 'expired')

    def test_date_verified_is_not_an_offer(self):
        self.assertEqual(extract('2026年10月17日〜10月20日 鮭 198円', 'iida', ''), [])

    def test_official_failure_falls_back_to_guide(self):
        import requests
        def fetch(url, **kwargs):
            if 'comodi-iida.co.jp' in url:
                raise requests.ConnectionError('offline')
            class Response:
                text = '<h1>コモディイイダ町屋店</h1><div class="flyer_title">2026年10月17日〜10月20日</div>'
                def raise_for_status(self): pass
            return Response()
        self.assertEqual(inspect_flyer('iida', fetch, date(2026,10,18))['status'], 'current')


if __name__ == '__main__':
    unittest.main()
