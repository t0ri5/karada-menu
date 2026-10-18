from datetime import date
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.flyer_ocr import (tax_price, candidates_from_rows, discover_images,
                               get_bytes, read_flyer, safe_url)
from scripts import update_deals

TODAY = date(2026, 10, 18)
FLYER = {'store': 'iida', 'source': '公式サイト', 'status': 'current',
         'url': 'https://www.comodi-iida.co.jp/store/tokyo/t006.html',
         'period': '2026-10-17〜2026-10-20'}
IMAGE = 'https://www.comodi-iida.co.jp/wp/wp-content/uploads/2026/10/flyer.jpg'


def row(text, x, y, width=100, height=20, score=.99):
    return {'text': text, 'score': score,
            'box': [[x,y],[x+width,y],[x+width,y+height],[x,y+height]]}


ROWS = [row('長ねぎ2本',100,100),row('159',100,125),row('(税込171-72)',100,150)]


class OcrTests(unittest.TestCase):
    def test_real_olympic_ocr_excerpt(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/olympic-ocr-excerpt.json').read_text(encoding='utf-8'))
        flyer=dict(FLYER,store='olympic',url=fixture['source'],period='2026-10-14〜2026-10-19')
        found=candidates_from_rows(fixture['rows'],fixture['width'],fixture['height'],flyer,
                                   'https://www.shufoo.net/oi.php?/c/2026/10/09/88289853300247/index/orig/1.jpg',
                                   TODAY,('ねぎ',),())
        self.assertEqual([(c['item'],c['price']) for c in found],[('長ねぎ2本',171.72)])

    def test_only_explicit_tax_prices_and_no_rounding(self):
        self.assertEqual(tax_price('（税込171.72）'), 171.72)
        self.assertEqual(tax_price('(税込171-72)'), 171.72)
        self.assertEqual(tax_price('税込各1,382円)'), 1382)
        for text in ['本体159円', '159円', '(税別159円)', '税込192円の品', '税込0円']:
            self.assertIsNone(tax_price(text))

    def test_candidate_is_unverified_even_inside_current_period(self):
        candidates = candidates_from_rows(ROWS,1000,1000,FLYER,IMAGE,TODAY,('ねぎ',),())
        self.assertEqual(len(candidates),1)
        self.assertEqual(candidates[0]['price'],171.72)
        self.assertEqual(candidates[0]['status'],'needs_confirmation')
        self.assertEqual(candidates[0]['sale_date_status'],'needs_confirmation')
        self.assertNotIn('date',candidates[0])

    def test_lost_decimal_or_wrong_tax_price_rejected(self):
        for text in ['(税込17172)', '(税込215円)']:
            rows = ROWS[:2] + [row(text,100,150)]
            self.assertEqual(candidates_from_rows(rows,1000,1000,FLYER,IMAGE,TODAY,('ねぎ',),()), [])

    def test_neighbouring_prices_and_low_confidence_rejected(self):
        rows = ROWS + [row('(税込192円)',101,150)]
        self.assertEqual(candidates_from_rows(rows,1000,1000,FLYER,IMAGE,TODAY,('ねぎ',),()), [])
        rows = [dict(ROWS[0],score=.4)] + ROWS[1:]
        self.assertEqual(candidates_from_rows(rows,1000,1000,FLYER,IMAGE,TODAY,('ねぎ',),()), [])

    def test_image_date_is_bound_to_its_own_period(self):
        html = f'''<div><a data-flyer="{IMAGE}"></a><p class="flyer-period">2026年10月17日〜20日</p></div>
        <div><a data-flyer="{IMAGE.replace('flyer','old')}"></a><p class="flyer-period">2026年10月14日〜16日</p></div>'''
        self.assertEqual(discover_images(FLYER,html,TODAY,None),[IMAGE])
        self.assertEqual(discover_images(dict(FLYER,status='expired'),html,TODAY,None),[])

    def test_only_approved_publishers_and_paths(self):
        self.assertTrue(safe_url(IMAGE))
        for url in ['http://www.comodi-iida.co.jp/wp/wp-content/uploads/f.jpg',
                    'https://www.comodi-iida.co.jp.attacker.test/wp/wp-content/uploads/f.jpg',
                    'https://localhost/f.jpg', 'file:///tmp/f.jpg',
                    'https://www.comodi-iida.co.jp/private/f.jpg',
                    'https://user:password@www.comodi-iida.co.jp/wp/wp-content/uploads/f.jpg']:
            self.assertFalse(safe_url(url))

    def test_redirects_not_followed_and_byte_limit(self):
        class Response:
            status_code=302
            headers={}
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def raise_for_status(self): pass
            def iter_content(self,*args): yield b'x'*10
        def fetch(url,**kwargs):
            self.assertFalse(kwargs['allow_redirects'])
            return Response()
        with self.assertRaises(ValueError): get_bytes(IMAGE,fetch)
        Response.status_code=200
        with patch('scripts.flyer_ocr.MAX_BYTES',5), self.assertRaises(ValueError):
            get_bytes(IMAGE,fetch)

    def test_ocr_failure_reported_without_losing_text_offers(self):
        def fail(_): raise RuntimeError('model unavailable')
        with patch('scripts.flyer_ocr.discover_images',return_value=[IMAGE]), \
             patch('scripts.flyer_ocr.get_bytes',return_value=b'image'):
            candidates, report = read_flyer(FLYER,'',TODAY,None,('ねぎ',),(),reader=fail)
        self.assertEqual(candidates,[])
        self.assertEqual(report['status'],'partial')
        self.assertEqual(report['pages'][0]['status'],'failed')

    def test_shufoo_issue_must_match_validated_html(self):
        flyer = dict(FLYER,store='olympic',source='Shufoo!')
        html='<li class="shop_chirashi_list_item_now"><span data-content_id="123"></span></li>'
        xml=b'<shop><shopId>891148</shopId><chirashis><chirashi><contentId>456</contentId></chirashi></chirashis></shop>'
        with patch('scripts.flyer_ocr.get_bytes',return_value=xml):
            self.assertEqual(discover_images(flyer,html,TODAY,None),[])

    def test_run_keeps_candidates_out_of_verified_deals(self):
        candidate = candidates_from_rows(ROWS,1000,1000,FLYER,IMAGE,TODAY,('ねぎ',),())[0]
        class Response:
            text='<title>町屋店 店舗情報 | コモディイイダ</title><p>東京都荒川区町屋3-18-11</p><p class="flyer-period">2026年10月17日〜20日</p><div>10月18日</div>'
            def raise_for_status(self): pass
        report={'store':'iida','status':'review_required','candidate_count':1,'pages':[]}
        with TemporaryDirectory() as tmp, patch.object(update_deals,'ROOT',Path(tmp)), \
             patch.object(update_deals,'STORES',{'iida':update_deals.STORES['iida']}), \
             patch.object(update_deals,'read_flyer',return_value=([candidate],report)):
            data=update_deals.run(fetch=lambda *a,**kw:Response(),today=TODAY)
        self.assertEqual(data['deals'],[])
        self.assertEqual(len(data['ocr_candidates']),1)
        self.assertEqual(data['stores'][0]['count'],0)
        self.assertEqual(data['flyers'][0]['item_extraction_status'],'review_required')


if __name__ == '__main__': unittest.main()
