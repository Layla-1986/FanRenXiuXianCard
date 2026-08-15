const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const target = path.join(
  __dirname,
  '..',
  '.superpowers',
  'brainstorm',
  'sword-array-qingzhu-model-v5.html',
);

function readPrototype() {
  return fs.readFileSync(target, 'utf8');
}

test('models the qingzhu sword as a dimensional jade artifact', () => {
  const html = readPrototype();

  for (const token of [
    'blade-shadow-shell',
    'blade-left-plane',
    'blade-right-plane',
    'blade-center-prism',
    'blade-tip-spark',
    'bamboo-seal-ring',
    'guard-ring-thickness',
    'guard-gold-lip',
    'grip-carved-wrap',
    'pommel-gem',
    'spirit-flow',
    'sword-depth-near',
    'sword-depth-far',
  ]) {
    assert.match(html, new RegExp(token));
  }

  assert.match(html, /viewBox="0 0 38 124"/);
  assert.match(html, /width:14px; height:52px/);
  assert.doesNotMatch(html, /\\.core-dot \\{\\s*\\.core-dot \\{/);
});

test('preserves the approved circular sword array behavior', () => {
  const html = readPrototype();

  assert.match(html, /animation:swordOrbit 20s linear infinite/);
  assert.match(html, /Math\.max\(1,Math\.round\(remain\/10\)\)/);
  assert.match(html, /i\*360\/count/);
  assert.match(html, /const phase=i\/count/);
  assert.match(html, /sword-depth-near/);
  assert.match(html, /sword-depth-far/);
  assert.doesNotMatch(html, /\$\\\{/);
  assert.match(html, /data-remain="80"/);
  assert.match(html, /data-remain="50"/);
  assert.match(html, /data-remain="20"/);
  assert.match(html, /data-remain="100"/);
  assert.match(html, /@media\(prefers-reduced-motion:reduce\)\{[^}]*\.spirit-flow\{animation:none[^}]*\}/);
});
