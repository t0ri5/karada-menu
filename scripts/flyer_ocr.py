"""Japanese flyer OCR. Results are review candidates, never verified offers.

Publisher periods do not establish the sale date of individual products.
Images are read transiently and are not copied into the public site.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
import hashlib
from io import BytesIO
import re
import unicodedata
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

MAX_BYTES = 16 * 1024 * 1024
MAX_PIXELS = 30_000_000
MAX_PAGES = 2
UA = {"User-Agent": "Mozilla/5.0 (compatible; KaradaMenu/1.2; personal flyer checker)"}
TAX_PRICE = re.compile(r"[（(\s]*税込\s*(?:各\s*)?[¥￥]?\s*(\d{1,3}(?:,\d{3})*|\d{1,5})(?:[.:-](\d{2}))?\s*円?\s*[)）]*")
NOT_PRODUCT = re.compile(r"税込|円|ポイント|エキス|つゆ|鍋|ラーメン|寿司|丼|カレー|キャンペーン|漬け|フライ|ソース|風味")


def normalize(text: str) -> str:
    return unicodedata.normalize('NFKC', text).strip()


def safe_url(url: str) -> bool:
    try:
        u = urlparse(url)
        port = u.port
    except ValueError:
        return False
    if u.scheme != 'https' or u.username or u.password or port not in (None, 443):
        return False
    if u.hostname == 'www.comodi-iida.co.jp':
        return u.path.startswith('/wp/wp-content/uploads/') and u.path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not u.query
    if u.hostname != 'www.shufoo.net':
        return False
    return (u.path == '/api/shopDetailNewXML/891148/'
            or re.fullmatch(r'/c/\d{4}/\d{2}/\d{2}/\d+/index/contents\.xml', u.path) is not None
            or (u.path == '/oi.php' and re.fullmatch(r'/c/\d{4}/\d{2}/\d{2}/\d+/index/orig/[01]\.jpg', u.query) is not None))


def get_bytes(url, fetch) -> bytes:
    if not safe_url(url):
        raise ValueError('Unapproved publisher URL')
    with fetch(url, headers=UA, timeout=(8, 30), stream=True, allow_redirects=False) as response:
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError('Publisher redirect or non-200 response')
        if int(response.headers.get('Content-Length', 0)) > MAX_BYTES:
            raise ValueError('Publisher file exceeds size limit')
        content = bytearray()
        for chunk in response.iter_content(65536):
            content.extend(chunk)
            if len(content) > MAX_BYTES:
                raise ValueError('Publisher file exceeds size limit')
    return bytes(content)


def discover_images(flyer, html, today, fetch) -> list[str]:
    if flyer.get('status') != 'current':
        return []
    if flyer['store'] == 'iida' and flyer['source'] == '公式サイト':
        # Import locally to avoid a circular dependency at module load time.
        if __package__:
            from .update_deals import parsed_ranges
        else:
            from update_deals import parsed_ranges
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        for anchor in soup.select('a[data-flyer]'):
            period = anchor.parent.select_one('.flyer-period')
            if not period or not any(a <= today <= b for a, b in parsed_ranges(period.get_text())):
                continue
            url = anchor['data-flyer']
            if safe_url(url) and url not in urls:
                urls.append(url)
        return urls[:MAX_PAGES]
    if flyer['store'] == 'olympic' and flyer['source'] == 'Shufoo!':
        soup = BeautifulSoup(html, 'html.parser')
        active = soup.select_one('.shop_chirashi_list_item_now [data-content_id]')
        if not active:
            return []
        root = ET.fromstring(get_bytes('https://www.shufoo.net/api/shopDetailNewXML/891148/?crosstype=portal&useUtf=true', fetch))
        if root.findtext('shopId') != '891148':
            raise ValueError('Shufoo shop does not match')
        # Bind images to the issue whose HTML period was actually validated.
        for issue in root.findall('./chirashis/chirashi'):
            if issue.findtext('contentId') != active['data-content_id']:
                continue
            start = datetime.strptime(issue.findtext('publishStartTime'), '%Y/%m/%d %H:%M:%S').date()
            end = datetime.strptime(issue.findtext('publishEndTime'), '%Y/%m/%d %H:%M:%S').date()
            if not start <= today <= end:
                return []
            contents = issue.findtext('contentsXml', '')
            config = ET.fromstring(get_bytes(contents, fetch).decode('shift_jis'))
            count = min(int(config.findtext('./configration/totalPages', '0')), MAX_PAGES)
            path = urlparse(contents).path.removesuffix('index/contents.xml')
            urls = ['https://www.shufoo.net/oi.php?' + path + f'index/orig/{n}.jpg'
                    for n in range(count)]
            return [url for url in urls if safe_url(url)]
    return []


@lru_cache(maxsize=1)
def ocr_engine():
    from rapidocr import RapidOCR, OCRVersion, ModelType
    return RapidOCR(params={
        'Det.ocr_version': OCRVersion.PPOCRV4,
        'Det.model_type': ModelType.MOBILE,
        'Rec.ocr_version': OCRVersion.PPOCRV4,
        'Rec.model_type': ModelType.MOBILE,
        'Rec.lang_type': 'japan',
        'Global.max_side_len': 4000,
        'Det.limit_side_len': 2400,
        'Det.limit_type': 'max',
        'Det.max_candidates': 5000,
        'EngineConfig.onnxruntime.intra_op_num_threads': 2,
        'EngineConfig.onnxruntime.inter_op_num_threads': 1,
    })


def recognize(content: bytes):
    from PIL import Image
    import numpy as np
    with Image.open(BytesIO(content)) as img:
        if img.format not in ('JPEG', 'PNG', 'WEBP') or img.width * img.height > MAX_PIXELS:
            raise ValueError('Unsupported image or excessive pixel count')
        width, height = img.size
        pixels = np.asarray(img.convert('RGB'))[:, :, ::-1].copy()
    output = ocr_engine()(pixels)
    rows = [] if output.txts is None else [
        {'box': box.tolist(), 'text': text, 'score': float(score)}
        for box, text, score in zip(output.boxes, output.txts, output.scores)]
    return rows, width, height


def bounds(row):
    xs, ys = zip(*row['box'])
    return min(xs), min(ys), max(xs), max(ys)


def tax_price(text):
    match = TAX_PRICE.fullmatch(normalize(text))
    if not match:
        return None
    value = Decimal(match[1].replace(',', '') + ('.' + match[2] if match[2] else ''))
    return float(value) if 0 < value <= 20000 else None


def corroborating_base(rows, tax_row, value, width, height):
    """Require the printed pre-tax price to corroborate an 8% food price.

    This rejects lost decimal points (19332 vs 193.32) and many neighbouring
    product mix-ups. Never calculate a tax-inclusive price absent from the OCR.
    """
    tx1, ty1, tx2, _ = bounds(tax_row)
    for row in rows:
        if row['score'] < .95:
            continue
        match = re.fullmatch(r'[¥￥]?(\d{1,3}(?:,\d{3})*|\d{1,5})円?', normalize(row['text']))
        if not match:
            continue
        x1, y1, x2, _ = bounds(row)
        if 0 <= ty1 - y1 <= .06 * height and abs((tx1 + tx2 - x1 - x2) / 2) <= .04 * width:
            base = int(match[1].replace(',', ''))
            exact = Decimal(base) * Decimal('1.08')
            if abs(Decimal(str(value)) - exact) < 1:
                return base
    return None


def candidates_from_rows(rows, width, height, flyer, image_url, today, keywords, exclude):
    prices = [r for r in rows if r['score'] >= .86 and tax_price(r['text']) is not None]
    names = [r for r in rows if r['score'] >= .86 and 2 <= len(normalize(r['text'])) <= 60
             and any(k in normalize(r['text']) for k in keywords)
             and not any(k in normalize(r['text']) for k in exclude)
             and not NOT_PRODUCT.search(normalize(r['text']))]
    found = []
    used_prices = set()
    for name in names:
        nx1, ny1, nx2, ny2 = bounds(name)
        options = []
        for index, price in enumerate(prices):
            px1, py1, px2, py2 = bounds(price)
            dy = py1 - ny2
            dx = abs((px1 + px2 - nx1 - nx2) / 2)
            if -.015 * height <= dy <= .13 * height and dx <= .095 * width:
                options.append(((dx / width) ** 2 + (max(dy, 0) / height) ** 2, index, price))
        options.sort(key=lambda x: x[0])
        if not options or options[0][1] in used_prices:
            continue
        # Two similarly close prices cannot be assigned to a product reliably.
        if len(options) > 1 and options[1][0] < options[0][0] * 1.35:
            continue
        _, index, price = options[0]
        value = tax_price(price['text'])
        base = corroborating_base(rows, price, value, width, height)
        if base is None:
            continue
        used_prices.add(index)
        item = normalize(name['text'])
        px1, py1, px2, py2 = bounds(price)
        nearby = [normalize(r['text']) for r in rows if r['score'] >= .86
                  and nx1 - .015 * width <= bounds(r)[0] <= max(nx2, px2)
                  and ny1 <= bounds(r)[1] <= py2
                  and re.search(r'\d+(?:g|kg|個|本|束|袋|丁|パック|切れ|尾)', normalize(r['text']))]
        qty = ' '.join(nearby)[:80] or '容量・単位をチラシで確認'
        candidate_id = hashlib.sha256(f"{flyer['store']}|{image_url}|{item}|{value}".encode()).hexdigest()[:20]
        found.append({'id': candidate_id, 'store': flyer['store'], 'item': item,
                      'price': value, 'qty': qty, 'source': flyer['url'], 'image_url': image_url,
                      'observed_at': today.isoformat(), 'flyer_period': flyer['period'],
                      'sale_date_status': 'needs_confirmation', 'status': 'needs_confirmation',
                      'method': 'japanese_ocr',
                      'evidence': {'name_text': name['text'], 'tax_price_text': price['text'],
                                   'confidence': round(min(name['score'], price['score']), 4),
                                   'base_price': base,
                                   'box': [round(min(nx1, px1)), round(min(ny1, py1)),
                                           round(max(nx2, px2)), round(max(ny2, py2))]}})
    return found[:25]


def read_flyer(flyer, html, today, fetch, keywords, exclude, reader=recognize):
    report = {'store': flyer['store'], 'status': 'no_images', 'pages': [], 'candidate_count': 0}
    candidates = []
    try:
        urls = discover_images(flyer, html, today, fetch)
        for url in urls:
            page = {'image_url': url}
            report['pages'].append(page)
            try:
                rows, width, height = reader(get_bytes(url, fetch))
                found = candidates_from_rows(rows, width, height, flyer, url, today, keywords, exclude)
                candidates.extend(found)
                page.update(status='ok', text_count=len(rows), candidate_count=len(found))
            except Exception as error:
                page.update(status='failed', message=type(error).__name__ + ': ' + str(error)[:160])
        if urls:
            report['status'] = ('partial' if any(p['status'] == 'failed' for p in report['pages'])
                                else 'review_required' if candidates else 'no_candidates')
    except Exception as error:
        report.update(status='failed', message=type(error).__name__ + ': ' + str(error)[:160])
    report['candidate_count'] = len(candidates)
    return candidates, report
