const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const target = path.join(
  __dirname,
  '..',
  '.superpowers',
  'brainstorm',
  'sword-array-qingzhu-model-v6.html',
);

function readPrototype() {
  return fs.readFileSync(target, 'utf8');
}

test('poses qingzhu swords as perspective flying swords instead of flat stickers', () => {
  const html = readPrototype();

  for (const token of [
    'sword-depth-front',
    'sword-depth-mid',
    'sword-depth-back',
    '--tilt',
    '--pitch',
    '--zscale',
    '--sweep',
    'perspective\\(260px\\)',
    'rotateX\\(var\\(--pitch\\)\\)',
    'rotateZ\\(var\\(--tilt\\)\\)',
    'array-perspective-ellipse',
    'sword-tail-ghost',
    'sword-floor-shadow',
  ]) {
    assert.match(html, new RegExp(token));
  }

  assert.doesNotMatch(html, /transform:rotate\(var\(--a\)\); transform-origin/);
});

test('keeps the approved circular quantity logic while adding per-sword perspective', () => {
  const html = readPrototype();

  assert.match(html, /Math\.max\(1,Math\.round\(remain\/10\)\)/);
  assert.match(html, /const angle=i\*360\/count/);
  assert.match(html, /sword\.style\.setProperty\('--a',angle\+'deg'\)/);
  assert.match(html, /sword\.style\.setProperty\('--tilt',tilt\+'deg'\)/);
  assert.match(html, /sword\.style\.setProperty\('--pitch',pitch\+'deg'\)/);
  assert.match(html, /sword\.style\.setProperty\('--zscale',zscale\)/);
  assert.match(html, /phaseY=Math\.sin/);
  assert.match(html, /data-remain="80"/);
  assert.match(html, /data-remain="50"/);
  assert.match(html, /data-remain="20"/);
  assert.match(html, /data-remain="100"/);
  assert.match(html, /@media\(prefers-reduced-motion:reduce\)\{[^}]*\.spirit-flow\{animation:none[^}]*\}/);
});
