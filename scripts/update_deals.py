"""Daily store data updater for Karada Menu.

Text-based, explicitly priced, dated items are treated as usable offers.
Image-based flyers are read with Japanese OCR as review candidates. Individual
sale dates and OCR text require confirmation before use in meal suggestions.

All sources are best effort and are subject to source-side permissions/markup.
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

if __package__:
    from .flyer_ocr import read_flyer
else:
    from flyer_ocr import read_flyer

SCRIPT_VERSION = "v7.0-japanese-flyer-ocr-review-20261018"
ROOT = Path(__file__).resolve().parents[1]
TODAY = datetime.now(ZoneInfo("Asia/Tokyo")).date()
STORES = {
    "olympic": ("オリンピック 荒川一丁目店", "https://tokubai.co.jp/" + quote("オリンピック") + "/279440"),
    "iida": ("コモディイイダ 町屋店", "https://tokubai.co.jp/" + quote("コモディイイダ") + "/7543"),
    "tairaya": ("TAIRAYA 町屋店", "https://tokubai.co.jp/TAIRAYA/260526"),
}
# Links open the publishers' websites instead of copying their flyer images.
# The listing may be useful even when the site prevents machine reading.
FLYER_SOURCES = {
    "olympic": [
        ("Shufoo!", "https://www.shufoo.net/pntweb/shopDetail/891148/", "shufoo"),
        ("チラシガイド", "https://chirashi-guide.com/東京都/荒川区/222269/", "guide"),
    ],
    "iida": [
        ("公式サイト", "https://www.comodi-iida.co.jp/store/tokyo/t006.html", "iida_official"),
        ("チラシガイド", "https://chirashi-guide.com/東京都/荒川区/2444/", "guide"),
    ],
}
KEYWORDS = (
    "鮭", "サケ", "さけ", "サーモン", "さば", "サバ", "タラ", "たら", "アジ", "あじ",
    "ブリ", "ぶり", "イカ", "いか", "えび", "エビ", "あさり", "アサリ", "ホタテ", "ほたて",
    "豆腐", "とうふ", "厚揚げ", "ブロッコリー", "ほうれん草", "小松菜", "キャベツ",
    "白菜", "玉ねぎ", "トマト", "きゅうり", "大根", "にんじん", "まいたけ", "しめじ",
    "えのき", "魚肉ソーセージ", "おさかなのソーセージ", "長ネギ", "ねぎ", "かぼちゃ",
    "大豆", "納豆", "ごぼう", "レタス", "チンゲン菜",
)
EXCLUDE = ("牛肉", "豚肉", "鶏肉", "ベーコン", "ハム", "ウインナー", "しいたけ", "椎茸", "シイタケ", "調理済", "弁当")
RE_QTY = re.compile(r"(?:\d+(?:\.\d+)?\s*(?:g|kg|ml|L|個|切れ|尾|パック|束|袋|本|株|丁)|100gあたり|各\d+\S{0,7})")
PRICE_PAIR = re.compile(r"(\d{1,3}(?:,\d{3})*|\d{1,5})\s*円\s*(\d{1,3}(?:,\d{3})*|\d{1,5})\s*円\s*\(税込\)")
DATE_RANGE = re.compile(
    r"(20\d\d)年\s*(\d{1,2})月\s*(\d{1,2})日\s*[〜～~\-–—]\s*"
    r"(?:(20\d\d)年\s*)?(?:(\d{1,2})月\s*)?(\d{1,2})日"
)
UA = {"User-Agent": "Mozilla/5.0 (compatible; KaradaMenu/1.1; personal flyer checker)"}


def extract(text: str, store: str, url: str, today: date | None = None) -> list[dict]:
    """Extract only explicitly adjacent name and *tax-inclusive* price from Tokubai."""
    current = today or TODAY
    start = text.find("今日の掲載")
    if start < 0:
        return []
    body = text[start + len("今日の掲載"):]
    stop = len(body)
    for marker in ("注目のお知らせ", "お店からのお知らせ", "店舗情報詳細"):
        j = body.find(marker)
        if j >= 0:
            stop = min(stop, j)
    body = body[:stop]
    found = []
    cursor = 0
    for match in PRICE_PAIR.finditer(body):
        prefix = body[cursor:match.start()]
        cursor = match.end()
        parts = [x.strip() for x in prefix.splitlines() if x.strip()]
        name = " ".join(parts[-5:]).strip()
        if not name or len(name) > 220:
            continue
        if not any(k in name for k in KEYWORDS) or any(k in name for k in EXCLUDE):
            continue
        price = int(match.group(2).replace(",", ""))
        if price <= 0 or price > 20000:
            continue
        qty = RE_QTY.search(name)
        found.append({
            "store": store, "item": name[:95], "price": price,
            "qty": qty.group(0) if qty else "単位要確認",
            "source": url, "date": current.isoformat(),
        })
    return found[:25]


def parsed_ranges(text: str) -> list[tuple[date, date]]:
    results = []
    for match in DATE_RANGE.finditer(text):
        try:
            start = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            end_year = int(match.group(4)) if match.group(4) else start.year
            end_month = int(match.group(5)) if match.group(5) else start.month
            # A December issue may end in January with the year omitted.
            if not match.group(4) and end_month < start.month:
                end_year += 1
            end = date(end_year, end_month, int(match.group(6)))
        except ValueError:
            continue
        if start <= end and (end - start).days <= 90:
            results.append((start, end))
    return results


def flyer_from_html(html: str, store: str, url: str, provider: str,
                    kind: str, today: date) -> dict:
    """Verify the flyer *date*, not flyer item prices."""
    soup = BeautifulSoup(html, "html.parser")
    for bad in soup(["script", "style", "noscript"]):
        bad.decompose()
    text = soup.get_text(" ", strip=True)
    compact = re.sub(r"\s+", "", text)
    expected = "オリンピック荒川一丁目店" if store == "olympic" else "コモディイイダ町屋店"
    identity_verified = expected in compact
    if kind == "iida_official":
        title = soup.title.get_text(strip=True) if soup.title else ""
        identity_verified = (store == "iida" and "町屋店" in title
                             and "コモディイイダ" in title
                             and "東京都荒川区町屋3-18-11" in compact)
    if not identity_verified:
        return {"store": store, "source": provider, "url": url, "status": "store_unverified", "period": ""}

    # Scope dates to actual flyer blocks: weekly page headings, nearby stores,
    # and archived issues must never validate a different flyer.
    selectors = {"guide": ".flyer_title", "shufoo": ".chirashi_info_public_date",
                 "iida_official": ".flyer-period"}
    if kind == "guide":
        soup = BeautifulSoup(html.split("最近掲載していたチラシ")[0], "html.parser")
    text = " ".join(node.get_text(" ", strip=True)
                    for node in soup.select(selectors[kind]))
    ranges = parsed_ranges(text)
    valid = [(start, end) for start, end in ranges if start <= today <= end]
    if valid:
        start, end = max(valid, key=lambda period: period[0])
        status = "current"
    elif ranges:
        start, end = max(ranges, key=lambda period: period[1])
        status = "expired" if end < today else "not_started"
    else:
        return {"store": store, "source": provider, "url": url, "status": "date_unverified", "period": ""}
    return {
        "store": store, "source": provider, "url": url,
        "status": status, "period": f"{start.isoformat()}〜{end.isoformat()}",
    }


def inspect_flyer(store: str, fetch=requests.get, today: date | None = None,
                  on_current=None) -> dict:
    current = today or TODAY
    sources = FLYER_SOURCES[store]
    first_fallback = {"store": store, "source": sources[0][0], "url": sources[0][1],
                      "status": "unverified", "period": ""}
    for provider, url, kind in sources:
        try:
            response = fetch(url, timeout=18, headers=UA)
            response.raise_for_status()
            flyer = flyer_from_html(response.text, store, url, provider, kind, current)
            if flyer["status"] == "current":
                if on_current:
                    on_current(flyer, response.text)
                return flyer
            # Track an explicit out-of-date issue or a site we can actually inspect.
            if first_fallback["status"] == "unverified":
                first_fallback = flyer
        except requests.RequestException:
            continue
    return first_fallback


def run(fetch=requests.get, today: date | None = None) -> dict:
    print("KARADA_SCRIPT_VERSION:", SCRIPT_VERSION)
    current = today or TODAY
    today_str = current.isoformat()
    data = {"updated_at": today_str, "status": "partial", "stores": [], "deals": [],
            "flyers": [], "ocr_candidates": [], "ocr_reports": []}

    def process_images(flyer, html):
        candidates, report = read_flyer(flyer, html, current, fetch, KEYWORDS, EXCLUDE)
        data['ocr_candidates'].extend(candidates)
        data['ocr_reports'].append(report)
        flyer['item_extraction_status'] = report['status']
        flyer['candidate_count'] = report['candidate_count']
        print('OCR_STATUS:', flyer['store'], report['status'], report['candidate_count'], flush=True)
        if report['status'] in ('failed', 'partial'):
            print('::warning::Flyer OCR could not read all pages for ' + flyer['store'])
    for store, (name, url) in STORES.items():
        state = {"id": store, "name": name, "url": url,
                 "status": "unavailable", "count": 0}
        try:
            response = fetch(url, timeout=18, headers=UA)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text("\n", strip=True)
            # Date selector MUST identify today, or product prices are not trusted.
            if not re.search(rf"{current.month}月\s*{current.day}日", text):
                state["status"] = "date_unverified"
            else:
                found = extract(text, store, url, current)
                state["status"] = "ok" if found else "no_extractable_offers"
                state["count"] = len(found)
                data["deals"].extend(found)
        except requests.RequestException as error:
            state["status"] = "fetch_failed"
            state["message"] = str(error)[:130]
        data["stores"].append(state)
        if store in FLYER_SOURCES:
            flyer = inspect_flyer(store, fetch, current, process_images)
            flyer.setdefault("item_extraction_status", "not_attempted")
            flyer.setdefault("candidate_count", 0)
            data["flyers"].append(flyer)
        time.sleep(0.15)

    output = ROOT / "data" / "latest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated", today_str, "offers", len(data["deals"]),
          [(s["id"], s["status"], s["count"]) for s in data["stores"]])
    print("FLYER_STATUS:", [(f["store"], f["source"], f["status"], f["period"])
                             for f in data["flyers"]])
    return data


if __name__ == "__main__":
    run()

# KARADA_MENU_COMPLETE_FILE_END_v6_1
