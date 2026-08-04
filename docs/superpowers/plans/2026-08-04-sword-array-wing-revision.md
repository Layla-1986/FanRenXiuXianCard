# Sword Array and Wing Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Great Geng formation read as a lively rotating circle with static balance-count swords, and turn the Wind-Thunder Wings into a small vertical progress marker with source-faithful colors.

**Architecture:** Keep the single-file prototype and its `--used` state contract. Add twelve static sword slots whose active count is controlled by a remaining-balance class, while independent ring, rune, ripple, and particle layers rotate beneath them. Reuse the local wing texture through the existing SVG viewport, then rotate and recolor it with CSS filters and lightning overlays.

**Tech Stack:** HTML, CSS animations, inline SVG, vanilla JavaScript, PowerShell structural tests, local browser verification.

## Global Constraints

- Keep the floating card at exactly 480 × 270 pixels.
- Preserve `--used`, `#percent`, `#used`, the three demo buttons, the unlock button, and the current background.
- Do not change `index.html` or connect a live usage API.
- Respect `prefers-reduced-motion` by disabling continuous movement and flashing.

---

### Task 1: Lock the revised visual contract in tests

**Files:**
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `original-artifact-refined.html` as UTF-8 text.
- Produces: assertions for twelve sword slots, three balance classes, static sword animation, rotating rings, and the vertical compact wing dimensions.

- [ ] **Step 1: Add failing assertions**

```powershell
Assert-True (($html | Select-String 'class="formation-sword' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve sword slots'
Assert-True ($html.Contains("widget.classList.remove('balance-high','balance-mid','balance-low')")) 'Updater must clear balance classes'
Assert-True ($html.Contains("widget.classList.add(balanceClass)")) 'Updater must apply a balance class'
Assert-True ($html.Contains('width:42px;height:24px')) 'Wing marker must be compact'
Assert-True ($html.Contains('rotate:90deg')) 'Wing marker must be vertical'
```

- [ ] **Step 2: Run the contract test and confirm RED**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: FAIL for missing sword slots, balance classes, and compact wing geometry.

- [ ] **Step 3: Commit the test after implementation passes**

Run: `git add tests/visual-spec.ps1 original-artifact-refined.html && git commit -m "优化剑阵余额联动与竖向风雷翅"`

---

### Task 2: Rebuild the Great Geng formation

**Files:**
- Modify: `original-artifact-refined.html`

**Interfaces:**
- Consumes: `--used` and one of `.balance-high`, `.balance-mid`, `.balance-low` on `#widget`.
- Produces: `.formation-rings`, `.formation-runes`, `.formation-particles`, `.formation-ripple`, and twelve `.formation-sword` elements.

- [ ] **Step 1: Replace node markers with twelve static swords**

```html
<span class="formation-swords" aria-hidden="true">
  <i class="formation-sword"></i><i class="formation-sword"></i><i class="formation-sword"></i>
  <i class="formation-sword"></i><i class="formation-sword"></i><i class="formation-sword"></i>
  <i class="formation-sword"></i><i class="formation-sword"></i><i class="formation-sword"></i>
  <i class="formation-sword"></i><i class="formation-sword"></i><i class="formation-sword"></i>
</span>
```

- [ ] **Step 2: Add independent moving layers**

```html
<i class="formation-rings"></i><i class="formation-runes"></i>
<i class="formation-particles"></i><i class="formation-ripple"></i>
```

Use clockwise rotation for `.formation-rings`, counter-clockwise rotation for `.formation-runes`, a pulsing scale for `.formation-ripple`, and circular background-position movement for `.formation-particles`. Do not assign animation to `.formation-swords` or `.formation-sword`.

- [ ] **Step 3: Map balance classes to lit sword counts**

```css
.balance-high .formation-sword:nth-child(-n+10),
.balance-mid .formation-sword:nth-child(-n+5),
.balance-low .formation-sword:nth-child(-n+2){opacity:1;filter:drop-shadow(0 0 5px #e7dc67) drop-shadow(0 0 10px #79d98e)}
```

All remaining sword slots retain `opacity:.16` and an antique-gold outline. Arrange the twelve slots at 30-degree increments with fixed transforms and a common transform origin.

- [ ] **Step 4: Adjust source-faithful palette**

Use ink green `#071912`, jade `#70d692`, pale gold `#dfc963`, and warm sword edge `#f1e39a`. Keep the supplied Great Geng texture below 35% opacity so the new sword count remains legible.

---

### Task 3: Convert the Wind-Thunder Wings to a vertical compact marker

**Files:**
- Modify: `original-artifact-refined.html`

**Interfaces:**
- Consumes: the existing `.wing-asset`, `.lightning`, `.wing-core`, and `--used` position formula.
- Produces: a 42 × 24 pixel marker rotated 90 degrees with silver-white, cyan-white, and pale-gold effects.

- [ ] **Step 1: Set compact vertical geometry**

```css
.wind-thunder-wings{width:42px;height:24px;rotate:90deg;transform-origin:50% 50%}
.lightning{width:38px;height:28px;rotate:90deg}
.wing-core{width:10px;height:10px}
```

Keep `left:calc(4% + var(--used)*92%)` for all three layers and vertically align their centers to the rail center.

- [ ] **Step 2: Recolor the texture and lightning**

Apply reduced saturation, a slight green-cyan hue shift, and higher brightness to `.wing-asset`. Use silver-white `#eaf8f3` for primary lightning and pale gold `#e4c96a` for the secondary arc; remove purple glow values.

- [ ] **Step 3: Retune motion**

Limit wing breathing to 2% scale variation and lightning opacity variation to a slow, non-strobing pulse. Preserve the existing progress transition.

---

### Task 4: Extend usage-state mapping and verify

**Files:**
- Modify: `original-artifact-refined.html`
- Test: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `setUsed(value: number)`.
- Produces: `.balance-high` for remaining balance at least 70%, `.balance-mid` for at least 30%, and `.balance-low` below 30%.

- [ ] **Step 1: Add balance-class mapping**

```javascript
const remaining=1-safe;
const balanceClass=remaining>=.7?'balance-high':remaining>=.3?'balance-mid':'balance-low';
widget.classList.remove('balance-high','balance-mid','balance-low');
widget.classList.add(balanceClass);
```

Call `setUsed(.2)` after event listeners are registered so the initial sword state is deterministic.

- [ ] **Step 2: Run structural verification**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1`

Expected: PASS with twelve sword slots, balance mapping, compact wing, local assets, and reduced-motion treatment.

- [ ] **Step 3: Verify browser states**

Open `http://127.0.0.1:55569/original-artifact-refined.html` and verify:

- 20% used: `80%`, ten bright static swords, vertical wing at 20%.
- 55% used: `45%`, five bright static swords, vertical wing at 55%.
- 85% used: `15%`, two bright static swords, vertical wing at 85%.
- 523 × 792 viewport: no horizontal overflow.
- Reduced motion: no ring rotation, particle flow, ripple, or lightning animation.

- [ ] **Step 4: Final verification and commit**

Run: `git diff --check` and repeat the PowerShell contract test. Commit only when both commands exit successfully.
