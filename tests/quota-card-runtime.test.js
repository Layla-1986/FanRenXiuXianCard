'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const scriptPath = path.join(__dirname, '..', 'scripts', 'quota-card.js');
const source = fs.readFileSync(scriptPath, 'utf8');
const syncAdvice = '\u8bf7\u6253\u5f00 Models \u9875\u540c\u6b65';

function createElement() {
  const listeners = new Map();
  const attributes = new Map();
  const classes = new Set();
  return {
    attributes,
    classList: {
      toggle(name, force) {
        if (force) classes.add(name); else classes.delete(name);
      }
    },
    dataset: {},
    style: { setProperty() {} },
    textContent: '',
    addEventListener(type, listener) { listeners.set(type, listener); },
    click() { listeners.get('click')?.(); },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    setAttribute(name, value) { attributes.set(name, String(value)); }
  };
}

function createStorage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); }
  };
}

async function flushAsyncWork() {
  await Promise.resolve();
  await Promise.resolve();
}

async function loadQuotaCard({ storage = createStorage(), fetchImpl = async () => ({ ok: true, json: async () => ({ status: 'fresh' }) }) } = {}) {
  const elements = {
    widget: createElement(),
    percent: createElement(),
    used: createElement(),
    unlockButton: createElement(),
    antigravityToggle: createElement(),
    antigravityPage: createElement(),
    agCredits: createElement(),
    agGeminiWeekly: createElement(),
    agGeminiFiveHour: createElement(),
    agClaudeWeekly: createElement(),
    agClaudeFiveHour: createElement(),
    agSyncStatus: createElement(),
    agSyncedAt: createElement()
  };
  const swords = Array.from({ length: 12 }, createElement);
  const states = ['.2', '.55', '.85'].map((used) => Object.assign(createElement(), { dataset: { used } }));
  const selectors = new Map([
    ['#widget', elements.widget], ['#percent', elements.percent], ['#used', elements.used],
    ['#unlockButton', elements.unlockButton], ['#antigravityToggle', elements.antigravityToggle],
    ['.antigravity-page', elements.antigravityPage], ['#agCredits', elements.agCredits],
    ['#agGeminiWeekly', elements.agGeminiWeekly], ['#agGeminiFiveHour', elements.agGeminiFiveHour],
    ['#agClaudeWeekly', elements.agClaudeWeekly], ['#agClaudeFiveHour', elements.agClaudeFiveHour],
    ['#agSyncStatus', elements.agSyncStatus], ['#agSyncedAt', elements.agSyncedAt]
  ]);
  const sandbox = {
    Intl,
    Date,
    Promise,
    console,
    fetch: fetchImpl,
    sessionStorage: storage,
    document: {
      querySelector(selector) { return selectors.get(selector) || null; },
      querySelectorAll(selector) {
        if (selector === '.formation-sword') return swords;
        if (selector === '[data-used]') return states;
        return [];
      }
    },
    setInterval() { return 1; }
  };
  sandbox.window = sandbox;
  vm.runInNewContext(source, sandbox, { filename: scriptPath });
  await flushAsyncWork();
  return { elements, storage, window: sandbox };
}

async function testPageSwitchAndSessionRestore() {
  const storage = createStorage();
  const first = await loadQuotaCard({ storage });
  assert.equal(first.elements.widget.dataset.page, 'codex');

  first.elements.antigravityToggle.click();
  await flushAsyncWork();
  assert.equal(first.elements.widget.dataset.page, 'antigravity');
  assert.equal(storage.getItem('quota-card-page'), 'antigravity');
  assert.equal(first.elements.antigravityToggle.getAttribute('aria-pressed'), 'true');
  assert.equal(first.elements.antigravityPage.getAttribute('aria-hidden'), 'false');

  const restored = await loadQuotaCard({ storage });
  assert.equal(restored.elements.widget.dataset.page, 'antigravity');
  assert.equal(restored.elements.antigravityToggle.getAttribute('aria-pressed'), 'true');
}

async function testFetchFailureRendersPendingWithoutNaN() {
  const runtime = await loadQuotaCard({ fetchImpl: async () => { throw new Error('offline'); } });
  assert.equal(runtime.elements.agSyncStatus.textContent, '\u5f85\u540c\u6b65');
  assert.equal(runtime.elements.agCredits.textContent, '\u2014');
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);
  assert.equal(Object.values(runtime.elements).some((element) => String(element.textContent).includes('NaN')), false);
}

async function testMissingValuesStayUnavailableInsteadOfZeroOrEpoch() {
  const runtime = await loadQuotaCard();
  runtime.window.renderAntigravityQuota({
    status: 'fresh',
    aiCredits: null,
    gemini: { weeklyRemaining: '', fiveHourRemaining: null },
    claudeGpt: { weeklyRemaining: undefined, fiveHourRemaining: '' },
    syncedAt: null
  });
  assert.equal(runtime.elements.agSyncStatus.textContent, '\u5df2\u540c\u6b65');
  for (const key of ['agCredits', 'agGeminiWeekly', 'agGeminiFiveHour', 'agClaudeWeekly', 'agClaudeFiveHour']) {
    assert.equal(runtime.elements[key].textContent, '\u2014', `${key} must be unavailable`);
  }
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);

  runtime.window.renderAntigravityQuota({ status: 'fresh', syncedAt: 'not-a-timestamp' });
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);
}

async function testStaleAndExpiredHaveDistinctAccessibleOutcomes() {
  const runtime = await loadQuotaCard();
  runtime.window.renderAntigravityQuota({
    status: 'stale', aiCredits: 12, gemini: { weeklyRemaining: 42, fiveHourRemaining: 36 },
    claudeGpt: { weeklyRemaining: 24, fiveHourRemaining: 18 }, syncedAt: '2026-08-13T08:00:00Z'
  });
  assert.equal(runtime.elements.agSyncStatus.textContent, '\u540c\u6b65\u5df2\u6ede\u540e');
  assert.equal(runtime.elements.agGeminiWeekly.textContent, '42%');

  runtime.window.renderAntigravityQuota({ status: 'expired' });
  assert.equal(runtime.elements.agSyncStatus.textContent, '\u6570\u636e\u5df2\u8fc7\u671f');
  assert.equal(runtime.elements.agCredits.textContent, '\u2014');
  assert.equal(runtime.elements.agGeminiWeekly.textContent, '\u2014');
  assert.equal(runtime.elements.agClaudeFiveHour.textContent, '\u2014');
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);
}

const tests = [
  ['page switching and session restoration', testPageSwitchAndSessionRestore],
  ['fetch failure renders a safe pending state', testFetchFailureRendersPendingWithoutNaN],
  ['null, empty, and invalid API values remain unavailable', testMissingValuesStayUnavailableInsteadOfZeroOrEpoch],
  ['stale and expired have distinct user-visible outcomes', testStaleAndExpiredHaveDistinctAccessibleOutcomes]
];

(async () => {
  for (const [name, test] of tests) {
    await test();
    console.log(`PASS: ${name}`);
  }
})().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
