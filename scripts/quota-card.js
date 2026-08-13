'use strict';

const widget = document.querySelector('#widget');
const percent = document.querySelector('#percent');
const usedLabel = document.querySelector('#used');
const swords = [...document.querySelectorAll('.formation-sword')];
const swordPairs = [[5, 6], [4, 7], [3, 8], [2, 9], [1, 10], [0, 11]];
const stateButtons = [...document.querySelectorAll('[data-used]')];
const unlockButton = document.querySelector('#unlockButton');

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

window.setUsed = setUsed;
setUsed(.2);
