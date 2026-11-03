'use strict';
const STORES=[
{id:'olympic',name:'オリンピック 荒川一丁目店',address:'東京都荒川区荒川1-6-1',url:'https://www.olympic-corp.co.jp/shop/71',flyerUrl:'https://www.shufoo.net/pntweb/shopDetail/891148/',flyerLabel:'Shufoo!',hours:'10:00～21:00'},
{id:'iida',name:'コモディイイダ 町屋店',address:'東京都荒川区町屋3-18-11',url:'https://comodi-iida.co.jp/store/tokyo/t006.html',flyerUrl:'https://www.comodi-iida.co.jp/store/tokyo/t006.html',flyerLabel:'公式サイト',hours:'9:00～22:00'},
{id:'tairaya',name:'TAIRAYA 町屋店',address:'東京都荒川区町屋3-20-15',url:'https://www.eco-s.co.jp/store/tairaya%E7%94%BA%E5%B1%8B%E5%BA%97/',flyerUrl:'https://tokubai.co.jp/TAIRAYA/260526',flyerLabel:'トクバイ',hours:'24時間'}
];
// Ingredients represent shopping amounts for TWO adults. No meat, meat extracts, or shiitake.
const DINNERS=[
['鮭としめじのレモン蒸し','鮭 2切れ|しめじ 1パック|玉ねぎ 1/2個|レモン 1個|ブロッコリー 1/2株','ホイルに玉ねぎ、鮭、しめじをのせて包み、フライパンで15分ほど蒸す。レモンを絞り、少量の減塩しょうゆで食べる。','ブロッコリーの温サラダ'],
['サバのトマト煮','サバ 2切れ|トマト缶 1/2缶|玉ねぎ 1個|にんにく 1片|小松菜 1束','サバを焼き、玉ねぎ・トマト缶・にんにくを加えて煮込む。小松菜を添える。','小松菜のごまあえ'],
['タラと白菜の生姜蒸し','タラ 2切れ|白菜 1/4玉|生姜 1片|えのき 1袋|にんじん 1本','白菜・えのき・にんじんの上にタラをのせ、生姜と酒少々で蒸す。','にんじんの酢あえ'],
['エビとブロッコリーのにんにく炒め','むきエビ 200g|ブロッコリー 1株|パプリカ 1個|にんにく 1片|木綿豆腐 1丁','少量のオリーブ油でにんにくとエビを炒め、下ゆでした野菜を加える。','冷ややっこ'],
['アジの香草焼き','アジ 2尾|トマト 2個|レタス 1/2玉|レモン 1個|大豆水煮 100g','アジにこしょうとハーブをまぶし焼く。トマトと大豆のサラダを添える。','大豆とトマトのサラダ'],
['豆腐とひじきの和風ハンバーグ','木綿豆腐 1丁|乾燥ひじき 10g|玉ねぎ 1/2個|卵 1個|大根 1/4本','水切り豆腐、戻したひじき、みじん切り玉ねぎ、卵を混ぜ、成形して焼く。大根おろしを添える。','大根おろしと青菜'],
['ブリの照り焼き風','ブリ 2切れ|もやし 1袋|ピーマン 2個|生姜 1片|きゅうり 1本','ブリを焼き、減塩しょうゆ・みりんを少量ずつ絡める。炒め野菜を添える。','きゅうりの酢の物'],
['イカとキャベツの塩レモン炒め','イカ 200g|キャベツ 1/4玉|しめじ 1袋|レモン 1個|トマト 2個','イカと野菜を短時間で炒め、レモンと黒こしょうで調味する。','トマトサラダ'],
['サワラの西京焼き風','サワラ 2切れ|無糖ヨーグルト 50g|減塩みそ 小さじ2|大根 1/4本|小松菜 1束','みそとヨーグルトを混ぜて魚に薄く塗り、冷蔵後に焦がさないよう焼く。','大根と小松菜の和え物'],
['あさりと豆腐の野菜蒸し','砂抜きあさり 250g|絹豆腐 1丁|白菜 1/4玉|長ねぎ 1本|生姜 1片','あさり・白菜・ねぎを蒸し、口が開いたら豆腐を加え温める。塩は追加せず生姜で香りづけ。','トマトとわかめのサラダ'],
['鮭の野菜あんかけ','生鮭 2切れ|にんじん 1本|玉ねぎ 1個|えのき 1袋|チンゲン菜 1束','焼いた鮭に、野菜を煮た薄味のあんをかける。','チンゲン菜のおひたし'],
['ツナと大豆のトマト煮','ツナ水煮缶 2缶|大豆水煮 150g|トマト缶 1/2缶|ズッキーニ 1本|玉ねぎ 1個','玉ねぎ・ズッキーニを炒め、ツナ、大豆、トマトを加え煮る。','レタスサラダ'],
['カレイの煮つけ（薄味）','カレイ 2切れ|生姜 1片|ごぼう 1本|ほうれん草 1束|にんじん 1本','水・酒・少量の減塩しょうゆとみりんで魚を煮る。煮汁は飲まない。','ごぼうのきんぴら'],
['エビと豆腐の中華蒸し','むきエビ 200g|絹豆腐 1丁|長ねぎ 1本|生姜 1片|ブロッコリー 1/2株','豆腐・エビ・生姜を蒸し、ねぎ・ごま油数滴・減塩しょうゆ少々で仕上げる。','ブロッコリーのごまあえ'],
['サンマの塩なしグリル','サンマ 2尾|大根 1/4本|かぼちゃ 1/8個|ほうれん草 1束','サンマを塩を振らずに焼き、大根おろし・すだちやレモンを添える。','かぼちゃの蒸し煮'],
['さわらの生姜レモン焼き','生さわら（塩なし）2切れ・約220g|ブロッコリー 1/2株|にんじん 1/2本|絹ごし豆腐 150g|ほうれん草 150g|乾燥わかめ 3g|生姜 1片|レモン 1個|米・もち麦（炊飯後）200～240g','さわらに生姜をまぶし少量のオリーブ油で両面焼いて中心まで加熱し、レモンと減塩しょうゆ小さじ1で仕上げる。ブロッコリー・にんじんを加熱して豆腐とすりごまのソースをかけ、ゆでたほうれん草と戻したわかめを酢で和える。もち麦入りご飯は1人100～120gを目安にする。','ブロッコリーとにんじんの豆腐ごまソース、ほうれん草とわかめの酢の物'],
['タラのアクアパッツァ','タラ 2切れ|ミニトマト 1パック|あさり 150g|にんにく 1片|ブロッコリー 1/2株','タラ・あさり・トマト・水とにんにくを蒸し煮。あさりの塩分を活かし塩を追加しない。','ブロッコリーの温野菜'],
['サバのカレー焼き','サバ 2切れ|カレー粉 小さじ1|キャベツ 1/4玉|きゅうり 1本|トマト 1個','サバにカレー粉をまぶして焼く。野菜を多めに添える。','キャベツときゅうりのサラダ'],
['エビの野菜たっぷり豆乳スープ煮','むきエビ 180g|無調整豆乳 250ml|白菜 1/4玉|しめじ 1袋|にんじん 1本','水と野菜で煮て、豆乳とエビを加える。沸騰させず、塩分控えめで仕上げる。','トマトの冷菜'],
['鮭のごま焼き','生鮭 2切れ|白ごま 大さじ1|小松菜 1束|えのき 1袋|豆腐 1/2丁','鮭にごまをまぶして焼く。小松菜とえのきをさっと煮て添える。','小松菜と豆腐のおひたし'],
['マグロのソテー香味だれ','加熱用マグロ 220g|長ねぎ 1本|生姜 1片|パプリカ 1個|レタス 1/2玉','マグロを十分加熱してソテーし、酢・生姜・ねぎの香味だれをかける。','パプリカサラダ'],
['豆腐と野菜の卵とじ','木綿豆腐 1丁|卵 2個|玉ねぎ 1個|小松菜 1束|まいたけ 1袋','野菜を薄味の昆布だしで煮、豆腐を入れ、卵でとじる。','大根の甘酢あえ'],
['アジの南蛮漬け（揚げない）','アジ 2尾|玉ねぎ 1個|にんじん 1本|ピーマン 2個|酢 大さじ3','焼いたアジを、酢と少量のしょうゆ・水で作った南蛮だれに野菜と漬ける。','ブロッコリー'],
['ホタテと青梗菜の生姜炒め','ホタテ 200g|チンゲン菜 2株|しめじ 1袋|生姜 1片|トマト 2個','ホタテと青梗菜を少量の油で炒め、生姜とこしょうで味付け。','トマトのマリネ'],
['イワシのトマト煮','イワシ 4尾|トマト缶 1/2缶|玉ねぎ 1個|にんにく 1片|キャベツ 1/4玉','下処理したイワシをトマトと玉ねぎで煮る。骨に注意する。','キャベツの温サラダ'],
['サーモンとアボカドの和風サラダ','刺身用サーモン 180g|アボカド 1個|レタス 1/2玉|きゅうり 1本|豆腐 1丁','サーモンは刺身用を購入し冷蔵保存。野菜と豆腐にのせ、酢・わさび・少量のしょうゆで食べる。','豆腐と野菜のサラダ'],
['豆と野菜のスパイスカレー','ミックスビーンズ 200g|トマト缶 1/2缶|玉ねぎ 1個|なす 2本|カレー粉 大さじ1','玉ねぎを炒め、豆と野菜・カレー粉を水とトマトで煮る。肉エキス入りカレールウは使わない。','無糖ヨーグルト'],
['カキとほうれん草の豆乳煮','加熱用カキ 200g|ほうれん草 1束|無調整豆乳 250ml|玉ねぎ 1個|しめじ 1袋','カキは中心まで十分に加熱。野菜と豆乳を合わせて軽く煮る。','にんじんラペ'],
['タラの梅しそ焼き','タラ 2切れ|梅干し 1個|大葉 4枚|大根 1/4本|ブロッコリー 1/2株','塩分の少ない梅干しを少量たたいて大葉と一緒にタラにのせ、焼く。','大根とブロッコリーのサラダ'],
['サバ缶と野菜のホイル蒸し','食塩不使用サバ水煮缶 2缶|キャベツ 1/4玉|しめじ 1袋|玉ねぎ 1個|レモン 1個','サバ缶と野菜を包み蒸し、レモンと黒こしょうで仕上げる。','きゅうりとトマトのサラダ']
];
const BREAKFAST=['納豆・小松菜おひたし・もち麦ご飯','無糖ヨーグルト・オートミール・キウイ','全粒粉トースト・ゆで卵・トマト','豆腐とわかめの減塩みそ汁・もち麦ご飯','無糖ヨーグルト・りんご・無塩ナッツ','納豆・きゅうり・雑穀ご飯','オートミール豆乳粥・ゆで卵'];
const LUNCH=['サバ水煮缶と野菜の丼（もち麦ご飯）','豆腐とわかめのそば（つゆは残す）','ツナ水煮と野菜の全粒粉サンド','野菜たっぷり豆乳うどん（麺少なめ）','エビと野菜の雑穀チャーハン（油控えめ）','大豆と野菜のトマトパスタ（乾麺控えめ）','鮭とブロッコリーの混ぜご飯'];
const SIDES=['もち麦ご飯 1人100～150g目安','野菜をもう1皿プラス','汁物なしでもOK'];
const DAY0=new Date(2026,9,18);let currentTab='today',chosenDay=dayNum(),selectedWeek=0,selectedDateOffset=0;let remoteFeed={updated_at:null,stores:[],deals:[],flyers:[],status:'未更新'};let deals=load('deals',[]),checks=load('checks',{}),servings=Number(load('servings',2));
function load(k,f){try{let v=JSON.parse(localStorage.getItem('km_'+k));return v??f}catch{return f}}function save(k,v){localStorage.setItem('km_'+k,JSON.stringify(v))}
function localToday(){const n=new Date();return new Date(n.getFullYear(),n.getMonth(),n.getDate())}
function dateAt(offset=0){const d=localToday();d.setDate(d.getDate()+offset);return d}
function absoluteDay(d){return Math.round((Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())-Date.UTC(2026,9,18))/86400000)}
function daysSinceStart(){return Math.max(0,absoluteDay(localToday()))}
function indexAt(offset=0){return ((absoluteDay(dateAt(offset))%DINNERS.length)+DINNERS.length)%DINNERS.length}
function dayNum(){return indexAt(0)}
function esc(s){return String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}
function formatDate(d,full=false){return `${full?d.getFullYear()+'年':''}${d.getMonth()+1}月${d.getDate()}日（${'日月火水木金土'[d.getDay()]}）`}
function dateOf(i){return formatDate(dateAt(i-dayNum()))}
function weekStart(offset=0){const d=dateAt(offset);d.setDate(d.getDate()-((d.getDay()+6)%7));return d}
function weekDates(shift=0){const start=weekStart();start.setDate(start.getDate()+shift*7);return Array.from({length:7},(_,i)=>{const d=new Date(start);d.setDate(start.getDate()+i);return d})}
function dailyMenu(i){const m=remoteFeed.daily_menu;return i===dayNum()&&currentFeed()&&m&&m.date===isoToday()&&Array.isArray(m.ingredients)&&m.ingredients.length&&m.title&&m.steps?m:null}
function ingredients(i){const m=dailyMenu(i);return m?m.ingredients:DINNERS[i][1].split('|').map(s=>s.trim())}
function title(i){return dailyMenu(i)?.title||DINNERS[i][0]}
function steps(i){return dailyMenu(i)?.steps||DINNERS[i][2]}
function side(i){return dailyMenu(i)?.side||DINNERS[i][3]}
function activeDeals(){const now=new Date();const today=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;return [...deals.filter(d=>!d.until||d.until>=today),...(remoteFeed.updated_at===today?(remoteFeed.deals||[]):[])]}
function matches(i){return activeDeals().filter(d=>ingredients(i).some(item=>item.includes(d.item)||d.item.includes(item.split(' ')[0])))}
function recommend(){return DINNERS.map((_,i)=>({i,score:matches(i).length})).filter(v=>v.score>0).sort((a,b)=>b.score-a.score).slice(0,5)}
function autoSelected(i){if(i!==dayNum())return i;if(dailyMenu(i))return i;const list=recommend();return list.length?list[0].i:i}
function isoToday(){const now=new Date();return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`}
function currentFeed(){return remoteFeed.updated_at===isoToday()}
function flyerFor(id){return currentFeed()?(remoteFeed.flyers||[]).find(f=>f.store===id):undefined}
function priceStatusText(s,f){if(!s)return '未確認';if(s.status==='fetch_failed')return '取得先への接続失敗';if(s.status==='date_unverified')return '掲載日を確認できません';if(s.count>0)return `${Number(s.count)}件`;return f?.item_extraction_status==='unsupported_image_extraction'?'テキスト商品0件・画像チラシの商品名と税込価格の読取りは未対応':'テキスト商品0件'}
  function flyerText(f){if(!f)return '公開日の自動確認はまだできていません';if(f.status==='current')return `本日有効なチラシを確認：${esc(f.period||'')}`;if(f.status==='expired')return `前回の掲載期間：${esc(f.period||'')}（本日有効か要確認）`;if(f.status==='not_started')return `掲載予定：${esc(f.period||'')}（本日は対象外）`;return '公開日の自動確認はできていません。掲載先でご確認ください。'}
function statusHtml(){const isToday=currentFeed();const latestOffers=activeDeals();const flyers=isToday?(remoteFeed.flyers||[]):[];const flyerCount=flyers.filter(f=>f.status==='current').length;return `<section class="card"><strong>  毎朝の献立・特売・チラシ更新</strong><p class="muted">取得日：${esc(remoteFeed.updated_at||'未取得')} ${isToday?'（本日）':'（本日未更新）'}</p><p class="muted">日付を確認できたチラシ：${flyerCount}店 ／   商品情報：${latestOffers.length+ocrCandidates().length}件（確認済み・登録済み ${latestOffers.length}件 ／ 画像候補 ${ocrCandidates().length}件）</p><button class="btn secondary" data-refresh="1">最新情報を読み直す</button><p class="muted">今日の献立：${esc(dailyMenu(dayNum())?.title||'固定30日献立（新データ未取得）')}。チラシの公開確認と、商品・価格の抽出は別です。チラシを見られても商品を自動取得できない場合があります。実売価格・在庫は店頭で確認してください。</p></section>`}
function cardMeal(i,full=true,offset=selectedDateOffset){const d=DINNERS[i];return `<article class="card"><div class="label">${formatDate(dateAt(offset),true)} の夕食 ${offset===0?'・今日':''}</div><div class="title">  ${esc(title(i))}</div><span class="pill">魚介・大豆中心</span><span class="pill">肉・シイタケ不使用</span><p class="muted">副菜：${esc(side(i))}<br>${SIDES[0]}</p>${matches(i).length?`<p><span class="badge">登録した特売食材と一致：${matches(i).map(d=>esc(d.item)).join('・')}</span></p>`:''}${full?`<div class="line"></div><h3>材料（2人分の目安）</h3><ul>${ingredients(i).map(s=>`<li>${esc(s)}</li>`).join('')}</ul><h3>作り方</h3><p>${esc(steps(i))}</p><div class="notice">調味料は減塩タイプを少量使用。主食量は体格・活動量・治療状況に合わせて調整してください。材料は概算で、正確な栄養価計算は行っていません。</div><div class="buttons" style="margin-top:12px"><button class="btn" data-add="${i}">  材料を買い物リストへ</button><button class="btn secondary" data-copy="${i}">  レシピをコピー</button></div>`:''}</article>`}
function today(){
  const base=chosenDay,i=selectedDateOffset===0?autoSelected(base):base;
  const start=dateAt(0);
  return `${statusHtml()}<section class="card"><div class="row"><div><div class="label">今日：${formatDate(start,true)}</div><h2>${selectedDateOffset===0?'今日のごはん':'選んだ日の献立'}</h2></div><button class="btn secondary" data-go="stores">特売を確認</button></div>
  <div class="buttons" style="margin:10px 0"><button class="btn secondary" data-reset-day="1">今日へ戻る</button><button class="btn outline" data-go="calendar">週ごとの献立を見る</button></div>
  <div class="daynav">${Array.from({length:30},(_,n)=>{const date=dateAt(n),index=indexAt(n);return `<button class="day ${selectedDateOffset===n?'active':''}" data-date-offset="${n}" aria-label="${formatDate(date,true)}"><small>${'日月火水木金土'[date.getDay()]}</small>${date.getMonth()+1}/${date.getDate()}</button>`}).join('')}</div>
  <p class="muted">日付は毎日自動で進みます。過去の献立を見るには「週ごとの献立」を開いてください。</p></section>
  <div class="grid"><div class="mini"><div class="label">朝食</div><strong>${esc(BREAKFAST[((i%7)+7)%7])}</strong></div><div class="mini"><div class="label">昼食</div><strong>${esc(LUNCH[((i%7)+7)%7])}</strong></div></div><div style="height:15px"></div>
  ${selectedDateOffset===0&&i!==base?'<div class="notice">登録済みの特売食材に合わせて本日の夕食候補を変更しました。価格は店頭で確認してください。</div>':''}
  ${cardMeal(i,true,selectedDateOffset)}
  ${recommend().length?`<section class="card"><h3>登録した特売食材を使える献立</h3>${recommend().map(x=>`<div class="checks"><span>${esc(title(x.i))}（一致${x.score}件）</span><button class="btn secondary" data-day="${x.i}">見る</button></div>`).join('')}</section>`:''}`;
}
function calendar(){
  const dates=weekDates(selectedWeek),start=dates[0],end=dates[6];
  const dateRange=`${start.getFullYear()}年${start.getMonth()+1}月${start.getDate()}日〜${end.getMonth()+1}月${end.getDate()}日`;
  return `<h2>30日間の献立</h2>
  <p class="muted"><strong>本日：${formatDate(localToday(),true)}</strong><br>表示週：${dateRange}。左スワイプで前週、右スワイプで翌週。ボタンでも切り替えられます。</p>
  <div class="buttons" style="margin:12px 0;justify-content:space-between">
  <button class="btn secondary" data-week-move="-1">← 前の週</button>
  <button class="btn outline" data-week-today="1">今日へ戻る</button>
  <button class="btn secondary" data-week-move="1">次の週 →</button>
  </div>
  <div id="calendar-weeks" aria-label="週別献立、左右にスワイプで週を切り替え" style="touch-action:pan-y">
  ${dates.map(date=>{const offset=Math.round((Date.UTC(date.getFullYear(),date.getMonth(),date.getDate())-Date.UTC(localToday().getFullYear(),localToday().getMonth(),localToday().getDate()))/86400000);
    const i=indexAt(offset),isToday=offset===0;
    return `<div class="card" ${isToday?'style="border:2px solid #20766a"':''}><div class="label">${formatDate(date,true)} ${isToday?'・今日':''}</div><h3>${esc(isToday?title(i):DINNERS[i][0])}</h3>
      <p class="muted">朝：${esc(BREAKFAST[i%7])}<br>昼：${esc(LUNCH[i%7])}<br>夕：${esc(isToday?title(i):DINNERS[i][0])} ＋ ${esc(isToday?side(i):DINNERS[i][3])}</p>
      <button class="btn secondary" data-date-offset="${offset}">レシピを開く →</button></div>`}).join('')}
  </div>`;
}
function ocrCandidates(){return currentFeed()?(remoteFeed.ocr_candidates||[]).filter(c=>c.status==='needs_confirmation'&&c.observed_at===isoToday()&&STORES.some(s=>s.id===c.store)&&!deals.some(d=>d.ocrCandidateId===c.id&&d.until>=isoToday())):[]}
function ocrStatusText(f){if(!f)return '';const messages={review_required:`画像から${Number(f.candidate_count||0)}件の読取候補（確認が必要）`,no_candidates:'画像を読み取りましたが、条件に合う候補はありません',no_images:'読取可能な画像を取得できませんでした',failed:'画像の読取りに失敗しました',partial:`画像の一部を読み取れませんでした・候補${Number(f.candidate_count||0)}件`,not_attempted:'掲載期間を確認できず画像を読み取っていません',unsupported_image_extraction:'このデータは画像読取り対応前のものです'};return messages[f.item_extraction_status]||''}
function safeOcrImageUrl(value){try{const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password)return '';if(u.hostname==='www.comodi-iida.co.jp'&&u.pathname.startsWith('/wp/wp-content/uploads/'))return u.href;if(u.hostname==='www.shufoo.net'&&u.pathname==='/oi.php'&&/^\?\/c\/\d{4}\/\d{2}\/\d{2}\/\d+\/index\/orig\/[01]\.jpg$/.test(u.search))return u.href}catch{}return ''}
function ocrReviewHtml(){const candidates=ocrCandidates();return `<section class="card" id="ocr-offers"><h3>画像から読み取った商品・${candidates.length}件（要確認）</h3><p class="muted">商品名を押すと、元のチラシ画像と確認・登録フォームを開けます。本日の販売対象・商品名・税込価格・容量を確認して登録してください。確認前の商品は献立には使いません。</p>${candidates.map(c=>`<details class="deal"><summary>${esc(c.item)} ／ 税込${Number(c.price).toLocaleString('ja-JP',{maximumFractionDigits:2})}円（要確認）</summary><p class="muted">${esc(STORES.find(s=>s.id===c.store)?.name||'')} ／ チラシ掲載期間：${esc(c.flyer_period||'')}<br>個別の販売日：未確認</p>${safeOcrImageUrl(c.image_url)?`<p><a href="${esc(safeOcrImageUrl(c.image_url))}" target="_blank" rel="noopener noreferrer">元のチラシ画像で確認する</a></p>`:''}<form data-ocr-form="${esc(c.id)}"><label class="f">商品名<input class="input" name="item" value="${esc(c.item)}" required maxlength="95"></label><label class="f">税込価格（円）<input class="input" name="price" type="number" min="0.01" max="20000" step="0.01" value="${Number(c.price)}" required></label><label class="f">容量・単位<input class="input" name="qty" value="${esc(c.qty?.startsWith('容量・')?'':c.qty||'')}" placeholder="2本・100gあたり等" maxlength="80" required></label><label class="checks"><input type="checkbox" name="confirmed" required><span>本日の販売対象・商品名・税込価格・容量をチラシで確認しました</span></label><button class="btn" type="submit">確認した内容を本日の特売に登録</button></form></details>`).join('')||'<p class="muted">現在、確認待ちの読取候補はありません。画像を読み取れない場合は下のフォームから手入力できます。</p>'}</section>`}
function stores(){
  const items=activeDeals();
  const storeCards=STORES.map(s=>{
    const flyer=flyerFor(s.id);
    const priceState=currentFeed()?(remoteFeed.stores||[]).find(x=>x.id===s.id):undefined;
    // Only external HTTPS links that belong to this app's hardcoded store list.
    const href=s.flyerUrl;
    const checked=flyer&&flyer.status==='current';
    const label=checked?'  当日チラシ掲載確認':'チラシを開いて内容を確認';
    return `<section class="card store"><h3>${esc(s.name)}</h3><div class="muted">${esc(s.address)}<br>営業時間：${esc(s.hours)}</div><p class="muted"><strong>${label}</strong><br>${flyerText(flyer)}<br>商品・価格の自動抽出：${esc(priceStatusText(priceState,flyer))}<br>${esc(ocrStatusText(flyer))}</p><div class="buttons" style="margin-top:10px"><a class="btn" href="${esc(href)}" target="_blank" rel="noopener noreferrer">  チラシを見る（${esc(s.flyerLabel)}）</a><a class="btn secondary" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">公式店舗ページ</a><a class="btn outline" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.name)}" target="_blank" rel="noopener noreferrer">地図</a></div></section>`;
  }).join('');
  return `<h2>  3店舗のチラシ・特売</h2>${statusHtml()}${ocrReviewHtml()}<section class="card"><h3>確認済み・登録済みの特売・${items.length}件</h3>${items.length?items.map(d=>`<div class="deal"><strong>${esc(d.item)} ${Number(d.price).toLocaleString()}円</strong> <span class="muted">${esc(d.qty||'')}</span><p class="muted">${esc(STORES.find(s=>s.id===d.store)?.name||d.store)} ／ ${d.source?`<a href="${esc(d.source)}" target="_blank" rel="noopener noreferrer">掲載元</a>`:'手入力・確認登録'}</p></div>`).join(''):'<p class="muted">本日、商品と税込価格の両方が確認できた特売情報はありません。下のチラシから価格を確認できます。</p>'}</section>${storeCards}<section class="card"><h3>  チラシで見つけた特売を記録</h3><p class="muted">価格の自動抽出ができないチラシでも、ここに登録すると献立候補に反映できます。</p><form id="dealform"><label class="f" for="store">店舗</label><select class="input" id="store" required>${STORES.map(s=>`<option value="${s.id}">${esc(s.name)}</option>`).join('')}</select><label class="f" for="item">食材名（例：鮭、ブロッコリー）</label><input class="input" id="item" required maxlength="40" placeholder="鮭"><div class="grid"><div><label class="f" for="price">価格（税込・円）</label><input class="input" id="price" type="number" min="1" max="999999" required placeholder="298"></div><div><label class="f" for="qty">容量や単位</label><input class="input" id="qty" maxlength="30" placeholder="2切れ / 100g"></div></div><label class="f" for="until">特売終了日（分かれば）</label><input class="input" id="until" type="date"><button class="btn" style="margin-top:13px" type="submit">＋ 特売を登録</button></form></section><section class="card"><h3>登録済みの特売（手入力メモ）</h3>${deals.length?deals.slice().reverse().map(d=>`<div class="deal"><div class="row"><div><strong>${esc(d.item)} ${Number(d.price).toLocaleString()}円</strong> <span class="muted">${esc(d.qty||'')}</span></div><button class="btn secondary" data-delete="${d.id}">削除</button></div><div class="muted">${esc(STORES.find(s=>s.id===d.store)?.name||'')} / ${d.until?`終了 ${esc(d.until)}`:'終了日未設定'} ${activeDeals().includes(d)?'':'（期限切れ）'}</div></div>`).join(''):'<div class="empty">まだ特売価格を登録していません。</div>'}<div class="buttons" style="margin-top:10px"><button class="btn outline" data-go="today">特売から献立を探す →</button></div></section>`;
}
function shopping(){let all=load('list',[]);return `<h2>  買い物リスト</h2><section class="card"><div class="row"><span class="muted">${all.length}品目・${servings}人分</span><button class="btn secondary" data-clear="list">リストを空にする</button></div><p class="muted">各献立の「材料を買い物リストへ」から追加できます。食材量は2人分レシピを基準にしています。人数変更時は数量を調整してください。</p>${all.length?all.map((v,i)=>`<label class="checks"><input type="checkbox" data-check="${i}" ${checks[v]?'checked':''}><span style="${checks[v]?'text-decoration:line-through;color:#84938a':''}">${esc(v)}</span></label>`).join(''):'<div class="empty">リストは空です。今日の献立から追加してください。</div>'}<div class="buttons" style="margin-top:14px"><button class="btn" data-share="list">リストを共有・コピー</button></div></section><section class="card"><h3>1週間分をまとめて追加</h3><p class="muted">選択中の日付から7日間の夕食食材をまとめます。</p><button class="btn secondary" data-addweek="1">7日分の材料を追加</button></section>`}
function settings(){return `<h2>設定・使い方</h2><section class="card"><h3>食事の基本ルール</h3><p>・通常の肉・肉エキス・シイタケは使用しません。<br>・魚介類・大豆製品・卵を中心にします。<br>・ハム・ソーセージは使用可能ですが、減塩のため今回の30日献立には入れていません。</p><h3>ご利用人数</h3><select class="input" id="servings"><option value="1" ${servings===1?'selected':''}>1人</option><option value="2" ${servings===2?'selected':''}>2人</option><option value="3" ${servings===3?'selected':''}>3人</option><option value="4" ${servings===4?'selected':''}>4人</option></select><p class="muted">レシピの材料表示は2人分の固定値です。人数選択は買い物画面の参考表示のみです。</p></section><section class="card"><h3>  ホーム画面に追加</h3><p><strong>iPhone：</strong>Safariで公開URLを開く → 共有 →「ホーム画面に追加」</p><p><strong>Android：</strong>Chromeで公開URLを開く → メニュー →「アプリをインストール」または「ホーム画面に追加」</p><button class="btn" id="install" style="display:none">アプリをインストール</button><p class="muted">HTTPSで公開する必要があります。ローカルファイルを開くだけではPWAのインストールやオフライン機能は動作しません。</p></section><section class="card"><h3>データと健康について</h3><p class="muted">買い物リストと特売メモはこの端末のブラウザ内に保存されます。サーバーとの同期やご家族とのデータ共有はありません。広告・トラッキング機能もありません。</p><p class="muted">減塩・飽和脂肪酸控えめ・食物繊維を意識した一般的な家庭献立です。糖尿病、腎疾患、アレルギー、服薬中の場合は医療者と食事量を調整してください。栄養成分・価格の自動算定は行っていません。</p></section>`}
function render(){document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x.dataset.tab===currentTab));document.getElementById('view').innerHTML=({today,calendar,stores,shopping,settings}[currentTab])();window.scrollTo({top:0,behavior:'instant'})}
function goto(tab){currentTab=tab;render()}
let calendarTouchStart=null;
document.addEventListener('touchstart',e=>{if(e.target.closest('#calendar-weeks'))calendarTouchStart={x:e.touches[0].clientX,y:e.touches[0].clientY}}, {passive:true});
document.addEventListener('touchend',e=>{if(!calendarTouchStart)return;const t=e.changedTouches[0],dx=t.clientX-calendarTouchStart.x,dy=t.clientY-calendarTouchStart.y;calendarTouchStart=null;if(currentTab==='calendar'&&Math.abs(dx)>65&&Math.abs(dx)>Math.abs(dy)*1.3){selectedWeek+=dx<0?-1:1;render()}},{passive:true});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const x=b.dataset;if(x.tab)goto(x.tab);else if(x.go)goto(x.go);else if(x.day!==undefined){chosenDay=Number(x.day);selectedDateOffset=0;goto('today')}else if(x.dateOffset!==undefined){selectedDateOffset=Number(x.dateOffset);chosenDay=indexAt(selectedDateOffset);goto('today')}else if(x.resetDay){selectedDateOffset=0;chosenDay=dayNum();goto('today')}else if(x.weekMove!==undefined){selectedWeek+=Number(x.weekMove);render()}else if(x.weekToday){selectedWeek=0;render()}else if(x.refresh){refreshFeed(true)}else if(x.add!==undefined){addIngredients([Number(x.add)]);alert('買い物リストに追加しました')}else if(x.addweek){addIngredients(Array.from({length:7},(_,i)=>(chosenDay+i)%30));alert('7日分の材料を追加しました')}else if(x.copy!==undefined){const i=Number(x.copy);copyText(`${title(i)}\n材料（2人分）\n${ingredients(i).join('\n')}\n作り方\n${steps(i)}`)}else if(x.delete){deals=deals.filter(d=>String(d.id)!==String(x.delete));save('deals',deals);render()}else if(x.clear==='list'){if(confirm('買い物リストを空にしますか？')){save('list',[]);checks={};save('checks',checks);render()}}else if(x.share==='list'){copyText(load('list',[]).join('\n'))}});
function addIngredients(ids){const existing=load('list',[]);const next=[...new Set([...existing,...ids.flatMap(i=>ingredients(i))])];save('list',next)}
async function copyText(s){try{if(navigator.share){await navigator.share({text:s,title:'からだ想い献立'});return}await navigator.clipboard.writeText(s);alert('コピーしました')}catch{prompt('テキストをコピーしてください',s)}}
function confirmOcrCandidate(id,values){const c=ocrCandidates().find(c=>c.id===id);const item=String(values.item||'').trim(),qty=String(values.qty||'').trim(),price=Number(values.price);if(!c||!values.confirmed||!item||item.length>95||!qty||qty.length>80||!Number.isFinite(price)||price<=0||price>20000)return false;deals.push({id:Date.now(),store:c.store,item,price,qty,until:isoToday(),ocrCandidateId:c.id,confirmedAt:isoToday(),source:c.source,method:'ocr_confirmed'});save('deals',deals);return true}
document.addEventListener('submit',e=>{const form=e.target;if(!form.dataset.ocrForm)return;e.preventDefault();if(!form.reportValidity())return;const values=new FormData(form);if(confirmOcrCandidate(form.dataset.ocrForm,{item:values.get('item'),price:values.get('price'),qty:values.get('qty'),confirmed:values.get('confirmed')==='on'}))render()});
document.addEventListener('submit',e=>{if(e.target.id!=='dealform')return;e.preventDefault();const item=document.getElementById('item').value.trim();const price=Number(document.getElementById('price').value);if(!item||!Number.isFinite(price)||price<=0)return;deals.push({id:Date.now(),store:document.getElementById('store').value,item,price,qty:document.getElementById('qty').value.trim(),until:document.getElementById('until').value});save('deals',deals);render()});
document.addEventListener('change',e=>{if(e.target.dataset.check!==undefined){const v=load('list',[])[Number(e.target.dataset.check)];checks[v]=e.target.checked;save('checks',checks);render()}else if(e.target.id==='servings'){servings=Number(e.target.value);save('servings',servings);render()}});
let installPrompt;window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;const b=document.getElementById('install');if(b)b.style.display='inline-flex'});document.addEventListener('click',e=>{if(e.target.id==='install'&&installPrompt){installPrompt.prompt();installPrompt=null}});
if('serviceWorker'in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('./sw.js').catch(()=>{});render();

async function refreshFeed(force=false){try{const r=await fetch('./data/latest.json?ts='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error(r.status);const obj=await r.json();if(!Array.isArray(obj.deals))throw Error('invalid data');remoteFeed=obj;if(force)alert('特売データを読み込みました')}catch(e){if(force)alert('更新データが取得できません。インターネット接続または公開設定を確認してください。')}render()}
refreshFeed();document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshFeed()});
