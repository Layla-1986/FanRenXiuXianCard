const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const root = path.resolve(__dirname, '..');
execFileSync('python', [path.join(root, 'scripts', 'build-formal-v1.py')], { cwd: root });

const html = fs.readFileSync(path.join(root, 'quota-card-app.html'), 'utf8');
const runtime = require(path.join(root, 'scripts', 'quota-card-app.js'));

assert.match(html, /id="drag-surface" class="pywebview-drag-region"/);
assert.match(html, /\.drag-surface\{position:absolute;inset:0;z-index:10/);
assert.match(html, /\.pages>\.page-switch\{right:49px;top:15px\}/);
assert.match(html, /id="page-switch"/);
assert.match(html, /id="lock-button"/);
assert.ok(html.indexOf('id="drag-surface"') < html.indexOf('id="page-switch"'));
assert.match(fs.readFileSync(path.join(root, 'scripts', 'quota-card-app.js'), 'utf8'), /bridge\('begin_drag'\)/);
assert.doesNotMatch(html, /正式版第一稿 · 示例数据/);
assert.doesNotMatch(html, /<h1>凡人 · 额度图卷<\/h1>/);
for (const id of [
  'weeklyPercent', 'fiveHourPercent', 'fiveHourReset', 'weeklyUsed', 'weeklyReset',
  'creditBalance', 'resetCreditExpiry', 'agCredits', 'agGeminiWeekly',
  'agGeminiFiveHour', 'agClaudeWeekly', 'agClaudeFiveHour'
]) assert.ok(html.includes(`id=&quot;${id}&quot;`), id);

assert.equal(runtime.percent(null), '—');
assert.equal(runtime.percent(0), '0%');
assert.equal(runtime.percent(100), '100%');
assert.equal(runtime.percent(Number.NaN), '—');
assert.equal(runtime.usdFromPoints('2500'), '$100.00');
assert.equal(runtime.usdFromPoints(null), '—');
assert.equal(runtime.resetCreditLabel({ availableResetCount: null }), '重置卡信息待同步');
assert.equal(runtime.resetCreditLabel({ availableResetCount: 0 }), '暂无可用重置卡');

console.log('quota-card-app: 1 test passed');
