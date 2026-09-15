'use strict';

const widget = document.querySelector('#widget');
const percent = document.querySelector('#percent');
const usedLabel = document.querySelector('#used');
const resetAt = document.querySelector('#resetAt');
const balance = document.querySelector('#balance');
const syncStatus = document.querySelector('#syncStatus');
const stateButtons = [...document.querySelectorAll('[data-remain]')];
const unlockButton = document.querySelector('#unlockButton');
const antigravityToggle = document.querySelector('#antigravityToggle');
const antigravityPage = document.querySelector('.antigravity-page');
const POINTS_PER_USD = 25;

const visualAnchors = [
  { at: 0, moon: .52, moonColor: '#806157', quotaTop: '#D5B564', quotaMid: '#A85B45', quotaBottom: '#6F3B31', primary: '#A85B45', secondary: '#76513E', accent: '#B47A4B', ember: '#7C352D', opacity: .46 },
  { at: 20, moon: .64, moonColor: '#B98B69', quotaTop: '#E8C98A', quotaMid: '#F0A94A', quotaBottom: '#A85B45', primary: '#F0A94A', secondary: '#B9794B', accent: '#D49A58', ember: '#A85B45', opacity: .62 },
  { at: 50, moon: .84, moonColor: '#DEC99D', quotaTop: '#EDF1D9', quotaMid: '#D5B564', quotaBottom: '#F0A94A', primary: '#D5B564', secondary: '#8FBA72', accent: '#E6C56A', ember: '#F0A94A', opacity: .78 },
  { at: 80, moon: 1.03, moonColor: '#D8F3EB', quotaTop: '#EDF9ED', quotaMid: '#78DDBF', quotaBottom: '#D5B564', primary: '#78DDBF', secondary: '#59D99D', accent: '#D5B564', ember: '#F0A94A', opacity: .9 },
  { at: 100, moon: 1.18, moonColor: '#EDF9ED', quotaTop: '#FFFFFF', quotaMid: '#71E2DC', quotaBottom: '#59D99D', primary: '#71E2DC', secondary: '#59D99D', accent: '#D5B564', ember: '#F0A94A', opacity: 1 }
];

const antigravityFields = {
  geminiWeekly: document.querySelector('#agGeminiWeekly'),
  geminiWeeklyReset: document.querySelector('#agGeminiWeeklyReset'),
  geminiFiveHour: document.querySelector('#agGeminiFiveHour'),
  geminiFiveHourReset: document.querySelector('#agGeminiFiveHourReset'),
  claudeWeekly: document.querySelector('#agClaudeWeekly'),
  claudeWeeklyReset: document.querySelector('#agClaudeWeeklyReset'),
  claudeFiveHour: document.querySelector('#agClaudeFiveHour'),
  claudeFiveHourReset: document.querySelector('#agClaudeFiveHourReset'),
  status: document.querySelector('#agSyncStatus'),
  syncedAt: document.querySelector('#agSyncedAt')
};

const STATUS_COPY = { fresh: '已同步', pending: '待同步', stale: '同步已滞后', expired: '数据已过期' };
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const hexToRgb = (hex) => hex.match(/[\da-f]{2}/gi).map((channel) => parseInt(channel, 16));
const mixHex = (from, to, progress) => '#' + hexToRgb(from).map((channel, index) => Math.round(channel + (hexToRgb(to)[index] - channel) * progress).toString(16).padStart(2, '0')).join('').toUpperCase();
const compact = (value) => String(Number(value.toFixed(3))).replace(/^0(?=\.)/, '');

function visualStateFor(remain) {
  const value = clamp(Number(remain) || 0, 0, 100);
  const upper = visualAnchors.find((anchor) => anchor.at >= value) || visualAnchors.at(-1);
  const lower = [...visualAnchors].reverse().find((anchor) => anchor.at <= value) || visualAnchors[0];
  const progress = upper.at === lower.at ? 0 : (value - lower.at) / (upper.at - lower.at);
  const mixNumber = (key) => lower[key] + (upper[key] - lower[key]) * progress;
  const mixColor = (key) => mixHex(lower[key], upper[key], progress);
  const moonFloor = visualAnchors.find((anchor) => anchor.at === 50);
  const moonIsFloored = value < moonFloor.at;
  return {
    value,
    moonEnergy: Math.max(value, moonFloor.at) / 100,
    moon: moonIsFloored ? moonFloor.moon : mixNumber('moon'),
    moonColor: moonIsFloored ? moonFloor.moonColor : mixColor('moonColor'),
    quotaTop: mixColor('quotaTop'),
    quotaMid: mixColor('quotaMid'),
    quotaBottom: mixColor('quotaBottom'),
    primary: mixColor('primary'),
    secondary: mixColor('secondary'),
    accent: mixColor('accent'),
    ember: mixColor('ember'),
    opacity: mixNumber('opacity')
  };
}

function renderRemaining(remain) {
  if (!widget || !percent || !usedLabel) return;
  const state = visualStateFor(remain);
  const shown = Math.round(state.value);
  const variables = {
    '--energy': compact(state.value / 100),
    '--moon-energy': compact(state.moonEnergy),
    '--moon-strength': compact(state.moon),
    '--moon-color': state.moonColor,
    '--quota-top': state.quotaTop,
    '--quota-mid': state.quotaMid,
    '--quota-bottom': state.quotaBottom,
    '--formation-primary': state.primary,
    '--formation-secondary': state.secondary,
    '--formation-accent': state.accent,
    '--formation-ember': state.ember,
    '--formation-opacity': compact(state.opacity)
  };
  Object.entries(variables).forEach(([name, value]) => widget.style.setProperty(name, value));
  widget.dataset.energyState = state.value >= 90 ? 'full' : state.value >= 65 ? 'stable' : state.value >= 35 ? 'waning' : state.value > 0 ? 'fading' : 'depleted';
  widget.setAttribute('aria-label', 'Codex 用量法宝封印图卷，七日余量 ' + shown + '%，已用 ' + (100 - shown) + '%');
  percent.textContent = shown + '%';
  usedLabel.textContent = '已用 ' + (100 - shown) + '%';
  stateButtons.forEach((button) => {
    const isCurrent = Number(button.dataset.remain) === state.value;
    button.classList.toggle('active', isCurrent);
    button.setAttribute('aria-pressed', String(isCurrent));
  });
}

function setUsed(value) {
  const numeric = Number.isFinite(Number(value)) ? Number(value) : 0;
  renderRemaining((1 - clamp(numeric, 0, 1)) * 100);
}

function formatPointBalance(value) {
  const points = Number(value);
  return Number.isFinite(points) && points >= 0 ? 'US$' + (points / POINTS_PER_USD).toFixed(2) : null;
}

function formatCodexReset(value) {
  const milliseconds = Number(value) * 1000;
  if (!Number.isFinite(milliseconds)) return '重置时间待定';
  const date = new Date(milliseconds);
  return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' }) + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' 重置';
}

function setCodexSyncStatus(status) {
  if (!syncStatus) return;
  syncStatus.dataset.state = status === 'fresh' ? 'live' : status === 'stale' ? 'stale' : status === 'preview' ? 'preview' : 'offline';
  syncStatus.textContent = status === 'fresh' ? '实时' : status === 'stale' ? '数据暂缓' : status === 'preview' ? '演示' : '等待服务';
}

let manualPreview = false;
async function fetchCodexQuota() {
  if (manualPreview) return;
  try {
    const response = await fetch('/api/codex-quota', { cache: 'no-store' });
    if (!response.ok) throw new Error('quota unavailable');
    const payload = await response.json();
    if (Number.isFinite(payload.remainingPercent)) renderRemaining(payload.remainingPercent);
    if (payload.resetsAt != null && resetAt) resetAt.textContent = formatCodexReset(payload.resetsAt);
    const dollarBalance = formatPointBalance(payload.creditBalance);
    if (dollarBalance && balance) balance.textContent = dollarBalance;
    setCodexSyncStatus(payload.status);
  } catch (_error) {
    setCodexSyncStatus('offline');
  }
}

function isMissingValue(value) {
  return value == null || (typeof value === 'string' && value.trim() === '');
}

function formatQuota(value, expired = false) {
  if (expired || isMissingValue(value)) return '—';
  const numeric = Number(value);
  return Number.isFinite(numeric) ? Math.min(100, Math.max(0, Math.round(numeric))) + '%' : '—';
}

function formatReset(value, expired = false) {
  if (expired || isMissingValue(value)) return '待同步';
  const safe = String(value).trim().slice(0, 32)
    .replace(/days?/gi, '天').replace(/hours?/gi, '时').replace(/minutes?/gi, '分')
    .replace(/\s*,\s*/g, '').replace(/\s+/g, '');
  return safe.endsWith('重置') ? safe : safe + '重置';
}

function formatSyncTime(value) {
  if (isMissingValue(value)) return '请打开 Models 页同步';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '请打开 Models 页同步';
  return '同步于 ' + new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).format(date);
}

function renderAntigravityQuota(payload = {}) {
  const status = ['fresh', 'pending', 'stale', 'expired'].includes(payload.status) ? payload.status : 'pending';
  const expired = status === 'expired';
  const values = {
    geminiWeekly: formatQuota(payload.gemini?.weeklyRemaining, expired),
    geminiWeeklyReset: formatReset(payload.gemini?.weeklyReset, expired),
    geminiFiveHour: formatQuota(payload.gemini?.fiveHourRemaining, expired),
    geminiFiveHourReset: formatReset(payload.gemini?.fiveHourReset, expired),
    claudeWeekly: formatQuota(payload.claudeGpt?.weeklyRemaining, expired),
    claudeWeeklyReset: formatReset(payload.claudeGpt?.weeklyReset, expired),
    claudeFiveHour: formatQuota(payload.claudeGpt?.fiveHourRemaining, expired),
    claudeFiveHourReset: formatReset(payload.claudeGpt?.fiveHourReset, expired)
  };
  Object.entries(values).forEach(([key, value]) => {
    if (antigravityFields[key]) antigravityFields[key].textContent = value;
  });
  if (antigravityFields.status) antigravityFields.status.textContent = STATUS_COPY[status];
  if (antigravityFields.syncedAt) antigravityFields.syncedAt.textContent = expired ? '请打开 Models 页同步' : formatSyncTime(payload.syncedAt);
  if (antigravityPage) antigravityPage.dataset.syncStatus = status;
}

async function fetchAntigravityQuota() {
  try {
    const response = await fetch('/api/antigravity-quota', { cache: 'no-store' });
    if (!response.ok) throw new Error('quota unavailable');
    renderAntigravityQuota(await response.json());
  } catch (_error) {
    renderAntigravityQuota({ status: 'pending' });
  }
}

function showCardPage(page, remember = true) {
  if (!widget) return;
  page = page === 'antigravity' ? 'antigravity' : 'codex';
  widget.dataset.page = page;
  const isAntigravity = page === 'antigravity';
  if (antigravityToggle) {
    antigravityToggle.setAttribute('aria-pressed', String(isAntigravity));
    antigravityToggle.setAttribute('aria-label', isAntigravity ? '返回 Codex 额度' : '查看反重力额度');
  }
  if (antigravityPage) antigravityPage.setAttribute('aria-hidden', String(!isAntigravity));
  if (remember) {
    try { sessionStorage.setItem('quota-card-page', page); } catch (_error) { /* storage can be disabled */ }
  }
  if (isAntigravity) fetchAntigravityQuota();
}

stateButtons.forEach((button) => {
  button.addEventListener('click', () => {
    manualPreview = true;
    setCodexSyncStatus('preview');
    renderRemaining(Number(button.dataset.remain));
  });
});

if (unlockButton) {
  unlockButton.addEventListener('click', () => {
    const unlocked = unlockButton.getAttribute('aria-pressed') !== 'true';
    unlockButton.setAttribute('aria-pressed', String(unlocked));
    unlockButton.classList.toggle('is-unlocked', unlocked);
    unlockButton.setAttribute('aria-label', unlocked ? '锁定悬浮窗' : '解锁悬浮窗');
  });
}

if (antigravityToggle) {
  antigravityToggle.addEventListener('click', () => {
    showCardPage(widget?.dataset.page === 'antigravity' ? 'codex' : 'antigravity');
  });
}

window.setUsed = setUsed;
window.visualStateFor = visualStateFor;
window.renderAntigravityQuota = renderAntigravityQuota;
window.fetchCodexQuota = fetchCodexQuota;
renderRemaining(80);
let initialPage = 'codex';
try { initialPage = sessionStorage.getItem('quota-card-page') || 'codex'; } catch (_error) { /* default Codex */ }
showCardPage(initialPage, false);
fetchCodexQuota();
fetchAntigravityQuota();
window.setInterval(fetchCodexQuota, 15000);
window.setInterval(fetchAntigravityQuota, 60000);
