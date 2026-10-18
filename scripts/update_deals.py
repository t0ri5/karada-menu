"""Best-effort fetch of visible, dated store promotions. Do not guess prices.
Public sites may block automated retrieval or alter markup; failed sources report errors.
"""
import json,re,sys,time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
TODAY=datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat()
STORES={
 'olympic':('オリンピック 荒川一丁目店','https://tokubai.co.jp/'+quote('オリンピック')+'/279440'),
 'iida':('コモディイイダ 町屋店','https://tokubai.co.jp/'+quote('コモディイイダ')+'/7543'),
 'tairaya':('TAIRAYA 町屋店','https://tokubai.co.jp/TAIRAYA/260526'),
}
KEYWORDS=('鮭','サケ','さけ','サーモン','さば','サバ','タラ','たら','アジ','あじ','ブリ','ぶり','イカ','いか','えび','エビ','あさり','アサリ','ホタテ','ほたて','豆腐','とうふ','厚揚げ','ブロッコリー','ほうれん草','小松菜','キャベツ','白菜','玉ねぎ','トマト','きゅうり','大根','にんじん','まいたけ','しめじ','えのき','魚肉ソーセージ','おさかなのソーセージ','長ネギ','ねぎ','かぼちゃ','大豆','納豆','ごぼう','レタス','チンゲン菜')
EXCLUDE=('牛肉','豚肉','鶏肉','ベーコン','ハム','ウインナー','しいたけ','椎茸','シイタケ','調理済','弁当')
RE_PRICE=re.compile(r'(\d{1,3}(?:,\d{3})*|\d{1,5})円')
RE_QTY=re.compile(r'(?:\d+(?:\.\d+)?\s*(?:g|kg|ml|L|個|切れ|尾|パック|束|袋|本|株|丁)|100gあたり|各\d+\S{0,7})')

def extract(text,store,url):
    """Parse adjacent product/price text, including newline-separated tokubai listings.

    Prices on tokubai are commonly displayed as 199円215円(税込), i.e.
    pre-tax then tax-inclusive. We report the tax-inclusive value.
    """
    start=text.find('今日の掲載')
    if start<0:return []
    body=text[start+len('今日の掲載'):]
    stop=len(body)
    for marker in ('注目のお知らせ','お店からのお知らせ','店舗情報詳細'):
        j=body.find(marker)
        if j>=0:stop=min(stop,j)
    body=body[:stop]
    # Each price terminates one offer; product names may span multiple lines.
    price_pair=re.compile(r'(\d{1,3}(?:,\d{3})*|\d{1,5})\s*円\s*(\d{1,3}(?:,\d{3})*|\d{1,5})\s*円\s*\(税込\)')
    found=[]; cursor=0
    for match in price_pair.finditer(body):
        prefix=body[cursor:match.start()]
        cursor=match.end()
        parts=[x.strip() for x in prefix.splitlines() if x.strip()]
        # Tokubai HTML often has a few navigation tokens between offers.
        name=' '.join(parts[-5:]).strip()
        if not name or len(name)>220:continue
        if not any(k in name for k in KEYWORDS) or any(k in name for k in EXCLUDE):continue
        price=int(match.group(2).replace(',',''))
        if price<=0 or price>20000:continue
        qty=RE_QTY.search(name)
        found.append({'store':store,'item':name[:95], 'price':price,
            'qty':qty.group(0) if qty else '単位要確認','source':url,'date':TODAY})
    return found[:25]

def run(fetch=requests.get):
    data={'updated_at':TODAY,'status':'partial','stores':[],'deals':[]}
    for store,(name,url) in STORES.items():
        state={'id':store,'name':name,'url':url,'status':'unavailable','count':0}
        try:
            r=fetch(url,timeout=18,headers={'User-Agent':'Mozilla/5.0 (compatible; MenuAssistant/1.0)'})
            r.raise_for_status()
            soup=BeautifulSoup(r.text,'html.parser')
            for tag in soup(['script','style','noscript']):tag.decompose()
            text=soup.get_text('\n',strip=True)
            # The site's day selector must point at current local date.
            m,d=map(int,TODAY[5:].split('-'))
            if not re.search(rf'{m}月\s*{d}日',text):
                state['status']='date_unverified'
            else:
                found=extract(text,store,url)
                state['status']='ok' if found else 'no_extractable_offers'
                state['count']=len(found)
                data['deals'].extend(found)
        except Exception as e: state['status']='fetch_failed';state['message']=str(e)[:130]
        data['stores'].append(state)
        time.sleep(.5)
    output=ROOT/'data'/'latest.json';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Updated',TODAY,'offers',len(data['deals']),[(s['id'],s['status']) for s in data['stores']])
    return data

if __name__=='__main__':run()
