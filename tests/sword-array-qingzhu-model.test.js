const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const target = path.join(
  __dirname,
  '..',
  '.superpowers',
  'brainstorm',
  'sword-array-qingzhu-model-v3.html',
);

function readPrototype() {
  return fs.readFileSync(target, 'utf8');
}

test('models a layered shared qingzhu sword glyph', () => {
  const html = readPrototype();

  for (const token of [
    'qingzhu-sword-glyph',
    'blade-core',
    'blade-edge',
    'blade-ridge',
    'sword-guard',
    'sword-grip',
  ]) {
    assert.match(html, new RegExp(token));
  }

  assert.match(html, /className='qingzhu-sword'/);
  assert.match(html, /setAttribute\('href','#qingzhu-sword-glyph'\)/);
});

test('preserves the original formation behavior', () => {
  const html = readPrototype();

  assert.match(html, /animation:swordOrbit 20s linear infinite/);
  assert.match(html, /Math\.max\(1,Math\.round\(remain\/10\)\)/);
  assert.match(html, /i\*360\/count/);
  assert.match(html, /width:10px; height:42px/);
  assert.match(
    html,
    /@media\(prefers-reduced-motion:reduce\)\{\.ring,\.runes,\.sword-orbit\{animation:none\}\}/,
  );
});
