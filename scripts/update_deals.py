"""Daily store data updater for Karada Menu.

Text-based, explicitly priced, dated items are treated as usable offers.
Image-based flyers are made *viewable*, with their publication period checked
separately. A flyer title/period is NEVER counted as a priced sale item.

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
    r"(20\d\d)年\s*(\d{1,2})月\s*(\d{1,2})日"
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
