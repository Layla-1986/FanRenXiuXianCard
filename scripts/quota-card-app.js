(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MortalQuotaCard = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const POINTS_PER_USD = 25;

  function finite(value) {
    if (value === null || value === undefined || value === '') return null;
    const number = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function percent(value) {
    const number = finite(value);
    return number !== null && number >= 0 && number <= 100 ? `${number}%` : '—';
  }

  function usdFromPoints(value) {
    const points = finite(value);
    return points !== null && points >= 0 ? `$${(points / POINTS_PER_USD).toFixed(2)}` : '—';
  }

  function dateLabel(value) {
    const seconds = finite(value);
    if (seconds === null || seconds < 0) return '待同步';
    const date = new Date(seconds * 1000);
    if (Number.isNaN(date.getTime())) return '待同步';
    return new Intl.DateTimeFormat('zh-CN', {
      month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false
    }).format(date).replace(/\//g, '月').replace(/日?\s/, '日 ');
  }

  function resetCreditLabel(credits) {
    if (!credits || finite(credits.availableResetCount) === null) return '重置卡信息待同步';
    if (Number(credits.availableResetCount) === 0) return '暂无可用重置卡';
    const expiry = dateLabel(credits.nearestResetCreditExpiresAt);
    return expiry === '待同步' ? `${credits.availableResetCount} 张重置卡` : `${credits.availableResetCount} 张 · ${expiry} 到期`;
  }

  function text(doc, id, value) {
    const element = doc && doc.getElementById(id);
    if (element) element.textContent = value;
  }

  function renderCodex(doc, data) {
    const five = data && data.fiveHour || {};
    const weekly = data && data.weekly || {};
    const credits = data && data.credits || {};
    text(doc, 'weeklyPercent', percent(weekly.remainingPercent));
    text(doc, 'fiveHourPercent', five.remainingPercent == null ? '余—' : `余${percent(five.remainingPercent)}`);
    text(doc, 'fiveHourReset', five.resetsAt == null ? '待同步' : `${dateLabel(five.resetsAt)} 重置`);
    text(doc, 'weeklyUsed', weekly.usedPercent == null ? '已用—' : `已用${percent(weekly.usedPercent)}`);
    text(doc, 'weeklyReset', weekly.resetsAt == null ? '待同步' : `${dateLabel(weekly.resetsAt)} 重置`);
    text(doc, 'creditBalance', usdFromPoints(credits.balance));
    text(doc, 'resetCreditExpiry', resetCreditLabel(credits));
    text(doc, 'codexStatus', data && data.status === 'fresh' ? '已同步' : data && data.status === 'stale' ? '缓存' : '待同步');
    text(doc, 'planType', data && data.planType ? String(data.planType).toUpperCase() : '—');
  }

  function renderAntigravity(doc, data) {
    const gemini = data && data.gemini || {};
    const claude = data && data.claudeGpt || {};
    text(doc, 'agCredits', data && data.aiCredits != null ? `可用灵石 ${data.aiCredits}` : '可用灵石 —');
    const fields = [
      ['agGeminiWeekly', gemini.weeklyRemaining], ['agGeminiFiveHour', gemini.fiveHourRemaining],
      ['agClaudeWeekly', claude.weeklyRemaining], ['agClaudeFiveHour', claude.fiveHourRemaining]
    ];
    fields.forEach(([id, value]) => text(doc, id, percent(value)));
    text(doc, 'agGeminiWeeklyReset', gemini.weeklyReset || '待同步');
    text(doc, 'agGeminiFiveHourReset', gemini.fiveHourReset || '待同步');
    text(doc, 'agClaudeWeeklyReset', claude.weeklyReset || '待同步');
    text(doc, 'agClaudeFiveHourReset', claude.fiveHourReset || '待同步');
  }

  function start() {
    const frames = [document.getElementById('page-codex'), document.getElementById('page-antigravity')];
    const pageSwitch = document.getElementById('page-switch');
    const lockButton = document.getElementById('lock-button');
    const dragSurface = document.getElementById('drag-surface');
    let page = 'codex';
    let locked = false;

    function show(next) {
      page = next === 'antigravity' ? 'antigravity' : 'codex';
      frames[0].hidden = page !== 'codex';
      frames[1].hidden = page !== 'antigravity';
      const destination = page === 'codex' ? 'Antigravity' : 'Codex';
      pageSwitch.setAttribute('aria-label', `切换到 ${destination}`);
      pageSwitch.title = `切换到 ${destination}`;
    }

    async function bridge(name, ...args) {
      const api = window.pywebview && window.pywebview.api;
      return api && typeof api[name] === 'function' ? api[name](...args) : null;
    }

    pageSwitch.addEventListener('click', async () => {
      show(page === 'codex' ? 'antigravity' : 'codex');
      await bridge('save_page', page);
    });
    dragSurface.addEventListener('mousedown', event => {
      if (event.button === 0) bridge('begin_drag');
    });
    function reflectLocked(value) {
      locked = Boolean(value);
      lockButton.setAttribute('aria-pressed', String(locked));
      lockButton.title = locked ? '已锁定；按 Ctrl+Alt+L 解锁' : '锁定位置并启用鼠标穿透';
    }
    window.addEventListener('mortalquota:lock-state', event => reflectLocked(event.detail));
    lockButton.addEventListener('click', async () => {
      reflectLocked(!locked);
      await bridge('set_locked', locked);
    });

    async function refreshCodex() {
      try {
        const response = await fetch('/api/codex-quota', { cache: 'no-store' });
        renderCodex(frames[0].contentDocument, response.ok ? await response.json() : null);
      } catch (_) { renderCodex(frames[0].contentDocument, null); }
    }
    async function refreshAntigravity() {
      try {
        const response = await fetch('/api/antigravity-quota', { cache: 'no-store' });
        renderAntigravity(frames[1].contentDocument, response.ok ? await response.json() : null);
      } catch (_) { renderAntigravity(frames[1].contentDocument, null); }
    }
    frames.forEach((frame, index) => frame.addEventListener('load', index ? refreshAntigravity : refreshCodex));
    window.addEventListener('pywebviewready', async () => {
      const state = await bridge('get_app_state');
      if (state) show(state.page);
    });
    show('codex');
    refreshCodex(); refreshAntigravity();
    setInterval(refreshCodex, 15000);
    setInterval(refreshAntigravity, 60000);
  }

  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
  }
  return { percent, usdFromPoints, dateLabel, resetCreditLabel, renderCodex, renderAntigravity };
});
