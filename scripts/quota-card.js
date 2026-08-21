'use strict';

const widget = document.querySelector('#widget');
const percent = document.querySelector('#percent');
const usedLabel = document.querySelector('#used');
const swords = [...document.querySelectorAll('.formation-sword')];
const swordPairs = [[5, 6], [4, 7], [3, 8], [2, 9], [1, 10], [0, 11]];
const stateButtons = [...document.querySelectorAll('[data-used]')];
const unlockButton = document.querySelector('#unlockButton');
const antigravityToggle = document.querySelector('#antigravityToggle');
const antigravityPage = document.querySelector('.antigravity-page');
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

const STATUS_COPY = {
  fresh: '已同步',
  pending: '待同步',
  stale: '同步已滞后',
  expired: '数据已过期'
};

function isMissingValue(value) {
  return value == null || (typeof value === 'string' && value.trim() === '');
}

function formatQuota(value, expired = false) {
  if (expired || isMissingValue(value)) return '—';
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${Math.min(100, Math.max(0, Math.round(numeric)))}%` : '—';
}

function formatReset(value, expired = false) {
  if (expired || isMissingValue(value)) return '待同步';
  const safe = String(value).trim().slice(0, 32)
    .replace(/days?/gi, '天').replace(/hours?/gi, '时').replace(/minutes?/gi, '分')
    .replace(/\s*,\s*/g, '').replace(/\s+/g, '');
  return safe.endsWith('重置') ? safe : `${safe}重置`;
}

function formatSyncTime(value) {
  if (isMissingValue(value)) return '请打开 Models 页同步';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '请打开 Models 页同步';
  return `同步于 ${new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).format(date)}`;
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
    try { sessionStorage.setItem('quota-card-page', page); } catch (_error) { /* session storage can be disabled */ }
  }
  if (isAntigravity) fetchAntigravityQuota();
}

function setUsed(value) {
  const numeric = Number.isFinite(Number(value)) ? Number(value) : 0;
  const used = Math.min(1, Math.max(0, numeric));
  const remaining = 1 - used;
  const usedPercent = Math.round(used * 100);
  const remainingPercent = 100 - usedPercent;
  const pairEnergy = remaining * swordPairs.length;
  const swordEnergy = Array(swords.length).fill(0);

  swordPairs.forEach((pair, pairIndex) => {
    const energy = Math.min(1, Math.max(0, pairEnergy - pairIndex));
    pair.forEach((swordIndex) => { swordEnergy[swordIndex] = energy; });
  });

  if (!widget || !percent || !usedLabel) return;

  widget.style.setProperty('--used', used.toFixed(4));
  widget.dataset.usedState = usedPercent >= 70 ? 'danger' : usedPercent >= 40 ? 'warning' : 'calm';
  widget.dataset.litSwords = String(swordEnergy.filter((energy) => energy > 0).length);
  widget.setAttribute('aria-label', `Codex 用量法宝封印图卷，七日余量 ${remainingPercent}%，已用 ${usedPercent}%`);

  percent.textContent = `${remainingPercent}%`;
  usedLabel.textContent = `已用 ${usedPercent}%`;
  swords.forEach((sword, index) => {
    const energy = swordEnergy[index] ?? 0;
    sword.style.setProperty('--sword-energy', energy.toFixed(3));
    sword.classList.toggle('is-lit', energy > 0);
  });

  stateButtons.forEach((button) => {
    const isCurrent = Math.abs(Number(button.dataset.used) - used) < .0001;
    button.classList.toggle('active', isCurrent);
    button.setAttribute('aria-pressed', String(isCurrent));
  });
}

stateButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setUsed(Number(button.dataset.used));
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
window.renderAntigravityQuota = renderAntigravityQuota;
setUsed(.2);
let initialPage = 'codex';
try { initialPage = sessionStorage.getItem('quota-card-page') || 'codex'; } catch (_error) { /* default Codex */ }
showCardPage(initialPage, false);
fetchAntigravityQuota();
window.setInterval(fetchAntigravityQuota, 60000);
