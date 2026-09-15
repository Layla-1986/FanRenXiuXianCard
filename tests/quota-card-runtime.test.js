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
  await new Promise((resolve) => setImmediate(resolve));
}

async function loadQuotaCard({ storage = createStorage(), fetchImpl } = {}) {
  const fetchCalls = [];
  const intervals = [];
  const defaultFetch = async (url) => ({
    ok: true,
    json: async () => url === '/api/codex-quota'
      ? { status: 'fresh', remainingPercent: 80, usedPercent: 20, resetsAt: 1787897582, creditBalance: 984.94351 }
      : { status: 'fresh' }
  });
  const request = async (...args) => {
    fetchCalls.push(args);
    return (fetchImpl || defaultFetch)(...args);
  };
  const elements = {
    widget: createElement(),
    percent: createElement(),
    used: createElement(),
    resetAt: createElement(),
    balance: createElement(),
    syncStatus: createElement(),
    unlockButton: createElement(),
    antigravityToggle: createElement(),
    antigravityPage: createElement(),
    agGeminiWeekly: createElement(),
    agGeminiWeeklyReset: createElement(),
    agGeminiFiveHour: createElement(),
    agGeminiFiveHourReset: createElement(),
    agClaudeWeekly: createElement(),
    agClaudeWeeklyReset: createElement(),
    agClaudeFiveHour: createElement(),
    agClaudeFiveHourReset: createElement(),
    agSyncStatus: createElement(),
    agSyncedAt: createElement()
  };
  const states = ['80', '50', '20', '100'].map((remain) => Object.assign(createElement(), { dataset: { remain } }));
  const selectors = new Map([
    ['#widget', elements.widget], ['#percent', elements.percent], ['#used', elements.used],
    ['#resetAt', elements.resetAt], ['#balance', elements.balance], ['#syncStatus', elements.syncStatus],
    ['#unlockButton', elements.unlockButton], ['#antigravityToggle', elements.antigravityToggle],
    ['.antigravity-page', elements.antigravityPage],
    ['#agGeminiWeekly', elements.agGeminiWeekly], ['#agGeminiFiveHour', elements.agGeminiFiveHour],
    ['#agGeminiWeeklyReset', elements.agGeminiWeeklyReset], ['#agGeminiFiveHourReset', elements.agGeminiFiveHourReset],
    ['#agClaudeWeekly', elements.agClaudeWeekly], ['#agClaudeFiveHour', elements.agClaudeFiveHour],
    ['#agClaudeWeeklyReset', elements.agClaudeWeeklyReset], ['#agClaudeFiveHourReset', elements.agClaudeFiveHourReset],
    ['#agSyncStatus', elements.agSyncStatus], ['#agSyncedAt', elements.agSyncedAt]
  ]);
  const sandbox = {
    Intl,
    Date,
    Promise,
    console,
    fetch: request,
    sessionStorage: storage,
    document: {
      querySelector(selector) { return selectors.get(selector) || null; },
      querySelectorAll(selector) {
        if (selector === '[data-remain]') return states;
        return [];
      }
    },
    setInterval(callback, milliseconds) { intervals.push({ callback, milliseconds }); return intervals.length; }
  };
  sandbox.window = sandbox;
  vm.runInNewContext(source, sandbox, { filename: scriptPath });
  await flushAsyncWork();
  return { elements, fetchCalls, intervals, storage, window: sandbox };
}

async function testCodexQuotaUsesReferenceVisualAndLiveDataContract() {
  const runtime = await loadQuotaCard();
  assert.equal(runtime.elements.percent.textContent, '80%');
  assert.equal(runtime.elements.used.textContent, '已用 20%');
  assert.equal(runtime.elements.balance.textContent, 'US$39.40');
  assert.match(runtime.elements.resetAt.textContent, /重置$/);
  assert.equal(runtime.elements.syncStatus.textContent, '实时');
  assert.equal(runtime.fetchCalls.some(([url]) => url === '/api/codex-quota'), true);
  assert.equal(runtime.intervals.some(({ milliseconds }) => milliseconds === 15000), true);

  runtime.window.setUsed(.5);
  assert.equal(runtime.elements.percent.textContent, '50%');
  assert.equal(runtime.elements.used.textContent, '已用 50%');
  assert.equal(runtime.elements.widget.dataset.energyState, 'waning');
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
  assert.equal(runtime.elements.agGeminiWeeklyReset.textContent, '\u5f85\u540c\u6b65');
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
  for (const key of ['agGeminiWeekly', 'agGeminiFiveHour', 'agClaudeWeekly', 'agClaudeFiveHour']) {
    assert.equal(runtime.elements[key].textContent, '\u2014', `${key} must be unavailable`);
  }
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);

  runtime.window.renderAntigravityQuota({
    status: 'fresh',
    gemini: { weeklyReset: '5天5时', fiveHourReset: '2时18分' },
    claudeGpt: { weeklyReset: '5天4时', fiveHourReset: '1时42分' }
  });
  assert.equal(runtime.elements.agGeminiWeeklyReset.textContent, '5天5时重置');
  assert.equal(runtime.elements.agClaudeFiveHourReset.textContent, '1时42分重置');

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
  assert.equal(runtime.elements.agGeminiWeekly.textContent, '\u2014');
  assert.equal(runtime.elements.agClaudeFiveHour.textContent, '\u2014');
  assert.equal(runtime.elements.agSyncedAt.textContent, syncAdvice);
}

const tests = [
  ['Codex page preserves the co-branded live quota contract', testCodexQuotaUsesReferenceVisualAndLiveDataContract],
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
