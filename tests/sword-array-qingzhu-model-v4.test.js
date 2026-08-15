const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const target = path.join(
  __dirname,
  '..',
  '.superpowers',
  'brainstorm',
  'sword-array-qingzhu-model-v4.html',
);

function readPrototype() {
  return fs.readFileSync(target, 'utf8');
}

test('renders the reference sword as a broad bamboo-jointed jade weapon', () => {
  const html = readPrototype();

  for (const token of [
    'blade-gold-inlay',
    'bamboo-joint',
    'guard-collar',
    'grip-wrap',
    'pommel-cap',
  ]) {
    assert.match(html, new RegExp(token));
  }

  assert.match(html, /viewBox="0 0 30 112"/);
  assert.match(html, /width:12px; height:46px/);
  assert.match(html, /setAttribute\('viewBox','0 0 30 112'\)/);
});

test('changes only the sword model and preserves the approved formation', () => {
  const html = readPrototype();

  assert.match(html, /animation:swordOrbit 20s linear infinite/);
  assert.match(html, /Math\.max\(1,Math\.round\(remain\/10\)\)/);
  assert.match(html, /i\*360\/count/);
  assert.match(
    html,
    /@media\(prefers-reduced-motion:reduce\)\{\.ring,\.runes,\.sword-orbit\{animation:none\}\}/,
  );
});
