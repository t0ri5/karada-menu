const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('app.js','utf8').split("if('serviceWorker'")[0];
const saved = new Map();
const context = vm.createContext({
  Date, URL, console,
  document:{addEventListener(){}},
  window:{addEventListener(){}},
  localStorage:{getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,v)},
});
vm.runInContext(source,context);
vm.runInContext(`
  const testCandidate={id:'candidate-1',store:'olympic',item:'長ねぎ2本',price:171.72,
    qty:'2本',status:'needs_confirmation',observed_at:isoToday()};
  remoteFeed={updated_at:isoToday(),deals:[],ocr_candidates:[testCandidate]};
`,context);
const run=code=>vm.runInContext(code,context);
assert.equal(run('activeDeals().length'),0,'Unconfirmed OCR must not affect meals');
assert.equal(run("confirmOcrCandidate('candidate-1',{item:'長ねぎ',price:171.72,qty:'2本',confirmed:false})"),false);
assert.equal(run('deals.length'),0);
assert.equal(run("confirmOcrCandidate('candidate-1',{item:'長ねぎ',price:171.72,qty:'',confirmed:true})"),false);
assert.equal(run("confirmOcrCandidate('candidate-1',{item:'長ねぎ',price:171.72,qty:'2本',confirmed:true})"),true);
assert.equal(run('deals[0].price'),171.72);
assert.equal(run('deals[0].until===isoToday()'),true);
assert.equal(run('ocrCandidates().length'),0,'Confirmed candidates must not be added twice');
assert.equal(run('activeDeals().length'),1);
run("remoteFeed.updated_at='2000-01-01';deals=[]");
assert.equal(run('ocrCandidates().length'),0,'Stale OCR data must be hidden');
assert.equal(run("confirmOcrCandidate('candidate-1',{item:'長ねぎ',price:171.72,qty:'2本',confirmed:true})"),false);
assert.equal(run("safeOcrImageUrl('javascript:alert(1)')"),'');
assert.equal(run("safeOcrImageUrl('https://attacker.test/image.jpg')"),'');
console.log('OCR review UI checks passed');
