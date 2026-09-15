const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
execFileSync('python', [path.join(root, 'scripts', 'build-formal-v1.py')], {
  cwd: root,
  stdio: 'pipe',
});

const artifact = fs.readFileSync(path.join(root, 'quota-card-formal-v1.html'), 'utf8');
const script = artifact.match(/<script>([\s\S]*?)<\/script>/)[1];
const documents = JSON.parse(script.match(/const documents = (.*);/)[1]);
const codexPage = documents[0];

function finalDeclarations(selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const matches = [...codexPage.matchAll(new RegExp(`${escaped}\\s*\\{([^}]+)\\}`, 'g'))];
  return matches.at(-1)?.[1] ?? '';
}

const motto = finalDeclarations('.five-hour-concept .motto');
const frame = finalDeclarations('.five-hour-concept .motto::before');

assert.match(motto, /background\s*:\s*none/, '题字本体不应再绘制第二层色带');
assert.match(motto, /box-shadow\s*:\s*none/, '题字本体不应再绘制第二层框线');
assert.match(frame, /border-top\s*:\s*1px/, '单层外框应保留上沿');
assert.match(frame, /border-bottom\s*:\s*1px/, '单层外框应保留下沿');

console.log('PASS: Codex bottom motto renders one visual frame');
